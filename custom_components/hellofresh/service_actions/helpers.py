"""Shared helpers for resolving loaded HelloFresh config entries."""

from __future__ import annotations

from custom_components.hellofresh.api import HelloFreshApiClient
from custom_components.hellofresh.const import CONF_CONFIG_ENTRY_ID, DOMAIN
from custom_components.hellofresh.data import HelloFreshConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError


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


def resolve_client(hass: HomeAssistant, call: ServiceCall) -> HelloFreshApiClient:
    """Resolve the API client for a service call."""
    entry = resolve_entry_from_service(hass, call)
    return entry.runtime_data.client


def resolve_client_for_entry(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> HelloFreshApiClient:
    """Resolve the API client for an optional config entry id."""
    return resolve_entry(hass, entry_id=entry_id).runtime_data.client
