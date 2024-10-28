import json
import os
import re

from flask import request, jsonify, Response, send_file, current_app
import requests
import boto3
from io import BytesIO
from app.extensions import db
from app.interaction.routes import interaction_blueprint
from compliance_lib_schemas.models import Interaction, InteractionCallRecording
from app.utils.helpers import s3_client

@interaction_blueprint.route('/<int:interaction_id>/release', methods=['POST'])
def release_interaction(interaction_id):
    # Get the message from the request
    data = request.get_json()
    message = data.get('message', '')

    # Log the message (for now, just print it)
    current_app.logger.info(f"Message for releasing interaction {interaction_id}: {message}")

    # Look up the interaction by ID
    interaction = Interaction.query.filter_by(id=interaction_id).first()

    if interaction:
        # Set retain_permanently to False
        interaction.retain_permanently = False
        db.session.commit()
        return jsonify({"status": "success", "message": f"Interaction {interaction_id} released"}), 200
    else:
        return jsonify({"status": "error", "message": "Interaction not found"}), 404
