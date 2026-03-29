"""
test_led_matrix.py
==================
Tests for led_matrix.py — Elegoo MAX7219 8×8 dot-matrix display.

Architecture notes
------------------
* led_matrix.py executes real hardware-setup code at import time (SPI init,
  DigitalInOut, Matrix8x8 constructor, brightness/fill/show calls).
* conftest.py has already injected MagicMock stubs for every CircuitPython
  package and set CWD to the project root, so the module-level
  `import led_matrix` below works on a standard desktop Python install.
* The initialisation state (SPI call args, brightness, fill, show) is
  snapshotted into _INIT immediately after the import, before any fixture
  can reset the mocks.
* An autouse per-test fixture resets the matrix mock's call history between
  tests so function tests are fully independent.
"""

import sys
from unittest.mock import call

import pytest

# ── Retrieve the stubs injected by conftest.py ────────────────────────────────
mock_board = sys.modules["board"]
mock_digitalio = sys.modules["digitalio"]
mock_busio = sys.modules["busio"]
mock_matrices = sys.modules["adafruit_max7219.matrices"]

# ── One-time module import ────────────────────────────────────────────────────
# Reset call history on every hardware stub so we see only the calls made by
# led_matrix.py itself, not by any earlier import or test run.
for _mod_name in ("led_matrix", "config"):
    sys.modules.pop(_mod_name, None)

mock_digitalio.reset_mock()
mock_digitalio.Direction.INPUT = "INPUT"
mock_digitalio.Direction.OUTPUT = "OUTPUT"
mock_busio.reset_mock()
mock_matrices.reset_mock()

import led_matrix  # noqa: E402  – intentionally after sys.modules manipulation

# ── Snapshot init state ───────────────────────────────────────────────────────
# Captured as plain Python objects so they survive any later reset_mock() calls.
_MATRIX = led_matrix.matrix  # alias: mock_matrices.Matrix8x8.return_value

_INIT = {
    # calls made on the matrix object during module startup
    "brightness_calls": list(_MATRIX.brightness.call_args_list),
    "fill_calls": list(_MATRIX.fill.call_args_list),
    "show_count": _MATRIX.show.call_count,
    # hardware-level call details (stored before any reset can clear them)
    "spi_kwargs": dict(mock_busio.SPI.call_args.kwargs),
    "cs_call": mock_digitalio.DigitalInOut.call_args,  # call(board.D5)
    "matrix8x8_call": mock_matrices.Matrix8x8.call_args,  # call(spi, cs)
}


# ── Per-test fixture ──────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_matrix_calls():
    """
    Clear the matrix mock's call history before every test so that assertions
    in function tests see only the calls made by that one test.

    Init tests are unaffected because they read from _INIT (a snapshot taken
    at collection time, before any test runs), not from the live mock.
    """
    _MATRIX.reset_mock()
    yield


# ── Initialisation: SPI bus ───────────────────────────────────────────────────


class TestSPIInit:
    """busio.SPI is constructed with the pins declared in config.json."""

    def test_spi_clock_pin_is_sck(self):
        assert _INIT["spi_kwargs"]["clock"] is mock_board.SCK

    def test_spi_mosi_pin_is_mosi(self):
        assert _INIT["spi_kwargs"]["MOSI"] is mock_board.MOSI


# ── Initialisation: chip-select pin ──────────────────────────────────────────


class TestCSPinInit:
    """The CS DigitalInOut is constructed with the board pin from config.json."""

    def test_cs_uses_d5_pin(self):
        assert _INIT["cs_call"] == call(mock_board.D5)


# ── Initialisation: Matrix8x8 object ─────────────────────────────────────────


class TestMatrix8x8Init:
    """Matrix8x8 is constructed with the SPI bus object and CS object."""

    def test_matrix8x8_receives_spi_object(self):
        args, _ = _INIT["matrix8x8_call"]
        assert args[0] is mock_busio.SPI.return_value

    def test_matrix8x8_receives_cs_object(self):
        args, _ = _INIT["matrix8x8_call"]
        assert args[1] is mock_digitalio.DigitalInOut.return_value


# ── Initialisation: startup sequence ─────────────────────────────────────────


class TestStartupSequence:
    """On import the display is initialised: brightness set, cleared, shown."""

    def test_brightness_applied_on_startup(self):
        """brightness() is called with the value from config.json (5)."""
        assert call(5) in _INIT["brightness_calls"]

    def test_fill_zero_called_on_startup(self):
        """fill(0) clears every LED on startup."""
        assert call(0) in _INIT["fill_calls"]

    def test_show_called_on_startup(self):
        """show() pushes the cleared frame to the physical display."""
        assert _INIT["show_count"] >= 1


# ── display_text() ────────────────────────────────────────────────────────────


class TestDisplayText:
    def test_clears_display_before_writing(self):
        led_matrix.display_text("A")
        _MATRIX.fill.assert_called_once_with(0)

    def test_renders_text_at_default_position(self):
        led_matrix.display_text("Hi")
        _MATRIX.text.assert_called_once_with("Hi", 0, 0)

    def test_renders_text_at_custom_x(self):
        led_matrix.display_text("X", x=3)
        _MATRIX.text.assert_called_once_with("X", 3, 0)

    def test_renders_text_at_custom_y(self):
        led_matrix.display_text("Y", y=4)
        _MATRIX.text.assert_called_once_with("Y", 0, 4)

    def test_renders_text_at_custom_xy(self):
        led_matrix.display_text("Z", x=2, y=3)
        _MATRIX.text.assert_called_once_with("Z", 2, 3)

    def test_calls_show_after_writing(self):
        led_matrix.display_text("!")
        _MATRIX.show.assert_called_once()

    def test_call_order_fill_text_show(self):
        """Operations must occur in exactly this sequence: fill → text → show."""
        led_matrix.display_text("seq")
        assert _MATRIX.mock_calls == [
            call.fill(0),
            call.text("seq", 0, 0),
            call.show(),
        ]


# ── display_pixel() ───────────────────────────────────────────────────────────


class TestDisplayPixel:
    def test_turns_pixel_on_by_default(self):
        """on defaults to True; int(True) == 1."""
        led_matrix.display_pixel(3, 4)
        _MATRIX.pixel.assert_called_once_with(3, 4, 1)

    def test_turns_pixel_on_explicitly(self):
        led_matrix.display_pixel(1, 2, on=True)
        _MATRIX.pixel.assert_called_once_with(1, 2, 1)

    def test_turns_pixel_off(self):
        """on=False; int(False) == 0."""
        led_matrix.display_pixel(5, 6, on=False)
        _MATRIX.pixel.assert_called_once_with(5, 6, 0)

    def test_calls_show_after_pixel_update(self):
        led_matrix.display_pixel(0, 0)
        _MATRIX.show.assert_called_once()

    def test_call_order_pixel_then_show(self):
        led_matrix.display_pixel(7, 7, on=True)
        assert _MATRIX.mock_calls == [
            call.pixel(7, 7, 1),
            call.show(),
        ]


# ── clear() ───────────────────────────────────────────────────────────────────


class TestClear:
    def test_fills_with_zero(self):
        led_matrix.clear()
        _MATRIX.fill.assert_called_once_with(0)

    def test_calls_show(self):
        led_matrix.clear()
        _MATRIX.show.assert_called_once()

    def test_call_order_fill_then_show(self):
        led_matrix.clear()
        assert _MATRIX.mock_calls == [call.fill(0), call.show()]


# ── set_brightness() ──────────────────────────────────────────────────────────


class TestSetBrightness:
    def test_normal_midrange_value(self):
        led_matrix.set_brightness(8)
        _MATRIX.brightness.assert_called_once_with(8)

    def test_minimum_boundary_zero(self):
        led_matrix.set_brightness(0)
        _MATRIX.brightness.assert_called_once_with(0)

    def test_maximum_boundary_fifteen(self):
        led_matrix.set_brightness(15)
        _MATRIX.brightness.assert_called_once_with(15)

    def test_negative_value_clamped_to_zero(self):
        led_matrix.set_brightness(-1)
        _MATRIX.brightness.assert_called_once_with(0)

    def test_large_negative_clamped_to_zero(self):
        led_matrix.set_brightness(-999)
        _MATRIX.brightness.assert_called_once_with(0)

    def test_value_just_above_max_clamped_to_fifteen(self):
        led_matrix.set_brightness(16)
        _MATRIX.brightness.assert_called_once_with(15)

    def test_large_value_clamped_to_fifteen(self):
        led_matrix.set_brightness(1000)
        _MATRIX.brightness.assert_called_once_with(15)

    def test_config_default_brightness_passes_unclamped(self):
        """The brightness in config.json (5) is within range and must not be clamped."""
        from config import matrix_brightness

        led_matrix.set_brightness(matrix_brightness)
        _MATRIX.brightness.assert_called_once_with(matrix_brightness)
