"""test_ultrasonic.py - test of both HC-SR04 sensors.

Expected result in the Thonny shell, a new block about every 0.4 s:

    L raw: 52.3 filtered: 52.1
    R raw: 48.7 filtered: 48.9

- Hold a hand / book in front of a sensor: its value follows the distance.
- Point the sensor at nothing (far away): raw shows None, after 3 such
  readings filtered also shows None.
- Covering only the LEFT sensor must not change the RIGHT value (and the
  other way round) - checks that the sensors do not disturb each other.

Run it from Thonny; the class files from src/ must be saved on the Pico.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython),
https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from ultrasonic import UltrasonicSensor

left = UltrasonicSensor(2, 3)      # TRIG = GP2, ECHO = GP3
right = UltrasonicSensor(12, 13)   # TRIG = GP12, ECHO = GP13

while True:
    for name, s in (("L", left), ("R", right)):
        s.trigger()          # sensor sends the ultrasonic burst
        time.sleep_ms(60)    # wait until the echo comes back (max ~38 ms)
        s.update()           # compute the distance from the echo time
        # raw = this single measurement in cm (None = no echo / out of range)
        # filtered = median of the last 3 valid measurements
        print(name, "raw:", s.raw_cm(), "filtered:", s.distance)
    print()
    time.sleep_ms(300)       # slow down the printing
