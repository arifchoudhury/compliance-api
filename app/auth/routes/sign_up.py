from flask import request, jsonify, current_app
from compliance_lib_schemas.models import User as UserModel
from app.extensions import db, bcrypt
from app.auth.schemas import SignUpSchema
from app.auth.tasks import send_welcome_email  # This function will be implemented to use Celery
from app.auth.routes import auth_blueprint
from marshmallow import ValidationError
# from app.task import send_welcome_email

@auth_blueprint.route('/signup', methods=["POST"])
def signup():
    schema = SignUpSchema()
    json = request.get_json(silent=True)
    
    if json is None:
        return jsonify({"success": False, "msg": "Invalid JSON"}), 400

    try:
        data = schema.load(json)
    except ValidationError as err:
        return jsonify({"success": False, "msg": err.messages}), 400

    email = data['email']
    password = data['password']
    fullname = data['fullname']

    # Check if user already exists
    if UserModel.query.filter_by(email=email).first():
        return jsonify({"success": False, "msg": "User already exists."}), 400

    # Create a new user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = UserModel(email=email, password=hashed_password, fullname=fullname, role_id=1)
    
    # Add user to the database
    db.session.add(new_user)
    db.session.commit()

    # Prepare and send welcome email asynchronously
    send_welcome_email.delay(new_user.email, new_user.fullname)

    return jsonify({"success": True, "msg": "User registered successfully."}), 201
