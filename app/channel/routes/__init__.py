from flask import Blueprint

channel_blueprint = Blueprint("channel", __name__)

from .channels import *