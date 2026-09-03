"""Custom types for hellofresh."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import HelloFreshApiClient
    from .coordinator import HelloFreshDataUpdateCoordinator


type HelloFreshConfigEntry = ConfigEntry[HelloFreshData]


@dataclass
class HelloFreshData:
    """Runtime data for hellofresh config entries."""

    client: HelloFreshApiClient
    coordinator: HelloFreshDataUpdateCoordinator
    integration: Integration
    options: dict[str, Any] = field(default_factory=dict)
