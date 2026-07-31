"""Base entity class for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.hellofresh.const import ATTRIBUTION, CONF_BASE_URL, CONF_CUSTOMER_ID, DOMAIN
from custom_components.hellofresh.coordinator import HelloFreshDataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class HelloFreshEntity(CoordinatorEntity[HelloFreshDataUpdateCoordinator]):
    """Base entity for HelloFresh."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HelloFreshDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        customer_id = coordinator.config_entry.data.get(CONF_CUSTOMER_ID) or coordinator.config_entry.entry_id
        self._attr_unique_id = f"{customer_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(customer_id))},
            name=coordinator.config_entry.title,
            manufacturer="HelloFresh",
            model="Account",
            configuration_url=coordinator.config_entry.data.get(CONF_BASE_URL),
        )
