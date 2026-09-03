"""Access-token expiry checks and config-entry persistence."""

from __future__ import annotations

import base64
import json
from time import time
from typing import TYPE_CHECKING

from custom_components.hellofresh.const import CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, LOGGER, TOKEN_REFRESH_SKEW_SECONDS

if TYPE_CHECKING:
    from custom_components.hellofresh.api import HelloFreshApiClient
    from custom_components.hellofresh.data import HelloFreshConfigEntry
    from homeassistant.core import HomeAssistant


def jwt_expiry(token: str) -> float | None:
    """Return the JWT ``exp`` claim as a UNIX timestamp, if present."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
    except ValueError, json.JSONDecodeError, UnicodeDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    exp = payload.get("exp")
    if exp is None:
        return None
    try:
        return float(exp)
    except TypeError, ValueError:
        return None


def access_token_needs_refresh(
    access_token: str | None,
    *,
    skew_seconds: float = TOKEN_REFRESH_SKEW_SECONDS,
) -> bool:
    """Return True when the access token is missing or near expiry."""
    if not access_token:
        return True
    exp = jwt_expiry(access_token)
    if exp is None:
        # Opaque tokens still work until the API rejects them; retry-on-401 handles that.
        return False
    return time() >= exp - skew_seconds


def persist_client_tokens(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
    client: HelloFreshApiClient,
) -> bool:
    """
    Write refreshed tokens back to the config entry when they change.

    Does not reload the integration. Callers must keep using the in-memory client.
    """
    current_access = entry.data.get(CONF_ACCESS_TOKEN)
    current_refresh = entry.data.get(CONF_REFRESH_TOKEN)
    if client.access_token == current_access and client.refresh_token == current_refresh:
        return False
    if not client.access_token:
        LOGGER.debug("Skipping token persist for %s; access token is empty", entry.entry_id)
        return False

    new_data = {
        **entry.data,
        CONF_ACCESS_TOKEN: client.access_token,
        CONF_REFRESH_TOKEN: client.refresh_token,
    }
    hass.config_entries.async_update_entry(entry, data=new_data)
    LOGGER.debug("Persisted refreshed HelloFresh tokens for %s", entry.entry_id)
    return True
