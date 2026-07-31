"""Service actions package for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol

from custom_components.hellofresh.const import (
    CONF_CONFIG_ENTRY_ID,
    CONF_QUERY,
    CONF_RECIPE_ID,
    CONF_SKIP,
    CONF_TAKE,
    DOMAIN,
    LOGGER,
)
from custom_components.hellofresh.service_actions.get_recipe import async_handle_get_recipe
from custom_components.hellofresh.service_actions.search_recipes import async_handle_search_recipes
from homeassistant.core import ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import config_validation as cv

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

SERVICE_GET_RECIPE = "get_recipe"
SERVICE_SEARCH_RECIPES = "search_recipes"

GET_RECIPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_RECIPE_ID): cv.string,
        vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
    }
)

SEARCH_RECIPES_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_QUERY): cv.string,
        vol.Optional(CONF_TAKE, default=20): vol.All(vol.Coerce(int), vol.Range(min=1, max=50)),
        vol.Optional(CONF_SKIP, default=0): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register HelloFresh service actions."""

    async def handle_get_recipe(call: ServiceCall) -> ServiceResponse:
        return await async_handle_get_recipe(hass, call)

    async def handle_search_recipes(call: ServiceCall) -> ServiceResponse:
        return await async_handle_search_recipes(hass, call)

    if not hass.services.has_service(DOMAIN, SERVICE_GET_RECIPE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_RECIPE,
            handle_get_recipe,
            schema=GET_RECIPE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SEARCH_RECIPES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEARCH_RECIPES,
            handle_search_recipes,
            schema=SEARCH_RECIPES_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    LOGGER.debug("Services registered for %s", DOMAIN)
