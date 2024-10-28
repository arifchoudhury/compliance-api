import re
from flask import current_app
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from email_validator import validate_email, EmailNotValidError
from app.extensions import db
from compliance_lib_schemas.models import ThirdPartyContact, Identifier, Channel

class ThirdPartyContactManager:
    def __init__(self):
        self.session = db.session

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
        
    def add_contact(self, contact_data):
        try:
            fullname = contact_data.get("fullname")
            email = contact_data.get("email")

            new_contact = ThirdPartyContact(fullname=fullname, email=email)
            self.session.add(new_contact)
            self.session.flush()  # Flush to get the new contact ID

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

            self.session.commit()
            return {"message": "Contact created successfully", "contact_id": new_contact.id}, 201
        except IntegrityError as e:
            self.session.rollback()
            error_info = str(e.orig)
            if 'UNIQUE constraint failed' in error_info:
                if 'fullname' in error_info:
                    return {"error": f"Fullname '{fullname}' already exists."}, 400
                elif 'email' in error_info:
                    return {"error": f"Email '{email}' already exists."}, 400
            return {"error": error_info}, 500

        except SQLAlchemyError as e:
            self.session.rollback()
            return {"error": str(e)}, 500

    def update_contact(self, contact_id, contact_data):
        try:
            contact = self.session.query(ThirdPartyContact).filter_by(id=contact_id).first()
            if not contact:
                return {"error": "Contact not found."}, 404

            # Ensure fullname and email cannot be changed
            if 'fullname' in contact_data and contact_data['fullname'] != contact.fullname:
                return {"error": "Fullname cannot be changed."}, 400

            if 'email' in contact_data and contact_data['email'] != contact.email:
                return {"error": "Email cannot be changed."}, 400

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

    def get_contact_with_identifiers(self, contact_id=None, contact_fullname=None):
        contacts_query = self.session.query(ThirdPartyContact)
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
                "email": contact.email
            }
                    
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

            result.append(contact_info)

        return result if not (contact_id or contact_fullname) else result[0] if result else None
