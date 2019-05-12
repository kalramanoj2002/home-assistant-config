import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import logging
import requests
from datetime import datetime

CONF_URL = 'url'

SENSOR_PREFIX = 'Renew '

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string
})



def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the sensor platform."""
    url = config.get(CONF_URL)
    
    try:
        data = RenewData(url)
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    entities = []
    for resource in data.data['result']:
        entities.append(RenewStuff(resource, hass))

    add_entities(entities)


# pylint: disable=abstract-method
class RenewData(object):
    """call the api to get the data"""

    def __init__(self, url):
        """Initialize."""
        self._url = url
        self.data = None
        self.update()

    def update(self):
        """Update the data from the api."""
        try:
            self.data = requests.get(self._url, timeout=60).json()
            _LOGGER.debug("Data = %s", self.data)
        except requests.exceptions.RequestException:
            _LOGGER.error("Error occurred while fetching data.")
            self.data = None
            return False


class RenewStuff(Entity):
    """Representation of a resource as an entity."""

    def __init__(self, data, hass):
        """Initialize the sensor."""
        self.data = data
        self._hass = hass
        self._name = SENSOR_PREFIX + data['name']
        self._friendly_name = data['name']
        self._state = None

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
        """Return the unit of measurement of this entity, if any."""
        return 'days'

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        return self.data

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        expiry_date = datetime.strptime(self.data['expiry_date'], '%m/%d/%Y')
        now = datetime.now()
        delta = expiry_date - now

        pending_days = delta.days - self.data['renew_days'] 
        if pending_days <= 0 :
            event_data = {
                'domain': 'notify',
                'service': 'notify',
                'service_data': { 'message' : self.data['name'] + ' is pending to renew' + str(pending_days) + 'days' }
            }
            self._hass.bus.async_fire(event_type = 'call_service', event_data = event_data)
        self._state = pending_days