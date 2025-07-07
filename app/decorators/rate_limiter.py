from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple
import logging

import app
from app.exceptions.custom_exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        self._requests: Dict[str, list] = {}
        self._limits: Dict[str, int] = {}

    def set_limit(self, tenant_id: str, limit: int) -> None:
        self._limits[tenant_id] = limit
        logger.info(f"Rate limit set for tenant {tenant_id}: {limit} requests/minute")

    def is_allowed(self, tenant_id: str, default_limit_per_minute: int = 100) -> Tuple[bool, int]:
        now = datetime.now(timezone.utc)
        rate_limit_time_window_minutes = app.config.Config.RATE_LIMIT_TIME_WINDOW_MINUTES
        requests_start_time = now - timedelta(minutes=rate_limit_time_window_minutes)

        tenant_rate_limit = self._limits.get(tenant_id, default_limit_per_minute)

        if tenant_id not in self._requests:
            self._requests[tenant_id] = []

        # Remove old requests outside the window
        self._requests[tenant_id] = [
            request_time for request_time in self._requests[tenant_id]
            if request_time > requests_start_time
        ]

        # Check if limit is exceeded
        current_requests = len(self._requests[tenant_id])
        if current_requests >= tenant_rate_limit:
            logger.warning(f"Rate limit exceeded for tenant {tenant_id}: {current_requests}/{tenant_rate_limit}")
            return False, tenant_rate_limit - current_requests

        self._requests[tenant_id].append(now)
        return True, tenant_rate_limit - current_requests - 1

    def get_remaining_requests(self, tenant_id: str, default_limit: int = 100) -> int:
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=1)

        limit = self._limits.get(tenant_id, default_limit)

        if tenant_id not in self._requests:
            return limit

        current_requests_count = sum(
            1 for req_time in self._requests[tenant_id]
            if req_time > start_time
        )

        return max(0, limit - current_requests_count)


rate_limiter = RateLimiter()


def rate_limit(default_limit: int = 100):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            tenant_id = request.headers.get('X-Tenant-ID')
            if not tenant_id:
                return jsonify({'error': 'X-Tenant-ID header is required'}), 400

            allowed, remaining = rate_limiter.is_allowed(tenant_id, default_limit)
            if not allowed:
                raise RateLimitExceededError(tenant_id)

            response = func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(rate_limiter._limits.get(tenant_id, default_limit))
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(int((datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp()))

            return response

        return decorated_function

    return decorator
