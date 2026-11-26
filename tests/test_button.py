"""test_button.py - test of the push button.

Expected result in the Thonny shell:

- Short press and release:     prints "short" once, at the release.
- Hold the button > 1 s:       prints "long" once, while still holding.
  Releasing after a long press prints nothing.
- Pressing quickly several times prints one "short" for each press,
  never two for a single press (checks the debounce).

Run it from Thonny; the class files from src/ must be saved on the Pico.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython),
https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from button import Button

btn = Button(15)   # GP15 to GND, internal pull-up
print("Press the button (short / hold > 1 s)")

while True:
    event = btn.update()   # returns "short", "long" or None
    if event:
        print(event)
    time.sleep_ms(20)      # check every 20 ms, as in main.py
