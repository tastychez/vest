import board
import digitalio

from config import fc22_pin

# Configure Digital Input using pin from config.json
fc22 = digitalio.DigitalInOut(getattr(board, fc22_pin))
fc22.direction = digitalio.Direction.INPUT
fc22.pull = digitalio.Pull.UP
