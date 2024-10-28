from flask import request, jsonify, current_app

from app.extensions import db
from app.role.routes import role_blueprint
from compliance_lib_schemas.models import Role, Policy

@role_blueprint.route("/<id>", methods=["PATCH"])
def update_role(id):
    
    new_role = request.get_json()
    
    # get the existing role
    existing_role = Role.query.filter_by(id=id).first()
    
    if not existing_role:
        return jsonify({"success": False, "msg": f"Role {id} not found"}), 400
    
    # update the existing role with new_role info
    existing_role.name = new_role["name"]
    existing_role.description = new_role["description"]
    existing_role.active = new_role["active"]

    # easiest way is to clear the policies then readd them
    existing_role.policy = []
    
    new_policies = new_role["policies"]
    
    for service in new_policies:
        service_policies = new_policies[service]
        for policy in service_policies:
            if policy["associated"]:
                p = db.session.query(Policy).filter(
                    Policy.service == service, 
                    Policy.action == policy["action"],
                    Policy.active == True
                ).first()
                # current_app.logger.info(p)
                existing_role.policy.append(p)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "msg": "Role updated"}), 200
    except Exception as err:
        db.session.rollback()
        current_app.logger.info(f"Failed to update role, error: {err}")
        return jsonify({"success": False, "msg": "Failed to update role"}), 500