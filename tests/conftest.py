"""
conftest.py
===========
Runs before any test module is imported by pytest.

Responsibilities
----------------
1. Add the project root to sys.path so source files are importable.
2. Change CWD to the project root so `open("config.json")` in config.py works.
3. Inject MagicMock stubs for every CircuitPython-only package into sys.modules
   so that `import board`, `import digitalio`, etc. don't raise ImportError on
   a standard desktop Python install.
"""

import os
import sys
from unittest.mock import MagicMock

# ── 1. Project root ────────────────────────────────────────────────────────────
# tests/conftest.py  →  parent  →  project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Change working directory so config.py can open("config.json") successfully.
# This must happen at module level (not inside a fixture) because test files
# may execute `import <source_module>` at collection time, before any fixture runs.
os.chdir(ROOT)

# ── 2. Hardware stubs ──────────────────────────────────────────────────────────

# board ── one distinct mock sentinel per pin used across the project ----------
board = MagicMock(name="board")
for _pin in ("D4", "D5", "D6", "D17", "SCK", "MOSI"):
    setattr(board, _pin, MagicMock(name=f"board.{_pin}"))

# digitalio -------------------------------------------------------------------
digitalio = MagicMock(name="digitalio")
digitalio.Direction.INPUT = "INPUT"
digitalio.Direction.OUTPUT = "OUTPUT"

# busio -----------------------------------------------------------------------
busio = MagicMock(name="busio")

# adafruit_max7219 + adafruit_max7219.matrices --------------------------------
matrices = MagicMock(name="adafruit_max7219.matrices")
adafruit_max7219 = MagicMock(name="adafruit_max7219")
adafruit_max7219.matrices = matrices  # `from adafruit_max7219 import matrices`

# ── 3. Inject into sys.modules ─────────────────────────────────────────────────
# Use plain assignment (not setdefault) so re-runs of conftest always use
# these exact objects.
sys.modules["board"] = board
sys.modules["digitalio"] = digitalio
sys.modules["busio"] = busio
sys.modules["adafruit_max7219"] = adafruit_max7219
sys.modules["adafruit_max7219.matrices"] = matrices
