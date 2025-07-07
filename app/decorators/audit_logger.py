from functools import wraps
from flask import request, g
import logging
from app.models.audit_log import AuditLog, AuditAction
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


def audit_log(action: AuditAction, resource_name_key: str = 'name'):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            tenant_id = request.headers.get('X-Tenant-ID')
            user_id = request.headers.get('X-User-ID', 'system')

            resource_name = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                json_data = request.get_json() or {}
                resource_name = json_data.get(resource_name_key)
            elif resource_name_key in kwargs:
                resource_name = kwargs[resource_name_key]

            g.audit_context = {
                'tenant_id': tenant_id,
                'user_id': user_id,
                'action': action,
                'resource_name': resource_name,
                'request_data': request.get_json() if request.method in ['POST', 'PUT', 'PATCH'] else None
            }
            try:
                result = func(*args, **kwargs)
                if tenant_id:
                    audit_service = AuditService()
                    audit_log_entry = AuditLog(
                        tenant_id=tenant_id,
                        action=action,
                        resource_name=resource_name or 'unknown',
                        resource_data=g.audit_context.get('request_data'),
                        user_id=user_id,
                        metadata={
                            'ip_address': request.remote_addr,
                            'user_agent': request.headers.get('User-Agent'),
                            'status': 'success'
                        }
                    )
                    audit_service.log_audit_event(audit_log_entry)
                return result
            except Exception as e:
                if tenant_id:
                    audit_service = AuditService()
                    audit_log_entry = AuditLog(
                        tenant_id=tenant_id,
                        action=action,
                        resource_name=resource_name or 'unknown',
                        resource_data=g.audit_context.get('request_data'),
                        user_id=user_id,
                        metadata={
                            'ip_address': request.remote_addr,
                            'user_agent': request.headers.get('User-Agent'),
                            'status': 'failed',
                            'error': str(e)
                        }
                    )
                    audit_service.log_audit_event(audit_log_entry)
        return decorated_function
    return decorator
