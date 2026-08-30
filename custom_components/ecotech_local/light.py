"""Fail-closed Radion placeholder entity."""
from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CONNECTION_TYPE, TYPE_REEFLINK
from .coordinator import EcoTechCoordinator
from .entity import EcoTechEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    if entry.data[CONF_CONNECTION_TYPE] == TYPE_REEFLINK:
        async_add_entities([EcoTechRadion(entry.runtime_data)])


class EcoTechRadion(EcoTechEntity, LightEntity):
    _attr_translation_key = "radion"
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, coordinator: EcoTechCoordinator) -> None:
        super().__init__(coordinator, "radion")

    @property
    def available(self) -> bool:
        return False

    @property
    def extra_state_attributes(self):
        return {"reason": "ReefLink has no verified public local command protocol"}

    async def async_turn_on(self, **kwargs):
        await self.coordinator.protocol.set_radion(True, kwargs.get(ATTR_BRIGHTNESS))

    async def async_turn_off(self, **kwargs):
        await self.coordinator.protocol.set_radion(False)
