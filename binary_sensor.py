"""Binary sensors for EcoTech Local."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import EcoTechCoordinator
from .entity import EcoTechEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([EcoTechReachable(entry.runtime_data)])


class EcoTechReachable(EcoTechEntity, BinarySensorEntity):
    _attr_translation_key = "reachable"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: EcoTechCoordinator) -> None:
        super().__init__(coordinator, "reachable")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("reachable"))
