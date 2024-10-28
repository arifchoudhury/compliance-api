import json

from flask import request, jsonify, current_app
from sqlalchemy import update

from app.extensions import db
from app.user.routes import user_blueprint
from compliance_lib_schemas.models import User, Role

@user_blueprint.route("/<id>", methods=["PATCH"])
def update_user(id):
    
    # 2 things that can update a user, to make it active / deactivated, change the roles
    # note we have had to use rolename instead of role.id due to the way formik handles select
    
    json = request.get_json()
    db_session = db.session()
    
    user = db_session.query(User).filter(User.id == id).first()
    
    if not user:
        return jsonify({"success": False, "msg": f"User id {id} does not exist!"}), 400
    
    new_role_name = json["role_name"]
    new_active = json["active"]
    
    if new_role_name != user.role_id:
        user.role = None
        new_role = db_session.query(Role).filter(Role.name == new_role_name).first()
        user.role = new_role
        
    if new_active != user.active:
        user.active = new_active

    try:
        db_session.commit()
        return jsonify(user.serialize), 200
    except Exception as err:
        db_session.rollback()
        current_app.logger.info(f"Failed to update user, error: {err}")
        return jsonify({"success": False, "msg": f"Failed to update user, error: {err}"}), 500
    
    
    