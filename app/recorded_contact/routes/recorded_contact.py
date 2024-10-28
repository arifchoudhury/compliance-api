import json

from flask import request, jsonify, current_app
import re 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.extensions import db
from app.recorded_contact.routes import recorded_contact_blueprint
from app.recorded_contact.managers import RecordedContactManager

contact_manager = RecordedContactManager()

@recorded_contact_blueprint.route('', methods=['GET'])
def get_all_recorded_contacts():
    try:
        contacts_data = contact_manager.get_contact_with_attributes_and_identifiers()
        # return jsonify({"contacts": contacts_data, "metadata": list(contacts_data[0].keys())})
        return jsonify({"contacts": contacts_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recorded_contact_blueprint.route('/<int:contact_id>', methods=['GET'])
def get_recorded_contact(contact_id):
    try:
        contact_data = contact_manager.get_contact_with_attributes_and_identifiers(
            contact_id=contact_id
        )
        if contact_data:
            return jsonify(contact_data)
        return jsonify({"error": "Contact not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recorded_contact_blueprint.route('', methods=['POST'])
def create_recorded_contact():
    try:
        contact_data = request.get_json()
        result, status_code = contact_manager.add_contact(contact_data)
        return jsonify(result), status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@recorded_contact_blueprint.route('/<int:contact_id>', methods=['PUT'])
def update_recorded_contact(contact_id):
    try:
        contact_data = request.get_json()
        result, status_code = contact_manager.update_contact(contact_id, contact_data)
        return jsonify(result), status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500