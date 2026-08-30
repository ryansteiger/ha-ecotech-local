"""Sensors for EcoTech Local."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import EcoTechCoordinator
from .entity import EcoTechEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    entities = [EcoTechConnectionStatus(coordinator)]
    if "rssi" in coordinator.data:
        entities.append(EcoTechSignalStrength(coordinator))
    async_add_entities(entities)


class EcoTechConnectionStatus(EcoTechEntity, SensorEntity):
    _attr_translation_key = "connection_status"
    _attr_icon = "mdi:lan-connect"

    def __init__(self, coordinator: EcoTechCoordinator) -> None:
        super().__init__(coordinator, "connection_status")

    @property
    def native_value(self):
        return self.coordinator.data.get("connection", "Unknown")

    @property
    def extra_state_attributes(self):
        return {"implementation_status": "diagnostic_only", "control_available": False}


class EcoTechSignalStrength(EcoTechEntity, SensorEntity):
    _attr_translation_key = "signal_strength"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_state_class = "measurement"

    def __init__(self, coordinator: EcoTechCoordinator) -> None:
        super().__init__(coordinator, "signal_strength")

    @property
    def native_value(self):
        return self.coordinator.data.get("rssi")
