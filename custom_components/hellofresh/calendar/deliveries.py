"""Delivery schedule calendar for hellofresh."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from custom_components.hellofresh.entity import HelloFreshEntity
from custom_components.hellofresh.utils.weeks import parse_iso_week
from homeassistant.components.calendar import CalendarEntity, CalendarEntityDescription, CalendarEvent

if TYPE_CHECKING:
    from custom_components.hellofresh.coordinator import HelloFreshDataUpdateCoordinator

ENTITY_DESCRIPTION = CalendarEntityDescription(
    key="deliveries",
    translation_key="deliveries",
)


def _meal_names_from_raw(meals: list[Any]) -> list[str]:
    """Extract meal names from raw delivery meal dicts."""
    names: list[str] = []
    for meal in meals:
        if not isinstance(meal, dict):
            continue
        recipe = meal.get("recipe") if isinstance(meal.get("recipe"), dict) else meal
        if isinstance(recipe, dict) and recipe.get("name"):
            names.append(str(recipe["name"]))
    return names


class HelloFreshDeliveryCalendar(CalendarEntity, HelloFreshEntity):
    """Calendar of HelloFresh delivery weeks."""

    def __init__(self, coordinator: HelloFreshDataUpdateCoordinator) -> None:
        """Initialize the calendar."""
        super().__init__(coordinator, ENTITY_DESCRIPTION)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        now = datetime.now(UTC)
        events = self._build_events(now - timedelta(days=1), now + timedelta(days=90))
        upcoming = [event for event in events if _event_end(event) >= now.date()]
        return upcoming[0] if upcoming else None

    async def async_get_events(
        self,
        hass: Any,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a time range."""
        return self._build_events(start_date, end_date)

    def _build_events(self, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        """Build calendar events from coordinator delivery data."""
        data = self.coordinator.data or {}
        past = data.get("past_deliveries")
        weeks: list[Any] = list(getattr(past, "weeks", []) or [])
        next_week = data.get("next_week")
        if next_week and not any(getattr(week, "week", None) == next_week for week in weeks):
            weeks.append(
                type(
                    "WeekStub",
                    (),
                    {"week": next_week, "meals": data.get("selected_meals") or []},
                )()
            )

        events: list[CalendarEvent] = []
        range_start = start_date.date() if hasattr(start_date, "date") else start_date
        range_end = end_date.date() if hasattr(end_date, "date") else end_date

        for week_item in weeks:
            week = getattr(week_item, "week", None)
            if not week:
                continue
            parsed = parse_iso_week(str(week))
            if not parsed:
                continue
            week_start, week_end = parsed
            if week_end < range_start or week_start > range_end:
                continue

            meals = getattr(week_item, "meals", []) or []
            names = _meal_names_from_raw(meals)
            description = ", ".join(names) if names else "HelloFresh delivery week"
            events.append(
                CalendarEvent(
                    start=week_start,
                    end=week_end + timedelta(days=1),  # exclusive end for all-day events
                    summary=f"HelloFresh {week}",
                    description=description,
                )
            )

        events.sort(key=lambda event: event.start)
        return events


def _event_end(event: CalendarEvent) -> date:
    """Return the inclusive end date for sorting/filtering."""
    end = event.end
    if isinstance(end, datetime):
        end_date = end.date()
    else:
        end_date = end
    # All-day events use an exclusive end date.
    return end_date - timedelta(days=1)
