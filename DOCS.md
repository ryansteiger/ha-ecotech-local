# EcoTech Local — Technical Docs v2

## 1. QD Mobius compatibility check

Your 2× MP10 QD and 1× MP40 QD: QuietDrive by itself does NOT prove Bluetooth/Mobius support. The controller must have a Mobius-ready radio module + firmware.

**How to verify:**

1. **Mobius app scan** (easiest): Install EcoTech Mobius on iOS/Android, create account, power a QD controller within 3ft, scan. If it appears as a tile with serial, it's Mobius-ready. If it never appears after 2min and power-cycle, it's legacy EcoSmart Live.
2. **EcoSmart Live Devices tab**: Go to https://ecosmartlive.com → Devices. Legacy QD controllers list "EcoSmart Live Mode" and show RF module version. Mobius-ready controllers show "Mobius Ready" badge or prompt "Upgrade to Mobius". Screenshot that page.
3. **Physical RF module**: Open QD controller (power off), look for module labeled "RF 3.0" vs "RF MOBIUS". ReefBuilders 2020 article: older Vortechs needed RF module swap before Mobius use. Bulk Reef Supply product pages for "Vortech MP10QD Mobius Ready" vs "Vortech MP10QD" differentiate SKU.
4. **HA Bluetooth scan**: Settings → System → Bluetooth → "i" — watch for advertisement `MOBIUS` with manufacturer data. If HA sees nothing even with proxy next to tank, controller isn't advertising Mobius.

**If not Mobius-ready:** you have 3 options:
- Swap RF module to Mobius-compatible (EcoTech part, ~$30-50, fits G3/G4/QD controllers post-2016, confirm serial compatibility)
- Keep that pump on ReefLink/ESL and accept cloud for that one device (not ideal, but safe)
- Leave it disconnected from HA until module swapped

Do NOT try to force-pair a legacy RF controller via Bluetooth — it doesn't have a BLE stack.

## 2. Why Radion G2 stays on ReefLink RF

From sources checked:

- Lincs Aquatics replacement RF module page: "This RF Module is Mobius compatible, and available for the Radion models below: XR15w G3 all versions, XR15w G4 all versions, XR30w G3 all versions with serial beginning in 6, XR30w G4 all versions." **G2 absent.**
- Reef2Reef thread g4-mobius-capable-wont-connect-to-reef-link.900845: Mobius and ESL modes are not interchangeable on same radio config.
- ReefBuilders 2020-06-01: "Beginning today June 1st, all new models of Vortech and Vectra pumps will ship with Mobius software... You will be able to downgrade to legacy EcoSmart Live within Mobius app." Downgrade path exists but not for G2 to upgrade.

**Implication for your 2× G2:**

- G2s speak 2.4GHz proprietary RF (nRF24-like) to ReefLink, which bridges to EcoSmart Live cloud via TCP/TLS. No public local HTTP interface; ReefLink does not expose REST. DNS redirection alone fails because ReefLink expects TLS + auth + session.
- ha-mobius / python-mobius does NOT speak this RF protocol. It speaks BLE GATT to Mobius devices.
- So G2s cannot be managed by this integration. Keep them on ReefLink for now, with a reserved LAN IP, and don't block ReefLink's cloud.

**ReefLink diagnostics from v1 (optional carry-over):**

If you still want ReefLink reachability:

- Reserve IP in router DHCP for ReefLink MAC
- In HA, add a `ping` binary_sensor or `command_line` sensor:

```yaml
binary_sensor:
  - platform: ping
    host: 192.168.1.XXX  # your ReefLink
    name: reeflink_reachable
    count: 2
    scan_interval: 60
```

- Check ReefLink's own local mDNS: `avahi-browse -a | grep -i reeflink` on HAOS terminal. Some firmware advertises `_http._tcp` but returns 404 — no usable local API.

Future path for G2s: upgrade to XR15 G5/G6 Blue (Mobius native) and sell G2s, or keep G2s on ESL and automate around them via smart plug on/off only (not spectrum control).

## 3. ESPHome Bluetooth proxy setup (required for distant tanks)

Your Pi 4 in a closet ≠ tank in living room. BLE range ~10m through air, less through water/glass/salt creep.

**Recommended:** ESP32-S3 DevKitC-1 N16R8, one per tank/area. More gives better coverage and more gateway candidates for RSSI-based gateway election.

**Why `active: true` is non-negotiable:**

- Passive proxy only forwards advertisements. This integration needs actual GATT connections (reading/writing characteristics like firmware, schedule points, operation state).
- Without `active: true`, you'll see devices discovered but connection fails with "no route" or timeout.
- Also set `esp32_ble_tracker.scan_parameters.active: true` so split advertisements that don't all carry manufacturer data are still found once fuller packet arrives.

**Flash steps:**

1. Install ESPHome on HA (Add-on)
2. New Device → Manual → paste `esphome/ecotech-bt-proxy.yaml` (edit wifi secrets)
3. Build + Install via USB, then adopt via WiFi
4. Place proxy within 1-2m of tank, not inside stand if stand is metal
5. In waterproof junction box (IP65) because reef humidity corrodes pins — even indoors, salt spray kills.
6. In HA → Settings → Devices & Services → ESPHome → device → Enable Bluetooth Proxy — confirm entity shows `active: true`
7. Restart Mobius integration — check logs for gateway election: which device holds gateway role based on RSSI

**Testing proxy:**

- In HA → Settings → System → Bluetooth → Scanner — you should see RSSI for MOBIUS devices via proxy MAC, not just Pi MAC
- Enable debug logging for EcoTech Local — logs show `connection attempts, gateway elections and failovers, and mesh scans`
- If proxy hits 3-connection limit (real limit on ESP32), integration serializes to 1 concurrent new connection attempt (MAX_CONCURRENT_CONNECTIONS=1) but multi-tank setups can still hit ceiling. Symptom: gateway flapping. Fix: add second proxy, reduce tank count per proxy.

## 4. Entity list (full, matching ha-mobius 0.4.1)

Per physical device (pump or light) — one HA device per physical:

- `sensor.{serial}_support_tier` — diagnostic, support tier (light/pump/pump-experimental/unsupported)
- `sensor.{serial}_error_state` — diagnostic, error state string
- `sensor.{serial}_schedule_point_count` — diagnostic, int
- `sensor.{serial}_mesh_address` — diagnostic, IPv6 address + last-heard attribute
- `sensor.{serial}_firmware_version` — diagnostic, Product OS + full per-component breakdown as attributes (Radio, Radio Bootloader, WLAN, etc. via get_firmware_versions())
- `sensor.{serial}_hardware_revision` — diagnostic, full breakdown
- Pumps only — main entities:
  - `sensor.{serial}_operation_state`
  - `sensor.{serial}_motor_speed` (raw)
  - `sensor.{serial}_flow_rate` (estimated GPH)
  - `sensor.{serial}_current_pump_mode`
- Lights only — main:
  - `sensor.{serial}_{channel}_intensity` — one per channel (%), via client-side schedule interpolation replicating official app (not a live device read — there isn't one; see python-mobius docs why)
- Lights only — diagnostic:
  - `sensor.{serial}_calibration` — completed True/False + last-calibration-date attribute (light-specific, confirmed via hardware + app UI gating)
- Plus advanced feature sensors (if device exposes): `local_control_enabled`, `auto_dim_timeout`, `max_fan_speed`, `fan_shutdown_enabled`

Per tank (synthetic device, not any one physical):

- `sensor.tank_{mlprefix}_gateway_device` — which device currently holds gateway role
- `sensor.tank_{mlprefix}_mesh_prefix` — mesh's shared prefix

Button:

- `button.{serial}_reboot` — every device, narrow write op allowed

Maintenance:

- Hourly clock sync per tank (automatic, via coordinator time sync task, not user-visible entity)

Diagnostics:

- Download diagnostics JSON via entry three-dot menu — includes gateway role, per-device registry health (rssi, mesh address, consecutive gateway failures), latest coordinator data/error, and live Bluetooth cache snapshot (whether HA's own stack sees device at all, independent of cached state).

## 5. Migration from v1 research preview

v1 created:
- `fan.mp10_*` locked entities (unavailable)
- `light.radion_g2_*` locked
- `button.feed_mode` locked
- `binary_sensor.reeflink_reachable`, `sensor.bluetooth_signal`, `sensor.connection_status`

v2 creates real sensor entities as above. Entity IDs will change. To avoid ghost entities:

1. In HA → Devices & Services → EcoTech Local → Delete entry
2. In HACS → remove old integration (or overwrite files), copy new v2 `custom_components/ecotech_local`
3. Restart HA, hard-refresh browser (clear frontend cache)
4. Re-add integration — select discovered MOBIUS devices
5. Update automations: replace `fan.mp10` with `sensor.<serial>_operation_state` triggers, etc.
6. If you had ReefLink IP config in v1, that config flow no longer exists — remove that part of config entry data manually if needed (edit `.storage/core.config_entries` while HA stopped, not recommended, or just delete entry)

## 6. Safety stance

This fork intentionally keeps ha-mobius read-only stance:

- No scene writes, no schedule overwrites, no feed mode start beyond what python-mobius has verified
- Reboot and clock sync are the only two write ops allowed because they are narrow, reversible, and verified on real hardware by r3pek
- Future writes (starting scenes, changing schedules) will be kept in lockstep with python-mobius upstream as it grows write capabilities — we will not get ahead of upstream with guessed packets

This is to avoid killing coral/pumps with bad packets.

## 7. Sources checked (for G2 incompatibility)

- Lincs Aquatics EcoTech Replacement RF Module — Mobius compatible list (G3/G4 only)
- ReefBuilders 2020-06-01 "Ecotech Vortech and Vectra Pumps Start Shipping With Mobius Software" — upgrade path via RF module swap, downgrade to ESL possible within Mobius app
- Reef2Reef thread g4-möbius-capable-won’t-connect-to-reef-link.900845 — Mobius vs ESL modes not interchangeable
- ha-mobius README and python-mobius PyPI docs — protocol writeup, manufacturer_id 0x0202, local_name MOBIUS, multi-device tank grouping via pan_id
- Bulk Reef Supply Vortech MP10QD Mobius Ready product page — SKU differentiation

## 8. Troubleshooting checklist

- Device not found: power-cycle QD controller, move proxy closer, check Mobius app sees it, check HA Bluetooth scanner sees manufacturer_id 514
- Device found but setup aborts "no manufacturer data": normal temporary — HA will auto-detect again within seconds once fuller advertisement arrives. If persists, RSSI too low or interference.
- Device already configured / merged into tank: expected for multi-device tanks — second device auto-added to existing tank entry, no further action
- Gateway flapping: add second proxy, check proxy active:true, check MAX_CONCURRENT_CONNECTIONS=1 throttling, check proxy 3-connection hardware limit
- Light intensity sensors show schedule interpolation not live read: expected — python-mobius docs explain why no live device read exists for lights (client-side schedule)
- ReefLink still needed for G2: yes, keep it

