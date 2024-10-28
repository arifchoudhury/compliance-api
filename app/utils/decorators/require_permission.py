from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import cache
from compliance_lib_schemas.models import User as UserModel, Role as RoleModel
from sqlalchemy.orm import joinedload

def requires_permission(service, action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            # Check if user data is in cache
            user_data = cache.get(f"user:{user_id}")

            if not user_data:
                # Fetch user from database if not in cache
                user = UserModel.query.options(
                    joinedload(UserModel.role).joinedload(RoleModel.policies)
                ).get(user_id)
                if not user:
                    return jsonify({"success": False, "msg": "User not found."}), 403

                # Extract permissions
                permissions = {}
                for policy in user.role.policies:
                    if policy.service in permissions:
                        permissions[policy.service].append(policy.action)
                    else:
                        permissions[policy.service] = [policy.action]

                # Cache the user data
                cache.set(f"user:{user_id}", {'permissions': permissions}, timeout=3600)  # Cache for 1 hour

            # Check if the required permission is in user's permissions
            if service not in user_data['permissions'] or action not in user_data['permissions'][service]:
                return jsonify({"success": False, "msg": "Permission denied."}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# def requires_permission(permission_name):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             user_id = get_jwt_identity()
#             # Check if user data is in cache
#             user_data = cache.get(f"user:{user_id}")

#             if not user_data:
#                 # Fetch user from database if not in cache
#                 user = UserModel.query.options(
#                     joinedload(UserModel.roles).joinedload(RoleModel.permissions)
#                 ).get(user_id)
#                 if not user:
#                     return jsonify({"success": False, "msg": "User not found."}), 403

#                 # Extract permissions
#                 permissions = {perm.name for role in user.roles for perm in role.permissions}
#                 user_data = {'permissions': permissions}

#                 # Cache the user data
#                 cache.set(f"user:{user_id}", user_data, timeout=3600)  # Cache for 1 hour

#             if permission_name not in user_data['permissions']:
#                 return jsonify({"success": False, "msg": "Permission denied."}), 403

#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator
