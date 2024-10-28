import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.retention.routes import retention_blueprint
from compliance_lib_schemas.models import RetentionPolicy

@retention_blueprint.route("", methods=["GET"])
def get_retention_policies():
    
    retention_policies = RetentionPolicy.query.all()
    
    results = []
    
    for retention_policy in retention_policies:
        results.append({
            "id": retention_policy.id,
            "name": retention_policy.name,
            "call_retention_days": retention_policy.call_retention_days,
            "sms_retention_days": retention_policy.sms_retention_days,
            "retain_metadata": retention_policy.retain_metadata
        })
        
    table_columns = [
        {"index": 0, "name": "id", "display": True},
        {"index": 1, "name": "name", "display": True},
        {"index": 2, "name": "call_retention_days", "display": True},
        {"index": 3, "name": "sms_retention_days", "display": True},
        {"index": 4, "name": "retain_metadata", "display": True},
    ]
        
    return jsonify({
        "retention_policies": results,
        "table_columns": table_columns
    }), 200

@retention_blueprint.route("", methods=["POST"])
def add_retention_policy():
    
    retention_data = request.get_json()
    
    fields = {
        "name": retention_data.get("name"),
        "call_retention_days": retention_data.get("call_retention_days"),
        "sms_retention_days": retention_data.get("sms_retention_days"),
        "retain_metadata": retention_data.get("retain_metadata")
    }

    # Check for any None values
    for field, value in fields.items():
        if value is None:
            return jsonify({"error": f"{field} cannot be None"}), 400
        
    retention_policy = RetentionPolicy.query.filter_by(name=fields['name']).first()
    if retention_policy:
        return jsonify(f"retention policy name {fields['name']} already in use"), 400
        
    retention_policy = RetentionPolicy(
        name = fields["name"],
        call_retention_days = fields["call_retention_days"],
        sms_retention_days = fields["sms_retention_days"],
        retain_metadata = fields["retain_metadata"]
    )
    
    db.session.add(retention_policy)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Retention policy created"}), 200
    except Exception as err:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to create retention policy, error: {err}"}), 500

    