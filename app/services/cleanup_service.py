from datetime import datetime, timezone
import logging
from typing import Dict, Any
from app.services.rule_service import RuleService
from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog, AuditAction

logger = logging.getLogger(__name__)


class CleanupService:
    def __init__(self):
        self.rule_service = RuleService()
        self.audit_service = AuditService()

    def cleanup_expired_rules(self) -> Dict[str, Any]:
        logger.info("Starting expired rules cleanup")

        try:
            deleted_count = self.rule_service.delete_expired_rules()
            audit_log = AuditLog(
                tenant_id='system',
                action=AuditAction.EXPIRED_CLEANUP,
                resource_name='expired_rules',
                resource_data={'deleted_count': deleted_count},
                user_id='system',
                metadata={'cleanup_time': datetime.now(timezone.utc).isoformat()}
            )
            self.audit_service.log_audit_event(audit_log)
            logger.info(f"Expired rules cleanup completed: {deleted_count} rules deleted")
            return {
                'status': 'success',
                'deleted_count': deleted_count,
                'timestamp': datetime.now(timezone.utc)
            }
        except Exception as e:
            logger.error(f"Expired rules cleanup failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }

    def cleanup_old_audit_logs(self, retention_days: int = 90) -> Dict[str, Any]:
        logger.info(f"Starting audit logs cleanup for the past: {retention_days} days)")

        try:
            deleted_count = self.audit_service.cleanup_old_logs(retention_days)
            logger.info(f"Audit logs cleanup completed: {deleted_count} logs deleted")
            return {
                'status': 'success',
                'deleted_count': deleted_count,
                'retention_days': retention_days,
                'timestamp': datetime.now(timezone.utc)
            }
        except Exception as e:
            logger.error(f"Audit logs cleanup failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }
