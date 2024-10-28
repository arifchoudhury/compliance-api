import json
from datetime import datetime
from flask import request, jsonify, current_app
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.recorded_contact.routes import recorded_contact_blueprint
from app.recorded_contact.schemas import AttributeSchema
from compliance_lib_schemas.models import RecordedContactAttribute, RecordedContactAudit, RecordedContact, RecordedContactAuditTypeEnum, Playlist
from app.playlist.tasks import associate_interactions_to_playlist
# from app.recorded_contact.schemas import RecordedContactAuditSchema

@recorded_contact_blueprint.route("/audit", methods=["GET"])
def get_recorded_contacts_audits():
    recorded_contacts = (
        db.session.query(RecordedContact)
        .options(joinedload(RecordedContact.audits).joinedload(RecordedContactAudit.playlist))
        .all()
    )

    result = []
    for contact in recorded_contacts:
        contact_info = {
            "id": contact.id,
            "fullname": contact.fullname,
            "email": contact.email,
            "audits": [],
            "last_audit_dates": contact.get_last_audit_date_by_type(db.session)  # Get last audit dates by type
        }

        for audit in contact.audits:
            audit_info = {
                "id": audit.id,
                "audit_notes": audit.audit_notes,
                "audit_type": audit.audit_type.value,
                "audit_start_date": audit.audit_start_date,
                "audit_end_date": audit.audit_end_date,
                "playlist": {
                    "id": audit.playlist.id,
                    "name": audit.playlist.name,
                    "description": audit.playlist.description,
                    "created_by_id": audit.playlist.created_by_id,
                    "status": audit.playlist.status,
                    "error_message": audit.playlist.error_message,
                }
            }
            contact_info["audits"].append(audit_info)
            
        # order the audits by id descending
        contact_info["audits"] = sorted(contact_info["audits"], key=lambda x: x["id"], reverse=True)

        result.append(contact_info)

    return jsonify(result)


@recorded_contact_blueprint.route("/audit", methods=["POST"])
def create_recorded_contact_audit():
    data = request.get_json()
    
    current_app.logger.info(f"Request data: {data}")

    # Extract data from the request
    recorded_contact_id = data.get('recorded_contact_id')
    audit_start_date = data.get('audit_start_date')
    audit_end_date = data.get('audit_end_date')
    audit_type = data.get('audit_type')
    
    # TODO replace with the actual user id when authentication is implemented
    created_by_id = 1
 
    # playlist name is made up of the audit type, recorded contact name and the current date
    playlist_name = f"{audit_type}_{recorded_contact_id}_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # audit description is made up of the audit type, recorded contact name, audit start date and audit end date, recorded contact id and created by id
    audit_description = f"{audit_type}_{recorded_contact_id}_{audit_start_date}_{audit_end_date}_{created_by_id}"

    # Validate audit type
    try:
        audit_type_enum = RecordedContactAuditTypeEnum(audit_type)
    except ValueError:
        return jsonify({"error": "Invalid audit type"}), 400
    
    # Initialize filters
    filters = {
        "recorded_contact_id": []
    }
    
    # Ensure recorded_contact_ids is a list, as thats how get_interactions work,
    # it'll only ever be 1 recorded_contact_id
    if not isinstance(recorded_contact_id, list):
        recorded_contact_id = [recorded_contact_id]

    # Populate filters with recorded_contact_ids
    filters["recorded_contact_id"] = recorded_contact_id
    filters["interaction_start_time"] = audit_start_date
    filters["interaction_end_time"] = audit_end_date

    try:
        # Create a new playlist
        new_playlist = Playlist(
            name=playlist_name,
            description=audit_description,
            created_by_id=created_by_id,
            status='pending',
        )
        db.session.add(new_playlist)
        db.session.flush()  # Ensure the playlist ID is available

        # Create a new audit record
        new_audit = RecordedContactAudit(
            recorded_contact_id=recorded_contact_id[0], # it'd only ever be 1
            audit_notes=audit_description,
            audit_type=audit_type_enum,
            playlist_id=new_playlist.id,
            audit_start_date=audit_start_date,
            audit_end_date=audit_end_date
        )
        db.session.add(new_audit)
        db.session.commit()
        
        associate_interactions_to_playlist(new_playlist.id, filters=filters)
        
        # return the new_audit as json using flask-mashmelow RecordedContactAuditSchema schema
        # RecordedContactAuditSchema_instance = RecordedContactAuditSchema()
        # result = RecordedContactAuditSchema_instance.dump(new_audit)
        # return jsonify(result), 201
        
        

        return jsonify({
            "message": "RecordedContactAudit and Playlist created successfully. Playlist generation in background",
            "audit_id": new_audit.id,
            "playlist_id": new_playlist.id
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"IntegrityError: {str(e)}")
        return jsonify({"error": str(e)}), 400