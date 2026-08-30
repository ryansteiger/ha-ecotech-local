# EcoTech Local for Home Assistant

**Research preview for HAOS + HACS.** This package safely checks whether Home Assistant can see an EcoTech Bluetooth controller and whether a ReefLink answers on your LAN. It does **not yet control pumps or lights** because no verified public command specification was found for Mobius Bluetooth or ReefLink's local interface.

The integration deliberately fails closed: the pump, Radion, and feed-mode controls appear as locked/unavailable rather than transmitting guessed packets to aquarium equipment.

## Hardware target

- Home Assistant OS on Raspberry Pi 4
- Two Radion G2 lights through ReefLink
- Two MP10 QuietDrive and one MP40 QuietDrive

Important: **QuietDrive does not by itself prove Bluetooth/Mobius support.** The controller must have a Mobius-ready radio module and compatible firmware. Controllers running legacy EcoSmart Live mode communicate through ReefLink instead.

## What works in this preview

- HACS-compatible repository layout
- Home Assistant Bluetooth discovery for common EcoTech/Mobius names
- Manual Bluetooth-address setup when discovery names do not match
- Local ReefLink IP setup
- Reachability sensor
- Bluetooth signal-strength sensor
- Connection-status sensor
- Locked Home Assistant fan, light, and feed-mode entities that cannot send unverified commands

## What does not work yet

- Pump speed/mode control
- Feed mode
- Radion brightness, channels, or schedules
- ReefLink RF command forwarding

Those require verified packet captures/specifications from the owner's devices or a documented vendor interface. DNS redirection alone is not enough: a cloud replacement must also reproduce authentication, encryption, sessions, and command formats.

## Manual installation (no GitHub account needed)

1. Download and unzip this package.
2. Copy `custom_components/ecotech_local` into the `config/custom_components/` folder in Home Assistant.
3. Restart Home Assistant.
4. Open **Settings → Devices & services → Add integration**.
5. Search for **EcoTech Local (Research Preview)**.
6. Add each Bluetooth pump by discovery or Bluetooth address, then add the ReefLink by its reserved LAN IP.

If `custom_components` does not exist, create it under the Home Assistant `config` folder.

## HACS installation (GitHub repository required)

1. Create an empty GitHub repository, for example `ha-ecotech-local`.
2. Upload the contents of this package to the repository root. Do not upload the outer ZIP as the only file.
3. In HACS, open **Integrations → three-dot menu → Custom repositories**.
4. Paste your repository URL and choose **Integration**.
5. Install **EcoTech Local (Research Preview)** and restart Home Assistant.

## First test

1. In **Settings → Devices & services → Bluetooth**, confirm the pump controller appears while it is powered.
2. If it does not appear by name, note its Bluetooth address and add it manually.
3. Reserve an IP address for ReefLink in your router, then add that IP in this integration.
4. Check the Reachable and Connection status entities.

A Bluetooth device being visible does not prove it accepts direct control. Do not assume a legacy QuietDrive controller is Bluetooth-capable unless it works in the Mobius app.

## Safe next development step

Capture only traffic from equipment you own, while issuing one harmless command at a time in the official app (for example, feed mode). Record firmware version, Bluetooth address, service UUIDs, characteristic UUIDs, write payload, notification payload, and before/after device state. Remove account identifiers and Wi-Fi credentials before sharing captures.

Once a command is repeatable and verified on the bench, implement it in `protocol.py`, add a read-back confirmation, and only then mark the corresponding Home Assistant entity available.

## Sources checked

- EcoTech equipment may run either Mobius or legacy EcoSmart Live; the modes are not interchangeable on the same radio configuration: https://www.reef2reef.com/threads/g4-m%C3%B6bius-capable-won%E2%80%99t-connect-to-reef-link.900845/
- Mobius-ready MP10/MP40 controllers are advertised as Bluetooth/app controllable: https://www.bulkreefsupply.com/vortech-mp10qd-mobius-ready-quietdrive-propeller-pump-ecotech-marine.html?queryID=0b1cda27a2c56ee5d60f5f49e3609b18&objectID=10706&indexName=brs_prod_m2_default_products
- Older compatible pumps may need a radio-module change before Mobius use: https://reefbuilders.com/2020/06/01/ecotech-vortech-and-vectra-pumps-start-shipping-with-mobius-software/

## Disclaimer

This is an independent community research project and is not affiliated with EcoTech Marine. Use only with equipment and networks you own. Keep the official controller available and test with livestock safety in mind.
