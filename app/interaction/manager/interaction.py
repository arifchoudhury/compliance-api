from app.extensions import db
from sqlalchemy.orm import aliased
from datetime import datetime
from flask import current_app
from sqlalchemy import or_, asc, desc
from collections import defaultdict

from compliance_lib_schemas.models import (
    Interaction, RecordedContact, RecordedContactAttribute, RecordedContactAttributeAssociation,
    ThirdPartyContact, Channel, Identifier
)
    
def is_valid_iso8601_date(value):
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def parse_datetime(value):
    try:
        # Convert ISO 8601 format to Python datetime
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        print(f"Error parsing datetime: {str(e)}")
        return None

def get_interactions(page=1, per_page=None, sort_by=None, sort_order='asc', interaction_ids=None, filters=None):
    
    try:
        recorded_identifier = aliased(Identifier, name='recorded_identifier')
        third_party_identifier = aliased(Identifier, name='third_party_identifier')
        
        # Two aliases for the RecordedContact table
        recorded_contact = aliased(RecordedContact, name='recorded_contact')
        third_party_contact_recorded = aliased(RecordedContact, name='third_party_contact_recorded')
        
        # Alias for ThirdPartyContact table
        third_party_contact = aliased(ThirdPartyContact, name='third_party_contact')
        
        interaction = aliased(Interaction)
        channel = aliased(Channel)

        # Base query with joins
        query = (
            db.session.query(interaction, recorded_identifier, third_party_identifier, recorded_contact, third_party_contact_recorded, third_party_contact, channel)
            .join(recorded_identifier, interaction.recorded_identifier_id == recorded_identifier.id)
            .join(third_party_identifier, interaction.third_party_identifier_id == third_party_identifier.id)
            # Join to RecordedContact for recorded_identifier and third_party_identifier
            .outerjoin(recorded_contact, recorded_identifier.recorded_contact_id == recorded_contact.id)
            .outerjoin(third_party_contact_recorded, third_party_identifier.recorded_contact_id == third_party_contact_recorded.id)
            # Join to ThirdPartyContact for third_party_identifier
            .outerjoin(third_party_contact, third_party_identifier.third_party_contact_id == third_party_contact.id)
            .join(channel, interaction.channel_id == channel.id)
        )

        # Apply filtering by interaction IDs if provided
        if interaction_ids:
            query = query.filter(interaction.id.in_(interaction_ids))
            
        # Apply dynamic filters
        # Apply dynamic filters
        if filters:
            for key, value in filters.items():
                if key == 'channel' and value:
                    query = query.filter(channel.name.in_(value))
                elif key == 'direction' and value:
                    query = query.filter(interaction.direction.in_(value))
                elif key == 'recorded_contact_id' and value:
                    query = query.filter(recorded_contact.id.in_(value))
                elif key == 'recorded_contact_email' and value:
                    query = query.filter(recorded_contact.email.in_(value))
                elif key == 'recorded_contact_fullname' and value:
                    query = query.filter(recorded_contact.fullname.in_(value))
                elif key == 'recorded_identifier' and value:
                    query = query.filter(recorded_identifier.identifier.in_(value))
                elif key == 'third_party_id' and value:
                    query = query.filter(third_party_contact.id.in_(value))
                # incase the third party is a recorded user
                elif key == 'third_party_contact_email' and value:
                    query = query.filter(or_(
                        third_party_contact.email.in_(value),  # ThirdPartyContact email filter
                        third_party_contact_recorded.email.in_(value)  # RecordedContact alias for third_party_identifier
                    ))
                elif key == 'third_party_contact_fullname' and value:
                    query = query.filter(or_(
                        third_party_contact.fullname.in_(value),  # ThirdPartyContact fullname filter
                        third_party_contact_recorded.fullname.in_(value)  # RecordedContact alias for third_party_identifier
                    ))
                elif key == 'third_party_identifier' and value:
                    query = query.filter(third_party_identifier.identifier.in_(value))
                elif key == 'interaction_start_time' and value:
                    if not is_valid_iso8601_date(value):
                        return {"error": "Invalid interaction_start_time format"}, 400
                    start_time = parse_datetime(value)
                    query = query.filter(interaction.start_time >= start_time)
                elif key == 'interaction_end_time' and value:
                    if not is_valid_iso8601_date(value):
                        return {"error": "Invalid interaction_end_time format"}, 400
                    end_time = parse_datetime(value)
                    query = query.filter(interaction.end_time <= end_time)

        # Apply sorting
        if sort_by:
            sort_column = getattr(interaction, sort_by, None)
            if sort_column:
                order = asc(sort_column) if sort_order == 'asc' else desc(sort_column)
                query = query.order_by(order)
        else:
            query = query.order_by(desc(interaction.id))

        total_records = query.count()
        
        # Apply pagination if per_page is specified
        if per_page is not None:
            query = query.offset((page - 1) * per_page).limit(per_page)

        interactions = query.all()
                
        interaction_dict = defaultdict(lambda: {
            "id": None,
            "external_id": None,
            "channel": None,
            "start_time": None,
            "end_time": None,
            "withheld": None,
            "direction": None,
            "recorded_identifier": None,
            "third_party_identifier": None,
            "recorded_contact": {
                "id": None,
                "fullname": None,
                "email": None,
            },
            "third_party_contact": {
                "id": None,
                "fullname": None,
                "email": None
            },
            "retention_end_date": None,
            "retain_permanently": None
        })

        # Process results
        for interaction, recorded_identifier, third_party_identifier, recorded_contact, third_party_contact_recorded, third_party_contact, channel in interactions:
            interaction_id = interaction.id
            interaction_data = interaction_dict[interaction_id]

            # Populate interaction data
            if not interaction_data["id"]:
                interaction_data.update({
                    "id": interaction.id,
                    "external_id": interaction.external_id,
                    "channel": channel.name,
                    "start_time": interaction.start_time.isoformat() if interaction.start_time else None,
                    "end_time": interaction.end_time.isoformat() if interaction.end_time else None,
                    "withheld": interaction.withheld,
                    "direction": interaction.direction,
                    "recorded_identifier": recorded_identifier.identifier,
                    "third_party_identifier": third_party_identifier.identifier,
                    "recorded_contact": {
                        "id": recorded_contact.id if recorded_contact else None,
                        "fullname": recorded_contact.fullname if recorded_contact else None,
                        "email": recorded_contact.email if recorded_contact else None,
                    },
                    "third_party_contact": {
                        "id": third_party_contact.id if third_party_contact else (
                            third_party_contact_recorded.id if third_party_contact_recorded else None),
                        "fullname": third_party_contact.fullname if third_party_contact else (
                            third_party_contact_recorded.fullname if third_party_contact_recorded else None),
                        "email": third_party_contact.email if third_party_contact else (
                            third_party_contact_recorded.email if third_party_contact_recorded else None)
                    },
                    "retention_end_date": interaction.retention_end_date,
                    "retain_permanently": interaction.retain_permanently
                })

        interactions = list(interaction_dict.values())
        
        return interactions, total_records

    except Exception as e:
        print(f"Error retrieving interactions: {str(e)}")
        return {"error": "Failed to retrieve interactions."}, 500
