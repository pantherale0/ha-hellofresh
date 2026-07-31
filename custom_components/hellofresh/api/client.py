"""Thin API wrapper around pyhellofresh for Home Assistant."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from pyhellofresh import (
    AccountBalance,
    CartPrice,
    HelloFreshAuthenticationError,
    HelloFreshClient,
    HelloFreshConnectionError,
    HelloFreshError,
    HelloFreshResponseError,
    PastDeliveries,
    Profile,
    Recipe,
    TokenResponse,
    WeeklyMenu,
)

from custom_components.hellofresh.const import LOGGER
from custom_components.hellofresh.utils.weeks import delivery_range, resolve_next_week

if TYPE_CHECKING:
    import aiohttp

# Re-export library exceptions under integration names for coordinator/config flow.
HelloFreshApiClientError = HelloFreshError
HelloFreshApiClientAuthenticationError = HelloFreshAuthenticationError
HelloFreshApiClientCommunicationError = HelloFreshConnectionError


class HelloFreshApiClient:
    """Home Assistant-facing wrapper around :class:`HelloFreshClient`."""

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        access_token: str | None = None,
        refresh_token: str | None = None,
        country: str = "GB",
        locale: str = "en-GB",
        base_url: str = "https://www.hellofresh.co.uk",
    ) -> None:
        """Initialize the client with an injected HA aiohttp session."""
        self._client = HelloFreshClient(
            session=session,
            access_token=access_token,
            refresh_token=refresh_token,
            country=country,
            locale=locale,
            base_url=base_url,
        )

    @property
    def client(self) -> HelloFreshClient:
        """Return the underlying pyhellofresh client."""
        return self._client

    @property
    def access_token(self) -> str | None:
        """Return the current access token."""
        return self._client.access_token

    @property
    def refresh_token(self) -> str | None:
        """Return the current refresh token."""
        return self._client.refresh_token

    @property
    def country(self) -> str:
        """Return the configured country code."""
        return self._client.country

    @property
    def locale(self) -> str:
        """Return the configured locale."""
        return self._client.locale

    @property
    def base_url(self) -> str:
        """Return the configured base URL."""
        return self._client.base_url

    async def async_start_passwordless_login(self, email: str) -> str:
        """Start passwordless login and return the public_id."""
        return await self._client.start_passwordless_login(email)

    async def async_finish_passwordless_login_from_url(
        self,
        url: str,
        *,
        public_id: str | None = None,
    ) -> TokenResponse:
        """Complete passwordless login from a magic-link URL."""
        return await self._client.finish_passwordless_login_from_url(url, public_id=public_id)

    async def async_finish_passwordless_login(
        self,
        *,
        code: str,
        email: str,
        public_id: str,
    ) -> TokenResponse:
        """Complete passwordless login with an extracted code."""
        return await self._client.finish_passwordless_login(
            code=code,
            email=email,
            public_id=public_id,
        )

    async def async_refresh_access_token(self) -> TokenResponse:
        """Refresh the access token using the stored refresh token."""
        return await self._client.refresh_access_token()

    async def async_get_profile(self) -> Profile:
        """Fetch the customer profile."""
        return await self._client.get_profile()

    async def async_get_customer_info(self) -> dict[str, Any]:
        """Fetch raw customer info."""
        return await self._client.get_customer_info()

    async def async_get_subscriptions(self) -> list[dict[str, Any]]:
        """Fetch subscription list."""
        return await self._client.get_subscriptions()

    async def async_get_balance(self, customer_id: str | None = None) -> AccountBalance:
        """Fetch account credit balance."""
        return await self._client.get_balance(customer_id)

    async def async_get_past_deliveries(
        self,
        range_start: str | None = None,
        range_end: str | None = None,
    ) -> PastDeliveries:
        """Fetch deliveries for an optional ISO-week range."""
        return await self._client.get_past_deliveries(range_start, range_end)

    async def async_get_menu(self, week: str) -> WeeklyMenu:
        """Fetch the weekly menu for an ISO week."""
        return await self._client.get_menu(week=week)

    async def async_get_cart_price(self, week: str) -> CartPrice:
        """Fetch cart price for a week."""
        return await self._client.get_cart_price(week=week)

    async def async_get_recipe(self, recipe_id: str) -> Recipe:
        """Fetch a full recipe by id."""
        return await self._client.get_recipe(recipe_id)

    async def async_search_recipes(
        self,
        query: str,
        *,
        take: int = 20,
        skip: int = 0,
    ) -> list[Recipe]:
        """Search recipes by keyword."""
        return await self._client.search_recipes(query, take=take, skip=skip)

    async def async_get_coordinator_payload(self) -> dict[str, Any]:
        """
        Fetch the batched payload used by the data update coordinator.

        Returns a dict of typed model objects plus lightweight summaries.
        """
        profile = await self.async_get_profile()
        customer_info = await self.async_get_customer_info()
        subscriptions = await self.async_get_subscriptions()
        customer_id = str(customer_info.get("uuid") or customer_info.get("id") or "")
        balance = await self.async_get_balance(customer_id or None)

        range_start, range_end = delivery_range()
        past_deliveries = await self.async_get_past_deliveries(range_start, range_end)
        next_week = resolve_next_week(
            api_next_week=past_deliveries.next_week,
            week_ids=[week.week for week in past_deliveries.weeks],
        )
        LOGGER.debug(
            "Deliveries: weeks=%s api_next=%s resolved_next=%s range=%s..%s",
            len(past_deliveries.weeks),
            past_deliveries.next_week,
            next_week,
            range_start,
            range_end,
        )

        menu: WeeklyMenu | None = None
        cart: CartPrice | None = None
        if next_week:
            try:
                menu = await self.async_get_menu(next_week)
            except HelloFreshResponseError as err:
                LOGGER.warning("Unable to fetch menu for %s: %s", next_week, err)
            try:
                cart = await self.async_get_cart_price(next_week)
            except HelloFreshResponseError as err:
                LOGGER.warning("Unable to fetch cart for %s: %s", next_week, err)

        selected_week = next(
            (week for week in past_deliveries.weeks if week.week == next_week),
            None,
        )
        selected_meals = selected_week.meals if selected_week else []

        active_subscription = _pick_active_subscription(subscriptions, customer_info)

        return {
            "profile": profile,
            "customer_info": customer_info,
            "subscriptions": subscriptions,
            "active_subscription": active_subscription,
            "balance": balance,
            "past_deliveries": past_deliveries,
            "next_week": next_week,
            "menu": menu,
            "cart": cart,
            "selected_meals": selected_meals,
            "customer_id": customer_id,
        }


def recipe_to_dict(recipe: Recipe) -> dict[str, Any]:
    """Convert a Recipe dataclass into a JSON-serializable dict."""
    return asdict(recipe)


def _pick_active_subscription(
    subscriptions: list[dict[str, Any]],
    customer_info: dict[str, Any],
) -> dict[str, Any] | None:
    """Pick the active subscription from raw API payloads."""
    active_id = customer_info.get("activeSubscriptionId")
    if active_id is not None:
        for sub in subscriptions:
            if str(sub.get("id") or sub.get("subscriptionId") or "") == str(active_id):
                return sub
    if subscriptions:
        return subscriptions[0]
    return None
