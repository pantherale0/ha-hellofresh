"""Service action: search_recipes."""

from __future__ import annotations

from typing import Any

from pyhellofresh import HelloFreshError

from custom_components.hellofresh.api import recipe_to_dict
from custom_components.hellofresh.const import CONF_QUERY, CONF_SKIP, CONF_TAKE, LOGGER
from custom_components.hellofresh.service_actions.helpers import resolve_client
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from homeassistant.exceptions import HomeAssistantError


async def async_handle_search_recipes(
    hass: HomeAssistant,
    call: ServiceCall,
) -> ServiceResponse:
    """Search recipes and return them as a service response."""
    query = call.data[CONF_QUERY]
    take = int(call.data.get(CONF_TAKE, 20))
    skip = int(call.data.get(CONF_SKIP, 0))
    client = resolve_client(hass, call)
    try:
        recipes = await client.async_search_recipes(query, take=take, skip=skip)
    except HelloFreshError as err:
        LOGGER.exception("search_recipes failed for %s", query)
        raise HomeAssistantError(
            translation_domain="hellofresh",
            translation_key="service_search_failed",
        ) from err

    payload: dict[str, Any] = {
        "query": query,
        "take": take,
        "skip": skip,
        "count": len(recipes),
        "recipes": [recipe_to_dict(recipe) for recipe in recipes],
    }
    return payload
