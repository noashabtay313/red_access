class RuleManagementException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class TenantNotFoundError(RuleManagementException):
    def __init__(self, tenant_id):
        super().__init__(f"Tenant '{tenant_id}' not found", 404)


class RuleNotFoundError(RuleManagementException):
    def __init__(self, rule_name, tenant_id):
        super().__init__(f"Rule '{rule_name}' not found for tenant '{tenant_id}'", 404)


class RuleAlreadyExistsError(RuleManagementException):
    def __init__(self, rule_name, tenant_id):
        super().__init__(f"Rule '{rule_name}' already exists for tenant '{tenant_id}'", 409)


class RateLimitExceededError(RuleManagementException):
    """Raised when rate limit is exceeded"""
    def __init__(self, tenant_id):
        super().__init__(f"Rate limit exceeded for tenant '{tenant_id}'", 429)


class ValidationError(RuleManagementException):
    def __init__(self, message):
        super().__init__(f"Validation error: {message}", 400)


class BulkOperationError(RuleManagementException):
    def __init__(self, message, failed_operations=None):
        super().__init__(message, 400)
        self.failed_operations = failed_operations or []