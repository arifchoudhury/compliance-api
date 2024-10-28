from functools import wraps
from flask import jsonify, request
from flask_jwt import jwt_required, current_identity  # Import Flask-JWT components

def check_permission(permission):
    def decorator(f):
        @wraps(f)
        @jwt_required()  # Ensures the route requires a valid JWT token
        def decorated_function(*args, **kwargs):
            user_permissions = {perm.name for role in current_identity.roles for perm in role.permissions}
            if permission not in user_permissions:
                return jsonify({"error": "Permission denied"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
