"""Refresh button for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.hellofresh.entity import HelloFreshEntity
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.hellofresh.coordinator import HelloFreshDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key="refresh",
        translation_key="refresh",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:refresh",
    ),
)


class HelloFreshRefreshButton(ButtonEntity, HelloFreshEntity):
    """Button that forces a coordinator refresh."""

    def __init__(
        self,
        coordinator: HelloFreshDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description)

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
