"""test_buzzer.py - test of the passive buzzer.

Expected result (about 16 s in total), the Thonny shell shows each step:

1. The tone (440 Hz) for 1 s, then 1 s silence.
2. Beeping for simulated distances, each for 2 s. The tone and the beep
   length stay the same, only the pause gets shorter smoothly:
   - 120 cm: silent (above 100 cm)
   - 100 cm: slow beeping, pause 800 ms
   - 70 cm:  pause about 570 ms
   - 40 cm:  pause about 340 ms
   - 20 cm:  pause about 190 ms
   - 10 cm:  fast beeping, pause about 115 ms
   - 6 cm:   continuous tone (8 cm and closer)
3. Silence at the end, the shell prints "done".

Run it from Thonny; the class files from src/ must be saved on the Pico.

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython),
https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from buzzer import Buzzer

bz = Buzzer(14)    # S = GP14

# 1. tone check
print("tone", bz.TONE_HZ, "Hz")
bz.tone(bz.TONE_HZ)
time.sleep(1)
bz.off()
time.sleep(1)

# 2. beeping as in the parking sensor
for d in (120, 100, 70, 40, 20, 10, 6):
    print("distance", d, "cm, pause", bz.pause_ms(d), "ms")
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < 2000:
        bz.update(d)       # silent / beeping / continuous tone
        time.sleep_ms(20)
bz.off()           # 3. silence
print("done")
