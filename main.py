import time

import led_matrix
from config import flash_interval
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


# ── Startup ────────────────────────────────────────────────────────────────────
led_matrix.clear()

# ── Main loop ─────────────────────────────────────────────────────────────────
_flash_on = False
_last_toggle = time.monotonic()
_last_triggered = False

while True:
    triggered = any_sensor_triggered()

    if triggered:
        now = time.monotonic()
        if now - _last_toggle >= flash_interval:
            _flash_on = not _flash_on
            if _flash_on:
                led_matrix.fill_all()
            else:
                led_matrix.clear()
            _last_toggle = now
    elif _last_triggered:
        led_matrix.clear()
        _flash_on = False

    _last_triggered = triggered
    time.sleep(0.05)
