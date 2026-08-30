"""Config flow for EcoTech Local."""
from __future__ import annotations

import ipaddress
import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ADDRESS,
    CONF_CONNECTION_TYPE,
    CONF_HOST,
    DOMAIN,
    TYPE_BLUETOOTH,
    TYPE_REEFLINK,
)

_BT_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class EcoTechLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._discovery: BluetoothServiceInfoBleak | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            if user_input[CONF_CONNECTION_TYPE] == TYPE_BLUETOOTH:
                return await self.async_step_bluetooth_manual()
            return await self.async_step_reeflink()
        schema = vol.Schema({vol.Required(CONF_CONNECTION_TYPE): vol.In({
            TYPE_BLUETOOTH: "Mobius / QuietDrive Bluetooth",
            TYPE_REEFLINK: "ReefLink local IP",
        })})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        self._discovery = discovery_info
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": discovery_info.name or discovery_info.address}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        assert self._discovery is not None
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery.name or self._discovery.address,
                data={CONF_CONNECTION_TYPE: TYPE_BLUETOOTH, CONF_ADDRESS: self._discovery.address},
            )
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovery.name or self._discovery.address},
        )

    async def async_step_bluetooth_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper()
            if _BT_RE.fullmatch(address):
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"EcoTech Bluetooth {address[-8:]}",
                    data={CONF_CONNECTION_TYPE: TYPE_BLUETOOTH, CONF_ADDRESS: address},
                )
            errors["base"] = "invalid_address"
        return self.async_show_form(
            step_id="bluetooth",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            errors=errors,
        )

    async def async_step_reeflink(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                ipaddress.ip_address(host)
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                await self.async_set_unique_id(f"reeflink-{host}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"ReefLink {host}",
                    data={CONF_CONNECTION_TYPE: TYPE_REEFLINK, CONF_HOST: host},
                )
        return self.async_show_form(
            step_id="reeflink",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )
