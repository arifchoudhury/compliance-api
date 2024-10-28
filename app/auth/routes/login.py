import logging
from datetime import datetime, timedelta
from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db, bcrypt, cache
from compliance_lib_schemas.models import User as UserModel, RefreshToken
from app.auth.schemas import LoginSchema
from app.user.schemas import UserSchema
from app.auth.routes import auth_blueprint

@auth_blueprint.route('/login', methods=["POST"])
def login():
    schema = LoginSchema()
    json = request.get_json(silent=True)
    
    if json is None:
        return jsonify({"success": False, "msg": "Invalid JSON"}), 400

    try:
        data = schema.load(json)
    except ValidationError as err:
        return jsonify({"success": False, "msg": err.messages}), 400

    email = data['email']
    password = data['password']

    user = UserModel.query.filter_by(email=email).first()

    if not user:
        logging.warning("Failed login attempt with email: %s", email)
        return jsonify({"success": False, "msg": "Email address or password incorrect"}), 401

    if user.is_locked_out():
        return jsonify({"success": False, "msg": "Account locked. Please try again later."}), 403

    if not bcrypt.check_password_hash(user.password, password):
        user.increment_failed_attempts()
        db.session.commit()  # Commit changes after incrementing failed attempts
        return jsonify({"success": False, "msg": "Email address or password incorrect"}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(identity=user.id)

    # Store the refresh token in the database
    expires_at = datetime.utcnow() + timedelta(days=30)  # Example expiration of 30 days
    refresh_token_entry = RefreshToken(token=refresh_token, user_id=user.id, expires_at=expires_at)
    db.session.add(refresh_token_entry)
    db.session.commit()

    # Fetch and cache user permissions
    user_data = UserSchema().dump(user)
    # i dont believe this is necessary to store in cache?
    # user_data["access_token"] = access_token
    # user_data["refresh_token"] = refresh_token
    
    # Initialize the permissions dictionary
    permissions = {}
    
    # Iterate over the policies associated with the user's role
    # for policy in user.role.policies:
    #     # Add the action to the appropriate service in the dictionary
    #     if policy.service in permissions:
    #         permissions[policy.service].append(policy.action)
    #     else:
    #         permissions[policy.service] = [policy.action]

    # Optionally, remove duplicates by converting lists to sets and back to lists
    # permissions = {service: list(set(actions)) for service, actions in permissions.items()}
    # user_data["permissions"] = permissions

    # Cache user data
    # cache.set(f"user:{user.id}", user_data, timeout=3600)  # Cache for 1 hour
    user_permissions = {perm.name for role in user.roles for perm in role.permissions}

    user.reset_failed_attempts()
    db.session.commit()  # Commit changes after resetting failed attempts

    return jsonify({"success": True, "data": {"access_token": access_token, "refresh_token": refresh_token, "user_permissions": user_permissions}}), 200
