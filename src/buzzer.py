"""buzzer.py - passive buzzer (HW-508) driven by PWM.

Contains the Buzzer class: parking-sensor style beeping with one constant
tone, the pause between beeps gets shorter smoothly as the obstacle gets
closer, continuous tone very close or at the STOP distance, mute.
Also contains the distance zones (ZONES) and zone_of() used by the
display bars.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython),
https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from machine import Pin, PWM

# ---------- display bar zones ----------
# Upper limits of the zones in cm, from the closest one. Used for the five
# bars on the display (zone 0 = nearest bar ... zone 4 = top bar).
ZONES = (8, 20, 40, 65, 100)
SILENT = len(ZONES)        # farther than the last zone
HYSTERESIS_CM = 2


def zone_of(distance, prev=SILENT):
    """Zone index for ``distance`` in cm: 0 = closest ... SILENT = too far.

    When the obstacle moves away by one zone, the previous zone is kept until
    the distance is more than ``HYSTERESIS_CM`` past the limit, so the bars
    do not flicker at a zone border.

    :param distance: distance in cm, or ``None`` (no data = ``SILENT``)
    :param prev: zone index returned last time
    """
    if distance is None:
        return SILENT
    new = SILENT
    for i, limit in enumerate(ZONES):
        if distance <= limit:
            new = i
            break
    if prev < SILENT and new == prev + 1 and distance <= ZONES[prev] + HYSTERESIS_CM:
        return prev
    return new


class Buzzer:
    """Parking-sensor style beeping on a passive buzzer.

    Like in a car, the tone (``TONE_HZ``) and the beep length stay the same,
    only the pause between beeps changes. It goes smoothly (linearly) from
    ``PAUSE_FAR_MS`` at ``START_CM`` to ``PAUSE_NEAR_MS`` just above
    ``CONTINUOUS_CM``; at ``CONTINUOUS_CM`` and closer the tone is
    continuous. Above ``START_CM`` the buzzer is silent. Both borders have a
    small hysteresis, so the sound does not switch back and forth.

    Call :meth:`update` regularly (every 20 ms) with the current distance.

    :param pin: GPIO number of the S pin
    """

    TONE_HZ = 440            # tone A4
    BEEP_MS = 70             # length of one beep
    START_CM = 100           # beeping starts below this distance
    CONTINUOUS_CM = 8        # continuous tone at this distance and closer
    PAUSE_FAR_MS = 800       # pause at START_CM
    PAUSE_NEAR_MS = 100      # pause just above CONTINUOUS_CM
    DUTY_ON = 32768          # 50 % duty cycle

    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.duty_u16(0)
        self.muted = False
        self.state = "silent"    # "silent", "beeping" or "continuous"
        self._on = False
        self._freq = 0
        self._last_ms = time.ticks_ms()

    def tone(self, freq):
        """Start a tone.

        :param freq: frequency in Hz
        """
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
        """Switch mute on / off.

        :returns: the new mute state (True = muted)
        """
        self.muted = not self.muted
        if self.muted:
            self.off()
        return self.muted

    def pause_ms(self, distance):
        """Pause between beeps for a distance (linear interpolation).

        :param distance: distance in cm
        :returns: pause in ms, from ``PAUSE_FAR_MS`` to ``PAUSE_NEAR_MS``
        """
        span = self.START_CM - self.CONTINUOUS_CM
        part = (distance - self.CONTINUOUS_CM) / span      # 0 near ... 1 far
        part = min(max(part, 0.0), 1.0)
        return int(self.PAUSE_NEAR_MS + part * (self.PAUSE_FAR_MS - self.PAUSE_NEAR_MS))

    def _new_state(self, distance):
        """Decide the sound state with hysteresis at both borders.

        :param distance: distance in cm or ``None``
        :returns: "silent", "beeping" or "continuous"
        """
        if distance is None:
            return "silent"
        h = HYSTERESIS_CM
        if self.state == "continuous" and distance <= self.CONTINUOUS_CM + h:
            return "continuous"
        if distance <= self.CONTINUOUS_CM:
            return "continuous"
        if self.state == "silent" and distance > self.START_CM:
            return "silent"
        if distance > self.START_CM + h:
            return "silent"
        return "beeping"

    def update(self, distance, stop=False):
        """Set the sound according to the distance.

        :param distance: distance in cm, or ``None`` (no data = silent)
        :param stop: True when the STOP distance is reached - continuous tone
        """
        self.state = self._new_state(distance)
        if self.muted:
            self.off()
            return
        if stop or self.state == "continuous":
            self.tone(self.TONE_HZ)
            return
        if self.state == "silent":
            self.off()
            return
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, self._last_ms)
        if self._on and elapsed >= self.BEEP_MS:
            self.off()
            self._last_ms = now
        elif not self._on and elapsed >= self.pause_ms(distance):
            self.tone(self.TONE_HZ)
            self._last_ms = now
