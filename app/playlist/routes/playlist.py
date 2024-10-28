import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.playlist.routes import playlist_blueprint
# from app.playlist.schemas import PlaylistSchema
from compliance_lib_schemas.models import Playlist, PlaylistInteractionAssociation
from compliance_lib_schemas.serializers import PlaylistSchema
from app.interaction.manager import get_interactions
from sqlalchemy import asc

playlist_schema = PlaylistSchema(many=True)

@playlist_blueprint.route("", methods=["GET"])
def get_playlists():
    
    playlists = Playlist.query.order_by(asc(Playlist.name)).all()
    result = playlist_schema.dump(playlists)
    return jsonify(result), 200

@playlist_blueprint.route("/<int:id>", methods=["GET"])
def get_playlist(id):
    
    # Extract query parameters for pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # filters
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    
    try:
        # Fetch all interaction IDs associated with the playlist
        interaction_ids = (
            db.session.query(PlaylistInteractionAssociation.interaction_id)
            .filter(PlaylistInteractionAssociation.playlist_id == id)
            .all()
        )
        
        if not interaction_ids:
            return jsonify([]), 200
        
        # Flatten the list of tuples returned by .all()
        interaction_ids = [interaction_id[0] for interaction_id in interaction_ids]

        # Reuse the refactored function to get the interactions by IDs
        interactions, total_records = get_interactions(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            interaction_ids=interaction_ids
        )

        return jsonify({
            "data": interactions,
            "total": total_records,
            "page": page,
            "per_page": per_page
        }), 200

    except Exception as e:
        print(f"Error retrieving playlist interactions: {str(e)}")
        return {"error": "Failed to retrieve playlist interactions."}, 500

