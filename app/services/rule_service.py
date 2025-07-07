from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
from app.utils.database import DatabaseManager
from app.models.rule import Rule
from app.exceptions.custom_exceptions import RuleNotFoundError, RuleAlreadyExistsError
from app.utils.validators import validate_rule_data

logger = logging.getLogger(__name__)


class RuleService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collection_name = 'rules'

    @property
    def collection(self):
        return self.db_manager.db[self.collection_name]

    def create_rule(self, tenant_id: str, rule_data: Dict[str, Any]) -> Rule:
        validated_data = validate_rule_data(rule_data)

        is_existing_rule = self.collection.find_one({
            'tenant_id': tenant_id,
            'name': validated_data['name']
        })

        if is_existing_rule:
            raise RuleAlreadyExistsError(validated_data['name'], tenant_id)

        rule = Rule(
            name=validated_data['name'],
            description=validated_data['description'],
            ip=validated_data['ip'],
            tenant_id=tenant_id,
            expired_date=validated_data.get('expired_date')
        )

        result = self.collection.insert_one(rule.to_dict())
        if result.inserted_id:
            logger.info(f"Rule '{rule.name}' created and saved for tenant '{tenant_id}'")
            return rule
        else:
            raise Exception("Failed to create rule")

    def get_rule(self, tenant_id: str, rule_name: str) -> Rule:
        rule_data = self.collection.find_one({
            'tenant_id': tenant_id,
            'name': rule_name
        })

        if not rule_data:
            raise RuleNotFoundError(rule_name, tenant_id)

        return Rule.from_dict(rule_data)

    def get_rules(self, tenant_id: str, include_expired: bool = True) -> List[Rule]:
        query = {'tenant_id': tenant_id}

        if not include_expired:
            query['$or'] = [
                {'expired_date': None},
                {'expired_date': {'$gt': datetime.now(timezone.utc)}}
            ]

        rules_data = self.collection.find(query).sort('created_at', -1)
        return [Rule.from_dict(rule_data) for rule_data in rules_data]

    def update_rule(self, tenant_id: str, rule_name: str, update_data: Dict[str, Any]) -> Rule:
        validated_data = validate_rule_data(update_data)

        existing_rule = self.collection.find_one({
            'tenant_id': tenant_id,
            'name': rule_name
        })

        if not existing_rule:
            raise RuleNotFoundError(rule_name, tenant_id)

        # Rule name is being changed
        if 'name' in validated_data and validated_data['name'] != rule_name:
            conflicting_rule = self.collection.find_one({
                'tenant_id': tenant_id,
                'name': validated_data['name']
            })
            if conflicting_rule:
                raise RuleAlreadyExistsError(validated_data['name'], tenant_id)

        validated_data['updated_at'] = datetime.now(timezone.utc)
        update_operation_result = self.collection.update_one(
            {'tenant_id': tenant_id, 'name': rule_name},
            {'$set': validated_data}
        )

        if update_operation_result.modified_count > 0:
            logger.info(f"Rule '{rule_name}' updated for tenant '{tenant_id}'")
            return self.get_rule(tenant_id, validated_data.get('name', rule_name))
        else:
            raise Exception("Failed to update rule")

    def delete_rule(self, tenant_id: str, rule_name: str) -> bool:
        delete_operation_result = self.collection.delete_one({
            'tenant_id': tenant_id,
            'name': rule_name
        })

        if delete_operation_result.deleted_count > 0:
            logger.info(f"Rule '{rule_name}' deleted for tenant '{tenant_id}'")
            return True
        else:
            raise RuleNotFoundError(rule_name, tenant_id)

    def delete_expired_rules(self, tenant_id: Optional[str] = None) -> int:
        query = {
            'expired_date': {'$lte': datetime.now(timezone.utc)}
        }

        if tenant_id:
            query['tenant_id'] = tenant_id

        result = self.collection.delete_many(query)
        deleted_count = result.deleted_count

        if deleted_count > 0:
            logger.info(f"{datetime.now(timezone.utc)} - Deleted {deleted_count} expired rules" +
                        (f" for tenant '{tenant_id}'" if tenant_id else ""))

        return deleted_count

    def get_rule_count(self, tenant_id: str) -> int:
        return self.collection.count_documents({'tenant_id': tenant_id})


# rename to search_rules_by_name_or_description
    def search_rules(self, tenant_id: str, search_query: str) -> List[Rule]:
        query = {
            'tenant_id': tenant_id,
            '$or': [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}}
            ]
        }

        rules_data = self.collection.find(query).sort('created_at', -1)
        return [Rule.from_dict(rule_data) for rule_data in rules_data]
