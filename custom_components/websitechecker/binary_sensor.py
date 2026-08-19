"""Binary sensor platform for websitechecker."""
from datetime import timedelta
import logging

import aiohttp
import async_timeout

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    CONF_USER_AGENT,
    CONF_VERIFY_SSL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up websitechecker binary sensor from a config entry."""
    # Combine original data with updated options
    config = {**entry.data, **entry.options}

    url = config[CONF_URL]
    name = config.get(CONF_NAME, url)
    user_agent = config.get(CONF_USER_AGENT, DEFAULT_USER_AGENT)
    update_interval = config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    verify_ssl = config.get(CONF_VERIFY_SSL, True)

    sensor = WebsiteCheckerSensor(
        hass, entry.entry_id, name, url, user_agent, update_interval, verify_ssl
    )

    async_add_entities([sensor], True)


class WebsiteCheckerSensor(BinarySensorEntity):
    """Representation of a WebsiteChecker binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self, hass, entry_id, name, url, user_agent, update_interval, verify_ssl
    ):
        """Initialize the sensor."""
        self._hass = hass
        self._attr_unique_id = f"websitechecker_{entry_id}"
        self._attr_name = name
        self._url = url
        self._user_agent = user_agent
        self._verify_ssl = verify_ssl
        self._update_interval = timedelta(minutes=update_interval)

        self._is_on = False
        self._last_status = None
        self._last_error_status = None

    @property
    def is_on(self):
        """Return True if the website is down/unreachable."""
        return self._is_on

    @property
    def scan_interval(self):
        """Scan interval duration."""
        return self._update_interval

    @property
    def extra_state_attributes(self):
        """Return entity specific attributes."""
        return {
            "url": self._url,
            "user_agent": self._user_agent,
            "last_status": self._last_status,
            "last_error_status": self._last_error_status,
        }

    async def async_update(self):
        """Check site status via HTTP GET."""
        headers = {"User-Agent": self._user_agent}
        session = async_get_clientsession(self._hass, verify_ssl=self._verify_ssl)

        try:
            async with async_timeout.timeout(10):
                async with session.get(self._url, headers=headers) as response:
                    status_code = response.status
                    if status_code < 500:
                        self._is_on = False
                        self._last_status = f"{status_code} - OK"
                    else:
                        self._is_on = True
                        self._last_status = f"{status_code} - HTTP Error"
                        self._last_error_status = self._last_status

        except aiohttp.ClientConnectorError:
            self._is_on = True
            self._last_status = "Connection Error"
            self._last_error_status = self._last_status
        except aiohttp.ServerTimeoutError:
            self._is_on = True
            self._last_status = "Timeout"
            self._last_error_status = self._last_status
        except Exception as err:
            _LOGGER.error("Error checking URL %s: %s", self._url, err)
            self._is_on = True
            self._last_status = "Error"
            self._last_error_status = str(err)