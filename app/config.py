import os
from dotenv import load_dotenv

#load_dotenv()   # load environment variables


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/rule_management')
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'rule_management')

    # Rate limiting configuration
    DEFAULT_RATE_LIMIT_PER_MINUTE = int(os.environ.get('DEFAULT_RATE_LIMIT_PER_MINUTE', 100))
    RATE_LIMIT_TIME_WINDOW_SECONDS = int(os.environ.get('RATE_LIMIT_TIME_WINDOW_SECONDS', 60))

    # Cleanup configuration
    EXPIRATION_CLEANUP_INTERVAL_SECONDS = int(os.environ.get('EXPIRATION_CLEANUP_INTERVAL_SECONDS', 300))
    AUDIT_LOG_RETENTION_DAYS = int(os.environ.get('AUDIT_LOG_RETENTION_DAYS', 90))

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


# class ProductionConfig(Config):
#     DEBUG = False
#     TESTING = False
#
#
# class TestingConfig(Config):
#     DEBUG = True
#     TESTING = True
#     MONGODB_URI = 'mongodb://localhost:27017/rule_management_test'
#     MONGODB_DATABASE = 'rule_management_test'
#
#
# config_mapping = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'testing': TestingConfig,
#     'default': DevelopmentConfig
# }


def get_config(environment='default'):
   #return config_mapping.get(environment, DevelopmentConfig)
    return DevelopmentConfig