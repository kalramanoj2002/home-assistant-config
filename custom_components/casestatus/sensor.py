import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import urllib.request
import re
import logging
from homeassistant.const import (CONF_NAME, ATTR_TIME)

DEFAULT_NAME = 'Case Status'
CONF_CASE_NUMBER = 'case_number'

_LOGGER = logging.getLogger(__name__)

# example 
URL_FORMAT = "https://egov.uscis.gov/casestatus/mycasestatus.do?appReceiptNum={0}"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CASE_NUMBER): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    case_number = config.get(CONF_CASE_NUMBER)
    name = config.get(CONF_NAME)
    add_devices([CaseStatusSensor(case_number, name)])


class CaseStatusSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, case_number, name):
        """Initialize the sensor."""
        self._state = None
        self._case_number = case_number
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
            url = URL_FORMAT.format(self._case_number)
            _LOGGER.debug("URL: %s", url)
            string_response = str(urllib.request.urlopen(url).read())
            starting_index = string_response.find('<h1>')
            if starting_index > 0:
                end_index = string_response.find('</h1>', starting_index + 5)
                string_result = string_response[starting_index:end_index]
                p = re.compile(r'<.*?>')
                tmp = p.sub('', string_result)
                self._state = tmp
                starting_index = string_response.find('<p>', end_index)
                end_index = string_response.find('</p>', starting_index + 4)
                p = re.compile(r'<.*?>')
                string_result = string_response[starting_index:end_index]
                tmp = p.sub('', string_result)
                self._status = tmp
            else:
                self._state = None
        except:
            _LOGGER.error("something happened in case status")
            self._state = None

       
