"""Suppoort for Ariston switch."""
from datetime import timedelta
from copy import deepcopy
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_SWITCHES, CONF_NAME

from .const import param_zoned
from .const import (
    DATA_ARISTON,
    DEVICES,
    PARAM_INTERNET_TIME,
    PARAM_INTERNET_WEATHER,
    PARAM_CH_AUTO_FUNCTION,
    PARAM_THERMAL_CLEANSE_FUNCTION,
    VALUE,
    VAL_OFF,
    VAL_ON,
    ZONED_PARAMS,
    PARAM_DHW_BOOST,
    PARAM_HP_QUIETE_MODE
)

SWITCH_CH_AUTO_FUNCTION = "CH Auto Function"
SWITCH_INTERNET_TIME = "Internet Time"
SWITCH_INTERNET_WEATHER = "Internet Weather"
SWITCH_THERMAL_CLEANSE_FUNCTION = "Thermal Cleanse Function"
SWITCH_POWER = "Power"
SWITCH_DHW_BOOST = "DHW Boost"
SWITCH_HP_QUIETE_MODE = "HP Silent mode"

SCAN_INTERVAL = timedelta(seconds=2)

switches_default = {
    PARAM_INTERNET_TIME: (SWITCH_INTERNET_TIME, "mdi:update"),
    PARAM_INTERNET_WEATHER: (SWITCH_INTERNET_WEATHER, "mdi:weather-partly-cloudy"),
    PARAM_CH_AUTO_FUNCTION: (SWITCH_CH_AUTO_FUNCTION, "mdi:radiator"),
    PARAM_THERMAL_CLEANSE_FUNCTION: (SWITCH_THERMAL_CLEANSE_FUNCTION, "mdi:allergy"),
    PARAM_DHW_BOOST: (SWITCH_DHW_BOOST, "mdi:water-boiler"),
    PARAM_HP_QUIETE_MODE: (SWITCH_HP_QUIETE_MODE, "mdi:volume-mute"),
}
SWITCHES = deepcopy(switches_default)
for param in switches_default:
    if param in ZONED_PARAMS:
        for zone in range (1, 7):
            SWITCHES[param_zoned(param, zone)] = (
                SWITCHES[param][0] + f' Zone{zone}',
                SWITCHES[param][1],
                SWITCHES[param][2]
            )
        del SWITCHES[param]


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a switches for Ariston."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    device = hass.data[DATA_ARISTON][DEVICES][name]
    add_entities(
        [
            AristonSwitch(name, device, switch_type)
            for switch_type in discovery_info[CONF_SWITCHES]
        ],
        True,
    )


class AristonSwitch(SwitchEntity):
    """Switch for Ariston."""

    def __init__(self, name, device, switch_type):
        """Initialize entity."""
        self._api = device.api.ariston_api
        self._icon = SWITCHES[switch_type][1]
        self._name = "{} {}".format(name, SWITCHES[switch_type][0])
        self._switch_type = switch_type
        self._state = None
        self._device = device.device

    @property
    def unique_id(self):
        """Return the unique id."""
        return f"{self._name}-{self._switch_type}"

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return True

    @property
    def name(self):
        """Return the name of this Switch device if any."""
        return self._name

    @property
    def icon(self):
        """Return the state attributes."""
        return self._icon

    @property
    def available(self):
        """Return True if entity is available."""
        try:
            return (
                self._api.available
                and not self._api.sensor_values[self._switch_type][VALUE] is None
            )
        except KeyError:
            return False

    @property
    def is_on(self):
        """Return true if switch is on."""
        try:
            if not self._api.available:
                return False
            return self._api.sensor_values[self._switch_type][VALUE] == VAL_ON
        except KeyError:
            return False

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._api.set_http_data(**{self._switch_type: VAL_ON})

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._api.set_http_data(**{self._switch_type: VAL_OFF})

    def update(self):
        """Update data"""
        return
