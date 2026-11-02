from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import httpx
from . import _core
from .errors import TransportError
from ._sync_methods import SyncMethods
from ._async_methods import AsyncMethods

class _Configuration:
    def _configure(self, base_url: str | None, api_key: str | None, env_file: str | Path | bool | None) -> None:
        self._settings = _core.configuration(env_file)
        self.base_url = _core.base_url(base_url or self._settings.get('PARSIAN_API_URL') or 'http://127.0.0.1:3101/v1')
        self._api_key = api_key if api_key is not None else self._settings.get('PARSIAN_API_KEY', '')

    def _credential(self, name: str, supplied: str | None) -> str:
        value = supplied if supplied is not None else self._settings.get('PARSIAN_' + name)
        if not isinstance(value, str) or not value:
            raise ValueError(f'Missing PARSIAN_{name}; supply it explicitly or in .env')
        return value

    def __repr__(self) -> str:
        return f'{type(self).__name__}(base_url={self.base_url!r})'

class Client(_Configuration, SyncMethods):
    """Synchronous HTTP client for a running Parsian Node.js service."""
    def __init__(self, base_url: str | None = None, api_key: str | None = None, *, timeout: float = 35.0,
                 env_file: str | Path | bool | None = None, transport: httpx.BaseTransport | None = None):
        self._configure(base_url, api_key, env_file)
        self._http = httpx.Client(timeout=timeout, transport=transport, follow_redirects=False)

    def request(self, method: str, path: str, *, query: Mapping[str, Any] | None = None, fields: Any = None) -> Any:
        method = method.upper()
        url = self.base_url + _core.relative_path(path)
        headers = {'accept': 'application/json'}
        if self._api_key:
            headers['x-api-key'] = self._api_key
        data = _core.form_fields(fields) if fields is not None else None
        if fields is not None:
            headers['content-type'] = 'application/x-www-form-urlencoded'
        try:
            response = self._http.request(method, url, params=query, data=data, headers=headers)
        except httpx.RequestError:
            raise TransportError(method) from None
        return _core.decode(response, method)

    def operation(self, command: str, **fields: Any) -> Any:
        method, path, query, body = _core.operation_request(command, fields)
        return self.request(method, path, query=query, fields=body)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

class AsyncClient(_Configuration, AsyncMethods):
    """Async counterpart with matching methods and no automatic retries."""
    def __init__(self, base_url: str | None = None, api_key: str | None = None, *, timeout: float = 35.0,
                 env_file: str | Path | bool | None = None, transport: httpx.AsyncBaseTransport | None = None):
        self._configure(base_url, api_key, env_file)
        self._http = httpx.AsyncClient(timeout=timeout, transport=transport, follow_redirects=False)

    async def request(self, method: str, path: str, *, query: Mapping[str, Any] | None = None, fields: Any = None) -> Any:
        method = method.upper()
        url = self.base_url + _core.relative_path(path)
        headers = {'accept': 'application/json'}
        if self._api_key:
            headers['x-api-key'] = self._api_key
        data = _core.form_fields(fields) if fields is not None else None
        if fields is not None:
            headers['content-type'] = 'application/x-www-form-urlencoded'
        try:
            response = await self._http.request(method, url, params=query, data=data, headers=headers)
        except httpx.RequestError:
            raise TransportError(method) from None
        return _core.decode(response, method)

    async def operation(self, command: str, **fields: Any) -> Any:
        method, path, query, body = _core.operation_request(command, fields)
        return await self.request(method, path, query=query, fields=body)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
