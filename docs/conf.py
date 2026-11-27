"""Sphinx configuration for the Ultrasonic Parking Sensor documentation.

Build (from the repository root):
    pip install -r docs/requirements.txt
    sphinx-build -b html docs docs/_build/html
or inside the docs folder: make html (Linux, macOS) / make.bat html (Windows).
"""
import os
import sys
import time

# The source code is in ../src. MicroPython-only modules (machine, framebuf,
# micropython, uasyncio) do not exist on a PC, so _stubs contains minimal
# stand-ins that do nothing; they are used only to build the documentation.
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("_stubs"))

# MicroPython time functions used by the code at import time
for name, func in (("ticks_ms", lambda: 0), ("ticks_us", lambda: 0),
                   ("ticks_diff", lambda a, b: a - b),
                   ("sleep_ms", lambda ms: None), ("sleep_us", lambda us: None)):
    if not hasattr(time, name):
        setattr(time, name, func)

project = "Ultrasonic Parking Sensor"
author = "Marek Šádek, Marek Gláser, Dávid Szalay"
copyright = "2026, " + author

extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode"]
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "undoc-members": False}

templates_path = []
exclude_patterns = ["_build", "_stubs"]
html_theme = "alabaster"


def _split_header(app, what, name, obj, options, lines):
    """Show the "Project:" line of the file header as its own paragraph."""
    for i in range(len(lines) - 1, 0, -1):
        if lines[i].startswith("Project:") and lines[i - 1].strip():
            lines.insert(i, "")


def setup(app):
    app.connect("autodoc-process-docstring", _split_header)
