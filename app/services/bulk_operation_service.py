from typing import List, Dict, Any
import logging
from app.services.rule_service import RuleService
from app.models.audit_log import AuditLog, AuditAction
from app.services.audit_service import AuditService
from app.exceptions.custom_exceptions import ValidationError

logger = logging.getLogger(__name__)


class BulkOperationService:
    def __init__(self):
        self.rule_service = RuleService()
        self.audit_service = AuditService()

    def process_bulk_operations(self, tenant_id: str, operations: List[Dict[str, Any]],
                                user_id: str = 'system') -> Dict[str, Any]:
        results = {
            'successful': [],
            'failed': [],
            'total': len(operations),
            'success_count': 0,
            'failure_count': 0
        }

        for index, operation in enumerate(operations):
            try:
                result = self._process_single_operation(tenant_id, operation)
                results['successful'].append({
                    'index': index,
                    'operation': operation,
                    'result': result
                })
                results['success_count'] += 1

            except Exception as err:
                error_info = {'index': index, 'operation': operation, 'error': str(err)}
                results['failed'].append(error_info)
                results['failure_count'] += 1
                logger.error(f"Bulk operation failed at index {index}: {err}")

        audit_log = AuditLog(
            tenant_id=tenant_id,
            action=AuditAction.BULK_CREATE,
            resource_name='bulk_operations',
            resource_data={
                'total_operations': results['total'],
                'successful': results['success_count'],
                'failed': results['failure_count']
            },
            user_id=user_id
        )
        self.audit_service.log_audit_event(audit_log)
        return results

    def _process_single_operation(self, tenant_id: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        operation_type = operation.get('operation', '').lower()
        data = operation.get('data', {})

        if operation_type == 'create':
            rule = self.rule_service.create_rule(tenant_id, data)
            return {'action': 'create', 'rule_name': rule.name, 'status': 'success'}

        elif operation_type == 'update':
            rule_name = operation.get('rule_name') or data.get('name')
            if not rule_name:
                raise ValidationError("Rule name is required for update operation")

            rule = self.rule_service.update_rule(tenant_id, rule_name, data)
            return {'action': 'update', 'rule_name': rule.name, 'status': 'success'}

        elif operation_type == 'delete':
            rule_name = operation.get('rule_name') or data.get('name')
            if not rule_name:
                raise ValidationError("Rule name is required for delete operation")

            self.rule_service.delete_rule(tenant_id, rule_name)
            return {'action': 'delete', 'rule_name': rule_name, 'status': 'success'}

        else:
            raise ValidationError(f"Unknown operation type: {operation_type}")
