"""Centralized runtime host detection and URL normalization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

DEFAULT_GITHUB_SERVER_URL = "https://github.com"
DEFAULT_GITHUB_API_URL = "https://api.github.com"
GITEA_API_SUFFIX = "/api/v1"
GITHUB_API_SUFFIX = "/api/v3"


class RuntimeHost(StrEnum):
    """Supported action runtime hosts."""

    GITEA = "gitea"
    GITHUB = "github"


@dataclass(frozen=True)
class ResolvedRuntimeHost:
    """Normalized host and URL values for one action run."""

    host: RuntimeHost
    api_url: str
    server_url: str
    repository: str
    ref: str


def normalize_url(url: str) -> str:
    """Normalize a URL-like value by trimming whitespace and trailing slashes."""

    return url.strip().rstrip("/")


def detect_runtime_host(*, api_url: str, server_url: str) -> RuntimeHost:
    """Detect the current runtime host from API or server URL inputs."""

    normalized_api_url = normalize_url(api_url)
    normalized_server_url = normalize_url(server_url)

    if normalized_api_url:
        if normalized_api_url == DEFAULT_GITHUB_API_URL or normalized_api_url.endswith(
            GITHUB_API_SUFFIX
        ):
            return RuntimeHost.GITHUB
        if normalized_api_url.endswith(GITEA_API_SUFFIX):
            return RuntimeHost.GITEA

    if normalized_server_url:
        if normalized_server_url == DEFAULT_GITHUB_SERVER_URL:
            return RuntimeHost.GITHUB
        return RuntimeHost.GITEA

    return RuntimeHost.GITEA


def default_server_url_for_host(host: RuntimeHost) -> str:
    """Return the default server URL for the detected host."""

    if host is RuntimeHost.GITHUB:
        return DEFAULT_GITHUB_SERVER_URL
    return ""


def default_api_url_for_host(host: RuntimeHost, *, server_url: str) -> str:
    """Return the default API URL for the detected host and server."""

    if host is RuntimeHost.GITHUB:
        return DEFAULT_GITHUB_API_URL

    normalized_server_url = normalize_url(server_url)
    if not normalized_server_url:
        return ""

    return f"{normalized_server_url}{GITEA_API_SUFFIX}"


def server_url_from_api_url(host: RuntimeHost, api_url: str) -> str:
    """Derive the matching server URL from a normalized API URL."""

    normalized_api_url = normalize_url(api_url)
    if not normalized_api_url:
        return default_server_url_for_host(host)

    if host is RuntimeHost.GITHUB:
        return DEFAULT_GITHUB_SERVER_URL

    if normalized_api_url.endswith(GITEA_API_SUFFIX):
        return normalized_api_url.removesuffix(GITEA_API_SUFFIX)

    return default_server_url_for_host(host)


def resolve_runtime_host(
    *,
    api_url: str,
    server_url: str,
    repository: str,
    ref: str,
) -> ResolvedRuntimeHost:
    """Resolve the runtime host once and normalize all downstream values."""

    normalized_api_url = normalize_url(api_url)
    normalized_server_url = normalize_url(server_url)
    host = detect_runtime_host(api_url=normalized_api_url, server_url=normalized_server_url)

    if not normalized_server_url:
        normalized_server_url = server_url_from_api_url(host, normalized_api_url)
    if not normalized_api_url:
        normalized_api_url = default_api_url_for_host(host, server_url=normalized_server_url)

    return ResolvedRuntimeHost(
        host=host,
        api_url=normalized_api_url,
        server_url=normalized_server_url,
        repository=repository,
        ref=ref,
    )
