import json

from flask import request, jsonify, current_app

from app import db
from app.user.routes import user_blueprint
from compliance_lib_schemas.models import User


@user_blueprint.route("/<user_id>", methods=["GET"])
def get_user(user_id):

    db_session = db.session()
    
    user = db_session.query(User).filter(User.id==user_id).first()
    
    if not user:
        return jsonify({"success": True, "msg": "user not found"}), 400
    else:
        user = user.serialize
        return jsonify(user), 200