"""Minimal stand-in for the MicroPython ``machine`` module, only so that
Sphinx can import the source code on a PC. It does nothing."""


class Pin:
    OUT, IN, PULL_UP, IRQ_RISING, IRQ_FALLING = 1, 0, 1, 1, 2

    def __init__(self, *args, **kwargs):
        pass

    def value(self, v=None):
        return 0

    def irq(self, *args, **kwargs):
        pass


class PWM:
    def __init__(self, *args, **kwargs):
        pass

    def freq(self, f):
        pass

    def duty_u16(self, d):
        pass


class SPI:
    def __init__(self, *args, **kwargs):
        pass

    def write(self, data):
        pass
