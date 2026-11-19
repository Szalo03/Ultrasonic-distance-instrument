"""test_display.py - test of the Nokia 5110 display.

Expected result on the display, repeating forever:

    Display
    test
    [a frame across the whole width that fills up from left to right]

- The bar grows by 4 px every 0.1 s, a full cycle takes about 2 s.
- Text must be sharp and readable. If the display is too dark or too light,
  change the contrast: PCD8544(..., contrast=0xB0) (range 0x80-0xFF).

Run it from Thonny; the class files from src/ must be saved on the Pico.

Author:  Marek Gláser
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
from machine import Pin, SPI
from nokia5110 import PCD8544

spi = SPI(0, baudrate=3_200_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
lcd = PCD8544(spi, Pin(17, Pin.OUT), Pin(20, Pin.OUT), Pin(21, Pin.OUT))  # CE, DC, RST

while True:
    for width in range(0, 84, 4):
        lcd.clear()                          # empty buffer
        lcd.text("Display", 0, 0, 1)         # 1st line, top left
        lcd.text("test", 0, 12, 1)           # 2nd line
        lcd.rect(0, 26, 84, 10, 1)           # frame over the whole width
        lcd.fill_rect(0, 26, width, 10, 1)   # bar inside, grows each step
        lcd.show()                           # send everything to the display
        time.sleep_ms(100)
