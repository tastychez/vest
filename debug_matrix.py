"""
Quick matrix diagnostic — run this standalone on the Pi.
Tests whether the MAX7219 is actually responding to SPI commands.
"""
import time

import board
import busio
import digitalio
from adafruit_max7219 import matrices

from config import matrix_brightness, matrix_clk_pin, matrix_cs_pin, matrix_mosi_pin

print(f"SPI pins  -> CLK={matrix_clk_pin}  MOSI={matrix_mosi_pin}  CS={matrix_cs_pin}")
print(f"Brightness -> {matrix_brightness}")

print("\n[1/4] Initializing SPI bus...")
spi = busio.SPI(
    clock=getattr(board, matrix_clk_pin),
    MOSI=getattr(board, matrix_mosi_pin),
)
cs = digitalio.DigitalInOut(getattr(board, matrix_cs_pin))
print("       SPI bus OK")

print("[2/4] Initializing MAX7219...")
matrix = matrices.Matrix8x8(spi, cs)
matrix.brightness(matrix_brightness)
print("       MAX7219 OK")

print("[3/4] Clearing matrix (all OFF)...")
matrix.fill(0)
matrix.show()
print("       -> Is the matrix OFF now? (wait 3s)")
time.sleep(3)

print("[4/4] Filling matrix (all ON)...")
matrix.fill(1)
matrix.show()
print("       -> Is the matrix ON now? (wait 3s)")
time.sleep(3)

print("\nNow blinking 5 times...")
for i in range(5):
    matrix.fill(0)
    matrix.show()
    time.sleep(0.3)
    matrix.fill(1)
    matrix.show()
    time.sleep(0.3)
    print(f"       blink {i + 1}/5")

print("\nClearing and cleaning up...")
matrix.fill(0)
matrix.show()
cs.deinit()
spi.deinit()
print("Done. Matrix should be OFF now.")
