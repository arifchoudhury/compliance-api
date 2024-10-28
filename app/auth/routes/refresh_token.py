from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.auth.routes import auth_blueprint

@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # This will automatically verify the refresh token and its validity
    current_user = get_jwt_identity()
    
    # Create new access token
    access_token = create_access_token(identity=current_user)
    
    return jsonify({'access_token': access_token})