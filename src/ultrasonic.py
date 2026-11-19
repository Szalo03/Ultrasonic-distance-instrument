"""ultrasonic.py - HC-SR04 ultrasonic distance sensor.

Contains the UltrasonicSensor class: TRIG pulse, non-blocking measurement
of the ECHO pulse by a pin interrupt and a median filter of the distance.

Author:  Marek Gláser
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from machine import Pin


class UltrasonicSensor:
    """HC-SR04 sensor with non-blocking echo measurement.

    The ECHO pulse is measured by a pin interrupt that only stores the time of
    the rising and falling edge, so the program never waits for the echo.
    Usage: call :meth:`trigger`, wait at least 40 ms (e.g. in an uasyncio
    task), then call :meth:`update` and read :attr:`distance`.

    A median of the last 3 valid readings removes random jumps. If 3 readings
    in a row are invalid (no echo, out of range), :attr:`distance` is ``None``.

    :param trig: GPIO number of the TRIG pin
    :param echo: GPIO number of the ECHO pin (through the 1k/2k divider)
    """

    SOUND_CM_PER_US = 0.0343   # speed of sound at about 20 degC
    MIN_CM = 2
    MAX_CM = 400
    FILTER_SIZE = 3
    MAX_MISSES = 3

    def __init__(self, trig, echo):
        self.trig = Pin(trig, Pin.OUT, value=0)
        self.echo = Pin(echo, Pin.IN)
        self.distance = None    # filtered distance in cm, or None
        self._rise_us = 0
        self._pulse_us = 0
        self._done = False
        self._history = []
        self._misses = 0
        # hard IRQ: the time stamp is taken immediately, even when the main
        # program is busy (e.g. sending data to the display)
        self.echo.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                      handler=self._on_echo, hard=True)

    def _on_echo(self, pin):
        # interrupt handler: only record the edge time
        now = time.ticks_us()
        if pin.value():
            self._rise_us = now
        else:
            self._pulse_us = time.ticks_diff(now, self._rise_us)
            self._done = True

    def trigger(self):
        """Send a 10 us TRIG pulse to start one measurement."""
        self._done = False
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

    def raw_cm(self):
        """Distance from the last measurement in cm, or ``None`` if invalid."""
        if not self._done:
            return None
        cm = self._pulse_us * self.SOUND_CM_PER_US / 2
        if cm < self.MIN_CM or cm > self.MAX_CM:
            return None
        return cm

    def update(self):
        """Process the last measurement and update :attr:`distance`."""
        cm = self.raw_cm()
        if cm is None:
            self._misses += 1
            if self._misses >= self.MAX_MISSES:
                self._history = []
                self.distance = None
            return self.distance
        self._misses = 0
        self._history.append(cm)
        if len(self._history) > self.FILTER_SIZE:
            self._history.pop(0)
        ordered = sorted(self._history)
        self.distance = ordered[len(ordered) // 2]
        return self.distance
