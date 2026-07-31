"""Diagnostics support for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.hellofresh.const import CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN
from homeassistant.const import CONF_EMAIL
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import HelloFreshConfigEntry

TO_REDACT = {
    CONF_EMAIL,
    CONF_ACCESS_TOKEN,
    CONF_REFRESH_TOKEN,
    "access_token",
    "refresh_token",
    "token",
    "email",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: HelloFreshConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    client = entry.runtime_data.client
    integration = entry.runtime_data.integration

    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)
    devices = dr.async_entries_for_config_entry(device_reg, entry.entry_id)
    device_info = []
    for device in devices:
        entities = er.async_entries_for_device(entity_reg, device.id)
        device_info.append(
            {
                "id": device.id,
                "name": device.name,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "entity_count": len(entities),
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "platform": entity.platform,
                        "original_name": entity.original_name,
                        "disabled": entity.disabled,
                    }
                    for entity in entities
                ],
            }
        )

    data = coordinator.data or {}
    data_sample = {
        "next_week": data.get("next_week"),
        "api_next_week": getattr(data.get("past_deliveries"), "next_week", None),
        "delivery_weeks": [week.week for week in getattr(data.get("past_deliveries"), "weeks", []) or []],
        "customer_id": data.get("customer_id"),
        "has_profile": data.get("profile") is not None,
        "has_balance": data.get("balance") is not None,
        "has_menu": data.get("menu") is not None,
        "menu_meal_count": len(getattr(data.get("menu"), "meals", []) or []),
        "has_cart": data.get("cart") is not None,
        "cart_grand_total": getattr(data.get("cart"), "grand_total", None),
        "selected_meals_count": len(data.get("selected_meals") or []),
        "subscription_keys": list((data.get("active_subscription") or {}).keys())
        if isinstance(data.get("active_subscription"), dict)
        else None,
        "active_subscription_skus": (data.get("customer_info") or {}).get("activeSubscriptionSkus"),
    }

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "unique_id": entry.unique_id,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "integration": {
            "name": integration.name,
            "version": integration.version,
            "domain": integration.domain,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
        },
        "api": {
            "base_url": client.base_url,
            "country": client.country,
            "locale": client.locale,
            "has_access_token": bool(client.access_token),
            "has_refresh_token": bool(client.refresh_token),
        },
        "devices": device_info,
        "data_sample": data_sample,
    }
