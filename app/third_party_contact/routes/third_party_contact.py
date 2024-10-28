import json

from flask import request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import re 

from app.extensions import db
from app.third_party_contact.routes import third_party_contact_blueprint
from app.third_party_contact.managers import ThirdPartyContactManager

contact_manager = ThirdPartyContactManager()

@third_party_contact_blueprint.route('', methods=['GET'])
def get_all_third_party_contacts():
    try:
        contacts_data = contact_manager.get_contact_with_identifiers()
        return jsonify(contacts_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@third_party_contact_blueprint.route('/<int:contact_id>', methods=['GET'])
def get_third_party_contact(contact_id):
    try:
        contact_data = contact_manager.get_contact_with_identifiers(
            contact_id=contact_id
        )
        if contact_data:
            return jsonify(contact_data)
        return jsonify({"error": "Contact not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@third_party_contact_blueprint.route('', methods=['POST'])
def create_third_party_contact_contact():
    try:
        contact_data = request.get_json()
        result, status_code = contact_manager.add_contact(contact_data)
        return jsonify(result), status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@third_party_contact_blueprint.route('/<int:contact_id>', methods=['PUT'])
def update_third_party_contact(contact_id):
    try:
        contact_data = request.get_json()
        result, status_code = contact_manager.update_contact(contact_id, contact_data)
        return jsonify(result), status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500