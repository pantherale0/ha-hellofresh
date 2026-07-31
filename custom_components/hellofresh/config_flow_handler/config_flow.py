"""Config flow for hellofresh."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pyhellofresh import HelloFreshAuthenticationError, HelloFreshConnectionError, HelloFreshError

from custom_components.hellofresh.api import HelloFreshApiClient
from custom_components.hellofresh.config_flow_handler.schemas import (
    get_email_country_schema,
    get_magic_link_confirm_schema,
    get_reauth_schema,
    get_reconfigure_schema,
    get_token_schema,
)
from custom_components.hellofresh.config_flow_handler.validators import (
    async_finish_magic_link,
    async_start_magic_link,
    async_validate_tokens,
)
from custom_components.hellofresh.const import (
    AUTH_METHOD_MAGIC_LINK,
    AUTH_METHOD_TOKEN,
    CONF_ACCESS_TOKEN,
    CONF_CODE,
    CONF_COUNTRY,
    CONF_CUSTOMER_ID,
    CONF_MAGIC_LINK,
    CONF_REFRESH_TOKEN,
    DOMAIN,
    LOGGER,
    get_region,
)
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

if TYPE_CHECKING:
    from custom_components.hellofresh.config_flow_handler.options_flow import HelloFreshOptionsFlow

ERROR_MAP = {
    "HelloFreshAuthenticationError": "auth",
    "HelloFreshApiClientAuthenticationError": "auth",
    "HelloFreshConnectionError": "connection",
    "HelloFreshApiClientCommunicationError": "connection",
    "ValueError": "invalid_auth_input",
}


class HelloFreshConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for hellofresh."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow state."""
        self._email: str | None = None
        self._country: str | None = None
        self._public_id: str | None = None

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HelloFreshOptionsFlow:
        """Return the options flow handler."""
        from custom_components.hellofresh.config_flow_handler.options_flow import HelloFreshOptionsFlow  # noqa: PLC0415

        return HelloFreshOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Show authentication method menu."""
        integration = async_get_loaded_integration(self.hass, DOMAIN)
        return self.async_show_menu(
            step_id="user",
            menu_options=[AUTH_METHOD_MAGIC_LINK, AUTH_METHOD_TOKEN],
            description_placeholders={
                "documentation_url": integration.documentation or "",
            },
        )

    async def async_step_magic_link(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Collect email/country and send a magic link."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = str(user_input[CONF_EMAIL])
            country = str(user_input[CONF_COUNTRY])
            self._email = email
            self._country = country
            try:
                self._public_id, _client = await async_start_magic_link(
                    self.hass,
                    email=email,
                    country=country,
                )
            except Exception as err:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(err)
            else:
                return await self.async_step_magic_link_confirm()

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        return self.async_show_form(
            step_id="magic_link",
            data_schema=get_email_country_schema(user_input),
            errors=errors,
            description_placeholders={
                "documentation_url": integration.documentation or "",
            },
        )

    async def async_step_magic_link_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Complete passwordless login with magic-link URL or code."""
        errors: dict[str, str] = {}

        if user_input is not None:
            magic_link = (user_input.get(CONF_MAGIC_LINK) or "").strip() or None
            code = (user_input.get(CONF_CODE) or "").strip() or None
            if not magic_link and not code:
                errors["base"] = "invalid_auth_input"
            else:
                try:
                    entry_data = await async_finish_magic_link(
                        self.hass,
                        email=self._email or "",
                        country=self._country or "GB",
                        public_id=self._public_id or "",
                        magic_link=magic_link,
                        code=code,
                    )
                    return await self._async_create_or_update(entry_data)
                except Exception as err:  # noqa: BLE001
                    errors["base"] = self._map_exception_to_error(err)

        return self.async_show_form(
            step_id="magic_link_confirm",
            data_schema=get_magic_link_confirm_schema(),
            errors=errors,
            description_placeholders={"email": self._email or ""},
        )

    async def async_step_token(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Advanced setup via pasted access/refresh tokens."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                entry_data = await async_validate_tokens(
                    self.hass,
                    access_token=user_input[CONF_ACCESS_TOKEN],
                    refresh_token=user_input.get(CONF_REFRESH_TOKEN),
                    country=user_input[CONF_COUNTRY],
                    email=user_input.get(CONF_EMAIL),
                )
                return await self._async_create_or_update(entry_data)
            except Exception as err:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(err)

        return self.async_show_form(
            step_id="token",
            data_schema=get_token_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Allow updating email/country and re-sending a magic link."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            email = str(user_input[CONF_EMAIL])
            country = str(user_input[CONF_COUNTRY])
            self._email = email
            self._country = country
            try:
                self._public_id, _client = await async_start_magic_link(
                    self.hass,
                    email=email,
                    country=country,
                )
            except Exception as err:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(err)
            else:
                return await self.async_step_magic_link_confirm()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_reconfigure_schema(entry.data),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reauthentication when tokens are invalid."""
        entry = self._get_reauth_entry()
        refresh_token = entry.data.get(CONF_REFRESH_TOKEN)
        if refresh_token:
            region = get_region(entry.data.get(CONF_COUNTRY, "GB"))
            client = HelloFreshApiClient(
                session=async_get_clientsession(self.hass),
                access_token=entry.data.get(CONF_ACCESS_TOKEN),
                refresh_token=refresh_token,
                country=region.country,
                locale=region.locale,
                base_url=region.base_url,
            )
            try:
                tokens = await client.async_refresh_access_token()
                entry_data_new = await async_validate_tokens(
                    self.hass,
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token or refresh_token,
                    country=region.country,
                    email=entry.data.get(CONF_EMAIL),
                )
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **entry_data_new},
                )
            except HelloFreshAuthenticationError, HelloFreshError:
                LOGGER.debug("Refresh failed during reauth; falling back to magic link")

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Collect email and send a new magic link for reauth."""
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            email = str(user_input[CONF_EMAIL])
            country = str(user_input[CONF_COUNTRY])
            self._email = email
            self._country = country
            try:
                self._public_id, _client = await async_start_magic_link(
                    self.hass,
                    email=email,
                    country=country,
                )
            except Exception as err:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(err)
            else:
                return await self.async_step_magic_link_confirm()

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=get_reauth_schema(
                entry.data.get(CONF_EMAIL, ""),
                entry.data.get(CONF_COUNTRY, "GB"),
            ),
            errors=errors,
            description_placeholders={"email": entry.data.get(CONF_EMAIL, "")},
        )

    async def _async_create_or_update(
        self,
        entry_data: dict[str, Any],
    ) -> config_entries.ConfigFlowResult:
        """Create a new entry or update reauth/reconfigure entry."""
        await self.async_set_unique_id(entry_data[CONF_CUSTOMER_ID])

        if self.source == config_entries.SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(),
                data=entry_data,
            )

        if self.source == config_entries.SOURCE_RECONFIGURE:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data=entry_data,
            )

        self._abort_if_unique_id_configured()
        title = entry_data.get(CONF_EMAIL) or f"HelloFresh ({entry_data[CONF_COUNTRY]})"
        return self.async_create_entry(title=title, data=entry_data)

    def _map_exception_to_error(self, exception: Exception) -> str:
        """Map API exceptions to user-facing error keys."""
        LOGGER.warning("Error in config flow: %s", exception)
        if isinstance(exception, HelloFreshAuthenticationError):
            return "auth"
        if isinstance(exception, HelloFreshConnectionError):
            return "connection"
        return ERROR_MAP.get(type(exception).__name__, "unknown")


__all__ = ["HelloFreshConfigFlowHandler"]
