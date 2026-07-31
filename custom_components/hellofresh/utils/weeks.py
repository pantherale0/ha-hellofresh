"""ISO week helpers for HelloFresh delivery weeks."""

from __future__ import annotations

from datetime import date, timedelta


def format_iso_week(value: date) -> str:
    """Format a date as HelloFresh ISO week string (YYYY-Www)."""
    iso = value.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def parse_iso_week(week: str) -> tuple[date, date] | None:
    """Parse HelloFresh week string into Monday–Sunday dates."""
    if not week or "-W" not in week:
        return None
    try:
        year_str, week_str = week.split("-W", maxsplit=1)
        year = int(year_str)
        week_num = int(week_str)
        start = date.fromisocalendar(year, week_num, 1)
        end = date.fromisocalendar(year, week_num, 7)
    except ValueError, TypeError:
        return None
    return start, end


def current_iso_week(today: date | None = None) -> str:
    """Return the current ISO week string."""
    return format_iso_week(today or date.today())


def delivery_range(
    today: date | None = None,
    *,
    past_weeks: int = 8,
    future_weeks: int = 8,
) -> tuple[str, str]:
    """Return (range_start, range_end) ISO weeks around today."""
    anchor = today or date.today()
    return (
        format_iso_week(anchor - timedelta(weeks=past_weeks)),
        format_iso_week(anchor + timedelta(weeks=future_weeks)),
    )


def resolve_next_week(
    *,
    api_next_week: str | None,
    week_ids: list[str],
    today: date | None = None,
) -> str:
    """
    Resolve the upcoming delivery week.

    Prefer the API's nextWeek when present; otherwise pick the earliest week
    at or after the current ISO week, falling back to the current week.
    """
    if api_next_week:
        return api_next_week

    anchor = today or date.today()
    current = current_iso_week(anchor)
    upcoming = sorted(week for week in week_ids if week and _week_sort_key(week) >= _week_sort_key(current))
    if upcoming:
        return upcoming[0]
    return current


def _week_sort_key(week: str) -> tuple[int, int]:
    """Sort key for ISO week strings."""
    parsed = parse_iso_week(week)
    if parsed is None:
        return (0, 0)
    start, _end = parsed
    iso = start.isocalendar()
    return (iso.year, iso.week)
