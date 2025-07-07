from functools import wraps
from flask import jsonify
import logging
from app.exceptions.custom_exceptions import RuleManagementException

logger = logging.getLogger(__name__)


def handle_errors(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuleManagementException as e:
            logger.error(f"Rule management error in {func.__name__}: {e.message}")
            return jsonify({
                'error': e.message,
                'status_code': e.status_code
            }), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'status_code': 500
            }), 500
    return decorated_function
