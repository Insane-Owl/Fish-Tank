import json
import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
try:
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        print("Config loaded successfully.")
except FileNotFoundError:  # fallback
    print("Config file not found, using fallback values.")
    config = {"PH_SLOPE": -5.77, "PH_INTERCEPT": 21.48}
except Exception as e:
    print(f"Failed to load config file: {e}")
    config = {"PH_SLOPE": -5.77, "PH_INTERCEPT": 21.48}

try:
    import adafruit_ads1x15.ads1115 as ADS
    import board
    import busio
    from adafruit_ads1x15 import ads1x15
    from adafruit_ads1x15.analog_in import AnalogIn

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    ph_channel = AnalogIn(ads, ads1x15.Pin.A0)
    tds_channel = AnalogIn(ads, ads1x15.Pin.A1)
    print("ADS1115 and I2C initialized successfully.")
except Exception as e:
    print(f"Failed to initialize ADS1115 and I2C: {e}")
    ph_channel = None
    tds_channel = None

try:
    from w1thermsensor import W1ThermSensor

    temp_sensor = W1ThermSensor()
    print("W1ThermSensor initialized successfully.")
except Exception as e:
    print(f"Failed to initialize W1ThermSensor: {e}")
    temp_sensor = None


def get_temperature() -> float:
    if temp_sensor is None:
        print("Temperature reading failed: temp_sensor is None")
        return 0.0
    try:
        temp_c = temp_sensor.get_temperature()
        temp_f = (temp_c * 9 / 5) + 32
        print(f"Temperature read successfully: {temp_f:.2f}°F")
        return temp_f
    except Exception as e:
        print(f"Temperature reading failed: {e}")
        return 0.0


def get_ph() -> float:
    if ph_channel is None:
        print("pH reading failed: ph_channel is None")
        return 0.0
    try:
        ph_val = (config["PH_SLOPE"] * ph_channel.voltage) + config["PH_INTERCEPT"]
        print(f"pH read successfully: {ph_val:.2f}")
        return ph_val
    except Exception as e:
        print(f"pH reading failed: {e}")
        return 0.0


def get_tds() -> float:
    if tds_channel is None:
        print("TDS reading failed: tds_channel is None")
        return 0.0

    try:
        # TDS requires temperature to calculate
        # fall back to 25.0 C if the temp sensor fails
        if temp_sensor is not None:
            try:
                temp_c = temp_sensor.get_temperature()
            except Exception as e:
                print(
                    f"TDS temperature compensation reading failed, falling back to 25.0°C: {e}"
                )
                temp_c = 25.0
        else:
            temp_c = 25.0

        tds_voltage = tds_channel.voltage
        comp_coeff = 1.0 + 0.02 * (temp_c - 25.0)
        comp_v = tds_voltage / comp_coeff
        # TDS formula: TDS (ppm) = (133.42V^3 - 255.86V^2 + 857.39V) x 0.5
        tds_val = (133.42 * comp_v**3 - 255.86 * comp_v**2 + 857.39 * comp_v) * 0.5
        print(f"TDS read successfully: {tds_val:.2f} ppm")
        return tds_val
    except Exception as e:
        print(f"TDS reading failed: {e}")
        return 0.0
