import atexit

import board
import busio
import digitalio
from adafruit_max7219 import matrices

from config import (
    matrix_brightness,
    matrix_clk_pin,
    matrix_cs_pin,
    matrix_mosi_pin,
)

# --- SPI bus (CLK + MOSI pulled from config.json) ---
spi = busio.SPI(
    clock=getattr(board, matrix_clk_pin),
    MOSI=getattr(board, matrix_mosi_pin),
)

# --- Chip-select pin (CS pulled from config.json) ---
cs = digitalio.DigitalInOut(getattr(board, matrix_cs_pin))

# --- 8x8 LED matrix (Elegoo MAX7219 Dot Matrix Module V02) ---
matrix = matrices.Matrix8x8(spi, cs)
matrix.brightness(matrix_brightness)  # 0 (dimmest) -> 15 (brightest)
matrix.fill(0)  # clear display on startup
matrix.show()


# --- Cleanup ----------------------------------------------------------------
# Registered with atexit so the SPI bus and CS GPIO are always released when
# the process exits normally (including Ctrl+C / KeyboardInterrupt).
# This prevents the lgpio "GPIO busy" error on the next run.


def _cleanup():
    try:
        matrix.fill(0)
        matrix.show()
    except Exception:
        pass
    try:
        cs.deinit()
    except Exception:
        pass
    try:
        spi.deinit()
    except Exception:
        pass


atexit.register(_cleanup)


# --- Public API -------------------------------------------------------------


def display_text(text, x=0, y=0):
    """Render a short string on the matrix at position (x, y)."""
    matrix.fill(0)
    matrix.text(text, x, y)
    matrix.show()


def display_pixel(x, y, on=True):
    """Light or clear a single pixel at (x, y)."""
    matrix.pixel(x, y, int(on))
    matrix.show()


def fill_all():
    """Turn on every LED in the matrix (danger / alert state)."""
    matrix.fill(1)
    matrix.show()


def clear():
    """Turn off all LEDs."""
    matrix.fill(0)
    matrix.show()


def set_brightness(level):
    """
    Change display brightness at runtime.
    level: int 0 (dimmest) to 15 (brightest)
    """
    matrix.brightness(max(0, min(15, level)))
