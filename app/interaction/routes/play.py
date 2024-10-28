import re
from flask import request, jsonify, Response
from app.extensions import db
from app.interaction.routes import interaction_blueprint
from compliance_lib_schemas.models import Interaction, InteractionCallRecording
from app.utils.helpers import s3_client

@interaction_blueprint.route('/<int:interaction_id>', methods=['GET'])
@interaction_blueprint.route('/<int:interaction_id>/<file_format>', methods=['GET'])
def stream_interaction(interaction_id, file_format=None):
    
    if not file_format:
        file_format = 'mp3'
    else:
        if file_format not in ['mp3', 'wav', 'transcription']:
            return jsonify({"error": "Unsupported file format"}), 400

    # Query the InteractionCallRecording for the specified file format
    call_recording = InteractionCallRecording.query.filter_by(
        interaction_id=interaction_id,
        file_format=file_format
    ).first()

    if not call_recording:
        return jsonify({"error": "InteractionCallRecording not found for the specified format"}), 404

    # Extract bucket name and file path from the s3_location
    s3_location = call_recording.s3_location
    match = re.match(r's3://([^/]+)/(.+)', s3_location)
    if not match:
        return jsonify({"error": "Invalid S3 location format"}), 400

    bucket_name = match.group(1)
    file_path = match.group(2)

    # Get the file content
    response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
    file_content = response['Body'].read()

    headers = {
        'Content-Type': 'audio/mpeg' if file_format == 'mp3' else 'audio/wav',
        'Content-Length': str(len(file_content))
    }

    return Response(file_content, status=200, headers=headers)
