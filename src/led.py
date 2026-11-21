"""led.py - LED (or a group of LEDs) on one GPIO pin.

Contains the Led class, used for the two red hazard LEDs of the rear
collision warning (both on GP26, active high).

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
from machine import Pin


class Led:
    """LED connected from a GPIO pin through a resistor to GND.

    Active high: the anode is on the GPIO side, so value 1 = LED on.

    :param pin: GPIO number
    """

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT, value=0)

    def on(self):
        """Switch the LED on."""
        self.pin.value(1)

    def off(self):
        """Switch the LED off."""
        self.pin.value(0)

    def set(self, state):
        """Switch the LED on (True) or off (False)."""
        self.pin.value(1 if state else 0)

    def toggle(self):
        """Change the LED state."""
        self.pin.value(1 - self.pin.value())
