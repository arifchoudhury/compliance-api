from flask import request, jsonify, current_app
from datetime import datetime
from marshmallow import ValidationError
from compliance_lib_schemas.models import User as UserModel
from app.extensions import db, bcrypt
from app.auth.schemas import ResetPasswordSchema
from app.auth.routes import auth_blueprint

@auth_blueprint.route('/reset-password', methods=["POST"])
def reset_password():
    schema = ResetPasswordSchema()
    json = request.get_json(silent=True)
    
    if json is None:
        return jsonify({"success": False, "msg": "Invalid JSON"}), 400

    try:
        data = schema.load(json)
    except ValidationError as err:
        return jsonify({"success": False, "msg": err.messages}), 400

    reset_token = data['reset_token']
    new_password = data['new_password']

    user = UserModel.query.filter_by(reset_token=reset_token).first()

    if not user or user.reset_token_expiration < datetime.utcnow():
        return jsonify({"success": False, "msg": "Invalid or expired reset token."}), 400

    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Update the user's password and clear the reset token
    user.password = hashed_password
    user.reset_token = None
    user.reset_token_expiration = None
    db.session.commit()

    return jsonify({"success": True, "msg": "Password has been reset successfully."}), 200
