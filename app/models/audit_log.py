from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum


class AuditAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"
    EXPIRED_CLEANUP = "expired_cleanup"


class AuditLog:
    def __init__(self, tenant_id: str, action: AuditAction, resource_name: str,
                 resource_data: Optional[Dict[str, Any]] = None,
                 user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.tenant_id = tenant_id
        self.action = action.value
        self.resource_name = resource_name
        self.resource_data = resource_data or {}
        self.user_id = user_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tenant_id': self.tenant_id,
            'action': self.action,
            'resource_name': self.resource_name,
            'resource_data': self.resource_data,
            'user_id': self.user_id,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        log = cls(
            tenant_id=data['tenant_id'],
            action=AuditAction(data['action']),
            resource_name=data['resource_name'],
            resource_data=data.get('resource_data'),
            user_id=data.get('user_id'),
            metadata=data.get('metadata')
        )
        log.timestamp = data.get('timestamp', datetime.now(timezone.utc))
        return log
