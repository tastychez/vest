import time

import board
import digitalio

from config import flying_fish_pin

flyingfish = digitalio.DigitalInOut(
    getattr(board, flying_fish_pin)
)  # Pin set via config.json
flyingfish.direction = digitalio.Direction.INPUT
flyingfish.pull = digitalio.Pull.UP
