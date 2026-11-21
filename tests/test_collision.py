"""test_collision.py - test of the rear collision warning with the LEFT sensor.

The shell prints the distance, the approach speed and the warning level
about 8 times per second, the LEDs show the level:

    dist  52.3 cm   speed  -1 cm/s   -
    dist  41.0 cm   speed  84 cm/s   DANGER

Expected result:

- Hand / book still or moving slowly (< 40 cm/s): level "-", LEDs off.
- Moving the hand away (speed negative): level stays "-".
- Fast approach from far (e.g. from 1.5 m in about 1 s): "WARNING",
  LEDs blink slowly.
- Still fast and closer than 60 cm: "DANGER", LEDs blink fast.
- Fast approach right up to the sensor (< 5 cm, or touch it): "CRASH",
  stays for 5 s.
- Stop the hand at e.g. 30 cm: the level goes back to "-" after about 1 s.
- Putting a hand in front of the sensor from the side must NOT give a
  warning (the jump in distance is ignored).

Use this test to tune WARN_SPEED, DANGER_CM ... in collision.py.

Run it from Thonny; the class files from src/ must be saved on the Pico.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from ultrasonic import UltrasonicSensor
from collision import CollisionWarning
from led import Led

NAMES = ("-", "WARNING", "DANGER", "CRASH")
sensor = UltrasonicSensor(2, 3)     # left sensor
warn = CollisionWarning()
hazard = Led(26)

while True:
    sensor.trigger()
    time.sleep_ms(60)
    sensor.update()
    level = warn.add(sensor.distance)
    d = sensor.distance
    print("dist", "  ---  " if d is None else "{:6.1f}".format(d), "cm",
          "  speed {:4.0f} cm/s  ".format(warn.speed), NAMES[level])
    # LEDs: slow blink for WARNING / CRASH, fast blink for DANGER
    period = 100 if level == 2 else 400
    hazard.set(level > 0 and (time.ticks_ms() // period) % 2 == 0)
    time.sleep_ms(60)               # same rate as main.py: 120 ms per sensor
