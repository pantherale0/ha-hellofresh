"""Service action: get_recipe."""

from __future__ import annotations

from typing import Any

from pyhellofresh import HelloFreshAuthenticationError, HelloFreshError

from custom_components.hellofresh.api import recipe_to_dict
from custom_components.hellofresh.const import CONF_RECIPE_ID, LOGGER
from custom_components.hellofresh.service_actions.helpers import resolve_client
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from homeassistant.exceptions import HomeAssistantError


async def async_handle_get_recipe(
    hass: HomeAssistant,
    call: ServiceCall,
) -> ServiceResponse:
    """Fetch a recipe and return it as a service response."""
    recipe_id = call.data[CONF_RECIPE_ID]
    client = resolve_client(hass, call)
    try:
        recipe = await client.async_get_recipe(recipe_id)
    except HelloFreshAuthenticationError as err:
        raise HomeAssistantError(
            translation_domain="hellofresh",
            translation_key="service_auth_failed",
        ) from err
    except HelloFreshError as err:
        LOGGER.exception("get_recipe failed for %s", recipe_id)
        raise HomeAssistantError(
            translation_domain="hellofresh",
            translation_key="service_recipe_failed",
        ) from err

    payload: dict[str, Any] = {"recipe": recipe_to_dict(recipe)}
    return payload
