import os
from datetime import timedelta

class Config:
    
    # Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'flask_api.log')
    
    # JWT Config
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Celery configuration
    # CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://user:password@localhost/vhost')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Redis Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    # CACHE_TYPE = 'redis'
    # CACHE_REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    # CACHE_REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    # CACHE_REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    # CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)  # Use None if no password
    
    # AWS Config
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', "your-access-key-id")
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', "your-access-key-KEY")
    AWS_REGION = os.getenv('AWS_REGION', "your-aws-region")
    AWS_SES_EMAIL_SOURCE = os.getenv('AWS_SES_EMAIL_SOURCE', "your-verified-email@example.com")

class DevelopmentConfig(Config):
    DEBUG = True
    
    # App Specific
    FRONTEND_URL= "http://127.0.0.1:5010"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
