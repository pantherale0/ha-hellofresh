"""Device info utilities for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.hellofresh.const import CONF_BASE_URL, CONF_CUSTOMER_ID, DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


def create_device_info(config_entry: ConfigEntry) -> DeviceInfo:
    """Create a DeviceInfo object for a HelloFresh account."""
    customer_id = config_entry.data.get(CONF_CUSTOMER_ID) or config_entry.entry_id
    return DeviceInfo(
        identifiers={(DOMAIN, str(customer_id))},
        name=config_entry.title or "HelloFresh Account",
        manufacturer="HelloFresh",
        model="Account",
        configuration_url=config_entry.data.get(CONF_BASE_URL),
    )


def get_device_identifiers(config_entry: ConfigEntry) -> set[tuple[str, str]]:
    """Get device identifiers for a config entry."""
    customer_id = config_entry.data.get(CONF_CUSTOMER_ID) or config_entry.entry_id
    return {(DOMAIN, str(customer_id))}
