from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Rule:
    def __init__(self, name: str, description: str, ip: str, tenant_id: str,
                 expired_date: Optional[datetime] = None):
        self.name = name
        self.description = description
        self.ip = ip
        self.expired_date = expired_date
        self.tenant_id = tenant_id
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'ip': self.ip,
            'expired_date': self.expired_date,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        rule = cls(
            name=data['name'],
            description=data['description'],
            ip=data['ip'],
            expired_date=data.get('expired_date'),
            tenant_id=data['tenant_id']
        )
        rule.created_at = data.get('created_at', datetime.now(timezone.utc))
        rule.updated_at = data.get('updated_at', datetime.now(timezone.utc))
        return rule

    def is_expired(self) -> bool:
        if self.expired_date is None:
            return False
        return datetime.now(timezone.utc) > self.expired_date
