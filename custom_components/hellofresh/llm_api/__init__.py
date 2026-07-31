"""HelloFresh LLM API registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.hellofresh.const import DOMAIN
from custom_components.hellofresh.llm_api.tools import API_PROMPT, build_hellofresh_tools
from homeassistant.helpers import llm
from homeassistant.helpers.llm import APIInstance, LLMContext

if TYPE_CHECKING:
    from custom_components.hellofresh.data import HelloFreshConfigEntry
    from homeassistant.core import HomeAssistant


class HelloFreshLLMAPI(llm.API):
    """LLM API exposing HelloFresh recipe and delivery tools."""

    def __init__(self, hass: HomeAssistant, entry: HelloFreshConfigEntry) -> None:
        """Initialize the API for a config entry."""
        super().__init__(
            hass=hass,
            id=f"{DOMAIN}-{entry.entry_id}",
            name=entry.title or "HelloFresh",
        )
        self._entry_id = entry.entry_id

    async def async_get_api_instance(self, llm_context: LLMContext) -> APIInstance:
        """Return tools for this HelloFresh account."""
        return APIInstance(
            api=self,
            api_prompt=API_PROMPT,
            llm_context=llm_context,
            tools=build_hellofresh_tools(self._entry_id),
        )


def async_register_llm_api(hass: HomeAssistant, entry: HelloFreshConfigEntry) -> None:
    """Register the HelloFresh LLM API and unload it with the config entry."""
    unregister = llm.async_register_api(hass, HelloFreshLLMAPI(hass=hass, entry=entry))
    entry.async_on_unload(unregister)
