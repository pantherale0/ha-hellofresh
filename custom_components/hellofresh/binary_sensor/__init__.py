"""Binary sensor platform for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.hellofresh.binary_sensor.connectivity import ENTITY_DESCRIPTIONS, HelloFreshBinarySensor
from custom_components.hellofresh.const import PARALLEL_UPDATES

if TYPE_CHECKING:
    from custom_components.hellofresh.data import HelloFreshConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

__all__ = ["PARALLEL_UPDATES", "async_setup_entry"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HelloFresh binary sensors."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(HelloFreshBinarySensor(coordinator, description) for description in ENTITY_DESCRIPTIONS)
