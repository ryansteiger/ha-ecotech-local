"""Fail-closed feed-mode placeholder entity."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CONNECTION_TYPE, TYPE_BLUETOOTH
from .coordinator import EcoTechCoordinator
from .entity import EcoTechEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    if entry.data[CONF_CONNECTION_TYPE] == TYPE_BLUETOOTH:
        async_add_entities([EcoTechFeedMode(entry.runtime_data)])


class EcoTechFeedMode(EcoTechEntity, ButtonEntity):
    _attr_translation_key = "feed_mode"
    _attr_icon = "mdi:fish-food"

    def __init__(self, coordinator: EcoTechCoordinator) -> None:
        super().__init__(coordinator, "feed_mode")

    @property
    def available(self) -> bool:
        return False

    @property
    def extra_state_attributes(self):
        return {"reason": "No verified Mobius BLE command format is installed"}

    async def async_press(self) -> None:
        await self.coordinator.protocol.start_feed_mode()
