"""Local reachability coordinator."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ADDRESS, CONF_CONNECTION_TYPE, CONF_HOST, DEFAULT_SCAN_INTERVAL, DOMAIN, TYPE_BLUETOOTH
from .protocol import EcoTechProtocolAdapter


class EcoTechCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"{DOMAIN}-{entry.entry_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.entry = entry
        self.protocol = EcoTechProtocolAdapter()

    async def _async_update_data(self) -> dict:
        connection_type = self.entry.data[CONF_CONNECTION_TYPE]
        if connection_type == TYPE_BLUETOOTH:
            address = self.entry.data[CONF_ADDRESS]
            info = bluetooth.async_last_service_info(self.hass, address, connectable=True)
            return {
                "reachable": info is not None,
                "rssi": getattr(info, "rssi", None) if info else None,
                "name": getattr(info, "name", None) if info else None,
                "connection": "Bluetooth advertisement seen" if info else "Not currently advertising",
                "control_available": False,
            }
        host = self.entry.data[CONF_HOST]
        try:
            reader, writer = await __import__("asyncio").wait_for(
                __import__("asyncio").open_connection(host, 80), timeout=3
            )
            writer.close()
            await writer.wait_closed()
            del reader
            reachable = True
        except (OSError, TimeoutError):
            reachable = False
        return {
            "reachable": reachable,
            "rssi": None,
            "name": "ReefLink",
            "connection": "TCP port 80 reachable" if reachable else "No response on TCP port 80",
            "control_available": False,
        }
