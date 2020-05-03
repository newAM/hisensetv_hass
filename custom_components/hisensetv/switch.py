""" Hisense Television Integration. """
from hisensetv import HisenseTv
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import CONF_BROADCAST_ADDRESS
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_MAC
from homeassistant.const import CONF_NAME
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import HomeAssistantType
from typing import Callable
from typing import Optional
import homeassistant.helpers.config_validation as cv
import logging
import platform
import socket
import subprocess as sp
import voluptuous as vol
import wakeonlan
import time

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "tv"
DEFAULT_PING_TIMEOUT = 1

DOMAIN = "hisensetv"
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_BROADCAST_ADDRESS): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    add_entities: Callable,
    discovery_info: Optional[dict] = None,
):
    """Set up a Hisense TV."""
    broadcast_address = config.get(CONF_BROADCAST_ADDRESS)
    host = config[CONF_HOST]
    mac = config[CONF_MAC]
    name = config[CONF_NAME]

    add_entities(
        [
            HisenseTvEntity(
                host=host, mac=mac, name=name, broadcast_address=broadcast_address,
            )
        ],
        True,
    )


class HisenseTvEntity(SwitchDevice):
    def __init__(self, host: str, mac: str, name: str, broadcast_address: str):
        self._name = name
        self._host = host
        self._mac = mac
        self._broadcast_address = broadcast_address
        self._is_on = True
        self._state = False
        self._last_state_change = 0

    def turn_on(self, **kwargs):
        if self._broadcast_address:
            wakeonlan.send_magic_packet(self._mac, ip_address=self._broadcast_address)
        else:
            wakeonlan.send_magic_packet(self._mac)

        self._state = True
        self._last_state_change = time.monotonic()

    def turn_off(self, **kwargs):
        try:
            with HisenseTv(self._host) as tv:
                tv.send_key_power()
            self._state = False
            self._last_state_change = time.monotonic()
        except socket.error as e:
            if "host is unreachable" in str(e).lower():
                _LOGGER.debug("unable to reach TV, likely powered off already")
            else:
                raise

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    def update(self):
        """Check if device is on and update the state."""
        # skip updating via ping if power state has changed in last 15s
        if time.monotonic() - self._last_state_change < 15:
            return

        if platform.system().lower() == "windows":
            ping_cmd = [
                "ping",
                "-n",
                "1",
                "-w",
                str(DEFAULT_PING_TIMEOUT * 1000),
                str(self._host),
            ]
        else:
            ping_cmd = [
                "ping",
                "-c",
                "1",
                "-W",
                str(DEFAULT_PING_TIMEOUT),
                str(self._host),
            ]

        status = sp.call(ping_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        self._state = not bool(status)
