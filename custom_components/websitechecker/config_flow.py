"""Config flow for websitechecker integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    CONF_USER_AGENT,
    CONF_VERIFY_SSL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_USER_AGENT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class WebsiteCheckerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Website Checker."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return WebsiteCheckerOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            url = user_input[CONF_URL]

            # Set unique ID based on URL to prevent duplicates
            await self.async_set_unique_id(url.lower())
            self._abort_if_unique_id_configured()

            name = user_input.get(CONF_NAME) or url

            return self.async_create_entry(
                title=name,
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_URL): cv.string,
                vol.Optional(CONF_NAME): cv.string,
                vol.Optional(CONF_USER_AGENT, default=DEFAULT_USER_AGENT): cv.string,
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): cv.positive_int,
                vol.Optional(CONF_VERIFY_SSL, default=True): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


class WebsiteCheckerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Website Checker options."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Retrieve settings from options if updated previously, falling back to original config_entry data
        current_data = {**self.config_entry.data, **self.config_entry.options}

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_USER_AGENT,
                    default=current_data.get(CONF_USER_AGENT, DEFAULT_USER_AGENT),
                ): cv.string,
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=current_data.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=current_data.get(CONF_VERIFY_SSL, True),
                ): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )