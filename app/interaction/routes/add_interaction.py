from app.extensions import db
from app.interaction.routes import interaction_blueprint
from compliance_lib_schemas.models import Interaction, Channel, Identifier, ThirdPartyContact, RecordedContact

from datetime import datetime, timedelta

from flask import jsonify, current_app, request

@interaction_blueprint.route("", methods=["POST"])
def add_interaction():
    
    interaction_info = request.get_json()
    
    channel = db.session.query(Channel).filter_by(name=interaction_info['channel']).first()
    
    if not channel:
        return jsonify({"success": False, "message": f"Channel type {interaction_info['channel']} does not exist!"}), 400
    
    interaction = db.session.query(Interaction).filter_by(external_id=interaction_info['external_id']).first()
    
    if interaction:
        db.session.delete(interaction)
    
    recorded_identifier = db.session.query(Identifier).filter_by(
        channel_id=channel.id,
        identifier=interaction_info['recorded_identifier'], 
        associated=True
    ).first()
    
    if not recorded_identifier:
        return jsonify({"success": False, "message": f"Recorded identifier {interaction_info['recorded_identifier']} is not currently associated to any contact for channel type {interaction_info['channel']}"}), 400
    
    third_party_identifier = db.session.query(Identifier).filter_by(identifier=interaction_info['third_party_identifier'], associated=True).first()
    
    if not third_party_identifier:
        # create a blank contact to store
        third_party_contact = ThirdPartyContact()
        third_party_identifier = Identifier(
            identifier = interaction_info['third_party_identifier'],
            third_party_contact = third_party_contact,
            channel = channel
        )
        db.session.add(third_party_identifier)
        
    associated_retention_policy = next(
        (policy for policy in recorded_identifier.recorded_contact.recorded_contact_retention_policies if policy.associated), 
        None
    )    
    
    interaction_start_time = datetime.strptime(interaction_info["start_time"], "%Y-%m-%dT%H:%M:%S")
    interaction_end_time = datetime.strptime(interaction_info["end_time"], "%Y-%m-%dT%H:%M:%S")

    retention_end_date = interaction_start_time + timedelta(days=associated_retention_policy.retention_policy.call_retention_days)
        
    interaction = Interaction(
        channel = channel,
        external_id = interaction_info['external_id'],
        start_time = interaction_start_time,
        end_time = interaction_end_time,
        withheld = interaction_info['withheld'],
        direction = interaction_info['direction'],
        recorded_identifier = recorded_identifier,
        third_party_identifier = third_party_identifier,
        retention_end_date = retention_end_date
    )
    
    db.session.add(interaction)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "interaction stored"}), 200
    except Exception as err:
        db.session.rollback()
        return jsonify({"success": False, "message": f"failed to store interaction: {err}"}), 500
    
    # contact_manager = ContactManager()
    
    # recorded_contact = contact_manager.get_contact_with_attributes_and_identifiers(
    #     contact_type='recorded', 
    #     contact_fullname=interaction_info['recorded_contact']['fullname']
    # )
    
    # if recorded_contact:
    #     if recorded_contact['channels']:
    #         if interaction_info['recorded_identifier'] not in recorded_contact['channels'][interaction_info['type']]:
    #             contact_manager.add_identifier_to_contact(
    #                 contact_id=recorded_contact['id'], 
    #                 channel_name=interaction_info['type'], 
    #                 identifier=interaction_info['recorded_identifier']
    #             )
    # else:
    #     contact_data = interaction_info['recorded_contact']
    #     contact_data[interaction_info['type']] = [interaction_info["recorded_identifier"]]
    #     recorded_contact = contact_manager.add_contact(contact_data, contact_type='recorded')
    
    # third_party_contact = contact_manager.get_contact_with_attributes_and_identifiers(
    #     contact_type='third_party', 
    #     contact_fullname=interaction_info['third_party_contact']['fullname']
    # )
    
    # if third_party_contact:
    #     current_app.logger.info(third_party_contact)
    #     if third_party_contact['channels']:
    #         if interaction_info['third_party_identifier'] not in third_party_contact['channels'][interaction_info['type']]:
    #             contact_manager.add_identifier_to_contact(
    #                 contact_id=third_party_contact['id'], 
    #                 channel_name=interaction_info['type'], 
    #                 identifier=interaction_info['third_party_identifier']
    #             )
    # else:
    #     current_app.logger.info("third party contact does not exist, creating")
    #     contact_data = interaction_info['third_party_contact']
    #     contact_data[interaction_info['type']] = [interaction_info["third_party_identifier"]]
    #     third_party_contact = contact_manager.add_contact(contact_data, contact_type='third_party')
        
        
    # # current_app.logger.info(recorded_contact)
    # # current_app.logger.info(third_party_contact)
    
    # recorded_identifier = db.session.query(Identifier).filter_by(identifier=interaction_info['recorded_identifier'], associated=True).first()
    # third_party_identifier = db.session.query(Identifier).filter_by(identifier=interaction_info['third_party_identifier'], associated=True).first()
    
    # # current_app.logger.info(recorded_identifier)
    # # current_app.logger.info(third_party_identifier)
    
    # current_app.logger.info(recorded_contact)
    

    # interaction = Interaction(
    #     external_id = interaction_info['external_id'],
    #     start_time = interaction_info['start_time'],
    #     end_time = interaction_info['end_time'],
    #     withheld = interaction_info['withheld'],
    #     direction = interaction_info['direction'],
    #     recorded_identifier = recorded_identifier,
    #     third_party_identifier = third_party_identifier
    # )
    
    # db.session.add(interaction)
    
    # try:
    #     db.session.commit()
    #     return jsonify({"success": True, "message": "interaction stored"}), 200
    # except Exception as err:
    #     return jsonify({"success": False, "message": f"failed to store interaction: {err}"}), 500


    # recorded_identifier = db.session.query(Identifier).filter_by(
    #     identifier=interaction_info['recorded_identifier'], 
    #     associated=True
    # ).first()
    
    # if not recorded_identifier:
    #     recorded_contact = interaction_info['recorded_contact']
    #     recorded_contact['channels'] = {
    #         interaction_info['type'] : [interaction_info['recorded_identifier']]
    #     } 
    #     try:
    #         contact_manager = ContactManager()
    #         recorded_contact, status_code = contact_manager.add_contact(contact_data=recorded_contact, contact_type="recorded")
    #         if status_code != 201:
    #             db.session.rollback()
    #             return jsonify(f"{recorded_contact}"), status_code
    #         recorded_identifier = next((identifier for identifier in recorded_contact.identifiers if identifier.identifier == interaction_info['recorded_identifier']), None)
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({"error": str(e)}), 500
    # else:
    #     recorded_contact = recorded_identifier.contact
    #     # TODO need to add the below logic
    #     # identifier already exists, see if the contact is the same
    #     # if recorded_identifier.contact.fullname:
    #     #     if recorded_identifier.contact.fullname == interaction_info['recorded_contact']['fullname']:
    #     #         # its the same contact - we only check the fullname matches
    #     #         pass
    #     #     else:
    #     #         # contact has changed, we need to handle this!
    #     #         pass
    #     # else:
    #     #     # we have no way of checking if the contact is the same or not, just leave it be!
    #     #     pass
        
    # third_party_identifier = db.session.query(Identifier).filter_by(
    #     identifier=interaction_info['third_party_identifier'], 
    #     associated=True
    # ).first()
    
    # if not third_party_identifier:
    #     third_party_contact = interaction_info['third_party_contact']
    #     third_party_contact['channels'] = {
    #         interaction_info['type'] : [interaction_info['third_party_identifier']]
    #     } 
    #     try:
    #         contact_manager = ContactManager()
    #         third_party_contact, status_code = contact_manager.add_contact(contact_data=interaction_info["third_party_contact"], contact_type="third_party")
    #         if status_code != 201:
    #             db.session.rollback()
    #             return jsonify(f"{third_party_contact}"), status_code
    #         third_party_identifier = next((identifier for identifier in recorded_contact.identifiers if identifier.identifier == interaction_info['third_party_identifier']), None)
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({"error": str(e)}), 500
    # else:
    #     third_party_contact = third_party_identifier.contact
    #     # TODO need to add the below logic
    #     # identifier already exists, see if the contact is the same
    #     # if third_party_identifier.contact.fullname:
    #     #     if third_party_identifier.contact.fullname == interaction_info['third_party_contact']['fullname']:
    #     #         # its the same contact - we only check the fullname matches
    #     #         pass
    #     #     else:
    #     #         # contact has changed, we need to handle this!
    #     #         pass
    #     # else:
    #     #     # we have no way of checking if the contact is the same or not, just leave it be!
    #     #     pass

    
    # interaction = Interaction(
    #     external_id = interaction_info['external_id'],
    #     start_time = interaction_info['start_time'],
    #     end_time = interaction_info['end_time'],
    #     withheld = interaction_info['withheld'],
    #     direction = interaction_info['direction'],
    #     recorded_identifier = recorded_identifier,
    #     third_party_identifier = third_party_identifier
    # )
    
