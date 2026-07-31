"""Account and menu sensors for hellofresh."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_components.hellofresh.entity import HelloFreshEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.helpers.typing import StateType

if TYPE_CHECKING:
    from custom_components.hellofresh.coordinator import HelloFreshDataUpdateCoordinator


def _minor_to_major(amount: float | None) -> float | None:
    """Convert HelloFresh minor currency units to major units."""
    if amount is None:
        return None
    return round(float(amount) / 100.0, 2)


def _menu_meals(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a compact summary of menu meals (kept small for recorder limits)."""
    menu = data.get("menu")
    if menu is None:
        return []
    meals: list[dict[str, Any]] = []
    for meal in menu.meals:
        recipe = meal.recipe
        if recipe is None:
            continue
        meals.append(
            {
                "recipe_id": recipe.id,
                "name": recipe.name,
            }
        )
    return meals


def _selected_meals_summary(data: dict[str, Any]) -> list[dict[str, str]]:
    """Return compact selected-meal summaries (id + name only)."""
    meals: list[dict[str, str]] = []
    for meal in data.get("selected_meals") or []:
        if not isinstance(meal, dict):
            continue
        recipe = meal.get("recipe") if isinstance(meal.get("recipe"), dict) else meal
        if not isinstance(recipe, dict):
            continue
        name = recipe.get("name")
        recipe_id = recipe.get("id") or meal.get("id")
        if not name and not recipe_id:
            continue
        entry: dict[str, str] = {}
        if recipe_id:
            entry["recipe_id"] = str(recipe_id)
        if name:
            entry["name"] = str(name)
        meals.append(entry)
    return meals


def _selected_meal_names(data: dict[str, Any]) -> list[str]:
    """Extract names from selected meal payloads."""
    return [meal["name"] for meal in _selected_meals_summary(data) if "name" in meal]


def _subscription_status(data: dict[str, Any]) -> str | None:
    """Return a human-readable subscription status."""
    sub = data.get("active_subscription")
    if not isinstance(sub, dict):
        return None
    for key in ("status", "subscriptionStatus", "state"):
        if sub.get(key):
            return str(sub[key])
    return "active" if sub else None


def _nested_get(data: dict[str, Any], *path: str) -> Any:
    """Walk nested dict keys; return None if any step is missing."""
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _subscription_plan(data: dict[str, Any]) -> str | None:
    """Return subscription plan / product sku if present."""
    sub = data.get("active_subscription")
    candidates: list[Any] = []
    if isinstance(sub, dict):
        candidates.extend(
            [
                sub.get("productSku"),
                sub.get("product_sku"),
                sub.get("planName"),
                sub.get("sku"),
                sub.get("name"),
                sub.get("handle"),
                _nested_get(sub, "product", "sku"),
                _nested_get(sub, "product", "name"),
                _nested_get(sub, "product", "handle"),
                _nested_get(sub, "product", "family"),
                _nested_get(sub, "box", "sku"),
                _nested_get(sub, "box", "name"),
            ]
        )
    info = data.get("customer_info") or {}
    if isinstance(info, dict):
        skus = info.get("activeSubscriptionSkus")
        if isinstance(skus, list):
            candidates.extend(skus)
        plan_ids = info.get("customerPlanIds")
        if isinstance(plan_ids, list) and not any(candidates):
            # UUIDs are a last resort when no human-readable plan is available.
            candidates.extend(plan_ids)

    for value in candidates:
        if value is not None and str(value).strip():
            return str(value)
    return None


@dataclass(frozen=True, kw_only=True)
class HelloFreshSensorEntityDescription(SensorEntityDescription):
    """Describe a HelloFresh sensor with a value extractor."""

    value_fn: Callable[[dict[str, Any]], StateType]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    currency_fn: Callable[[dict[str, Any]], str | None] | None = None


ENTITY_DESCRIPTIONS: tuple[HelloFreshSensorEntityDescription, ...] = (
    HelloFreshSensorEntityDescription(
        key="account_credit",
        translation_key="account_credit",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:cash",
        value_fn=lambda d: _minor_to_major(getattr(d.get("balance"), "amount", None)),
        currency_fn=lambda d: getattr(d.get("balance"), "currency_code", None),
        attrs_fn=lambda d: {
            "cash": _minor_to_major(getattr(d.get("balance"), "cash", None)),
            "bonus": _minor_to_major(getattr(d.get("balance"), "bonus", None)),
        },
    ),
    HelloFreshSensorEntityDescription(
        key="adults",
        translation_key="adults",
        icon="mdi:account",
        value_fn=lambda d: getattr(d.get("profile"), "adults", None),
    ),
    HelloFreshSensorEntityDescription(
        key="children",
        translation_key="children",
        icon="mdi:account-child",
        value_fn=lambda d: getattr(d.get("profile"), "children", None),
    ),
    HelloFreshSensorEntityDescription(
        key="total_people",
        translation_key="total_people",
        icon="mdi:account-group",
        value_fn=lambda d: getattr(d.get("profile"), "total_people", None),
    ),
    HelloFreshSensorEntityDescription(
        key="dietary_exclusions",
        translation_key="dietary_exclusions",
        icon="mdi:food-off",
        value_fn=lambda d: len(getattr(d.get("profile"), "exclusions", []) or []),
        attrs_fn=lambda d: {
            "exclusions": list(getattr(d.get("profile"), "exclusions", []) or []),
            "dietary_preferences": list(getattr(d.get("profile"), "dietary_preferences", []) or []),
        },
    ),
    HelloFreshSensorEntityDescription(
        key="next_delivery_week",
        translation_key="next_delivery_week",
        icon="mdi:calendar-week",
        value_fn=lambda d: d.get("next_week"),
    ),
    HelloFreshSensorEntityDescription(
        key="selected_meals",
        translation_key="selected_meals",
        icon="mdi:food",
        value_fn=lambda d: len(d.get("selected_meals") or []),
        attrs_fn=lambda d: {
            "meals": _selected_meals_summary(d),
            "meal_names": _selected_meal_names(d),
        },
    ),
    HelloFreshSensorEntityDescription(
        key="available_meals",
        translation_key="available_meals",
        icon="mdi:food-variant",
        value_fn=lambda d: len(getattr(d.get("menu"), "meals", []) or []),
        attrs_fn=lambda d: {
            "meal_names": [meal["name"] for meal in _menu_meals(d)],
            "recipe_ids": [meal["recipe_id"] for meal in _menu_meals(d)],
        },
    ),
    HelloFreshSensorEntityDescription(
        key="cart_grand_total",
        translation_key="cart_grand_total",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:cart",
        value_fn=lambda d: getattr(d.get("cart"), "grand_total", None),
        currency_fn=lambda d: getattr(d.get("balance"), "currency_code", None),
        attrs_fn=lambda d: {
            "sub_total": getattr(d.get("cart"), "sub_total", None),
            "shipping_amount": getattr(d.get("cart"), "shipping_amount", None),
            "discount_amount": getattr(d.get("cart"), "discount_amount", None),
            "coupon_code": getattr(d.get("cart"), "coupon_code", None),
        },
    ),
    HelloFreshSensorEntityDescription(
        key="subscription_status",
        translation_key="subscription_status",
        icon="mdi:clipboard-check",
        value_fn=_subscription_status,
    ),
    HelloFreshSensorEntityDescription(
        key="subscription_plan",
        translation_key="subscription_plan",
        icon="mdi:package-variant",
        value_fn=_subscription_plan,
    ),
    HelloFreshSensorEntityDescription(
        key="active_subscription_id",
        translation_key="active_subscription_id",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:identifier",
        value_fn=lambda d: (
            str(
                (d.get("customer_info") or {}).get("activeSubscriptionId")
                or (d.get("active_subscription") or {}).get("id")
                or ""
            )
            or None
        ),
    ),
)


class HelloFreshSensor(SensorEntity, HelloFreshEntity):
    """HelloFresh sensor entity."""

    entity_description: HelloFreshSensorEntityDescription
    # Meal lists can still get large; never persist them to the recorder DB.
    _unrecorded_attributes = frozenset({"meals", "meal_names", "recipe_ids"})

    def __init__(
        self,
        coordinator: HelloFreshDataUpdateCoordinator,
        entity_description: HelloFreshSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return currency for monetary sensors when available."""
        if self.entity_description.currency_fn and self.coordinator.data:
            currency = self.entity_description.currency_fn(self.coordinator.data)
            if currency:
                return currency
        return self.entity_description.native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return optional attributes."""
        if not self.coordinator.data or not self.entity_description.attrs_fn:
            return None
        return self.entity_description.attrs_fn(self.coordinator.data)
