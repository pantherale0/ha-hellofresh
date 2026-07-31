"""Core DataUpdateCoordinator implementation for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pyhellofresh import HelloFreshAuthenticationError, HelloFreshError

from custom_components.hellofresh.const import CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, LOGGER
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.hellofresh.data import HelloFreshConfigEntry


class HelloFreshDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and distribute HelloFresh account data."""

    config_entry: HelloFreshConfigEntry

    async def _async_setup(self) -> None:
        """Run one-time coordinator setup before the first refresh."""
        LOGGER.debug("Coordinator setup complete for %s", self.config_entry.entry_id)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch batched HelloFresh data and persist refreshed tokens."""
        client = self.config_entry.runtime_data.client
        try:
            data = await client.async_get_coordinator_payload()
        except HelloFreshAuthenticationError as err:
            LOGGER.warning("Authentication error - %s", err)
            raise ConfigEntryAuthFailed(
                translation_domain="hellofresh",
                translation_key="authentication_failed",
            ) from err
        except HelloFreshError as err:
            LOGGER.exception("Error communicating with HelloFresh API")
            raise UpdateFailed(
                translation_domain="hellofresh",
                translation_key="update_failed",
            ) from err

        await self._async_persist_tokens()
        return data

    async def _async_persist_tokens(self) -> None:
        """Write refreshed tokens back to the config entry when they change."""
        client = self.config_entry.runtime_data.client
        current_access = self.config_entry.data.get(CONF_ACCESS_TOKEN)
        current_refresh = self.config_entry.data.get(CONF_REFRESH_TOKEN)
        if client.access_token == current_access and client.refresh_token == current_refresh:
            return

        new_data = {
            **self.config_entry.data,
            CONF_ACCESS_TOKEN: client.access_token,
            CONF_REFRESH_TOKEN: client.refresh_token,
        }
        self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
        LOGGER.debug("Persisted refreshed HelloFresh tokens for %s", self.config_entry.entry_id)
