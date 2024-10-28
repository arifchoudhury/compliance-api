import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.playlist.routes import playlist_blueprint
from compliance_lib_schemas.models import Playlist, PlaylistInteractionAssociation, Interaction
from compliance_lib_schemas.serializers import PlaylistSchema
from app.interaction.manager import get_interactions
from app.playlist.tasks import associate_interactions_to_playlist

playlist_schema = PlaylistSchema(many=True)

@playlist_blueprint.route("", methods=["POST"])
def add():
    data = request.json

    playlist_name = data.get("name")
    playlist_description = data.get("description")
    recording_ids = data.get("recording_ids", [])
    filters = data.get("filters", {})
    
    current_app.logger.info(filters)
    
    # Define keys that should not be converted to lists
    keys_to_exclude = {'interaction_start_time', 'interaction_end_time'}

    # Ensure all filter values are lists, except for the excluded keys
    for key, value in filters.items():
        if key not in keys_to_exclude and not isinstance(value, list):
            filters[key] = [value]
    
    current_app.logger.info(filters)

    if not playlist_name:
        return jsonify({"error": "Playlist name is required."}), 400

    existing_playlist = db.session.query(Playlist).filter_by(name=playlist_name).first()
    if existing_playlist:
        return jsonify({"error": "A playlist with this name already exists."}), 400

    try:
        new_playlist = Playlist(
            name=playlist_name,
            description=playlist_description,
            created_by_id=1,  # Replace with actual user ID
            status='pending'
        )
        db.session.add(new_playlist)
        db.session.commit()

        # Queue Celery task for full processing
        #associate_interactions_to_playlist(new_playlist.id, recording_ids, filters)
        associate_interactions_to_playlist.delay(new_playlist.id, recording_ids, filters)

        return jsonify({"message": "Playlist created successfully! Processing in the background"}, 201)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@playlist_blueprint.route("/<int:playlist_id>/interactions", methods=["POST"])
def add_interactions_to_existing_playlist(playlist_id):
    data = request.json

    recording_ids = data.get("recording_ids", [])
    filters = data.get("filters", {})
    
    # Ensure all filter values are lists
    for key, value in filters.items():
        if not isinstance(value, list):
            filters[key] = [value]

    try:
        # Check if playlist exists
        playlist = db.session.query(Playlist).get(playlist_id)
        if not playlist:
            return jsonify({"error": "Playlist not found."}), 404

        # Add interactions to the playlist
        #associate_interactions_to_playlist(playlist.id, recording_ids, filters)
        associate_interactions_to_playlist.delay(playlist.id, recording_ids, filters)

        return jsonify({"message": f"Interactions added to playlist id {playlist.id}. Processing in the background."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
