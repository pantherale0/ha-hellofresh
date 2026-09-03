"""Core DataUpdateCoordinator implementation for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pyhellofresh import HelloFreshAuthenticationError, HelloFreshError

from custom_components.hellofresh.const import LOGGER
from custom_components.hellofresh.utils.tokens import persist_client_tokens
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
            await client.async_ensure_fresh_token()
            data = await client.async_get_coordinator_payload()
        except HelloFreshAuthenticationError as err:
            data = await self._async_retry_after_refresh(err)
        except HelloFreshError as err:
            LOGGER.exception("Error communicating with HelloFresh API")
            raise UpdateFailed(
                translation_domain="hellofresh",
                translation_key="update_failed",
            ) from err
        finally:
            persist_client_tokens(self.hass, self.config_entry, client)
        return data

    async def _async_retry_after_refresh(self, err: HelloFreshAuthenticationError) -> dict[str, Any]:
        """Retry the payload fetch after an explicit token refresh."""
        client = self.config_entry.runtime_data.client
        if not client.refresh_token:
            LOGGER.warning("Authentication error - %s", err)
            raise ConfigEntryAuthFailed(
                translation_domain="hellofresh",
                translation_key="authentication_failed",
            ) from err
        try:
            await client.async_refresh_access_token()
            return await client.async_get_coordinator_payload()
        except HelloFreshAuthenticationError as retry_err:
            LOGGER.warning("Authentication error - %s", retry_err)
            raise ConfigEntryAuthFailed(
                translation_domain="hellofresh",
                translation_key="authentication_failed",
            ) from retry_err
