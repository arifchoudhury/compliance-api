import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.user.routes import user_blueprint
from compliance_lib_schemas.models import User, Role
from app.user.forms import UserCreateForm
# from contact.models import Group

@user_blueprint.route("", methods=["POST"])
def create_user():
    
    json = request.get_json()
    
    current_app.logger.info(json)
    
    db_session = db.session()
    
    form = UserCreateForm.from_json(json)
        
    if not form.validate():
        current_app.logger.info(f"form had errors: {form.errors}")
        return jsonify({"success": False, "msg": form.errors}), 400

    user = db_session.query(User)\
        .filter(
            User.email==json["email"],
            # User.active==True
        )\
        .first()
    
    if user:
        # TODO is this the correct response code?!
        return jsonify({"success": True, "msg": "User already exists"}), 409
    else:
        # create user
        
        # look up role
        role = db_session.query(Role).filter(Role.name == json["role_name"], Role.active==True).first()
        # group = db_session.query(Group).filter_by(name=json['group_name']).first()
        
        if not role:
            return jsonify({"success": False, "msg": f"Role id {json['role_id']} does not exist!"}), 400
        
        user = User(
            fullname=json["fullname"],
            email=json["email"],
            active=json["active"],
            role=role,
            # group=group
        )
        
        db_session.add(user)
                
    try:
        db_session.commit()
    except Exception as err:
        db_session.rollback()
        current_app.logger.info(f"Failed to create user, error: {err}")
        return jsonify({"success": False, "msg": f"Failed to create user, error: {err}"}), 500
    
    # TODO this needs to be moved to a queue
    # if form.send_welcome_email.data:
    #     try:
    #         send_welcome_email = SendWelcomeEmailTask(sender="me@arifthedev.com", region_name="eu-west-2") # TODO this should be already configured on startup
    #         send_welcome_email.generate_welcome_email(recipient=[form.email.data])
            
    #     except Exception as err:
    #         current_app.logger.warning(f"Failed to send welcome email, error: {err}")
    #         return jsonify({"success": False, "msg": f"Failed to send welcome email sent to {user.email}"}), 200
        
    
    return jsonify(user.serialize), 200