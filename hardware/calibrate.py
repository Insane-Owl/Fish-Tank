import json
import os
import time

from sensor import ph_channel

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

stored_v4 = None
stored_v7 = None


def get_stable_voltage(samples: int = 10, delay: float = 0.5) -> float:
    # takes multiple readings and averages them to avoid fluctuations
    readings = []
    for i in range(samples):
        readings.append(ph_channel.voltage)
        time.sleep(delay)
    return sum(readings) / len(readings)


def calibrate_ph() -> None:
    global stored_v4, stored_v7

    if stored_v4 is None or stored_v7 is None:
        # waiting on other reading
        return

    # both readings are ready, calculate slope and intercept
    slope = (4.0 - 7.0) / (stored_v4 - stored_v7)
    intercept = 7.0 - slope * stored_v7

    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    config["PH_SLOPE"] = slope
    config["PH_INTERCEPT"] = intercept

    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

    print(
        f"Successfully calibrated PH sensor. Slope: {slope:.3f}, Intercept: {intercept:.3f}"
    )

    # reset variables
    stored_v4 = None
    stored_v7 = None


def button_7_pressed() -> None:
    global stored_v7
    print("pH 7 button pressed, reading voltage...")
    stored_v7 = get_stable_voltage()
    print("pH 7 voltage read and saved.")
    calibrate_ph()


def button_4_pressed() -> None:
    global stored_v4
    print("pH 4 button pressed, reading voltage...")
    stored_v4 = get_stable_voltage()
    print("pH 4 voltage read and saved.")
    calibrate_ph()
