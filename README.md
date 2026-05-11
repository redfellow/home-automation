# Home Automation

Home Assistant configuration snippets and helper scripts for a small Windows-based
home automation setup.

## Contents

- `ruuvi_scan.py` - BLE-to-MQTT bridge for Ruuvi sensors. It scans for Ruuvi
  Bluetooth advertisements, decodes measurements, publishes Home Assistant MQTT
  discovery config, and sends sensor state updates.
- `configuration.yaml` - Home Assistant configuration entries used to load the
  included packages and set trusted reverse proxy ranges.
- `automations.yaml` - Home Assistant automations for PC sleep/resume behavior,
  light notifications, and activity tracking.
- `spot-price.yaml` - Home Assistant package for Finnish electricity spot price
  sensors and helpers.
- `spot-price-sleep-timer.yaml` - Template sensors that convert current spot
  price into a desktop PC sleep timeout.

## Requirements

The Python bridge uses:

- Python 3
- `bleak`
- `paho-mqtt`
- An MQTT broker reachable from the machine running the script

Install the Python dependencies with:

```powershell
pip install bleak paho-mqtt
```

## Notes

These files are intended as examples and personal configuration, not a polished
drop-in Home Assistant add-on. You will likely need to adjust entity names,
device IDs, MQTT broker address, file paths, proxy settings, and Home Assistant
package includes for your own environment.

The checked-in configuration may include internal Home Assistant IDs, local IP
addresses, and descriptive device/entity names. Those are not credentials, but
review them before publishing or reusing the files in another setup.
