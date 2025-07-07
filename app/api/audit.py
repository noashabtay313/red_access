from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
import logging
from app.services.audit_service import AuditService
from app.decorators.rate_limiter import rate_limit
from app.decorators.tenant_validator import validate_tenant
from app.decorators.error_handler import handle_errors

logger = logging.getLogger(__name__)

audit_blue_print = Blueprint('audit', __name__, url_prefix='/api/v1/audit')


@audit_blue_print.route('/logs', methods=['GET'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='read')
def get_audit_logs(tenant_id: str):
    audit_service = AuditService()

    limit = min(int(request.args.get('limit', 100)), 1000)  # Maximum 1000 logs
    days = int(request.args.get('days', 30))
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    logs = audit_service.get_audit_logs(
        tenant_id=tenant_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

    logs_data = []
    for log in logs:
        logs_data.append({
            'action': log.action,
            'resource_name': log.resource_name,
            'user_id': log.user_id,
            'timestamp': log.timestamp.isoformat(),
            'metadata': log.metadata
        })

    return jsonify({
        'audit_logs': logs_data,
        'total_count': len(logs_data),
        'tenant_id': tenant_id,
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        }
    }), 200


@audit_blue_print.route('/summary', methods=['GET'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='read')
def get_audit_summary(tenant_id: str):
    audit_service = AuditService()

    days = int(request.args.get('days', 30))
    summary = audit_service.get_audit_summary(tenant_id, days)

    return jsonify(summary), 200
