"""Minimal stand-in for the MicroPython ``framebuf`` module (for Sphinx only)."""
MONO_VLSB = 0


class FrameBuffer:
    """Drawing surface (does nothing on a PC)."""

    def __init__(self, *args):
        pass

    def __getattr__(self, name):
        return lambda *args, **kwargs: 0
