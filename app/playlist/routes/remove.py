import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.playlist.routes import playlist_blueprint
from compliance_lib_schemas.models import PlaylistInteractionAssociation

@playlist_blueprint.route("/<int:playlist_id>/interactions/<int:interaction_id>", methods=["DELETE"])
def remove_interaction_from_playlist(playlist_id, interaction_id):
    try:
        # Query the association table to find the specific record
        association = (
            db.session.query(PlaylistInteractionAssociation)
            .filter_by(playlist_id=playlist_id, interaction_id=interaction_id)
            .first()
        )

        # If no association is found, return a 404
        if not association:
            return jsonify({"error": "Interaction not found in playlist."}), 404

        # Remove the association from the database
        db.session.delete(association)
        db.session.commit()

        return jsonify({"message": "Interaction removed from playlist successfully."}), 200

    except Exception as e:
        print(f"Error removing interaction from playlist: {str(e)}")
        return jsonify({"error": "Failed to remove interaction from playlist."}), 500
