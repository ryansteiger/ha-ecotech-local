"""Shared entities."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcoTechCoordinator


class EcoTechEntity(CoordinatorEntity[EcoTechCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: EcoTechCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.unique_id or coordinator.entry.entry_id}-{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.unique_id or self.coordinator.entry.entry_id)},
            name=self.coordinator.entry.title,
            manufacturer="EcoTech Marine",
            model="Local research preview",
            configuration_url=None,
        )
