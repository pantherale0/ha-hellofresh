"""Custom integration to integrate HelloFresh with Home Assistant."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_EMAIL, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .api import HelloFreshApiClient
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_COUNTRY,
    CONF_LOCALE,
    CONF_REFRESH_TOKEN,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    LOGGER,
)
from .coordinator import HelloFreshDataUpdateCoordinator
from .data import HelloFreshData
from .llm_api import async_register_llm_api
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import HelloFreshConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CALENDAR,
    Platform.SENSOR,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration and register service actions."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
) -> bool:
    """Set up HelloFresh from a config entry."""
    client = HelloFreshApiClient(
        session=async_get_clientsession(hass),
        access_token=entry.data.get(CONF_ACCESS_TOKEN),
        refresh_token=entry.data.get(CONF_REFRESH_TOKEN),
        country=entry.data[CONF_COUNTRY],
        locale=entry.data[CONF_LOCALE],
        base_url=entry.data[CONF_BASE_URL],
    )

    update_hours = float(entry.options.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS))
    coordinator = HelloFreshDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=timedelta(hours=update_hours),
        always_update=False,
    )

    entry.runtime_data = HelloFreshData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    async_register_llm_api(hass, entry)

    LOGGER.debug(
        "HelloFresh entry set up for %s (%s)",
        entry.data.get(CONF_EMAIL),
        entry.data.get(CONF_COUNTRY),
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
