import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from marshmallow import ValidationError
from compliance_lib_schemas.models import User as UserModel
from app.extensions import db
from app.auth.routes import auth_blueprint
from app.auth.schemas import ForgotPasswordSchema
from app.auth.tasks import send_forgot_password_email

@auth_blueprint.route('/forgot-password', methods=["POST"])
def forgot_password():
    schema = ForgotPasswordSchema()
    json = request.get_json(silent=True)
    
    if json is None:
        return jsonify({"success": False, "msg": "Invalid JSON"}), 400

    try:
        data = schema.load(json)
    except ValidationError as err:
        return jsonify({"success": False, "msg": err.messages}), 400

    email = data['email']

    user = UserModel.query.filter_by(email=email).first()

    if not user:
        # To avoid revealing whether the email exists, just return a success message
        return jsonify({"success": True, "msg": "If the email exists, a reset token will be sent."}), 200

    # Generate a secure reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    # Prepare email content
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
    subject = "Password Reset Request"
    body = f"To reset your password, click the following link: {reset_url}\nIf you did not request this password reset, please ignore this email."

    # Send the reset email asynchronously
    send_forgot_password_email.delay(user.email, subject, body)

    return jsonify({"success": True, "msg": "If the email exists, a reset token will be sent."}), 200
