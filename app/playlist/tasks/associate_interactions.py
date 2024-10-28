# from celery import shared_task
from flask import current_app
from app.extensions import db, celery
from compliance_lib_schemas.models import Playlist, PlaylistInteractionAssociation, Interaction
from app.interaction.manager import get_interactions

@celery.task
def associate_interactions_to_playlist(playlist_id, interaction_ids=None, filters=None):
    current_app.logger.info("in associate_interactions_to_playlist")
    current_app.logger.info(f"associate_interactions_to_playlist called with playlist_id={playlist_id}, interaction_ids={interaction_ids}, filters={filters}")

    try:
    # Fetch playlist
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            raise ValueError("Playlist not found")

        interaction_ids_to_associate = []
        
        if filters:
            # Lookup interactions
            interactions_data, _ = get_interactions(
                page=1,
                per_page=None,
                filters=filters
            )
            current_app.logger.info(interactions_data)
            interaction_ids_to_associate = [interaction['id'] for interaction in interactions_data]

        if interaction_ids:
            interactions_from_ids = db.session.query(Interaction.id).filter(Interaction.id.in_(interaction_ids)).all()
            valid_ids = [interaction.id for interaction in interactions_from_ids]
            if len(valid_ids) != len(interaction_ids):
                raise ValueError("Some interaction IDs are invalid.")
            interaction_ids_to_associate = list(set(valid_ids))

        if not interaction_ids_to_associate:
            raise ValueError("No interactions to associate with the playlist.")

        # Create associations
        for interaction_id in interaction_ids_to_associate:
            association = PlaylistInteractionAssociation(
                playlist_id=playlist.id,
                interaction_id=interaction_id
            )
            db.session.add(association)
            
        # set the playlist status to created
        playlist.status = 'created'

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing playlist {playlist_id}: {str(e)}")
