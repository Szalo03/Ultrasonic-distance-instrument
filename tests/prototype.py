"""prototype.py - first prototype of the parking sensor (week 2).

A quick first test written in one file to check that the hardware works
together: one HC-SR04 sensor (blocking measurement with time_pulse_us), the
Nokia 5110 display (PCD8544 class, later moved to src/nokia5110.py), the
buzzer and the button. Shows the distance and a bar on the display, beeps
faster as the obstacle gets closer, short press of the button = mute.
Replaced by the final program in src/.

Author:  Marek Šádek
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import machine
import time
import framebuf

# ==========================================
# 1. NOKIA 5110 DISPLAY CLASS (PCD8544)
# MicroPython Nokia 5110 PCD8544 84x48 LCD driver
# https://github.com/mcauser/micropython-pcd8544
# ==========================================
class PCD8544(framebuf.FrameBuffer):
    def __init__(self, spi, cs, dc, rst):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = 84
        self.height = 48
        self.buffer = bytearray((self.height // 8) * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        
        self.command(0x21) # Extended instruction set
        self.command(0xBF) # Contrast
        self.command(0x04) # Temperature coefficient
        self.command(0x14) # Bias
        self.command(0x20) # Basic instruction set
        self.command(0x0C) # Normal display mode
        self.clear()
        self.show()

    def command(self, data):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def clear(self):
        self.fill(0)

    def show(self):
        self.command(0x40)
        self.command(0x80)
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(self.buffer)
        self.cs.value(1)

# ==========================================
# 2. HC-SR04 SENSOR FUNCTION
# ==========================================
def measure_distance(trig_pin, echo_pin):
    trig_pin.value(0)
    time.sleep_us(2)
    
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    
    try:
        pulse_time = machine.time_pulse_us(echo_pin, 1, 30000)
        if pulse_time > 0:
            return (pulse_time * 0.0343) / 2
    except OSError:
        pass
    return -1.0

# ==========================================
# 3. MAIN PROGRAM
# ==========================================
# Pin configuration (see Pin assignment in README)
# TRIG=2, ECHO=3 (via 1k/2k divider), CE=17, SCK=18, DIN=19, DC=20, RST=21, LIGHT=22,
# Buzzer_S=14, Button=15
trig = machine.Pin(2, machine.Pin.OUT)
echo = machine.Pin(3, machine.Pin.IN)

rst = machine.Pin(21, machine.Pin.OUT)
dc = machine.Pin(20, machine.Pin.OUT)
cs = machine.Pin(17, machine.Pin.OUT)
bl = machine.Pin(22, machine.Pin.OUT)
bl.value(1) # Backlight (1 = off, active low)

# Button to GND, internal pull-up (pressed = 0)
button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# Buzzer initialisation (PWM tone) on GP14
buzzer = machine.PWM(machine.Pin(14))
buzzer.freq(1000) # Tone frequency 1 kHz
buzzer.duty_u16(0) # Buzzer silent at start

# SPI display initialisation
spi = machine.SPI(0, baudrate=3200000, polarity=0, phase=0, 
                  sck=machine.Pin(18), mosi=machine.Pin(19))
lcd = PCD8544(spi, cs, dc, rst)

# Welcome screen
lcd.clear()
lcd.text("Radar s", 18, 10, 1)
lcd.text("buzzerem", 14, 25, 1)
lcd.show()
time.sleep(2)

# Variables for non-blocking beeping
last_beep_time = time.ticks_ms()
buzzer_is_on = False

# Button variables (mute)
muted = False
last_button = 1
last_press_time = time.ticks_ms()

while True:
    dist = measure_distance(trig, echo)
    current_time = time.ticks_ms()

    # Button: toggle mute on press (1 -> 0 transition), 200 ms debounce
    state = button.value()
    if last_button == 1 and state == 0:
        if time.ticks_diff(current_time, last_press_time) > 200:
            muted = not muted
            last_press_time = current_time
    last_button = state
    
    lcd.clear()
    lcd.text("Vzdalenost:", 0, 0, 1)
    
    if dist >= 0:
        lcd.text("{:.1f} cm".format(dist), 0, 15, 1)
        
        # Bar indicator (gets shorter as the distance decreases)
        bar_length = int(min(dist, 84))
        lcd.fill_rect(0, 30, bar_length, 8, 1) 
        
        # Buzzer beeping logic
        if dist < 10.0:
            # Critical distance: continuous tone
            buzzer.duty_u16(32768) # 50 % duty cycle for a loud tone
            buzzer_is_on = True
        elif dist < 50.0:
            # Normal distance: beep rate depends on distance
            # Interval: e.g. 40 cm = 400 ms pause, 10 cm = 100 ms pause
            beep_interval = int(dist * 10) 
            
            # Toggle the buzzer when the interval has elapsed
            if time.ticks_diff(current_time, last_beep_time) > beep_interval:
                buzzer_is_on = not buzzer_is_on
                if buzzer_is_on:
                    buzzer.duty_u16(32768) # Sound on
                else:
                    buzzer.duty_u16(0)     # Sound off
                last_beep_time = current_time
        else:
            # Safe distance (above 50 cm): silent
            buzzer.duty_u16(0)
            buzzer_is_on = False
            
    else:
        lcd.text("Mimo dosah", 0, 15, 1)
        buzzer.duty_u16(0) # Silent on measurement error

    if muted:
        buzzer.duty_u16(0) # Muted by the button
        lcd.text("MUTE", 0, 40, 1)

    lcd.show()
    time.sleep_ms(50)
