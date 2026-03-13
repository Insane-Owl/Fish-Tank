import json
import os
import time

import requests
import sensor

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(config_path, "r") as config_file:
    config = json.load(config_file)

server_ip = config["server_ip"]
API_URL = f"http://{server_ip}/api/sensors"

while True:
    temp = sensor.get_temperature()
    ph_level = sensor.get_ph()
    tds_level = sensor.get_tds()

    payload = {"temperature": temp, "ph": ph_level, "tds": tds_level}

    try:
        response = requests.post(API_URL, json=payload)
        print(f"Sent data. Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send data: {e}")

    time.sleep(60)
