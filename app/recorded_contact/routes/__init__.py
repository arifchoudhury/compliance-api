from flask import Blueprint

recorded_contact_blueprint = Blueprint("recorded_contact", __name__)

from .recorded_contact import *
from .recorded_contact_attribute import *
from .recorded_contact_audit import *