import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import urllib.request
import re
import logging
from homeassistant.const import (CONF_NAME, ATTR_TIME)

DEFAULT_NAME = 'NJ transit'
CONF_ROUTE = 'route'
CONF_DIRECTION = 'direction'
CONF_STOP_ID = 'stop_id'

_LOGGER = logging.getLogger(__name__)

URL_FORMAT = "http://mybusnow.njtransit.com/bustime/wireless/html/eta.jsp?route={0}&direction={1}&id={2}&showAllBusses=off"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ROUTE): cv.string,
    vol.Required(CONF_DIRECTION): cv.string,
    vol.Required(CONF_STOP_ID): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    route = config.get(CONF_ROUTE)
    direction = config.get(CONF_DIRECTION)
    stop_id = config.get(CONF_STOP_ID)
    name = config.get(CONF_NAME)
    add_devices([NJTransitSensor(route, direction, stop_id, name)])


class NJTransitSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, route, direction, stop_id, name):
        """Initialize the sensor."""
        self._state = None
        self._route = route
        self._direction = direction
        self._stop_id = stop_id
        self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'min'   

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            url = URL_FORMAT.format(self._route, self._direction, self._stop_id)
            _LOGGER.debug("URL: %s", url)
            string_response = str(urllib.request.urlopen(url).read())
            string_response = string_response.replace('<hr />', '<hr/>')
            starting_index = string_response.find('<hr/>')
            if starting_index > 0:
                end_index = string_response.find('<hr/>', starting_index + 5)
                string_result = string_response[starting_index:end_index]
                p = re.compile(r'<.*?>')
                tmp = p.sub('', string_result)
                tmp = tmp.replace('\\r', '').replace('\\n', '').replace('\\t', '').replace('&nbsp;', ' ')
                time_remaining_index = tmp.find('MIN')
                if time_remaining_index != -1:
                    time_remaining = tmp[time_remaining_index - 3:time_remaining_index]
                    self._state = time_remaining
                else:
                    self._state = None
            else:
                self._state = None
        except:
            _LOGGER.error("something happened")
            self._state = None

       
