"""The one-way membrane.

The pathogen frame makes one failure mode very easy to drift into: code that
propagates itself into systems whose owners did not invite it. That is a worm,
it is illegal, and it is not what this is.

The rule is structural, not advisory:

    PANGENOME PULLS. IT NEVER PUSHES.

The organism may READ any public registry, repository, or feed that any human
could read with a browser. It may acquire capability packets into itself. It may
never transmit a packet, a payload, or an instruction OUT to another host, agent
or endpoint. There is no outbound conjugation: `pilus.conjugate()` moves plasmids
only between hosts that live inside this one process.

Enforced here, at the only place the organism is allowed to touch the network.
Every fetch goes through `fetch()`, which refuses anything but GET, refuses
request bodies, and refuses non-allowlisted hosts.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import urlparse

__all__ = ["OutboundRefused", "fetch", "fetch_json", "ALLOWED_HOSTS"]

USER_AGENT = "pangenome-organism/0.1 (+https://github.com/sammyghe/pangenome)"

# Hosts the organism is permitted to sense. Public, unauthenticated, read-only.
ALLOWED_HOSTS = {
    "registry.modelcontextprotocol.io",
    "api.github.com",
    "raw.githubusercontent.com",
    "pypi.org",
    "registry.npmjs.org",
}


class OutboundRefused(RuntimeError):
    """Raised when something attempts to transmit out through the membrane."""


def _guard(url: str, method: str, body: object) -> None:
    if method.upper() != "GET":
        raise OutboundRefused(
            f"membrane: only GET is permitted; refused {method.upper()} {url}"
        )
    if body is not None:
        raise OutboundRefused(
            "membrane: outbound request bodies are forbidden — "
            "the organism pulls, it never pushes"
        )
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise OutboundRefused(f"membrane: https required, got {parsed.scheme!r}")
    if (parsed.hostname or "") not in ALLOWED_HOSTS:
        raise OutboundRefused(
            f"membrane: host {parsed.hostname!r} is not in the sensing allowlist"
        )


def fetch(url: str, *, method: str = "GET", body: object = None,
          timeout: int = 20, token: str | None = None) -> bytes:
    """The organism's only route to the network. Read-only, allowlisted."""
    _guard(url, method, body)
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.URLError as e:
        raise ConnectionError(f"sense failed for {url}: {e}") from e


def fetch_json(url: str, *, timeout: int = 20, token: str | None = None):
    return json.loads(fetch(url, timeout=timeout, token=token).decode("utf-8"))
