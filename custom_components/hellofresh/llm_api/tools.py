"""LLM tools for HelloFresh recipe and account queries."""

from __future__ import annotations

from typing import Any

from pyhellofresh import HelloFreshAuthenticationError, HelloFreshError
import voluptuous as vol

from custom_components.hellofresh.api import recipe_to_dict
from custom_components.hellofresh.const import CONF_QUERY, CONF_RECIPE_ID, CONF_SKIP, CONF_TAKE, LOGGER
from custom_components.hellofresh.service_actions.helpers import resolve_client_for_entry, resolve_entry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm
from homeassistant.helpers.llm import LLMContext, ToolInput
from homeassistant.util.json import JsonObjectType


class SearchHelloFreshRecipesTool(llm.Tool):
    """Search the HelloFresh recipe catalog."""

    name = "SearchHelloFreshRecipes"
    description = (
        "Search HelloFresh recipes by keyword (for example pasta, chicken, tacos). "
        "Returns compact results with recipe_id and name. "
        "Use GetHelloFreshRecipe with a recipe_id for full details."
    )
    parameters = vol.Schema(
        {
            vol.Required(CONF_QUERY): str,
            vol.Optional(CONF_TAKE, default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=25)),
            vol.Optional(CONF_SKIP, default=0): vol.All(vol.Coerce(int), vol.Range(min=0)),
        }
    )

    def __init__(self, entry_id: str) -> None:
        """Store the config entry this tool is bound to."""
        self._entry_id = entry_id

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: ToolInput,
        llm_context: LLMContext,
    ) -> JsonObjectType:
        """Search recipes and return a compact JSON payload."""
        query = str(tool_input.tool_args[CONF_QUERY])
        take = int(tool_input.tool_args.get(CONF_TAKE, 10))
        skip = int(tool_input.tool_args.get(CONF_SKIP, 0))
        client = resolve_client_for_entry(hass, entry_id=self._entry_id)
        try:
            recipes = await client.async_search_recipes(query, take=take, skip=skip)
        except HelloFreshAuthenticationError as err:
            raise HomeAssistantError(
                translation_domain="hellofresh",
                translation_key="service_auth_failed",
            ) from err
        except HelloFreshError as err:
            LOGGER.exception("LLM search_recipes failed for %s", query)
            raise HomeAssistantError(
                translation_domain="hellofresh",
                translation_key="service_search_failed",
            ) from err

        return {
            "query": query,
            "count": len(recipes),
            "recipes": [
                {
                    "recipe_id": recipe.id,
                    "name": recipe.name,
                    "headline": recipe.headline,
                    "prep_time": recipe.prep_time,
                    "difficulty": recipe.difficulty,
                    "website_url": recipe.website_url,
                }
                for recipe in recipes
            ],
        }


class GetHelloFreshRecipeTool(llm.Tool):
    """Fetch full details for one HelloFresh recipe."""

    name = "GetHelloFreshRecipe"
    description = (
        "Fetch full HelloFresh recipe details by recipe_id, including ingredients, "
        "steps, nutrition, allergens, and timings."
    )
    parameters = vol.Schema({vol.Required(CONF_RECIPE_ID): str})

    def __init__(self, entry_id: str) -> None:
        """Store the config entry this tool is bound to."""
        self._entry_id = entry_id

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: ToolInput,
        llm_context: LLMContext,
    ) -> JsonObjectType:
        """Fetch a recipe and return it as JSON."""
        recipe_id = str(tool_input.tool_args[CONF_RECIPE_ID])
        client = resolve_client_for_entry(hass, entry_id=self._entry_id)
        try:
            recipe = await client.async_get_recipe(recipe_id)
        except HelloFreshAuthenticationError as err:
            raise HomeAssistantError(
                translation_domain="hellofresh",
                translation_key="service_auth_failed",
            ) from err
        except HelloFreshError as err:
            LOGGER.exception("LLM get_recipe failed for %s", recipe_id)
            raise HomeAssistantError(
                translation_domain="hellofresh",
                translation_key="service_recipe_failed",
            ) from err

        return {"recipe": recipe_to_dict(recipe)}


class GetHelloFreshDeliverySummaryTool(llm.Tool):
    """Summarize the linked HelloFresh account delivery status."""

    name = "GetHelloFreshDeliverySummary"
    description = (
        "Get a summary of the configured HelloFresh account: next delivery week, "
        "selected meal names, available meal count, account credit, and subscription status."
    )
    parameters = vol.Schema({})

    def __init__(self, entry_id: str) -> None:
        """Store the config entry this tool is bound to."""
        self._entry_id = entry_id

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: ToolInput,
        llm_context: LLMContext,
    ) -> JsonObjectType:
        """Return a compact account/delivery summary from coordinator data."""
        entry = resolve_entry(hass, entry_id=self._entry_id)
        data: dict[str, Any] = entry.runtime_data.coordinator.data or {}
        balance = data.get("balance")
        menu = data.get("menu")
        selected = data.get("selected_meals") or []
        meal_names: list[str] = []
        for meal in selected:
            if not isinstance(meal, dict):
                continue
            recipe = meal.get("recipe") if isinstance(meal.get("recipe"), dict) else meal
            if isinstance(recipe, dict) and recipe.get("name"):
                meal_names.append(str(recipe["name"]))

        credit = None
        currency = None
        if balance is not None:
            credit = round(float(balance.amount) / 100.0, 2)
            currency = balance.currency_code

        sub = data.get("active_subscription")
        status = None
        if isinstance(sub, dict):
            status = sub.get("status") or sub.get("subscriptionStatus") or sub.get("state")

        result: dict[str, Any] = {
            "email": entry.title,
            "country": entry.data.get("country"),
            "next_delivery_week": data.get("next_week"),
            "selected_meal_count": len(selected),
            "selected_meal_names": meal_names,
            "available_meal_count": len(getattr(menu, "meals", []) or []),
            "meals_ready": getattr(menu, "meals_ready", None),
            "account_credit": credit,
            "currency": currency,
            "subscription_status": status,
            "cart_grand_total": getattr(data.get("cart"), "grand_total", None),
        }
        return result  # type: ignore[return-value]


def build_hellofresh_tools(entry_id: str) -> list[llm.Tool]:
    """Build the LLM tool list for a config entry."""
    return [
        GetHelloFreshDeliverySummaryTool(entry_id),
        SearchHelloFreshRecipesTool(entry_id),
        GetHelloFreshRecipeTool(entry_id),
    ]


API_PROMPT = (
    "You can use HelloFresh tools to help with meal planning. "
    "Call GetHelloFreshDeliverySummary for the user's upcoming box and account status. "
    "Call SearchHelloFreshRecipes to find recipes by keyword, then GetHelloFreshRecipe "
    "with a recipe_id for ingredients and cooking steps. "
    "Do not invent recipe ids; only use ids returned by search or delivery summary tools."
)
