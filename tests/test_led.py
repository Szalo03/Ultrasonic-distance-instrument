"""test_led.py - test of the red hazard LEDs on GP26.

Expected result:

1. Both LEDs light for 1 s, then go off for 1 s.
2. Blinking like hazard lights (0.4 s on / 0.4 s off) for 4 s.
3. Fast blinking (0.1 s on / 0.1 s off) for 2 s.
4. Both LEDs off at the end, the shell prints "done".

Run it from Thonny; the class files from src/ must be saved on the Pico.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from led import Led

hazard = Led(26)

hazard.on()                 # 1. on
time.sleep(1)
hazard.off()
time.sleep(1)

for _ in range(5):          # 2. hazard-light blinking
    hazard.toggle()
    time.sleep_ms(400)
    hazard.toggle()
    time.sleep_ms(400)

for _ in range(10):         # 3. fast blinking
    hazard.toggle()
    time.sleep_ms(100)
    hazard.toggle()
    time.sleep_ms(100)

hazard.off()                # 4. off
print("done")
