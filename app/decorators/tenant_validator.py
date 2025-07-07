from functools import wraps
from flask import request, jsonify
from typing import Set, Dict
import logging

logger = logging.getLogger(__name__)


class TenantValidator:
    def __init__(self):
        # The following fields are initiated here.
        # If this was a real application these fields' data would be loaded from the DB
        self._valid_tenants: Set[str] = set()
        self._tenant_permissions: Dict[str, Set[str]] = {}

    def register_tenant(self, tenant_id: str, permissions: Set[str] = None) -> None:
        self._valid_tenants.add(tenant_id)
        self._tenant_permissions[tenant_id] = permissions or {'read', 'write', 'delete'}
        logger.info(f"Tenant registered: {tenant_id}")

    def has_permission(self, tenant_id: str, permission: str) -> bool:
        if tenant_id not in self._tenant_permissions:
            return permission in {'read', 'write', 'delete'}
        return permission in self._tenant_permissions[tenant_id]


tenant_validator = TenantValidator()


def validate_tenant(required_permission: str = 'read'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            tenant_id = request.headers.get('X-Tenant-ID')
            if not tenant_id:
                return jsonify({'error': 'X-Tenant-ID header is required'}), 400

            if not tenant_validator.has_permission(tenant_id, required_permission):
                return jsonify({'error': f'Tenant {tenant_id} does not have a permission for {required_permission}'}), 403

            # Add tenant_id to kwargs for easy access in the function
            kwargs['tenant_id'] = tenant_id
            return f(*args, **kwargs)

        return decorated_function

    return decorator
