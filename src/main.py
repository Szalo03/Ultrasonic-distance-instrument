"""main.py - main program of the ultrasonic parking sensor.

Creates all components, connects them and runs the application.
Saved on the Pico as main.py, so it starts automatically after power-on.

Connects all components and runs them as uasyncio tasks:

- measure_task: sensors are triggered alternately every 60 ms
- button_task:  button is checked every 20 ms, switches the modes
- buzzer_task:  buzzer is updated every 20 ms
- display_task: display is redrawn every 150 ms
- light_task:   hazard LEDs are updated every 50 ms

After power-on the device waits in STANDBY: display off,
buzzer and LEDs silent. A press of the button starts the application.

Modes:

- NORMAL:  distances, bars, beeping. Short press = mute, long press = SET.
- SET:     current distance blinks, buzzer silent. Long press = save it as
           the STOP distance. Short press = delete the saved STOP distance
           (or just go back if none is saved). Cancelled after 15 s.
- MESSAGE: "SAVED" / "DELETED" is shown for 1.5 s, then back to NORMAL.

When the STOP distance is reached, a big "STOP" is shown and the buzzer
plays a continuous tone. The STOP distance is stored in settings.json.

Rear collision warning (in NORMAL mode, see collision.py):

- WARNING: an obstacle approaches fast - the red hazard LEDs blink
- DANGER:  still fast and close - "PREPARE FOR CRASH" blinks, LEDs blink
           fast, alarm sound (also when muted)
- CRASH:   the obstacle reached the bumper - "CRASH" and CRASH_TEXT are
           shown for 5 s (any button press confirms it), LEDs keep blinking

Authors: Marek Šádek, Marek Gláser, Dávid Szalay
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import json
import time
import micropython
import uasyncio as asyncio
from machine import Pin, SPI

from nokia5110 import PCD8544
from ultrasonic import UltrasonicSensor
from buzzer import Buzzer, zone_of, SILENT
from button import Button
from led import Led
from collision import CollisionWarning, NONE, WARNING, DANGER, CRASH

micropython.alloc_emergency_exception_buf(100)

# ---------- pins (see Pin assignment in README) ----------
LEFT_TRIG, LEFT_ECHO = 2, 3
RIGHT_TRIG, RIGHT_ECHO = 12, 13
BUZZER_PIN = 14
BUTTON_PIN = 15
LCD_CE, LCD_SCK, LCD_DIN, LCD_DC, LCD_RST, LCD_LIGHT = 17, 18, 19, 20, 21, 22
HAZARD_PIN = 26          # both red LEDs, each with its own resistor

# ---------- settings ----------
MEASURE_MS = 60          # time for one sensor, the other one follows
SET_TIMEOUT_MS = 15_000  # SET mode is cancelled after this time
MESSAGE_MS = 1_500       # how long "SAVED" / "DELETED" is shown
BLINK_MS = 300           # blink half-period
SETTINGS_FILE = "settings.json"
CRASH_TEXT = "eCall 112"  # max 10 characters, e.g. "GAME OVER"

MODE_NORMAL, MODE_SET, MODE_MESSAGE = 0, 1, 2

# ---------- components ----------
left = UltrasonicSensor(LEFT_TRIG, LEFT_ECHO)
right = UltrasonicSensor(RIGHT_TRIG, RIGHT_ECHO)
buzzer = Buzzer(BUZZER_PIN)
button = Button(BUTTON_PIN)

spi = SPI(0, baudrate=3_200_000, polarity=0, phase=0,
          sck=Pin(LCD_SCK), mosi=Pin(LCD_DIN))
lcd = PCD8544(spi, Pin(LCD_CE, Pin.OUT), Pin(LCD_DC, Pin.OUT), Pin(LCD_RST, Pin.OUT),
              flip_text=True)   # display mounted upside down: text rotated 180 deg
backlight = Pin(LCD_LIGHT, Pin.OUT, value=1)   # active low: 1 = off, not used
hazard = Led(HAZARD_PIN)
collision = (CollisionWarning(), CollisionWarning())   # left, right


# ---------- STOP distance in flash ----------
def load_stop():
    """Read the saved STOP distance, or None if nothing is saved."""
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f).get("stop_cm")
    except (OSError, ValueError):
        return None


def save_stop(cm):
    """Write the STOP distance to flash (None = no STOP distance)."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"stop_cm": cm}, f)
    except OSError:
        print("Cannot save", SETTINGS_FILE)


# ---------- application state ----------
mode = MODE_NORMAL
mode_since = time.ticks_ms()
message = ""
stop_cm = load_stop()


def set_mode(new_mode, text=""):
    global mode, mode_since, message
    mode = new_mode
    mode_since = time.ticks_ms()
    message = text


def in_mode_ms():
    """Time spent in the current mode in ms."""
    return time.ticks_diff(time.ticks_ms(), mode_since)


def blink_on():
    """True / False alternating every BLINK_MS."""
    return (time.ticks_ms() // BLINK_MS) % 2 == 0


def closest(a, b):
    """Smaller of two distances, ignoring None."""
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


def stop_reached():
    """True when the STOP distance is set and reached by one of the sensors."""
    d = closest(left.distance, right.distance)
    return stop_cm is not None and d is not None and d <= stop_cm


def warning_level():
    """Highest collision warning level of both sensors (only in NORMAL mode)."""
    if mode != MODE_NORMAL:
        return NONE
    return max(collision[0].level, collision[1].level)


def blink(period_ms):
    """True / False alternating every period_ms."""
    return (time.ticks_ms() // period_ms) % 2 == 0


def fy(y, h=8, top=0, bottom=48):
    """Y position of a text line.

    With rotated text (lcd.flip_text) the lines of a text block between
    ``top`` and ``bottom`` are mirrored, so that they read in the right order
    when the display is turned upside down. ``h`` is the text height.
    """
    if lcd.flip_text:
        return top + bottom - y - h
    return y


def num_text(cm):
    """Distance as a whole number, or '---' when there is no data."""
    if cm is None:
        return "---"
    return str(int(cm + 0.5))


# ---------- drawing ----------
# Screen 84 x 48 px:
#   top:    left distance | "cm" | right distance
#   middle: bars above each half of the bumper - they show the free space:
#           far away all 5 are lit, they disappear as the obstacle gets closer
#   bottom: rear bumper seen from above, MUTE inside
#   STOP:   big text over the middle when the STOP distance is reached
BAR_WIDTHS = (10, 16, 22, 28, 34)  # nearest bar (at the bumper) ... top bar
LEFT_X, RIGHT_X = 23, 61           # centre of the left / right bumper half
BAR_Y0, BAR_STEP, BAR_H = 33, 5, 4
BAR_OUTLINES = True               # draw the other bars as thin 1 px lines
BUMPER = ((3, 44), (6, 41), (12, 39), (22, 38), (62, 38), (72, 39), (78, 41), (81, 44))
# left tail light (y, x_from, x_to): a wedge under the bumper corner, 1 px gap
# from the bumper line; the right light is mirrored (x -> 84 - x)
TAIL_LIGHT = ((42, 12, 17), (43, 9, 16), (44, 7, 14), (45, 7, 11))
bar_zones = [SILENT, SILENT]       # zone of each side, for hysteresis


def draw_bumper():
    for dy in (0, 1):                               # 2 px thick line
        for (x0, y0), (x1, y1) in zip(BUMPER, BUMPER[1:]):
            lcd.line(x0, y0 + dy, x1, y1 + dy, 1)
    lcd.fill_rect(3, 44, 2, 4, 1)                   # left side
    lcd.fill_rect(80, 44, 2, 4, 1)                  # right side
    for y, x0, x1 in TAIL_LIGHT:                    # tail lights
        lcd.hline(x0, y, x1 - x0 + 1, 1)
        lcd.hline(84 - x1, y, x1 - x0 + 1, 1)


def draw_bars(side, cm):
    """Bars of one side (0 = left, 1 = right).

    Only the bar at the obstacle's distance is filled: the bar nearest to the
    bumper for zone 0 ... the top bar for zone 4. Above 100 cm no bar is
    filled. The other bars are thin 1 px lines (if BAR_OUTLINES).
    """
    zone = SILENT
    if cm is not None:
        bar_zones[side] = zone_of(cm, bar_zones[side])
        zone = bar_zones[side]
    cx = RIGHT_X if side else LEFT_X
    for i, w in enumerate(BAR_WIDTHS):
        x, y = cx - w // 2, BAR_Y0 - i * BAR_STEP
        if i == zone:
            lcd.fill_rect(x, y, w, BAR_H, 1)
        elif BAR_OUTLINES:
            lcd.hline(x, y + BAR_H // 2, w, 1)      # thin 1 px line


def draw_normal():
    ltext = num_text(left.distance)
    rtext = num_text(right.distance)
    lcd.text(ltext, 0, 0, 1)
    lcd.text(rtext, 84 - 8 * len(rtext), 0, 1)      # right-aligned
    lcd.text("cm", 34, 0, 1)
    draw_bars(0, left.distance)
    draw_bars(1, right.distance)
    draw_bumper()
    if buzzer.muted:
        lcd.text("MUTE", 26, 40 if lcd.flip_text else 41, 1)  # rotated glyph sits 1 px lower
    if warning_level() == DANGER:
        # blinking inverted box, more important than STOP
        inv = blink(BLINK_MS)
        lcd.fill_rect(4, 10, 76, 21, 1 if inv else 0)
        lcd.rect(4, 10, 76, 21, 1)
        lcd.text("PREPARE", 14, fy(12, 8, 10, 31), 0 if inv else 1)
        lcd.text("FOR CRASH", 6, fy(21, 8, 10, 31), 0 if inv else 1)
    elif stop_reached():
        lcd.fill_rect(4, 10, 76, 21, 0)             # clear space under the text
        lcd.rect(4, 10, 76, 21, 1)
        lcd.big_text("STOP", 10, 13)


def draw_crash():
    if blink(BLINK_MS):
        lcd.big_text("CRASH", 2, fy(6, 16))
    lcd.text(CRASH_TEXT, 42 - 4 * len(CRASH_TEXT), fy(30), 1)   # centred


def draw_set():
    lcd.text("SET STOP", 10, fy(0), 1)
    d = closest(left.distance, right.distance)
    if blink_on():
        t = num_text(d) + ("cm" if d is not None else "")
        lcd.big_text(t, 42 - 8 * len(t), fy(12, 16))  # centred, 16 px high
    lcd.text("hold:save", 6, fy(32), 1)
    if stop_cm is not None:
        lcd.text("click:del", 6, fy(40), 1)
    else:
        lcd.text("click:back", 2, fy(40), 1)


def draw_message():
    if message == "SAVED":
        lcd.big_text("SAVED", 2, fy(8, 16))
        t = num_text(stop_cm) + "cm"
    else:
        lcd.big_text("STOP", 10, fy(8, 16))
        t = "deleted"
    lcd.text(t, 42 - 4 * len(t), fy(32), 1)         # centred


# ---------- tasks ----------
async def measure_task():
    sensors = (left, right)
    i = 0
    while True:
        sensor = sensors[i]
        sensor.trigger()
        await asyncio.sleep_ms(MEASURE_MS)
        sensor.update()
        collision[i].add(sensor.distance)           # speed and warning level
        i = 1 - i


async def button_task():
    global stop_cm
    while True:
        event = button.update()
        if warning_level() == CRASH:
            if event:                               # any press confirms the crash
                collision[0].reset()
                collision[1].reset()
        elif mode == MODE_NORMAL:
            if event == "short":
                buzzer.toggle_mute()
            elif event == "long":
                set_mode(MODE_SET)
        elif mode == MODE_SET:
            if event == "long":
                d = closest(left.distance, right.distance)
                if d is not None:                   # save only a valid distance
                    stop_cm = round(d, 1)
                    save_stop(stop_cm)
                    set_mode(MODE_MESSAGE, "SAVED")
            elif event == "short":
                if stop_cm is not None:             # delete the saved value
                    stop_cm = None
                    save_stop(None)
                    set_mode(MODE_MESSAGE, "DELETED")
                else:
                    set_mode(MODE_NORMAL)           # nothing saved: just back
            elif in_mode_ms() > SET_TIMEOUT_MS:
                set_mode(MODE_NORMAL)               # timeout, nothing changed
        elif mode == MODE_MESSAGE:
            if in_mode_ms() > MESSAGE_MS:
                set_mode(MODE_NORMAL)
        await asyncio.sleep_ms(20)


async def buzzer_task():
    while True:
        level = warning_level()
        if level == DANGER:
            # alarm: two alternating tones, plays also when muted
            buzzer.tone(600 if blink(150) else 800)
        elif level == CRASH or mode != MODE_NORMAL:
            buzzer.off()                            # silent in SET / MESSAGE
        else:
            buzzer.update(closest(left.distance, right.distance), stop_reached())
        await asyncio.sleep_ms(20)


async def light_task():
    while True:
        level = warning_level()
        if level == WARNING or level == CRASH:
            hazard.set(blink(400))                  # like hazard lights
        elif level == DANGER:
            hazard.set(blink(100))                  # fast
        else:
            hazard.off()
        await asyncio.sleep_ms(50)


async def display_task():
    while True:
        lcd.clear()
        if warning_level() == CRASH:
            draw_crash()
        elif mode == MODE_NORMAL:
            draw_normal()
        elif mode == MODE_SET:
            draw_set()
        else:
            draw_message()
        lcd.show()
        await asyncio.sleep_ms(150)


async def wait_for_start():
    """STANDBY after power-on: everything off until the button is pressed."""
    lcd.clear()
    lcd.show()
    while button.update() is None:                  # short or long press
        await asyncio.sleep_ms(20)


async def main():
    await wait_for_start()
    lcd.clear()
    lcd.big_text("PARK", 10, fy(8, 16))
    lcd.text("sensor", 18, fy(32), 1)
    lcd.show()
    await asyncio.sleep_ms(1_500)
    asyncio.create_task(measure_task())
    asyncio.create_task(button_task())
    asyncio.create_task(buzzer_task())
    asyncio.create_task(display_task())
    asyncio.create_task(light_task())
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
finally:
    # after Stop / Ctrl+C in Thonny: silence the buzzer and clear the display
    buzzer.off()
    hazard.off()
    lcd.clear()
    lcd.show()
    asyncio.new_event_loop()
