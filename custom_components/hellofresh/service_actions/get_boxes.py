"""Service actions to get the latest meal boxes from HelloFresh."""

from __future__ import annotations

from typing import Any

from pyhellofresh import HelloFreshError

from custom_components.hellofresh.api import recipe_to_dict
from custom_components.hellofresh.const import LOGGER
from custom_components.hellofresh.service_actions.helpers import async_call_authenticated_from_service
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from homeassistant.exceptions import HomeAssistantError


async def async_handle_get_meals_for_week_offset(
    hass: HomeAssistant,
    call: ServiceCall,
) -> ServiceResponse:
    """Fetch the latest meal boxes and return them as a service response."""
    offset = call.data.get("offset", 0)
    try:
        boxes = await async_call_authenticated_from_service(
            hass,
            call,
            lambda client: client.get_meals_for_week_offset(offset),
        )
    except HelloFreshError as err:
        LOGGER.exception("get_meals_for_week_offset failed")
        raise HomeAssistantError(
            translation_domain="hellofresh",
            translation_key="service_boxes_failed",
        ) from err

    payload: dict[str, Any] = {"boxes": [recipe_to_dict(box) for box in boxes]}
    return payload
