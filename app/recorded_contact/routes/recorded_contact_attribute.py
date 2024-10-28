import json

from flask import request, jsonify, current_app
from marshmallow import ValidationError

from app.extensions import db
from app.recorded_contact.routes import recorded_contact_blueprint
from app.recorded_contact.schemas import AttributeSchema
from compliance_lib_schemas.models import RecordedContactAttribute


@recorded_contact_blueprint.route("/attribute", methods=["GET"])
def get_attributes():

    response = []
    
    attributes = RecordedContactAttribute.query.all()
    
    for attribute in attributes:
        response.append({
            "id": attribute.id,
            "name": attribute.name,
            "regex": attribute.regex,
            "required": attribute.required,
            "unique": attribute.unique
        })
        
    return jsonify({"attributes": response}), 200

@recorded_contact_blueprint.route("/attribute/<attribute_id>", methods=["GET"])
def get_attribute(attribute_id):

    attribute = RecordedContactAttribute.query.filter_by(id=attribute_id).first()
    
    if attribute:
        attribute = attribute.serialize()
        return jsonify(attribute), 200
    else:
        attribute = {}
        return jsonify(attribute), 404

@recorded_contact_blueprint.route("/attribute", methods=["POST"])
def add_attribute():
    
    schema = AttributeSchema()
    
    json = request.get_json(silent=True)
    
    if json is None:
        return jsonify({"success": False, "msg": "Invalid JSON"}), 400

    try:
        data = schema.load(json)
    except ValidationError as err:
        return jsonify({"success": False, "msg": err.messages}), 400
    
    name = data['name']
    regex = data['regex']
    required = data['required']
    unique = data['unique']

    attribute = db.session.query(RecordedContactAttribute).filter_by(name=name).first()
    if attribute:
        return jsonify({"success": False, "msg": f"Attribute {name} already exists!"})
    
    attribute = RecordedContactAttribute(
        name=name,
        regex=regex,
        required=required,
        unique=unique
    )
    
    db.session.add(attribute)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "msg": "Attribute created"}), 200
    except Exception as err:
        db.session.rollback()
        current_app.logger.info(f"Failed to create attribute, error: {err}")
        return jsonify({"success": False, "msg": f"Failed to create attribute, error: {err}"}), 500