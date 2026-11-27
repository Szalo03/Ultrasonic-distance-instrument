Getting started
===============

1. The Pico W needs the MicroPython firmware (on our lab board it was already
   installed). If it is missing, download the firmware for the Raspberry Pi
   Pico W (`download <https://micropython.org/download/RPI_PICO_W/>`_), hold
   BOOTSEL, connect USB and copy the ``.uf2`` file to the ``RPI-RP2`` drive.
2. Wire the components according to the schematic and the pin assignment in the
   `README <https://github.com/Szalo03/Ultrasonic-distance-instrument>`_.
3. Copy all files from the :file:`src` folder to the Pico, e.g. in Thonny:
   open each file and use *File → Save as → Raspberry Pi Pico* with the same
   name.
4. Reset the Pico (reconnect USB, or press Ctrl+D in the Thonny shell).
   :file:`main.py` starts automatically.

Only built-in MicroPython modules are needed: ``machine``, ``time``,
``framebuf``, ``uasyncio``, ``json``, ``micropython``.

The tests in the :file:`tests` folder can be run from Thonny (*Run*) with the
class files saved on the Pico. The expected result is described at the top of
each test file.

Building this documentation
---------------------------

On a PC with Python 3, from the repository root::

   pip install -r docs/requirements.txt
   sphinx-build -b html docs docs/_build/html

or inside the :file:`docs` folder: ``make html`` (Linux, macOS) or
``make.bat html`` (Windows). The result is in :file:`docs/_build/html`.

The folder :file:`docs/_stubs` contains empty stand-ins of the MicroPython-only
modules (``machine``, ``framebuf``, ``micropython``, ``uasyncio``), so that the
source code can be imported on a PC. They are used only for the documentation.
