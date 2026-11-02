from __future__ import annotations
import json
import math
import os
import re
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote, urlsplit
from dotenv import dotenv_values
from .errors import ApiError, ProtocolError

OPERATIONS = json.loads(files('parsianapi').joinpath('_operations.json').read_text(encoding='utf-8'))
_OPERATIONS = {op['command']: op for op in OPERATIONS}

def configuration(env_file: str | Path | None | bool = None) -> dict[str, str]:
    data: dict[str, str] = {}
    if env_file is not False:
        path = Path(env_file) if env_file else Path.cwd() / '.env'
        if path.is_file():
            data.update({k: v for k, v in dotenv_values(path, encoding='utf-8-sig', interpolate=False).items() if v is not None and v != ''})
    data.update(os.environ)
    return data

def base_url(value: str) -> str:
    p = urlsplit(value)
    if p.scheme not in ('http', 'https') or not p.netloc or p.username or p.password or p.query or p.fragment:
        raise ValueError('base_url must be an HTTP(S) service URL without credentials, query or fragment')
    result = value.rstrip('/')
    return result if result.endswith('/v1') else result + '/v1'

def relative_path(value: str) -> str:
    p = urlsplit(value)
    if not value.startswith('/') or value.startswith('//') or p.netloc or p.scheme or p.query or p.fragment or '\\' in value:
        raise ValueError('Use a relative API path and pass query separately')
    if any(part in ('.', '..') for part in value.split('/')):
        raise ValueError('Path traversal is not allowed')
    return value

def amount(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= 9007199254740991:
        raise ValueError('amount must be a positive integer in IRR, at most 2**53-1')
    return value

def clean(values: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in values.items() if v is not None and v != ''}

def login_fields(settings: Mapping[str, str], username: str | None, password: str | None, mobile_number: str | None) -> dict[str, Any]:
    for value in (username, password, mobile_number):
        if value is not None and (not isinstance(value, str) or not value):
            raise ValueError('Explicit login fields must be nonempty strings')
    return clean({'username':username if username is not None else settings.get('PARSIAN_USER'),'password':password if password is not None else settings.get('PARSIAN_PASS'),'mobileNumber':mobile_number if mobile_number is not None else settings.get('PARSIAN_MOBILE')})

def form_fields(value: Any, prefix: str = '') -> dict[str, str]:
    if value is None:
        return {prefix: 'null'} if prefix else {}
    if isinstance(value, Mapping):
        out: dict[str, str] = {}
        for k, v in value.items():
            if not isinstance(k, str) or k in ('__proto__', 'constructor', 'prototype'):
                raise ValueError('Invalid field name')
            out.update(form_fields(v, f'{prefix}.{k}' if prefix else k))
        return out
    if isinstance(value, (list, tuple)):
        out = {}
        for i, v in enumerate(value):
            if i > 1000:
                raise ValueError('Too many array elements')
            out.update(form_fields(v, f'{prefix}.{i}' if prefix else str(i)))
        return out
    if not prefix or not isinstance(value, (str, int, float, bool)):
        raise ValueError('Unsupported form value')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Non-finite values are not supported')
    return {prefix: 'true' if value is True else 'false' if value is False else str(value)}

def _properties(schema: dict[str, Any]) -> dict[str, Any]:
    result = dict(schema.get('properties', {}))
    for variant in schema.get('anyOf', []):
        result.update(variant.get('properties', {}))
    return result

def _normal(name: str) -> str:
    return re.sub('[^a-z0-9]', '', name.lower())

def _resolve(key: str, allowed: Mapping[str, Any]) -> str:
    found = next((name for name in allowed if _normal(name) == _normal(key)), None)
    if found is None:
        raise ValueError(f'Unknown operation field: {key}')
    return found

def map_body(value: Any, schema: dict[str, Any]) -> Any:
    if isinstance(value, Mapping) and schema.get('type') == 'array':
        if set(value) != {str(i) for i in range(len(value))}:
            raise ValueError('Array indices must start at zero and be contiguous')
        return [map_body(value[str(i)], schema.get('items', {})) for i in range(len(value))]
    if isinstance(value, Mapping):
        props = _properties(schema)
        return {(_resolve(k, props) if props else k): map_body(v, props.get(_resolve(k, props), {}) if props else {}) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [map_body(v, schema.get('items', {})) for v in value]
    return value

def operation_request(command: str, fields: dict[str, Any]) -> tuple[str, str, dict[str, Any] | None, Any]:
    command = command.replace('_', '-')
    if command not in _OPERATIONS:
        raise ValueError(f'Unknown operation: {command}')
    op = _OPERATIONS[command]
    route = op['path']
    query: dict[str, Any] = {}
    body: dict[str, Any] = {}
    parameters = {p['name']: p for p in op['parameters']}
    props = _properties(op['bodySchema'])
    array_body = None
    for key, value in fields.items():
        if value is None:
            continue
        if op['bodySchema'].get('type') == 'array' and key == 'items':
            array_body = map_body(value, op['bodySchema'])
            continue
        candidates = {**props, **parameters}
        name = _resolve(key, candidates)
        parameter = parameters.get(name)
        if parameter and parameter['in'] == 'path':
            if not isinstance(value, str) or not value:
                raise ValueError(f'{name} must be a nonempty string')
            route = route.replace('{' + name + '}', quote(value, safe=''))
        elif parameter:
            query[name] = value
        else:
            body[name] = map_body(value, props[name])
    if '{' in route:
        raise ValueError('Missing path parameter')
    return op['method'], route, query or None, array_body if array_body is not None else body if op['method'] != 'GET' else None

def decode(response: Any, method: str) -> Any:
    try:
        payload = response.json()
    except (ValueError, UnicodeError):
        if not 200 <= response.status_code < 300:
            raise ApiError(response.status_code, None) from None
        raise ProtocolError(method) from None
    if not 200 <= response.status_code < 300:
        raise ApiError(response.status_code, payload)
    return payload
