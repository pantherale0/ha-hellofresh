"""
API package for hellofresh.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client for polling.
    Service actions may call the API client for on-demand recipe queries.
"""

from .client import (
    HelloFreshApiClient,
    HelloFreshApiClientAuthenticationError,
    HelloFreshApiClientCommunicationError,
    HelloFreshApiClientError,
    recipe_to_dict,
)

__all__ = [
    "HelloFreshApiClient",
    "HelloFreshApiClientAuthenticationError",
    "HelloFreshApiClientCommunicationError",
    "HelloFreshApiClientError",
    "recipe_to_dict",
]
