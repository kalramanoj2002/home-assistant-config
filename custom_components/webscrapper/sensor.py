import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import urllib.request
import re
import logging
from homeassistant.const import (CONF_NAME, ATTR_TIME)

DEFAULT_NAME = 'Web Scrapper'
CONF_WEB_URL = 'web_url'
CONF_STATE_START_STRING = 'state_start_string'
CONF_STATE_END_STRING = 'state_end_string'
CONF_STATUS_START_STRING = 'status_start_string'
CONF_STATUS_END_STRING = 'status_end_string'

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_WEB_URL): cv.string,
    vol.Required(CONF_STATE_START_STRING): cv.string,
    vol.Required(CONF_STATE_END_STRING): cv.string,
    vol.Required(CONF_STATUS_START_STRING): cv.string,
    vol.Required(CONF_STATUS_END_STRING): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    web_url = config.get(CONF_WEB_URL)
    state_start_string = config.get(CONF_STATE_START_STRING)
    state_end_string = config.get(CONF_STATE_END_STRING)
    status_start_string = config.get(CONF_STATUS_START_STRING)
    status_end_string = config.get(CONF_STATUS_END_STRING)
    name = config.get(CONF_NAME)
    add_devices([WebScrapperSensor(web_url, state_start_string, state_end_string, status_start_string, status_end_string, name)])


class WebScrapperSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, web_url, state_start_string, state_end_string, status_start_string, status_end_string, name):
        """Initialize the sensor."""
        self._state = None
        self._web_url = web_url
        self._state_start_string = state_start_string
        self._state_end_string = state_end_string
        self._status_start_string = status_start_string
        self._status_end_string = status_end_string
        self._name = name
        self._status = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def state_attributes(self):
        """Return the state of the sensor."""
        return {
            "status": self._state,
            "details": self._status
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ''   

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            url = self._web_url
            _LOGGER.debug("URL: %s", url)
            string_response = str(urllib.request.urlopen(url).read())
            """
            calculate state
            """
            starting_index = string_response.find(self._state_start_string)
            if starting_index > 0:
                end_index = string_response.find(self._state_end_string, starting_index + len(self._state_end_string))
                starting_index = starting_index + len(self._state_start_string)
                string_result = string_response[starting_index:end_index]
                p = re.compile(r'<.*?>')
                tmp = p.sub('', string_result)
                self._state = tmp
            else:
                self._state = "no state found"
            
            """
            calculate status
            """
            starting_index = string_response.find(self._status_start_string)
            if starting_index > 0:
                end_index = string_response.find(self._status_end_string, starting_index + len(self._status_end_string))
                string_result = string_response[starting_index:end_index]
                p = re.compile(r'<.*?>')
                tmp = p.sub('', string_result)
                self._status = tmp
            else:
                self._status = "no status found"
        except:
            _LOGGER.error("something happened in web scrapping")
            self._state = "something gone bad"

       
