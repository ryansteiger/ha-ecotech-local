# EcoTech Local for Home Assistant

Local-only Home Assistant integration for EcoTech Marine Mobius-protocol pumps and lights, rebased on the verified work of **[r3pek/ha-mobius](https://github.com/r3pek/ha-mobius)** and **[python-mobius](https://pypi.org/project/python-mobius/)**.

> Not affiliated with or endorsed by EcoTech Marine, AquaIllumination, or any vendor. See python-mobius docs for the full protocol writeup this is built on.

## What this is (v2)

This repo was originally a research preview that probed Bluetooth and ReefLink LAN reachability but refused to send unverified commands. **v2 rebases that preview on the proven ha-mobius stack** so your QD pumps get real, safe, local control via Bluetooth LE — no cloud, no ReefLink DNS tricks.

**Current hardware target (yours):**
- 2× Radion G2 (NOT Mobius — stays on ReefLink RF, see below)
- 2× MP10 QuietDrive (QD) — Mobius-ready if it appears in Mobius app
- 1× MP40 QuietDrive (QD) — same
- HAOS on Raspberry Pi 4 with HACS, Bluetooth available

### What works today (inherited from ha-mobius 0.4.1)

- **Autodiscovery**: HA's Bluetooth integration triggers setup when it sees `MOBIUS` or manufacturer ID `0x0202` (514) / `0x0001`. No manual scanning needed. Handles split advertisement packets that don't all carry identifying data.
- **Multi-device tanks**: devices sharing one Thread mesh (one tank) are grouped as a single config entry — one device relays for the others via Thread CoAP relay, rather than each opening its own BLE connection.
- **One HA device per physical device** with model, manufacturer, serial, and firmware version ("Product OS" — the meaningful single firmware label from the app) in the device registry.
- **Sensors — all read-only** (matching ha-mobius deliberate choice):
  - Every device: support tier, error state, schedule point count, mesh address (device's Thread mesh-local IPv6 + last-heard attribute), firmware version (full per-component breakdown as attributes), hardware revision (full breakdown)
  - Pumps — main entities (not diagnostic): operation state, motor speed (raw), estimated flow (GPH), current pump mode
  - Lights — main: one intensity sensor per channel (%) via client-side schedule interpolation that python-mobius replicates from the official app (not a live device read — there isn't one). Diagnostic: calibration completed True/False + last-calibration-date attribute (light-only, confirmed via hardware)
  - Per-tank synthetic device: which device currently holds gateway role, mesh prefix
- **Reboot button** for every device
- **Automatic hourly clock sync** per tank (maintenance task, not per-poll)
- **Debug logging**: Enable via Settings → Devices & Services → EcoTech Local → Enable debug logging — surfaces connection attempts, gateway elections/failovers, mesh scans. Built to make "why isn't this connecting" diagnosable from logs alone.
- **Diagnostics download**: entry's three-dot menu → Download diagnostics — includes registry/coordinator state per device and whether HA's Bluetooth stack currently sees each device at all (independent of cached state).

**Explicitly NOT implemented (safe fail-closed):** starting scenes, changing schedules, feed mode writes, brightness writes beyond reboot/clock-sync. That's intentional — control support is kept in lockstep with python-mobius itself as it grows verified write capabilities, rather than getting ahead of it. Sending guessed packets to reef gear would be unsafe.

## Why G2 Radions are different

From Lincs Aquatics RF module compatibility list and ReefBuilders 2020-06-01 article:

- Mobius-compatible RF modules exist for: XR15w G3 all versions, XR15w G4 all versions, XR30w G3 versions with serial beginning in 6, XR30w G4 all versions.
- **G2 is not listed** — no Mobius RF module upgrade path. G2s talk legacy 2.4GHz RF via ReefLink to EcoSmart Live cloud.
- QD Vortechs starting June 1 2020 ship with Mobius natively. Older QDs can be upgraded by swapping the RF module in the controller — check EcoSmart Live Devices tab: if it says Mobius-ready, you're good.

So for your 2× G2: they stay on ReefLink for now. Keep the ReefLink reserved IP, don't block it. For your 3× QD pumps: if they show in Mobius app, they'll show in HA via this integration.

## Bluetooth proxy — you probably need one

Your Pi is far from the tank. Every Mobius device must be within BLE range of something HA can talk to — either the Pi's adapter or an ESPHome Bluetooth proxy near the tank.

**You need `active: true`**. This integration needs GATT connections (reading/writing attributes), not just advertisement forwarding. Passive-only proxy is not enough.

Example ESPHome config is in `esphome/ecotech-bt-proxy.yaml` (adapted from ha-mobius):

```yaml
# Board: ESP32-S3 DevKitC-1 N16R8
esphome:
  name: bt-aquarium
  friendly_name: bt-aquarium
esp32:
  variant: esp32s3
  flash_size: 16MB
  framework:
    type: esp-idf
psram:
  mode: octal
logger:
api:
ota:
  - platform: esphome
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
esp32_ble:
  use_psram: true
esp32_ble_tracker:
  scan_parameters:
    active: true
bluetooth_proxy:
  active: true
button:
  - platform: restart
    name: "BT Proxy Restart"
    icon: "mdi:restart"
    entity_category: diagnostic
```

Flash to an ESP32-S3 DevKitC-1 N16R8, put in a waterproof junction box near tank, adopt in ESPHome.

Confirmed working hardware (from ha-mobius): ESP32-S3 DevKitC-1 N16R8 (one per tank/area), waterproof junction box.

## Install

### HACS (recommended)

1. In HACS → Integrations → 3-dot menu → Custom repositories
2. Add `https://github.com/ryansteiger/ha-ecotech-local` type: Integration
3. Install "EcoTech Local", restart HA
4. Settings → Devices & Services → Add Integration → EcoTech Local — it will auto-find Mobius devices, or pick from already-seen-but-unconfigured

Or click: [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ryansteiger&repository=ha-ecotech-local&category=integration)

### Manual

Copy `custom_components/ecotech_local/` into `config/custom_components/`, restart.

## Requirements (auto-installed)

From manifest.json (copied from ha-mobius):

```
python-mobius~=0.5.0
bleak-retry-connector>=3.0
```

No manual pip needed — HA installs on load.

## Migration from v1 research preview

v1 used domain `ecotech_local` with same name but no real protocol — it created locked fan/light entities and ReefLink reachability sensors. v2 uses same domain but completely different backend.

1. Remove v1 config entries (Settings → Devices & Services → EcoTech Local → delete). Your YAML not affected.
2. Delete `custom_components/ecotech_local` old version, copy new v2 in (or HACS update will do it).
3. Restart HA, clear browser cache if entities ghost.
4. Add integration again — QD pumps will now appear via Bluetooth, not via manual address.
5. Keep ReefLink IP reservation for G2s — ReefLink diagnostics moved to DOCS.md; G2s are not managed by this integration yet. If you still want G2 reachability ping, see DOCS.md ReefLink section to run a separate ping sensor.

Breaking: entity_ids will change from `fan.mp10_...` locked entities to real `sensor.mp10_operation_state` etc. Update automations.

## License

GPLv2 — see LICENSE. Same as ha-mobius to stay compatible. Original ha-mobius © r3pek, this fork © Ryan Steiger with credit.

## Acknowledgements

- [r3pek/ha-mobius](https://github.com/r3pek/ha-mobius) — the integration this is rebased on
- [python-mobius](https://pypi.org/project/python-mobius/) — protocol reverse engineering and device library
- ESPHome bluetooth_proxy docs
- Lincs Aquatics / ReefBuilders articles for Mobius RF module compatibility lists
