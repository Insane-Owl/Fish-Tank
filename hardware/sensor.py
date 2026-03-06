import time

from w1thermsensor import W1ThermSensor

temp_sensor = W1ThermSensor()

while True:
    print(temp_sensor.get_temperature())
    time.sleep(1)
