from marshmallow import Schema, fields, validate, ValidationError as MarshmallowValidationError
import ipaddress
from typing import Dict, Any


class RuleSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    ip = fields.Str(required=True)
    expired_date = fields.DateTime(required=False, allow_none=True)

    def validate_ip(self, value: str) -> str:
        try:
            ipaddress.ip_address(value)
            return value
        except ValueError:
            raise MarshmallowValidationError("Invalid IP address format")


class BulkOperationSchema(Schema):
    operations = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1, max=100))


def validate_rule_data(data: Dict[str, Any]) -> Dict[str, Any]:
    schema = RuleSchema()
    try:
        validated_data = schema.load(data)
        if 'ip' in validated_data:
            try:
                ipaddress.ip_address(validated_data['ip'])
            except ValueError:
                raise MarshmallowValidationError("Invalid IP address format")
        return validated_data
    except MarshmallowValidationError as e:
        from app.exceptions.custom_exceptions import ValidationError
        raise ValidationError(str(e))


def validate_bulk_operations(data: Dict[str, Any]) -> Dict[str, Any]:
    schema = BulkOperationSchema()
    try:
        return schema.load(data)
    except MarshmallowValidationError as e:
        from app.exceptions.custom_exceptions import ValidationError
        raise ValidationError(str(e))
