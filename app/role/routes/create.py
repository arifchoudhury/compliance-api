from flask import request, jsonify, current_app

from app.extensions import db
from app.role.routes import role_blueprint
from compliance_lib_schemas.models import Role, Policy

@role_blueprint.route("/add", methods=["POST"])
def add_role():
    
    json = request.get_json()
    
    # todo check if active?
    role = Role.query.filter.by(name = json["name"]).first()
    
    if role:
        return jsonify({"success": False, "msg": "role already exists"}), 409
    
    role = Role(name=json["name"], description=json["description"])
    
    policies = json["policies"]
    
    for service in policies:
        service_policies = policies[service]
        for policy in service_policies:
            if policy["associated"]:
                p = db.session.query(Policy).filter(
                    Policy.service == service, 
                    Policy.action == policy["action"],
                    Policy.active == True
                ).first()
                # current_app.logger.info(p)
                role.policy.append(p)
            
    db.session.add(role)
            
    try:
        db.session.commit()
        return jsonify({"success": True, "msg": "Role created"}), 200
    except Exception as err:
        db.session.rollback()
        current_app.logger.info(f"Failed to create role, error: {err}")
        return jsonify({"success": False, "msg": "Failed to create role"}), 500

    
    
