"""Minimal stand-in for MicroPython ``uasyncio`` (for Sphinx only).
``run`` does not start the program, so importing main.py is harmless."""


def run(coro):
    coro.close()


def new_event_loop():
    pass
