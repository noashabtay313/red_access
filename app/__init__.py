import logging
from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from pymongo.errors import PyMongoError

from app.config import get_config
from app.utils.database import DatabaseManager
from app.services.cleanup_service import CleanupService
from app.exceptions.custom_exceptions import RuleManagementException

from app.api.rules import rules_blue_print
from app.api.bulk_operations import bulk_blue_print
from app.api.audit import audit_blue_print


def create_app(config_name='default'):
    app = Flask(__name__)

    config = get_config(config_name)
    app.config.from_object(config)

    setup_logging(app)
    setup_database(app)

    # Enable CORS
    CORS(app)

    app.register_blueprint(rules_blue_print)
    app.register_blueprint(bulk_blue_print)
    app.register_blueprint(audit_blue_print)

    setup_scheduler(app)

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Rule Management API',
            'version': '1.0.0',
            'endpoints': {
                'rules': '/api/v1/rules',
                'bulk_operations': '/api/v1/bulk/rules',
                'audit': '/api/v1/audit'
            }
        })

    return app


def setup_logging(app):
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=log_level,
        format=log_format,
        filename=app.config.get('LOG_FILE'),
        filemode='a'
    )

    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    app.logger.info(f"Application started with log level: {app.config.get('LOG_LEVEL')}")


def setup_database(app):
    try:
        db_manager = DatabaseManager(
            connection_string=app.config.get('MONGODB_URI'),
            database_name=app.config.get('DATABASE_NAME')
        )

        # Test the connection
        db_manager.get_database().command('ping')
        app.logger.info("Database connection established successfully")

        # Store database manager in app context for access in other parts
        app.db_manager = db_manager

    except PyMongoError as e:
        app.logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise RuleManagementException(f"Database connection failed: {str(e)}")
    except Exception as e:
        app.logger.error(f"Unexpected error during database setup: {str(e)}")
        raise RuleManagementException(f"Database setup failed: {str(e)}")



def setup_scheduler(app):
    global scheduler

    if scheduler is not None:
        app.logger.warning("Scheduler already initialized")
        return

    try:
        scheduler = BackgroundScheduler()

        # Configure cleanup service
        cleanup_service = CleanupService(app.db_manager)

        rate_limiter_cleanup_interval = app.config.get('EXPIRATION_CLEANUP_INTERVAL_SECONDS', 300)
        audit_logs_cleanup_interval = app.config.get('AUDIT_LOG_RETENTION_DAYS', 90)
        scheduler.add_job(
            func=cleanup_service.cleanup_expired_rules,
            trigger=IntervalTrigger(seconds=rate_limiter_cleanup_interval),
            id='cleanup_expired_rules',
            name='Cleanup expired rules',
            replace_existing=True
        )
        scheduler.add_job(
            func=cleanup_service.cleanup_old_audit_logs,
            trigger=IntervalTrigger(days=audit_logs_cleanup_interval),
            id='cleanup_old_audit_logs',
            name='Cleanup old audit logs',
            replace_existing=True
        )
        scheduler.start()
        atexit.register(lambda: shutdown_scheduler(app))
    except Exception as e:
        app.logger.error(f"Failed to setup scheduler: {str(e)}")
        raise RuleManagementException(f"Scheduler setup failed: {str(e)}")


def shutdown_scheduler(app):
    global scheduler
    if scheduler:
        try:
            scheduler.shutdown()
            app.logger.info("Background scheduler shut down successfully")
        except Exception as e:
            app.logger.error(f"Error shutting down scheduler: {str(e)}")
        finally:
            scheduler = None
