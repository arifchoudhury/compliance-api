import json
import logging
from flask import request, jsonify, current_app
from sqlalchemy.orm import aliased
from sqlalchemy.engine.row import Row

from app.extensions import db
from app.interaction.routes import interaction_blueprint
from compliance_lib_schemas.models import (
    Channel, Interaction, RecordedContact, ThirdPartyContact, Identifier
)

@interaction_blueprint.route('/filters/fields', methods=['GET'])
def get_filter_fields():
    
    new_fields = ['channel', 'direction', 'recorded_contact_email', 'recorded_contact_fullname', 'recorded_identifier', 'third_party_contact_email', 'third_party_contact_fullname', 'third_party_identifier']

    return jsonify(new_fields), 200

@interaction_blueprint.route('/filters/values/<field_name>', methods=['GET'])
def get_filter_values(field_name):
    def get_channel_names():
        return Channel.query.with_entities(Channel.name).distinct().all()

    def get_directions():
        return ["inbound", "outbound"]

    def get_recorded_contact_emails():
        return RecordedContact.query.with_entities(RecordedContact.email).filter(
            RecordedContact.email != ''
        ).distinct().all()

    def get_recorded_contact_fullnames():
        return RecordedContact.query.with_entities(RecordedContact.fullname).filter(
            RecordedContact.fullname != ''
        ).distinct().all()

    def get_recorded_identifiers():
        return Identifier.query.filter(
            Identifier.recorded_contact_id.isnot(None)
        ).all()

    def get_third_party_contact_emails():
        return ThirdPartyContact.query.with_entities(ThirdPartyContact.email).filter(
            ThirdPartyContact.email != ''
        ).distinct().all()

    def get_third_party_contact_fullnames():
        return ThirdPartyContact.query.with_entities(ThirdPartyContact.fullname).filter(
            ThirdPartyContact.fullname != ''
        ).distinct().all()

    def get_third_party_identifiers():
        return Identifier.query.filter(
            Identifier.third_party_contact_id.isnot(None)
        ).all()

    # Mapping field names to query functions
    query_map = {
        "channel": get_channel_names,
        "direction": get_directions,
        "recorded_contact_email": get_recorded_contact_emails,
        "recorded_contact_fullname": get_recorded_contact_fullnames,
        "recorded_identifier": get_recorded_identifiers,
        "third_party_contact_email": get_third_party_contact_emails,
        "third_party_contact_fullname": get_third_party_contact_fullnames,
        "third_party_identifier": get_third_party_identifiers
    }

    # Fetch the appropriate query function based on field_name
    query_func = query_map.get(field_name)
    
    if query_func is None:
        return jsonify({"error": "Field not supported"}), 400

    # Execute the query
    values = query_func()
        
    # Define a helper function to extract values from query results
    def extract_values(results):
        if not results:
            return []
        
        # Check if results are Row objects (which are tuple-like)
        if isinstance(results[0], Row):
            # For Row objects, extract the first element of each Row
            return [row[0] for row in results]
        else:
            # Handle object results
            return [getattr(item, 'identifier', str(item)) for item in results]


    # Process the query results
    response = extract_values(values)
    
    return jsonify(response)