from flask import request, jsonify, current_app

from app.extensions import db
from app.role.routes import role_blueprint
from compliance_lib_schemas.models import Role

@role_blueprint.route("", methods=["GET"])
def list_roles():
    
    roles = Role.query.all()
    
    roles = [r.serialize for r in roles]
    
    return jsonify({"roles": roles }), 200

@role_blueprint.route("/<id>", methods=["GET"])
def list_role(id):
    
    role = Role.query.filter(
        Role.id == id
    ).first()
    
    role = role.serialize
    
    return jsonify(role), 200