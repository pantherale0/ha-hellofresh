"""Constants for hellofresh."""

from __future__ import annotations

from logging import Logger, getLogger
from typing import Final, NamedTuple

from homeassistant.helpers.selector import SelectOptionDict

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "hellofresh"
ATTRIBUTION: Final = "Data provided by HelloFresh"

PARALLEL_UPDATES: Final = 1

DEFAULT_UPDATE_INTERVAL_HOURS: Final = 1.0
DEFAULT_COUNTRY: Final = "GB"
# Refresh slightly before JWT expiry so service/LLM calls do not hit a 401 first.
TOKEN_REFRESH_SKEW_SECONDS: Final = 120.0

CONF_ACCESS_TOKEN: Final = "access_token"
CONF_REFRESH_TOKEN: Final = "refresh_token"
CONF_COUNTRY: Final = "country"
CONF_LOCALE: Final = "locale"
CONF_BASE_URL: Final = "base_url"
CONF_CUSTOMER_ID: Final = "customer_id"
CONF_UPDATE_INTERVAL_HOURS: Final = "update_interval_hours"
CONF_MAGIC_LINK: Final = "magic_link"
CONF_CODE: Final = "code"
CONF_CONFIG_ENTRY_ID: Final = "config_entry_id"
CONF_RECIPE_ID: Final = "recipe_id"
CONF_QUERY: Final = "query"
CONF_TAKE: Final = "take"
CONF_SKIP: Final = "skip"

AUTH_METHOD_MAGIC_LINK: Final = "magic_link"
AUTH_METHOD_TOKEN: Final = "token"


class RegionInfo(NamedTuple):
    """HelloFresh regional endpoint settings."""

    country: str
    locale: str
    base_url: str
    label: str


# Common HelloFresh markets supported by config flow selectors.
REGIONS: Final[dict[str, RegionInfo]] = {
    "AT": RegionInfo("AT", "de-AT", "https://www.hellofresh.at", "Austria"),
    "AU": RegionInfo("AU", "en-AU", "https://www.hellofresh.com.au", "Australia"),
    "BE": RegionInfo("BE", "nl-BE", "https://www.hellofresh.be", "Belgium"),
    "CA": RegionInfo("CA", "en-CA", "https://www.hellofresh.ca", "Canada"),
    "CH": RegionInfo("CH", "de-CH", "https://www.hellofresh.ch", "Switzerland"),
    "DE": RegionInfo("DE", "de-DE", "https://www.hellofresh.de", "Germany"),
    "DK": RegionInfo("DK", "da-DK", "https://www.hellofresh.dk", "Denmark"),
    "FR": RegionInfo("FR", "fr-FR", "https://www.hellofresh.fr", "France"),
    "GB": RegionInfo("GB", "en-GB", "https://www.hellofresh.co.uk", "United Kingdom"),
    "IE": RegionInfo("IE", "en-IE", "https://www.hellofresh.ie", "Ireland"),
    "IT": RegionInfo("IT", "it-IT", "https://www.hellofresh.it", "Italy"),
    "LU": RegionInfo("LU", "fr-LU", "https://www.hellofresh.lu", "Luxembourg"),
    "NL": RegionInfo("NL", "nl-NL", "https://www.hellofresh.nl", "Netherlands"),
    "NO": RegionInfo("NO", "nb-NO", "https://www.hellofresh.no", "Norway"),
    "NZ": RegionInfo("NZ", "en-NZ", "https://www.hellofresh.co.nz", "New Zealand"),
    "SE": RegionInfo("SE", "sv-SE", "https://www.hellofresh.se", "Sweden"),
    "US": RegionInfo("US", "en-US", "https://www.hellofresh.com", "United States"),
}

COUNTRY_OPTIONS: Final[list[SelectOptionDict]] = [
    SelectOptionDict(value=code, label=f"{info.label} ({code})") for code, info in REGIONS.items()
]


def get_region(country: str) -> RegionInfo:
    """Return region info for a country code, defaulting to GB."""
    return REGIONS.get(country.upper(), REGIONS[DEFAULT_COUNTRY])
