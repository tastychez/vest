import time

import led_matrix
from config import flash_interval
from dht11 import read as dht11_read
from fc22sbx import fc22, fc22_2
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
    fc22_raw = fc22.value
    fc22_2_raw = fc22_2.value
    fish_raw = flyingfish.value
    fc22_alert = not fc22_raw       # LOW → smoke / gas present
    fc22_2_alert = not fc22_2_raw   # LOW → smoke / gas present (sensor 2)
    fish_alert = not fish_raw       # LOW → moisture present
    return fc22_raw, fc22_2_raw, fish_raw, fc22_alert, fc22_2_alert, fish_alert


# ── Startup ────────────────────────────────────────────────────────────────────
led_matrix.clear()

# ── Main loop ─────────────────────────────────────────────────────────────────
_flash_on = False
_last_toggle = time.monotonic()
_last_triggered = False
_last_print = time.monotonic()

DEBUG_INTERVAL = 1.0

while True:
    fc22_raw, fc22_2_raw, fish_raw, fc22_alert, fc22_2_alert, fish_alert = any_sensor_triggered()
    triggered = fc22_2_alert or fish_alert

    now = time.monotonic()
    if now - _last_print >= DEBUG_INTERVAL:
        print(
            f"[DEBUG] FC-22#1  raw={fc22_raw}  alert={fc22_alert} | "
            f"FC-22#2  raw={fc22_2_raw}  alert={fc22_2_alert} | "
            f"FlyingFish  raw={fish_raw}  alert={fish_alert} | "
            f"triggered={triggered}"
        )
        _last_print = now

    if triggered:
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
