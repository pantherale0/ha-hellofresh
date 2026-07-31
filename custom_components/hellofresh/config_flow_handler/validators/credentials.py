"""Credential validation helpers for hellofresh config flow."""

from __future__ import annotations

from typing import Any

from custom_components.hellofresh.api import HelloFreshApiClient
from custom_components.hellofresh.const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_COUNTRY,
    CONF_CUSTOMER_ID,
    CONF_LOCALE,
    CONF_REFRESH_TOKEN,
    get_region,
)
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


async def async_validate_tokens(
    hass: HomeAssistant,
    *,
    access_token: str,
    refresh_token: str | None,
    country: str,
    email: str | None = None,
) -> dict[str, Any]:
    """
    Validate tokens by fetching customer info.

    Returns config entry data ready to store.
    """
    region = get_region(country)
    client = HelloFreshApiClient(
        session=async_get_clientsession(hass),
        access_token=access_token,
        refresh_token=refresh_token,
        country=region.country,
        locale=region.locale,
        base_url=region.base_url,
    )
    info = await client.async_get_customer_info()
    customer_id = str(info.get("uuid") or info.get("id") or "")
    if not customer_id:
        msg = "Customer id missing from HelloFresh response"
        raise ValueError(msg)

    return {
        CONF_EMAIL: email or info.get("email") or "",
        CONF_ACCESS_TOKEN: client.access_token or access_token,
        CONF_REFRESH_TOKEN: client.refresh_token or refresh_token,
        CONF_COUNTRY: region.country,
        CONF_LOCALE: region.locale,
        CONF_BASE_URL: region.base_url,
        CONF_CUSTOMER_ID: customer_id,
    }


async def async_start_magic_link(
    hass: HomeAssistant,
    *,
    email: str,
    country: str,
) -> tuple[str, HelloFreshApiClient]:
    """Start passwordless login and return (public_id, client)."""
    region = get_region(country)
    client = HelloFreshApiClient(
        session=async_get_clientsession(hass),
        country=region.country,
        locale=region.locale,
        base_url=region.base_url,
    )
    public_id = await client.async_start_passwordless_login(email)
    return public_id, client


async def async_finish_magic_link(
    hass: HomeAssistant,
    *,
    email: str,
    country: str,
    public_id: str,
    magic_link: str | None = None,
    code: str | None = None,
) -> dict[str, Any]:
    """Finish passwordless login and return config entry data."""
    region = get_region(country)
    client = HelloFreshApiClient(
        session=async_get_clientsession(hass),
        country=region.country,
        locale=region.locale,
        base_url=region.base_url,
    )

    if magic_link:
        tokens = await client.async_finish_passwordless_login_from_url(
            magic_link,
            public_id=public_id,
        )
    elif code:
        tokens = await client.async_finish_passwordless_login(
            code=code,
            email=email,
            public_id=public_id,
        )
    else:
        msg = "Magic link URL or code is required"
        raise ValueError(msg)

    return await async_validate_tokens(
        hass,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        country=country,
        email=email,
    )
