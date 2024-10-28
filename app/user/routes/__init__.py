from flask import Blueprint

user_blueprint = Blueprint("user", __name__)

from .list import *
from .user import *
from .create import *
from .update import *