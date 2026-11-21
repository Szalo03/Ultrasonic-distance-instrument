"""buzzer.py - passive buzzer (HW-508) driven by PWM.

Contains the distance zones (ZONES), the zone_of() function shared with the
display bars, and the Buzzer class: parking-sensor style beeping, continuous
tone at the STOP distance and mute.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from machine import Pin, PWM

# Distance zones, like a car parking sensor: the sound is the same inside one
# zone and changes by a small step at the next zone. The beep is always the
# same length, only the pause gets shorter and the tone slightly higher.
# (max_cm, pause_ms, tone_hz) - pause_ms 0 = continuous tone
ZONES = (
    (8, 0, 560),       # zone 0: continuous tone
    (20, 90, 540),     # zone 1: fast beeping
    (40, 160, 520),    # zone 2
    (65, 260, 500),    # zone 3
    (100, 380, 480),   # zone 4: slow beeping
)
SILENT = len(ZONES)    # farther than the last zone: no sound
BEEP_MS = 70           # length of one beep
HYSTERESIS_CM = 2


def zone_of(distance, prev=SILENT):
    """Zone index for ``distance`` in cm: 0 = closest ... SILENT = too far.

    When the obstacle moves away by one zone, the previous zone is kept until
    the distance is more than ``HYSTERESIS_CM`` past the limit, so the sound
    and the bars do not flicker at a zone border.

    :param distance: distance in cm, or ``None`` (no data = ``SILENT``)
    :param prev: zone index returned last time
    """
    if distance is None:
        return SILENT
    new = SILENT
    for i, zone in enumerate(ZONES):
        if distance <= zone[0]:
            new = i
            break
    if prev < SILENT and new == prev + 1 and distance <= ZONES[prev][0] + HYSTERESIS_CM:
        return prev
    return new


class Buzzer:
    """Parking-sensor style beeping on a passive buzzer.

    Call :meth:`update` regularly (every 20 ms) with the current distance.
    The sound follows the distance zones (``ZONES``); when ``stop`` is True
    (the saved STOP distance is reached) a continuous tone is played.

    :param pin: GPIO number of the S pin
    """

    DUTY_ON = 32768          # 50 % duty cycle

    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.duty_u16(0)
        self.muted = False
        self.zone = SILENT
        self._on = False
        self._freq = 0
        self._last_ms = time.ticks_ms()

    def tone(self, freq):
        """Start a tone with the given frequency in Hz."""
        if freq != self._freq:
            self.pwm.freq(freq)
            self._freq = freq
        self.pwm.duty_u16(self.DUTY_ON)
        self._on = True

    def off(self):
        """Stop the sound."""
        self.pwm.duty_u16(0)
        self._on = False

    def toggle_mute(self):
        """Switch mute on / off. Returns the new mute state."""
        self.muted = not self.muted
        if self.muted:
            self.off()
        return self.muted

    def update(self, distance, stop=False):
        """Set the sound according to ``distance`` in cm (``None`` = no data).

        :param stop: True when the STOP distance is reached - continuous tone
        """
        self.zone = zone_of(distance, self.zone)
        if self.muted or (self.zone == SILENT and not stop):
            self.off()
            return
        if stop:
            self.tone(ZONES[0][2])          # continuous tone at STOP
            return
        _, pause_ms, freq = ZONES[self.zone]
        if pause_ms == 0:
            self.tone(freq)                 # continuous tone
            return
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, self._last_ms)
        if self._on and elapsed >= BEEP_MS:
            self.off()
            self._last_ms = now
        elif not self._on and elapsed >= pause_ms:
            self.tone(freq)
            self._last_ms = now
