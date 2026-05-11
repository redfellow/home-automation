import asyncio
from bleak import BleakScanner
import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime

MQTT_BROKER = "192.168.0.194"

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(
    filename=r"J:\apps\ruuvireader\ruuvi_state.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

logging.info("Ruuvi BLE MQTT bridge started")

# -----------------------
# MQTT setup
# -----------------------
client = mqtt.Client()

# Enable automatic reconnect backoff:
# start at 1s, max 120s between retries
client.reconnect_delay_set(min_delay=1, max_delay=120)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT connected successfully")
    else:
        logging.warning(f"MQTT connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warning(f"Unexpected MQTT disconnect (code {rc}). Will auto-reconnect.")

client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

# -----------------------
# Ruuvi logic
# -----------------------
RUUVI_MANUFACTURER_ID = 0x0499
discovered = set()

def decode_ruuvi(data):
    if len(data) < 24 or data[0] != 0x05:
        return None

    temp = int.from_bytes(data[1:3], "big", signed=True) * 0.005
    humidity = data[3] * 0.5
    pressure = int.from_bytes(data[4:6], "big") + 50000

    power_info = int.from_bytes(data[13:15], "big")
    battery = (power_info >> 5) + 1600
    battery_pct = max(0, min(100, int((battery - 2200) / (3000 - 2200) * 100)))
    tx_power = (power_info & 0x1F) * 2 - 40

    return {
        "temperature": round(temp, 2),
        "humidity": round(humidity, 2),
        "pressure": pressure,
        "battery": battery,
        "battery_pct": battery_pct,
        "tx_power": tx_power
    }

def publish_discovery(mac):
    base = mac.replace(":", "")

    device = {
        "identifiers": [base],
        "name": f"Ruuvi {mac}",
        "manufacturer": "Ruuvi"
    }

    sensors = {
        "temperature": "°C",
        "humidity": "%",
        "pressure": "hPa",
        "battery": "mV",
        "battery_pct": "%",
        "tx_power": "dBm",
        "rssi": "dBm"
    }

    for key, unit in sensors.items():
        topic = f"homeassistant/sensor/{base}/{key}/config"

        payload = {
            "name": f"{mac} {key}",
            "state_topic": f"ruuvi/{base}/state",
            "unit_of_measurement": unit,
            "value_template": f"{{{{ value_json.{key} }}}}",
            "unique_id": f"{base}_{key}",
            "device": device
        }

        client.publish(topic, json.dumps(payload), retain=True)

def detection_callback(device, advertisement_data):
    mfg_data = advertisement_data.manufacturer_data

    if RUUVI_MANUFACTURER_ID in mfg_data:
        raw = mfg_data[RUUVI_MANUFACTURER_ID]
        decoded = decode_ruuvi(raw)

        if decoded:
            mac = device.address
            base = mac.replace(":", "")

            decoded["rssi"] = advertisement_data.rssi

            if mac not in discovered:
                publish_discovery(mac)
                discovered.add(mac)

            client.publish(f"ruuvi/{base}/state", json.dumps(decoded))

async def main():
    scanner = BleakScanner(detection_callback)
    await scanner.start()

    while True:
        await asyncio.sleep(1)

asyncio.run(main())
