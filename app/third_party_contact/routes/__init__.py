from flask import Blueprint

third_party_contact_blueprint = Blueprint('third_party_contact', __name__)
from .third_party_contact import *