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
        self.tenant_id = tenant_id
        self.expired_date = expired_date
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'ip': self.ip,
            'tenant_id': self.tenant_id,
            'expired_date': self.expired_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        rule = cls(
            name=data['name'],
            description=data['description'],
            ip=data['ip'],
            tenant_id=data['tenant_id'],
            expired_date=data.get('expired_date')
        )
        rule.created_at = data.get('created_at', datetime.now(timezone.utc))
        rule.updated_at = data.get('updated_at', datetime.now(timezone.utc))
        return rule

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        if self.expired_date is None:
            return False
        return datetime.now(timezone.utc) > self.expired_date