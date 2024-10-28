import re
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from email_validator import validate_email, EmailNotValidError
from flask import current_app

from app.extensions import db
from compliance_lib_schemas.models import (
    RecordedContact, 
    RecordedContactAttribute, 
    RecordedContactAttributeAssociation,
    RecordedContactRetentionPolicy,
    Channel,
    Identifier,
    RetentionPolicy
)

class RecordedContactManager:
    def __init__(self):
        self.session = db.session

    def get_existing_association(self, contact_id, attribute_id):
        return self.session.query(RecordedContactAttributeAssociation).filter_by(
            recorded_contact_id=contact_id,
            recorded_contact_attribute_id=attribute_id,
            associated=True
        ).first()

    def get_existing_identifier(self, contact_id, channel_id, identifier_value):
        return self.session.query(Identifier).filter_by(
            recorded_contact_id=contact_id,
            channel_id=channel_id,
            identifier=identifier_value,
            associated=True
        ).first()
        
    def validate_email_format(self, email):
        try:
            v = validate_email(email)
            return True
        except EmailNotValidError:
            return False
        
    def add_identifier_to_contact(self, contact_id, channel_name, identifier):
        
        channel = self.session.query(Channel).filter_by(name=channel_name).first()
        
        current_app.logger.info(channel)
        
        store = Identifier(
            identifier=identifier,
            channel=channel,
            contact_id=contact_id
        )
        self.session.add(store)
        self.session.flush()
    
    def disassociate_identifier_from_contact(self, identifier, contact_id):
        
        i = self.session.query(Identifier).filter_by(contact_id=contact_id, identifier=identifier, associated=True).first()
        
        if i:
            i.associated = False
            i.date_disassociated = datetime.now()
            
        self.session.add(i)
        
    def check_associated_value_exists(self, attribute_id, associated_value):
        try:
            # Query the RecordedContactAttributeAssociation table to check if the associated value exists
            association = (
                self.session.query(RecordedContactAttributeAssociation)
                .filter_by(
                    recorded_contact_attribute_id=attribute_id,
                    associated_value=associated_value,
                    associated=True
                )
                .first()
            )
            
            if association:
                recorded_contact = association.recorded_contact
                return {
                    "contact_id": recorded_contact.id,
                    "fullname": recorded_contact.fullname,
                    "email": recorded_contact.email
                }
            else:
                return {}
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e  # Propagate the exception for handling at a higher level

    def add_contact(self, contact_data):
        try:
            fullname = contact_data.get("fullname")
            email = contact_data.get("email")
            retention_policy = contact_data.get("retention_policy")

            # Validate fullname
            if not fullname:
                return {"error": "fullname is required."}, 400

            # Validate email format
            if not email or not self.validate_email_format(email):
                return {"error": "Valid email is required."}, 400
                        
            existing_contact = self.session.query(RecordedContact).filter_by(email=email).first()
            if existing_contact:
                return {"error": f"email {email} is already in use."}, 400
            
            existing_retention_policy = self.session.query(RetentionPolicy).filter_by(name=retention_policy).first()
            if not existing_retention_policy:
                return {"error": f"retention policy {retention_policy} does not exist."}, 400
            
            new_contact = RecordedContact(fullname=fullname, email=email)
            self.session.add(new_contact)
            self.session.flush()  # Flush to get the new contact ID

            # Process attributes (assuming attributes other than fullname and email)
            for attribute_name, attribute_value in contact_data.items():
                if attribute_name not in ["fullname", "email", "channels", "retention_policy"]:
                    attribute = self.session.query(RecordedContactAttribute).filter_by(name=attribute_name).first()
                    
                    if not attribute:
                        # self.session.rollback()  # Rollback the session to discard the changes
                        return {"error": f"Attribute '{attribute_name}' does not exist."}, 400

                    # Perform attribute checks
                    if attribute.regex and attribute_value:
                        if not re.match(attribute.regex, attribute_value):
                            return {"error": f"Value '{attribute_value}' does not match regex for attribute '{attribute_name}'."}, 400

                    if attribute.required and not attribute_value:
                        return {"error": f"Attribute '{attribute_name}' is required."}, 400
                    
                    if attribute.unique:
                        associated_value_exists = self.check_associated_value_exists(attribute.id, attribute_value)
                        if associated_value_exists:
                            return {
                                "error": (
                                    f"Attribute '{attribute_name}' must have unique values, but the value '{attribute_value}' "
                                    f"is already associated with contact ID: {associated_value_exists['contact_id']}, "
                                    f"Name: {associated_value_exists['fullname']}, "
                                    f"Email: {associated_value_exists['email']}"
                                )
                            }, 400

                    attribute_association = RecordedContactAttributeAssociation(
                        recorded_contact_id=new_contact.id,
                        recorded_contact_attribute_id=attribute.id,
                        associated_value=attribute_value
                    )
                    self.session.add(attribute_association)

            # Process channels and identifiers
            channels = contact_data.get("channels", {})
            for channel_name, identifiers in channels.items():
                channel = self.session.query(Channel).filter_by(name=channel_name).first()
                if not channel:
                    self.session.rollback()  # Rollback the session to discard the changes
                    return {"error": f"Channel '{channel_name}' does not exist."}, 400

                for identifier_value in identifiers:
                    identifier = self.session.query(Identifier).filter_by(identifier=identifier_value, associated=True).first()
                    if identifier:
                        return {"error": f"Identifier {identifier_value} is alreaedy associated to contact {identifier.contact.fullname}"}, 400
                    identifier = Identifier(identifier=identifier_value, recorded_contact_id=new_contact.id, channel_id=channel.id)
                    self.session.add(identifier)
                    
            contact_retention_policy_association = RecordedContactRetentionPolicy(
                retention_policy=existing_retention_policy,
                recorded_contact=new_contact
            )
            self.session.add(contact_retention_policy_association)

            self.session.commit()
            return {"message": "Contact created successfully", "contact_id": new_contact.id}, 201
        except IntegrityError as e:
            self.session.rollback()
            error_info = str(e.orig)
            # if 'UNIQUE constraint failed' in error_info:
            #     if 'fullname' in error_info:
            #         return {"error": f"Fullname '{fullname}' already exists."}, 400
            #     elif 'email' in error_info:
            #         return {"error": f"Email '{email}' already exists."}, 400
            return {"error": error_info}, 500

        except SQLAlchemyError as e:
            self.session.rollback()
            return {"error": str(e)}, 500

    def update_contact(self, contact_id, contact_data):
        try:
            contact = self.session.query(RecordedContact).filter_by(id=contact_id).first()
            if not contact:
                return {"error": "Contact not found."}, 404

            # Ensure fullname and email cannot be changed
            if 'fullname' in contact_data and contact_data['fullname'] != contact.fullname:
                return {"error": "Fullname cannot be changed."}, 400

            if 'email' in contact_data and contact_data['email'] != contact.email:
                return {"error": "Email cannot be changed."}, 400
            
            existing_retention_policy_association = None
            for policy_association in contact.recorded_contact_retention_policies:
                if policy_association.associated:
                    existing_retention_policy_association = policy_association
                    break
                
            if 'retention_policy' in contact_data and contact_data['retention_policy'] != policy_association.retention_policy.name:
                new_retention_policy = self.session.query(RetentionPolicy).filter_by(name=contact_data['retention_policy']).first()
                if not new_retention_policy:
                    return {"error": f"retention policy {contact_data['retention_policy']} not found"}, 400

                existing_retention_policy_association.associated = False
                existing_retention_policy_association.date_disassociated = datetime.now()
                
                recorded_contact_retention_policy = RecordedContactRetentionPolicy(
                    recorded_contact = contact,
                    retention_policy = new_retention_policy
                )
                
                self.session.add(recorded_contact_retention_policy)
            
            # TODO Need to do!!!
            # if 'retention_policy' in contact_data and contact_data['retention_policy'] != contact.email:
            #     return {"error": "Email cannot be changed."}, 400

            # Process attributes (assuming attributes other than fullname and email)
            for attribute_name, attribute_value in contact_data.items():
                if attribute_name not in ["id", "fullname", "email", "channels", "retention_policy"]:
                    attribute = self.session.query(RecordedContactAttribute).filter_by(name=attribute_name).first()
                    
                    if not attribute:
                        # self.session.rollback()  # Rollback the session to discard the changes
                        return {"error": f"Attribute '{attribute_name}' does not exist."}, 400

                    # Perform attribute checks
                    if attribute.regex and attribute_value:
                        if not re.match(attribute.regex, attribute_value):
                            return {"error": f"Value '{attribute_value}' does not match regex for attribute '{attribute_name}'."}, 400

                    if attribute.required and not attribute_value:
                        return {"error": f"Attribute '{attribute_name}' is required."}, 400

                    if attribute.unique:
                        associated_value_exists = self.check_associated_value_exists(attribute.id, attribute_value)
                        if associated_value_exists:
                            if associated_value_exists['contact_id'] != contact.id:
                                return {
                                    "error": (
                                        f"Attribute '{attribute_name}' must have unique values, but the value '{attribute_value}' "
                                        f"is already associated with contact ID: {associated_value_exists['contact_id']}, "
                                        f"Name: {associated_value_exists['fullname']}, "
                                        f"Email: {associated_value_exists['email']}"
                                    )
                                }, 400

                    # Check if the attribute value has changed
                    existing_association = self.get_existing_association(contact.id, attribute.id)
                    if existing_association and existing_association.associated_value != attribute_value:
                        existing_association.associated = False
                        existing_association.date_disassociated = datetime.now()
                        self.session.add(existing_association)

                        new_association = RecordedContactAttributeAssociation(
                            recorded_contact_id=contact.id,
                            recorded_contact_attribute_id=attribute.id,
                            associated_value=attribute_value
                        )
                        self.session.add(new_association)
                    elif not existing_association:
                        new_association = RecordedContactAttributeAssociation(
                            recorded_contact_id=contact.id,
                            recorded_contact_attribute_id=attribute.id,
                            associated_value=attribute_value
                        )
                        self.session.add(new_association)

            # Process channels and identifiers
            channels = contact_data.get("channels", {})
            for channel_name, identifiers in channels.items():
                channel = self.session.query(Channel).filter_by(name=channel_name).first()
                if not channel:
                    # self.session.rollback()  # Rollback the session to discard the changes
                    return {"error": f"Channel '{channel_name}' does not exist."}, 400

                existing_identifiers = {identifier.identifier for identifier in self.session.query(Identifier).filter_by(recorded_contact_id=contact.id, channel_id=channel.id, associated=True).all()}

                # Add new identifiers
                for identifier_value in identifiers:
                    if identifier_value not in existing_identifiers:
                        new_identifier = Identifier(identifier=identifier_value, recorded_contact_id=contact.id, channel_id=channel.id)
                        self.session.add(new_identifier)

                # Disassociate removed identifiers
                for identifier_value in existing_identifiers:
                    if identifier_value not in identifiers:
                        existing_identifier = self.get_existing_identifier(contact.id, channel.id, identifier_value)
                        existing_identifier.associated = False
                        existing_identifier.date_disassociated = datetime.now()
                        self.session.add(existing_identifier)

            self.session.commit()
            return {"message": "Contact updated successfully"}, 200

        except SQLAlchemyError as e:
            self.session.rollback()
            return {"error": str(e)}, 500

    def get_contact_with_attributes_and_identifiers(self, contact_id=None, contact_fullname=None):
        contacts_query = self.session.query(RecordedContact)
        if contact_id:
            contacts_query = contacts_query.filter_by(id=contact_id)
        if contact_fullname:
            contacts_query = contacts_query.filter_by(fullname=contact_fullname)

        contacts = contacts_query.all()
        result = []
        
        for contact in contacts:
            contact_info = {
                "id": contact.id,
                "fullname": contact.fullname,
                "email": contact.email,
            }
            
            associated_retention_policy = None
            for policy_association in contact.recorded_contact_retention_policies:
                if policy_association.associated:
                    associated_retention_policy = policy_association
                    break
                
            contact_info["retention_policy"] = associated_retention_policy.retention_policy.name
            
            associations = self.session.query(RecordedContactAttributeAssociation).filter_by(recorded_contact_id=contact.id, associated=True).all()
            for assoc in associations:
                attribute = self.session.query(RecordedContactAttribute).filter_by(id=assoc.recorded_contact_attribute_id).first()
                contact_info[attribute.name] = assoc.associated_value
                    
            # Initialize the channels dictionary
            contact_info['channels'] = {}

            # Query all channels
            channels = self.session.query(Channel).all()
            for channel in channels:
                contact_info['channels'][channel.name] = []

            # Get all associated identifiers for the contact
            identifiers = self.session.query(Identifier).filter_by(recorded_contact_id=contact.id, associated=True).all()

            # Loop through each identifier and append to the correct channel
            for identifier in identifiers:
                channel = next((ch for ch in channels if ch.id == identifier.channel_id), None)
                if channel:
                    contact_info['channels'][channel.name].append(identifier.identifier)

            # # Get channels and identifiers
            # contact_info['channels'] = {}
            # identifiers = self.session.query(Identifier).filter_by(contact_id=contact.id, associated=True).all()
            # for identifier in identifiers:
            #     channel = self.session.query(Channel).filter_by(id=identifier.channel_id).first()
            #     if channel.name not in contact_info['channels']:
            #         contact_info['channels'][channel.name] = []
            #     contact_info['channels'][channel.name].append(identifier.identifier)

            result.append(contact_info)

        return result if not (contact_id or contact_fullname) else result[0] if result else None
