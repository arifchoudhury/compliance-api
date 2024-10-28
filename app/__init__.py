# app/__init__.py

import os
from flask import Flask
from .config import config
from .extensions import db, migrate, cors, ma, init_extensions, celery # always remember to keep celery import!!
from .celery_config import make_celery  # Import the make_celery and celery function from celery_config

# Routes
from .auth.routes import auth_blueprint
from .user.routes import user_blueprint
from .third_party_contact.routes import third_party_contact_blueprint
from .recorded_contact.routes import recorded_contact_blueprint
from .channel.routes import channel_blueprint
from .retention.routes import retention_blueprint
from .user.routes import user_blueprint
from .interaction.routes import interaction_blueprint
from .playlist.routes import playlist_blueprint

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(third_party_contact_blueprint, url_prefix='/third-party-contact')
    app.register_blueprint(recorded_contact_blueprint, url_prefix='/recorded-contact')
    app.register_blueprint(channel_blueprint, url_prefix='/channel')
    app.register_blueprint(retention_blueprint, url_prefix='/retention')
    app.register_blueprint(interaction_blueprint, url_prefix='/interaction')
    app.register_blueprint(playlist_blueprint, url_prefix='/playlist')

    # Initialize Celery with the app's configuration
    app.celery = make_celery(app)

    return app

# Expose the celery instance at the package level
celery = make_celery(create_app())
