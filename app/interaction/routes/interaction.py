import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.interaction.routes import interaction_blueprint
from app.interaction.manager import get_interactions

@interaction_blueprint.route("", methods=["GET"])
def get_all_interactions():
    
    # TODO this doesnt return interactions between 2 recorded contacts!
    
    # Extract query parameters for pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # filters
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Filters
    filters = {
        "channel": request.args.getlist('channel'),
        "direction": request.args.getlist('direction'),
        "recorded_contact_email": request.args.getlist('recorded_contact_email'),
        "recorded_contact_fullname": request.args.getlist('recorded_contact_fullname'),
        "recorded_identifier": request.args.getlist('recorded_identifier'),
        "third_party_contact_email": request.args.getlist('third_party_contact_email'),
        "third_party_contact_fullname": request.args.getlist('third_party_contact_fullname'),
        "third_party_identifier": request.args.getlist('third_party_identifier'),
        "interaction_start_time": request.args.get("interaction_start_time"),
        "interaction_end_time": request.args.get("interaction_end_time")
    }
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
        
    try:

        interactions, total_records = get_interactions(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters
        )

        # TODO update this to return has_next, etc as per best pratices
        return jsonify({
            "data": interactions,
            "total": total_records,
            "page": page,
            "per_page": per_page
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
