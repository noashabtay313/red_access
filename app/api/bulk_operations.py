from flask import Blueprint, request, jsonify
import logging

import app
from app.services.bulk_operation_service import BulkOperationService
from app.decorators.rate_limiter import rate_limit
from app.decorators.audit_logger import audit_log
from app.decorators.error_handler import handle_errors
from app.models.audit_log import AuditAction
from app.utils.validators import validate_bulk_operations

logger = logging.getLogger(__name__)

bulk_blue_print = Blueprint('bulk_operations', __name__, url_prefix='/api/v1/bulk')


@bulk_blue_print.route('/rules', methods=['POST'])
@handle_errors
@rate_limit(default_limit=app.config.Config.DEFAULT_RATE_LIMIT_PER_MINUTE)
@audit_log(action=AuditAction.BULK_CREATE, resource_name_key='operations')
def bulk_operations(tenant_id: str):
    bulk_service = BulkOperationService()
    request_data = request.get_json()

    if not request_data:
        return jsonify({'error': 'Request body is required'}), 400

    validated_data = validate_bulk_operations(request_data)
    operations = validated_data['operations']
    user_id = request.headers.get('X-User-ID', 'system')

    results = bulk_service.process_bulk_operations(tenant_id, operations, user_id)
    if results['failure_count'] == 0:
        status_code = 200
    elif results['success_count'] == 0:
        status_code = 400
    else:
        status_code = 207  # multiple resource request

    return jsonify({
        'message': 'Bulk operations processed',
        'results': results,
        'summary': {
            'total_operations': results['total'],
            'successful': results['success_count'],
            'failed': results['failure_count'],
            'success_rate': f"{(results['success_count'] / results['total'] * 100):.1f}%"
        }
    }), status_code
