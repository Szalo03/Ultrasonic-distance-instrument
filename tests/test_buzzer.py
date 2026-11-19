"""test_buzzer.py - test of the passive buzzer.

Expected result (about 15 s in total), the Thonny shell shows each step:

1. Four tones, each 0.4 s, getting higher: 350, 500, 750, 1000 Hz.
2. 1 s silence.
3. Beeping for simulated distances, each for 2 s. The sound changes in
   steps (zones), inside one zone it stays the same:
   - 120 cm: silent (above 100 cm)
   - 90 cm:  slow beeping, 500 Hz        (zone 71-100 cm)
   - 60 cm:  faster, 550 Hz              (zone 51-70 cm)
   - 45 cm:  faster, 600 Hz              (zone 36-50 cm)
   - 30 cm:  fast beeping, 650 Hz        (zone 26-35 cm)
   - 20 cm:  continuous tone, 700 Hz     (25 cm and closer)
4. Silence at the end.

Run it from Thonny; the class files from src/ must be saved on the Pico.

Author:  Marek Gláser
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from buzzer import Buzzer

bz = Buzzer(14)    # S = GP14

# 1. tone check
for f in (350, 500, 750, 1000):
    print("tone", f, "Hz")
    bz.tone(f)
    time.sleep_ms(400)
bz.off()
time.sleep(1)      # 2. silence

# 3. beeping as in the parking sensor
for d in (120, 90, 60, 45, 30, 20):
    print("distance", d, "cm")
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < 2000:
        bz.update(d)       # picks the zone: silent / beeping / continuous tone
        time.sleep_ms(20)
bz.off()           # 4. silence
print("done")
