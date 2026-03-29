import time

import led_matrix
from dht11 import read as dht11_read
from fc22sbx import fc22
from flyingfish import flyingfish

# ── Sensor helpers ─────────────────────────────────────────────────────────────


def any_sensor_triggered():
    """
    Return True if at least one *gas/air* sensor reports a detection event.

    Only the two gas sensors drive the LED matrix.  The DHT11 is read
    separately for informational purposes (temperature / humidity logging)
    but does NOT trigger the alert state.

    Sensor polarity
    ---------------
    FC-22 (smoke / gas)    – active LOW: DO pulls LOW when gas detected
    Flying Fish (moisture) – active LOW: DO pulls LOW when water detected
    """
    fc22_alert = not fc22.value  # LOW → smoke / gas present
    fish_alert = not flyingfish.value  # LOW → moisture present
    return fc22_alert or fish_alert


# ── Output helpers ─────────────────────────────────────────────────────────────


def show_alert():
    """
    All LEDs ON = danger  (red equivalent on the monochrome matrix).
    A fully-lit 8×8 matrix is the brightest, most eye-catching state.
    """
    led_matrix.fill_all()


def show_safe():
    """
    All LEDs OFF = all clear  (green equivalent on the monochrome matrix).
    A blank display means no sensor has fired.
    """
    led_matrix.clear()


# ── Startup ────────────────────────────────────────────────────────────────────
show_safe()

# ── Main loop ─────────────────────────────────────────────────────────────────
# _last_triggered tracks the previous sensor state so we only push a new frame
# to the matrix when the state actually changes, avoiding unnecessary SPI writes
# and visible flicker.
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
