import json

from flask import request, jsonify, current_app

from app.extensions import db
from app.channel.routes import channel_blueprint
from compliance_lib_schemas.models import Channel

# TODO update to use marshmellow
@channel_blueprint.route("", methods=["GET"])
def get_channels():
    
    response = []
    
    channels = Channel.query.all()
    
    for channel in channels:
        response.append(channel.serialize())
        
    return jsonify(response), 200