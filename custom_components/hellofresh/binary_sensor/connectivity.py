"""Binary sensors for hellofresh."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_components.hellofresh.entity import HelloFreshEntity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.hellofresh.coordinator import HelloFreshDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class HelloFreshBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a HelloFresh binary sensor."""

    is_on_fn: Callable[[Any, bool], bool]


ENTITY_DESCRIPTIONS: tuple[HelloFreshBinarySensorEntityDescription, ...] = (
    HelloFreshBinarySensorEntityDescription(
        key="api_connectivity",
        translation_key="api_connectivity",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:cloud-check",
        is_on_fn=lambda _data, last_success: last_success,
    ),
    HelloFreshBinarySensorEntityDescription(
        key="meals_ready",
        translation_key="meals_ready",
        icon="mdi:food-turkey",
        is_on_fn=lambda data, _last_success: bool(getattr(data.get("menu"), "meals_ready", False) if data else False),
    ),
)


class HelloFreshBinarySensor(BinarySensorEntity, HelloFreshEntity):
    """HelloFresh binary sensor."""

    entity_description: HelloFreshBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: HelloFreshDataUpdateCoordinator,
        entity_description: HelloFreshBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(
            self.coordinator.data,
            self.coordinator.last_update_success,
        )
