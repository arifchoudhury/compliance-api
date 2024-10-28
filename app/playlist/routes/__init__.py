from flask import Blueprint

playlist_blueprint = Blueprint("platlist", __name__)

from .playlist import *
from .add import *
from .remove import *