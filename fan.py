"""Fail-closed pump placeholder entity."""
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CONNECTION_TYPE, TYPE_BLUETOOTH
from .coordinator import EcoTechCoordinator
from .entity import EcoTechEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    if entry.data[CONF_CONNECTION_TYPE] == TYPE_BLUETOOTH:
        async_add_entities([EcoTechPump(entry.runtime_data)])


class EcoTechPump(EcoTechEntity, FanEntity):
    _attr_translation_key = "pump"
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = 100

    def __init__(self, coordinator: EcoTechCoordinator) -> None:
        super().__init__(coordinator, "pump")

    @property
    def available(self) -> bool:
        return False

    @property
    def extra_state_attributes(self):
        return {"reason": "No verified Mobius BLE command format is installed"}

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs):
        await self.coordinator.protocol.set_pump(percentage or 50)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.protocol.set_pump(0)

    async def async_set_percentage(self, percentage: int) -> None:
        await self.coordinator.protocol.set_pump(percentage)
