import time

import board
import neopixel

import led_matrix
from cnt5 import is_detected as cnt5_detected
from config import neopixel_count, neopixel_pin
from fc22sbx import fc22
from flyingfish import flyingfish

# ── NeoPixel status LED ────────────────────────────────────────────────────────
# Pin and count are set in config.json; change them there, not here.
pixels = neopixel.NeoPixel(
    getattr(board, neopixel_pin),
    neopixel_count,
    brightness=0.3,
    auto_write=False,
)

RED = (255, 0, 0)
GREEN = (0, 255, 0)


# ── Sensor helpers ─────────────────────────────────────────────────────────────


def any_sensor_triggered():
    """
    Return True if at least one sensor reports a detection event.

    Sensor polarity
    ---------------
    FC-22 (smoke / gas)     – active LOW: DO pulls LOW when gas detected
    Flying Fish (moisture)  – active LOW: DO pulls LOW when water detected
    CNT5 (IR obstacle)      – active LOW: handled inside is_detected()
    """
    fc22_alert = not fc22.value  # LOW  → smoke / gas present
    fish_alert = not flyingfish.value  # LOW  → moisture present
    cnt5_alert = cnt5_detected()  # True → obstacle in range
    return fc22_alert or fish_alert or cnt5_alert


# ── Output helpers ─────────────────────────────────────────────────────────────


def show_alert():
    """Red NeoPixel + exclamation mark on the matrix → danger."""
    pixels.fill(RED)
    pixels.show()
    led_matrix.display_text("!")


def show_safe():
    """Green NeoPixel + blank matrix → all clear."""
    pixels.fill(GREEN)
    pixels.show()
    led_matrix.clear()


# ── Startup ────────────────────────────────────────────────────────────────────
show_safe()

# ── Main loop ─────────────────────────────────────────────────────────────────
# Track the previous state so we only redraw when something actually changes,
# avoiding unnecessary SPI writes and LED flicker.
_last_triggered = None

while True:
    triggered = any_sensor_triggered()

    if triggered != _last_triggered:
        if triggered:
            show_alert()
        else:
            show_safe()
        _last_triggered = triggered

    time.sleep(0.1)  # poll every 100 ms
