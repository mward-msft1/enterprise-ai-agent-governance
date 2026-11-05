"""Minimal Graph client with an injectable transport.

The default tenant transport uses the Python standard library. Tests pass a
recording transport so no network is required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from eagov.errors import GovernanceError


@dataclass
class GraphResponse:
    status: int
    body: dict[str, Any]
    headers: dict[str, str]


class Transport(Protocol):
    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
    ) -> GraphResponse: ...


@dataclass
class RecordingTransport:
    """In-memory transport for tests and offline demonstrations."""

    scripted: list[GraphResponse] = field(default_factory=list)
    calls: list[dict[str, Any]] = field(default_factory=list)

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
    ) -> GraphResponse:
        parsed = json.loads(body.decode("utf-8")) if body else None
        self.calls.append(
            {"method": method, "url": url, "headers": dict(headers), "body": parsed}
        )
        if not self.scripted:
            return GraphResponse(status=200, body={"value": []}, headers={})
        return self.scripted.pop(0)


class UrllibTransport:
    """Live HTTP transport. Used only after placeholder checks pass."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
    ) -> GraphResponse:
        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                payload = json.loads(raw) if raw else {}
                return GraphResponse(
                    status=response.status,
                    body=payload if isinstance(payload, dict) else {"value": payload},
                    headers={k: v for k, v in response.headers.items()},
                )
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GovernanceError(
                f"Graph HTTP {exc.code} for {method} {url}: {detail[:500]}"
            ) from exc
        except URLError as exc:
            raise GovernanceError(f"Graph network error for {url}: {exc.reason}") from exc


class GraphClient:
    def __init__(
        self,
        token_provider,
        transport: Transport | None = None,
        base_url: str = "https://graph.microsoft.com/v1.0",
    ):
        self.token_provider = token_provider
        self.transport = transport or UrllibTransport()
        self.base_url = base_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> GraphResponse:
        token = self.token_provider()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        payload = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(body).encode("utf-8")
        if extra_headers:
            headers.update(extra_headers)
        url = path if path.startswith("https://") else f"{self.base_url}{path}"
        return self.transport.send(method, url, headers, payload)

    def get(self, path: str, extra_headers: dict[str, str] | None = None) -> GraphResponse:
        return self.request("GET", path, extra_headers=extra_headers)

    def post(
        self,
        path: str,
        body: dict[str, Any],
        extra_headers: dict[str, str] | None = None,
    ) -> GraphResponse:
        return self.request("POST", path, body=body, extra_headers=extra_headers)
