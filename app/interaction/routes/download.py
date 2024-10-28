import json
import os
import re

from flask import request, jsonify, Response, send_file
import requests
import boto3
from io import BytesIO
from app.extensions import db
from app.interaction.routes import interaction_blueprint
from compliance_lib_schemas.models import Interaction, InteractionCallRecording
from app.utils.helpers import s3_client

@interaction_blueprint.route('/download/<int:interaction_id>', methods=['GET'])
@interaction_blueprint.route('/download/<int:interaction_id>/<string:file_format>', methods=['GET'])
def download_interaction_via_presigned_url(interaction_id, file_format=None):
    
    # TODO will this be customer specific?
    if file_format is None:
        file_format = 'mp3'  # Default file format
        
    # Query the InteractionCallRecording entry
    recording = InteractionCallRecording.query.filter_by(interaction_id=interaction_id, file_format=file_format).first()
    
    if not recording:
        return jsonify({'error': 'Recording not found'}), 404
    
    # Extract the bucket name and file key from the s3_location
    s3_location = recording.s3_location
    bucket_name = s3_location.split('/')[2]
    file_key = '/'.join(s3_location.split('/')[3:])
    
    # Generate a presigned URL
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=3600  # URL expiration time in seconds
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Fetch the file from the presigned URL
    try:
        response = requests.get(presigned_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch the file from S3', 'details': str(e)}), 500

    # Send the file to the client as an attachment
    return send_file(
        BytesIO(response.content),
        download_name=f"{interaction_id}.{file_format}",
        as_attachment=True
    )