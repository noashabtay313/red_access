from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import logging
from app.utils.database import DatabaseManager
from app.models.audit_log import AuditLog, AuditAction

logger = logging.getLogger(__name__)


class AuditService:

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collection_name = 'audit_logs'

    @property
    def collection(self):
        return self.db_manager.db[self.collection_name]

    def log_audit_event(self, audit_log: AuditLog) -> bool:
        try:
            result = self.collection.insert_one(audit_log.to_dict())
            if result.inserted_id:
                logger.debug(f"Audit event logged: {audit_log.action} for {audit_log.resource_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return False

    def get_audit_logs(self, tenant_id: str, limit: int = 100,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[AuditLog]:
        query = {'tenant_id': tenant_id}

        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date

        logs_data = self.collection.find(query).sort('timestamp', -1).limit(limit)
        return [AuditLog.from_dict(log_data) for log_data in logs_data]

    def get_audit_summary(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        pipeline = [
            {
                '$match': {
                    'tenant_id': tenant_id,
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': '$action',
                    'count': {'$sum': 1}
                }
            }
        ]

        results = list(self.collection.aggregate(pipeline))
        summary = {result['_id']: result['count'] for result in results}

        return {
            'tenant_id': tenant_id,
            'period_days': days,
            'total_events': sum(summary.values()),
            'events_by_action': summary
        }

    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        result = self.collection.delete_many({
            'timestamp': {'$lt': cutoff_date}
        })

        deleted_count = result.deleted_count
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old audit logs")

        return deleted_count
