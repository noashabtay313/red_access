import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/rule_management')
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'rule_management')
    # Rate limiting configuration
    DEFAULT_RATE_LIMIT_PER_MINUTE = int(os.environ.get('DEFAULT_RATE_LIMIT_PER_MINUTE', 100))
    RATE_LIMIT_TIME_WINDOW_MINUTES = int(os.environ.get('RATE_LIMIT_TIME_WINDOW_MINUTES', 1))
    # Cleanup configuration
    EXPIRATION_CLEANUP_INTERVAL_SECONDS = int(os.environ.get('EXPIRATION_CLEANUP_INTERVAL_SECONDS', 300))
    AUDIT_LOG_RETENTION_DAYS = int(os.environ.get('AUDIT_LOG_RETENTION_DAYS', 90))
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


def get_config():
    return DevelopmentConfig

