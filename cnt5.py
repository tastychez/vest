import board
import digitalio

from config import cnt5_pin

# --- CNT5 Infrared Sensor ---
# Digital output sensor: HIGH = no obstacle / no detection
#                        LOW  = obstacle or IR reflection detected
cnt5 = digitalio.DigitalInOut(getattr(board, cnt5_pin))
cnt5.direction = digitalio.Direction.INPUT


def is_detected():
    """Return True when the CNT5 sensor detects an obstacle/IR reflection."""
    return not cnt5.value  # Active LOW: sensor pulls pin LOW on detection
