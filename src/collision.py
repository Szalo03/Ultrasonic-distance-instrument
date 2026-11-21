"""collision.py - rear collision warning: detects an obstacle approaching fast.

Contains the CollisionWarning class (one per sensor): approach speed from a
line fit, time to collision and the warning levels NONE / WARNING / DANGER /
CRASH. Pure logic without hardware, so it can be tested on its own.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time

NONE, WARNING, DANGER, CRASH = 0, 1, 2, 3


class CollisionWarning:
    """Collision warning for one sensor.

    Feed it every new distance with :meth:`add`. From the last few distances
    it computes the approach speed (cm/s, positive = getting closer) by a
    least-squares line fit, which is much less noisy than the difference of
    two readings. Then it decides the warning level:

    - ``WARNING``: approaching faster than ``WARN_SPEED`` and the time to
      collision (distance / speed) is shorter than ``WARN_TTC_MS``
    - ``DANGER``:  still approaching fast and closer than ``DANGER_CM``
    - ``CRASH``:   in DANGER the obstacle got closer than ``CRASH_CM``
      (or the sensor lost it right at the bumper)

    A jump bigger than ``MAX_STEP_CM`` between two readings starts the speed
    fit again, so an object put in front of the sensor from the side is not
    taken as a fast approach.

    A level is kept for ``HOLD_MS`` after its condition ends (CRASH for
    ``CRASH_HOLD_MS``), so the warning does not flicker.
    """

    WARN_SPEED = 40         # cm/s - slower approach is normal parking
    WARN_TTC_MS = 3000      # warning when collision is less than 3 s away
    DANGER_CM = 60
    CRASH_CM = 5
    LOST_NEAR_CM = 30       # sensor lost the obstacle closer than this = crash
    HOLD_MS = 1000
    CRASH_HOLD_MS = 5000
    WINDOW = 4              # number of readings for the speed fit
    MAX_STEP_CM = 40        # bigger jump between readings = a different object

    def __init__(self):
        self.level = NONE
        self.speed = 0.0
        self._samples = []  # (time_ms, distance_cm)
        self._since = time.ticks_ms()

    def reset(self):
        """Clear the warning (e.g. after the crash message was confirmed)."""
        self.level = NONE
        self.speed = 0.0
        self._samples = []
        self._since = time.ticks_ms()

    def _fit_speed(self):
        n = len(self._samples)
        if n < 3:
            return 0.0
        t0 = self._samples[0][0]
        ts = [time.ticks_diff(t, t0) / 1000 for t, _ in self._samples]
        ds = [d for _, d in self._samples]
        mt = sum(ts) / n
        md = sum(ds) / n
        den = sum((t - mt) ** 2 for t in ts)
        if den == 0:
            return 0.0
        slope = sum((t - mt) * (d - md) for t, d in zip(ts, ds)) / den
        return -slope       # distance going down = positive approach speed

    def add(self, distance, now_ms=None):
        """Add a new distance in cm (``None`` = no data). Returns the level."""
        if now_ms is None:
            now_ms = time.ticks_ms()
        target = NONE
        if distance is None:
            last = self._samples[-1][1] if self._samples else None
            self._samples = []
            self.speed = 0.0
            if self.level == DANGER and last is not None and last <= self.LOST_NEAR_CM:
                target = CRASH
        else:
            if self._samples and abs(distance - self._samples[-1][1]) > self.MAX_STEP_CM:
                self._samples = []          # e.g. a hand put in from the side
            self._samples.append((now_ms, distance))
            if len(self._samples) > self.WINDOW:
                self._samples.pop(0)
            self.speed = self._fit_speed()
            if self.speed >= self.WARN_SPEED:
                ttc_ms = distance / self.speed * 1000
                if distance <= self.DANGER_CM:
                    target = DANGER
                elif ttc_ms <= self.WARN_TTC_MS:
                    target = WARNING
            if self.level >= DANGER and distance <= self.CRASH_CM:
                target = CRASH
        self._set(target, now_ms)
        return self.level

    def _set(self, target, now_ms):
        if target >= self.level:
            if target != NONE:
                self._since = now_ms        # condition still active
            self.level = target
            return
        hold = self.CRASH_HOLD_MS if self.level == CRASH else self.HOLD_MS
        if time.ticks_diff(now_ms, self._since) > hold:
            self.level = target
            self._since = now_ms
