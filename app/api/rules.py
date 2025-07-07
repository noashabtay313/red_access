from flask import Blueprint, request, jsonify
import logging
from app.services.rule_service import RuleService
from app.decorators.rate_limiter import rate_limit
from app.decorators.tenant_validator import validate_tenant
from app.decorators.audit_logger import audit_log
from app.decorators.error_handler import handle_errors
from app.models.audit_log import AuditAction

logger = logging.getLogger(__name__)

rules_blue_print = Blueprint('rules', __name__, url_prefix='/api/v1/rules')


@rules_blue_print.route('', methods=['POST'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='write')
@audit_log(action=AuditAction.CREATE, resource_name_key='name')
def create_rule(tenant_id: str):
    rule_service = RuleService()
    rule_data = request.get_json()

    if not rule_data:
        return jsonify({'error': 'Request body is required'}), 400

    rule = rule_service.create_rule(tenant_id, rule_data)
    return jsonify({
        'message': 'Rule created successfully',
        'rule': {
            'name': rule.name,
            'description': rule.description,
            'ip': rule.ip,
            'expired_date': rule.expired_date.isoformat() if rule.expired_date else None,
            'created_at': rule.created_at.isoformat(),
            'updated_at': rule.updated_at.isoformat()
        }
    }), 201


@rules_blue_print.route('', methods=['GET'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='read')
def get_rules(tenant_id: str):
    rule_service = RuleService()
    include_expired = request.args.get('include_expired', 'true').lower() == 'true'
    search_query = request.args.get('search', '')

    if search_query:
        rules = rule_service.search_rules(tenant_id, search_query)
    else:
        rules = rule_service.get_rules(tenant_id, include_expired)

    rules_data = []
    for rule in rules:
        rules_data.append({
            'name': rule.name,
            'description': rule.description,
            'ip': rule.ip,
            'expired_date': rule.expired_date.isoformat() if rule.expired_date else None,
            'is_expired': rule.is_expired(),
            'created_at': rule.created_at.isoformat(),
            'updated_at': rule.updated_at.isoformat()
        })

    return jsonify({
        'rules': rules_data,
        'total_count': len(rules_data),
        'tenant_id': tenant_id
    }), 200


@rules_blue_print.route('/<rule_name>', methods=['GET'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='read')
def get_rule(rule_name: str, tenant_id: str):
    rule_service = RuleService()
    rule = rule_service.get_rule(tenant_id, rule_name)

    return jsonify({
        'rule': {
            'name': rule.name,
            'description': rule.description,
            'ip': rule.ip,
            'expired_date': rule.expired_date.isoformat() if rule.expired_date else None,
            'is_expired': rule.is_expired(),
            'created_at': rule.created_at.isoformat(),
            'updated_at': rule.updated_at.isoformat()
        }
    }), 200


@rules_blue_print.route('/<rule_name>', methods=['PUT'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='write')
@audit_log(action=AuditAction.UPDATE, resource_name_key='rule_name')
def update_rule(rule_name: str, tenant_id: str):
    rule_service = RuleService()
    update_data = request.get_json()

    if not update_data:
        return jsonify({'error': 'Request body is required'}), 400
    rule = rule_service.update_rule(tenant_id, rule_name, update_data)

    return jsonify({
        'message': 'Rule updated successfully',
        'rule': {
            'name': rule.name,
            'description': rule.description,
            'ip': rule.ip,
            'expired_date': rule.expired_date.isoformat() if rule.expired_date else None,
            'created_at': rule.created_at.isoformat(),
            'updated_at': rule.updated_at.isoformat()
        }
    }), 200


@rules_blue_print.route('/<rule_name>', methods=['DELETE'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='delete')
@audit_log(action=AuditAction.DELETE, resource_name_key='rule_name')
def delete_rule(rule_name: str, tenant_id: str):
    rule_service = RuleService()
    rule_service.delete_rule(tenant_id, rule_name)

    return jsonify({
        'message': f'Rule "{rule_name}" deleted successfully'
    }), 200


@rules_blue_print.route('/stats', methods=['GET'])
@handle_errors
@rate_limit(default_limit=100)
@validate_tenant(required_permission='read')
def get_rule_stats(tenant_id: str):
    rule_service = RuleService()

    total_rules = rule_service.get_rule_count(tenant_id)
    all_rules = rule_service.get_rules(tenant_id, include_expired=True)

    active_rules_count = sum(1 for rule in all_rules if not rule.is_expired())
    expired_rules_count = total_rules - active_rules_count

    return jsonify({
        'tenant_id': tenant_id,
        'total_rules': total_rules,
        'active_rules': active_rules_count,
        'expired_rules': expired_rules_count,
        'statistics': {
            'rules_created_today': 0,  # Could be implemented with date filtering
            'rules_updated_today': 0,  # Could be implemented with date filtering
        }
    }), 200
