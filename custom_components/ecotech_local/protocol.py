"""Fail-closed protocol adapters for undocumented EcoTech transports."""
from __future__ import annotations


class ProtocolUnavailableError(RuntimeError):
    """Raised when a verified local protocol adapter is unavailable."""


class EcoTechProtocolAdapter:
    """Interface reserved for verified owner-device protocol implementations."""

    control_available = False

    async def set_pump(self, percentage: int) -> None:
        raise ProtocolUnavailableError(
            "Pump control is locked: no verified Mobius BLE command format is installed."
        )

    async def set_radion(self, on: bool, brightness: int | None = None) -> None:
        raise ProtocolUnavailableError(
            "Radion control is locked: ReefLink has no verified public local command protocol."
        )

    async def start_feed_mode(self) -> None:
        raise ProtocolUnavailableError(
            "Feed mode is locked until a verified device protocol adapter is installed."
        )
