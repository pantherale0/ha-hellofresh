"""Contribute HelloFresh tools to Home Assistant LLM APIs when supported.

Home Assistant discovers this platform from the ``llm`` integration and calls
``async_get_tools`` per request. On older cores without the contributor API,
this module is unused; the dedicated HelloFresh LLM API is still registered via
``llm.async_register_api`` in ``llm_api/``.

See: https://developers.home-assistant.io/docs/core/llm/
"""

from __future__ import annotations

from typing import Any

from custom_components.hellofresh.const import DOMAIN
from custom_components.hellofresh.llm_api.tools import API_PROMPT, build_hellofresh_tools
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.llm import LLMContext


@callback
def async_get_tools(
    hass: HomeAssistant,
    llm_context: LLMContext,
    api_id: str,
) -> Any | None:
    """Return HelloFresh tools for Assist (or compatible) LLM APIs."""
    # Prefer contributing into Assist; dedicated HelloFresh API already has its tools.
    if api_id.startswith(f"{DOMAIN}-"):
        return None

    try:
        llm_component = __import__("homeassistant.components.llm", fromlist=["*"])
    except ImportError:
        return None

    llm_tools_cls = getattr(llm_component, "LLMTools", None)
    if llm_tools_cls is None:
        return None

    entries = [entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.runtime_data is not None]
    if not entries:
        return None

    tools = []
    for entry in entries:
        tools.extend(build_hellofresh_tools(entry.entry_id))

    return llm_tools_cls(tools=tools, prompt=API_PROMPT)
