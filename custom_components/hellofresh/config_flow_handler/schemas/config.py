"""Config flow schemas for hellofresh."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.hellofresh.const import (
    CONF_ACCESS_TOKEN,
    CONF_CODE,
    CONF_COUNTRY,
    CONF_MAGIC_LINK,
    CONF_REFRESH_TOKEN,
    COUNTRY_OPTIONS,
    DEFAULT_COUNTRY,
)
from homeassistant.const import CONF_EMAIL
from homeassistant.helpers import selector


def get_email_country_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """Schema for email + country collection."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_EMAIL,
                default=defaults.get(CONF_EMAIL, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL),
            ),
            vol.Required(
                CONF_COUNTRY,
                default=defaults.get(CONF_COUNTRY, DEFAULT_COUNTRY),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=COUNTRY_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
        },
    )


def get_magic_link_confirm_schema() -> vol.Schema:
    """Schema for magic-link / code confirmation."""
    return vol.Schema(
        {
            vol.Optional(CONF_MAGIC_LINK): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.URL),
            ),
            vol.Optional(CONF_CODE): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
            ),
        },
    )


def get_token_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """Schema for advanced token paste setup."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_EMAIL,
                default=defaults.get(CONF_EMAIL, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL),
            ),
            vol.Required(
                CONF_COUNTRY,
                default=defaults.get(CONF_COUNTRY, DEFAULT_COUNTRY),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=COUNTRY_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
            vol.Required(CONF_ACCESS_TOKEN): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
            vol.Optional(CONF_REFRESH_TOKEN): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
        },
    )


def get_reconfigure_schema(defaults: Mapping[str, Any]) -> vol.Schema:
    """Schema for reconfigure (region + email display)."""
    return get_email_country_schema(defaults)


def get_reauth_schema(email: str, country: str) -> vol.Schema:
    """Schema for reauth email confirmation before sending a new magic link."""
    return get_email_country_schema({CONF_EMAIL: email, CONF_COUNTRY: country})


# Backwards-compatible aliases expected by package exports.
def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """Alias used by package exports; user flow starts with a menu."""
    return get_email_country_schema(defaults)


__all__ = [
    "get_email_country_schema",
    "get_magic_link_confirm_schema",
    "get_reauth_schema",
    "get_reconfigure_schema",
    "get_token_schema",
    "get_user_schema",
]
