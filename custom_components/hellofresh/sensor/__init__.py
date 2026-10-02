"""Sensor platform for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.hellofresh.const import PARALLEL_UPDATES
from custom_components.hellofresh.sensor.account import (
    ENTITY_DESCRIPTIONS,
    SUBSCRIPTION_ENTITY_KEYS,
    HelloFreshSensor,
)

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
    """Set up HelloFresh sensors."""
    coordinator = entry.runtime_data.coordinator
    has_subscription = coordinator.data.get("active_subscription") is not None
    async_add_entities(
        HelloFreshSensor(coordinator, description)
        for description in ENTITY_DESCRIPTIONS
        if has_subscription or description.key not in SUBSCRIPTION_ENTITY_KEYS
    )
