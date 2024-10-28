from flask import Blueprint

retention_blueprint = Blueprint("retention", __name__)

from .retention import *