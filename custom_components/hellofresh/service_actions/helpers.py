"""Shared helpers for resolving loaded HelloFresh config entries."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import NoReturn, TypeVar

from pyhellofresh import HelloFreshAuthenticationError

from custom_components.hellofresh.api import HelloFreshApiClient
from custom_components.hellofresh.const import CONF_CONFIG_ENTRY_ID, DOMAIN
from custom_components.hellofresh.data import HelloFreshConfigEntry
from custom_components.hellofresh.utils.tokens import persist_client_tokens
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

T = TypeVar("T")


def resolve_entry(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> HelloFreshConfigEntry:
    """Resolve a loaded HelloFresh config entry."""
    if entry_id:
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN or entry.runtime_data is None:
            raise HomeAssistantError(
                translation_domain="hellofresh",
                translation_key="service_entry_not_found",
            )
        return entry  # type: ignore[return-value]

    entries = [entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.runtime_data is not None]
    if not entries:
        raise HomeAssistantError(
            translation_domain="hellofresh",
            translation_key="service_no_entries",
        )
    if len(entries) > 1:
        raise HomeAssistantError(
            translation_domain="hellofresh",
            translation_key="service_multiple_entries",
        )
    return entries[0]  # type: ignore[return-value]


def resolve_entry_from_service(hass: HomeAssistant, call: ServiceCall) -> HelloFreshConfigEntry:
    """Resolve the config entry targeted by a service call."""
    return resolve_entry(hass, entry_id=call.data.get(CONF_CONFIG_ENTRY_ID))


def _raise_service_auth_failed(err: HelloFreshAuthenticationError) -> NoReturn:
    """Raise the translated service authentication error."""
    raise HomeAssistantError(
        translation_domain="hellofresh",
        translation_key="service_auth_failed",
    ) from err


async def async_call_authenticated(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
    operation: Callable[[HelloFreshApiClient], Awaitable[T]],
) -> T:
    """
    Run an API operation after ensuring tokens are valid, then persist them.

    pyhellofresh does not refresh tokens for unauthenticated-or-optional endpoints
    such as recipe search. This helper refreshes proactively and retries once on 401.
    """
    client = entry.runtime_data.client
    try:
        try:
            await client.async_ensure_fresh_token()
        except HelloFreshAuthenticationError as err:
            _raise_service_auth_failed(err)

        try:
            result = await operation(client)
        except HelloFreshAuthenticationError as err:
            if not client.refresh_token:
                _raise_service_auth_failed(err)
            try:
                await client.async_refresh_access_token()
                result = await operation(client)
            except HelloFreshAuthenticationError as retry_err:
                _raise_service_auth_failed(retry_err)
        return result
    finally:
        persist_client_tokens(hass, entry, client)


async def async_call_authenticated_from_service(
    hass: HomeAssistant,
    call: ServiceCall,
    operation: Callable[[HelloFreshApiClient], Awaitable[T]],
) -> T:
    """Run an authenticated API operation for a service call."""
    return await async_call_authenticated(hass, resolve_entry_from_service(hass, call), operation)
