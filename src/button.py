"""button.py - push button with debounce and short / long press detection.

Contains the Button class. In the application a short press mutes the
buzzer and a long press opens the STOP distance setting.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from machine import Pin


class Button:
    """Push button connected between a GPIO pin and GND (internal pull-up).

    Call :meth:`update` regularly (every 20 ms). It returns ``"short"`` when
    the button is released after a short press, ``"long"`` as soon as the
    button has been held for ``long_ms``, otherwise ``None``.

    A new state is accepted only when it has been stable for ``debounce_ms``,
    which removes contact bounce.

    :param pin: GPIO number
    :param long_ms: minimum length of a long press in ms
    :param debounce_ms: time the state must be stable in ms
    """

    def __init__(self, pin, long_ms=1000, debounce_ms=30):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.long_ms = long_ms
        self.debounce_ms = debounce_ms
        self._raw = 1
        self._raw_since = time.ticks_ms()
        self._stable = 1        # 1 = released, 0 = pressed
        self._pressed_at = 0
        self._long_sent = False

    def is_pressed(self):
        """Debounced state: ``True`` while the button is held."""
        return self._stable == 0

    def update(self):
        """Read the pin and return ``"short"``, ``"long"`` or ``None``."""
        now = time.ticks_ms()
        raw = self.pin.value()
        if raw != self._raw:
            self._raw = raw
            self._raw_since = now
            return None
        if raw != self._stable and time.ticks_diff(now, self._raw_since) >= self.debounce_ms:
            self._stable = raw
            if raw == 0:                      # pressed
                self._pressed_at = now
                self._long_sent = False
            elif not self._long_sent:         # released after a short press
                return "short"
            return None
        if (self._stable == 0 and not self._long_sent
                and time.ticks_diff(now, self._pressed_at) >= self.long_ms):
            self._long_sent = True
            return "long"
        return None
