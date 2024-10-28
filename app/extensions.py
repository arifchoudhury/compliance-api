import logging
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from celery import Celery
from flask_bcrypt import Bcrypt  # Import Flask-Bcrypt
from flask_caching import Cache
from flask_jwt_extended import JWTManager
# from compliance_lib_schemas.models import Base as ComplianceBase, TokenBlocklist
# from compliance_lib_models import ComplianceBase, SessionLocal, TokenBlocklist

# Configure logging (moved here from init_extensions)
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'), logging.INFO)
logging.basicConfig(
    level=log_level,
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler(os.getenv('LOG_FILE', 'flask_api.log'))  # Output to file
    ]
)

# Instantiate extensions
# db = SQLAlchemy()
# migrate = Migrate()
cors = CORS()
ma = Marshmallow()
celery = Celery(__name__)
bcrypt = Bcrypt()  # Initialize Bcrypt
cache = Cache()
jwt = JWTManager()

# @jwt.token_in_blocklist_loader
# def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
#     """
#     Check if the token's unique identifier (jti) is in the blocklist.
#     """
#     jti = jwt_payload["jti"]
#     token = TokenBlocklist.query.filter_by(jti=jti).first()
#     return token is not None

def init_extensions(app):
    """
    Initialize the Flask extensions.
    """
    # Initialize SQLAlchemy with the Flask app
    # db.init_app(app)
    
    # Configure Flask-Migrate with SQLAlchemy
    # migrate.init_app(app, db)

    # Initialize CORS
    cors.init_app(app)
    
    # Initialize Marshmallow
    ma.init_app(app)
    
    bcrypt.init_app(app)
    
    cache.init_app(app)
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Configure Celery
    # celery.conf.update(
    #     broker_url=app.config['CELERY_BROKER_URL'],
    #     result_backend=app.config['CELERY_RESULT_BACKEND']
    # )

    # class ContextTask(celery.Task):
    #     def __call__(self, *args, **kwargs):
    #         with app.app_context():
                # return self.run(*args, **kwargs)

    # celery.Task = ContextTask

    # Bind the session to the compliance models
    # ComplianceBase.query = db.session.query_property()
    # ComplianceBase.query = SessionLocal.query_property()
