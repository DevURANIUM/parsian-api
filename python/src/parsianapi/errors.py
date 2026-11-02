from __future__ import annotations
from typing import Any

class ParsianError(Exception):
    """Base class for library errors."""

class ApiError(ParsianError):
    def __init__(self, status_code: int, payload: Any):
        self.status_code = status_code
        self.payload = payload
        info = payload if isinstance(payload, dict) else {}
        self.code = info.get('code')
        self.bank_status = info.get('bankStatus')
        self.next_action = info.get('nextAction')
        super().__init__(f'API request failed (HTTP {status_code}' + (f', {self.code}' if self.code else '') + ')')

class TransportError(ParsianError):
    def __init__(self, method: str):
        self.request_may_have_succeeded = method.upper() not in ('GET', 'HEAD', 'OPTIONS')
        super().__init__('API service connection failed or timed out; no automatic retry was attempted')

class ProtocolError(ParsianError):
    def __init__(self, method: str):
        self.request_may_have_succeeded = method.upper() not in ('GET', 'HEAD', 'OPTIONS')
        super().__init__('API service returned an invalid JSON response')
