from flask import Blueprint

role_blueprint = Blueprint("role", __name__)

from .list import *
from .create import *
from .update import *