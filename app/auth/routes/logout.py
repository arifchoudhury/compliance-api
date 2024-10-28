from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime
from compliance_lib_schemas.models import TokenBlocklist, RefreshToken
from app.extensions import db, cache
from app.auth.routes import auth_blueprint

@auth_blueprint.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  # 'jti' is the unique identifier for the JWT

    # Add the JWT to the blocklist
    blocklist_entry = TokenBlocklist(jti=jti, created_at=datetime.utcnow(), expires_at=datetime.utcnow())
    db.session.add(blocklist_entry)
    db.session.commit()

    # Optionally remove the refresh token from the database
    refresh_token = RefreshToken.query.filter_by(token=jti).first()
    if refresh_token:
        db.session.delete(refresh_token)
        db.session.commit()

    # Clear the user's cached data
    jwt_identity = get_jwt_identity()
    cache.delete(f"user:{jwt_identity}")

    return jsonify({"success": True, "msg": "Successfully logged out"}), 200
