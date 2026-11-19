"""nokia5110.py - driver for the Nokia 5110 (PCD8544) display.

Contains the PCD8544 class: SPI communication with the display, drawing
through framebuf and enlarged text (big_text) for STOP / CRASH messages.

Authors: Marek Šádek (original class in tests/prototype.py),
         Marek Gláser (documentation, big_text)
Project: Ultrasonic parking sensor (Raspberry Pi Pico W, MicroPython)
         https://github.com/Szalo03/Ultrasonic-distance-instrument
"""
import time
import framebuf


class PCD8544(framebuf.FrameBuffer):
    """Nokia 5110 LCD, 84 x 48 px, connected over SPI.

    The class is a ``framebuf.FrameBuffer``, so all its drawing methods
    (``text``, ``fill_rect``, ``rect``, ``line`` ...) can be used. Nothing is
    sent to the display until :meth:`show` is called.

    :param spi: configured ``machine.SPI`` object
    :param cs: chip enable pin (CE), ``machine.Pin`` output
    :param dc: data / command pin, ``machine.Pin`` output
    :param rst: reset pin, ``machine.Pin`` output
    :param contrast: contrast value 0x80-0xFF
    """

    WIDTH = 84
    HEIGHT = 48

    def __init__(self, spi, cs, dc, rst, contrast=0xBF):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.contrast = contrast
        self.buffer = bytearray((self.HEIGHT // 8) * self.WIDTH)
        super().__init__(self.buffer, self.WIDTH, self.HEIGHT, framebuf.MONO_VLSB)
        self.cs.value(1)
        self.init_display()

    def init_display(self):
        """Reset the controller and send the initialisation commands."""
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        self.command(0x21)           # extended instruction set
        self.command(self.contrast)  # contrast (Vop)
        self.command(0x04)           # temperature coefficient
        self.command(0x14)           # bias 1:48
        self.command(0x20)           # basic instruction set
        self.command(0x0C)           # normal display mode
        self.clear()
        self.show()

    def command(self, data):
        """Send one command byte."""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def clear(self):
        """Clear the frame buffer (call :meth:`show` to apply)."""
        self.fill(0)

    def big_text(self, text, x, y, scale=2, c=1):
        """Draw text enlarged ``scale`` times (the built-in font is 8 x 8 px).

        :param text: string to draw
        :param x: left edge in px
        :param y: top edge in px
        :param scale: enlargement factor, 2 = 16 x 16 px characters
        :param c: colour, 1 = black pixels
        """
        w = 8 * len(text)
        small = framebuf.FrameBuffer(bytearray(w), w, 8, framebuf.MONO_VLSB)
        small.text(text, 0, 0, 1)
        for sy in range(8):
            for sx in range(w):
                if small.pixel(sx, sy):
                    self.fill_rect(x + sx * scale, y + sy * scale, scale, scale, c)

    def show(self):
        """Send the whole frame buffer to the display."""
        self.command(0x40)  # Y address 0
        self.command(0x80)  # X address 0
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(self.buffer)
        self.cs.value(1)
