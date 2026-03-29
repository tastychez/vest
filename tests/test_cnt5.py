"""
test_cnt5.py
============
Unit tests for cnt5.py – CNT5 infrared obstacle sensor.

What is tested
--------------
* The correct board pin (taken from config.json) is passed to DigitalInOut.
* The sensor object's direction is set to INPUT.
* is_detected() honours the active-LOW polarity of the sensor:
    - pin LOW  (value = False) → is_detected() returns True
    - pin HIGH (value = True)  → is_detected() returns False
"""

import importlib
import sys

import pytest

# ── Hardware stubs (injected by tests/conftest.py) ────────────────────────────
mock_board = sys.modules["board"]
mock_digitalio = sys.modules["digitalio"]


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def cnt5_mod():
    """
    Import cnt5.py exactly once per test-module session, with a clean mock slate.

    Evicting 'cnt5' and 'config' from sys.modules before import guarantees that
    module-level code re-executes against freshly-reset hardware stubs, so call
    counts don't bleed in from other test files.
    """
    # Clear any previously cached imports
    for name in ("cnt5", "config"):
        sys.modules.pop(name, None)

    # Reset digitalio mock so call history starts at zero
    mock_digitalio.reset_mock()
    mock_digitalio.Direction.INPUT = "INPUT"
    mock_digitalio.Direction.OUTPUT = "OUTPUT"

    mod = importlib.import_module("cnt5")
    yield mod

    # Teardown: remove modules so the next test file starts clean
    for name in ("cnt5", "config"):
        sys.modules.pop(name, None)


# ── Initialisation ────────────────────────────────────────────────────────────


class TestCNT5Initialisation:
    def test_cnt5_object_exists(self, cnt5_mod):
        """Module must expose a top-level `cnt5` sensor object."""
        assert hasattr(cnt5_mod, "cnt5"), (
            "cnt5.py should define a module-level variable named 'cnt5'"
        )

    def test_digital_in_out_called_once(self, cnt5_mod):
        """DigitalInOut should be instantiated exactly once during module load."""
        assert mock_digitalio.DigitalInOut.call_count == 1

    def test_correct_pin_passed_to_digital_in_out(self, cnt5_mod):
        """
        DigitalInOut must receive the pin object that corresponds to the
        'cnt5_pin' key in config.json (default: 'D6' → board.D6).
        """
        import config

        mock_digitalio.DigitalInOut.assert_called_once_with(
            getattr(mock_board, config.cnt5_pin)
        )

    def test_direction_set_to_input(self, cnt5_mod):
        """
        The sensor direction must be INPUT.
        Verifies: cnt5.direction = digitalio.Direction.INPUT
        """
        assert cnt5_mod.cnt5.direction == "INPUT"


# ── is_detected() – active-LOW logic ─────────────────────────────────────────


class TestIsDetected:
    """
    The CNT5 is an active-LOW sensor:
        pin LOW  (value = False) → obstacle detected → is_detected() == True
        pin HIGH (value = True)  → no obstacle       → is_detected() == False
    """

    def test_returns_true_when_pin_is_low(self, cnt5_mod):
        """Obstacle present: sensor pulls DO pin LOW."""
        cnt5_mod.cnt5.value = False
        assert cnt5_mod.is_detected() is True

    def test_returns_false_when_pin_is_high(self, cnt5_mod):
        """No obstacle: sensor lets DO pin float HIGH."""
        cnt5_mod.cnt5.value = True
        assert cnt5_mod.is_detected() is False

    def test_detection_toggles_correctly(self, cnt5_mod):
        """Rapid toggling must produce the correct result on every transition."""
        for pin_value, expected in [(False, True), (True, False), (False, True)]:
            cnt5_mod.cnt5.value = pin_value
            assert cnt5_mod.is_detected() is expected, (
                f"With pin={pin_value}, expected is_detected()={expected}"
            )

    def test_is_detected_is_boolean(self, cnt5_mod):
        """is_detected() should return a plain Python bool, not a MagicMock."""
        cnt5_mod.cnt5.value = False
        result = cnt5_mod.is_detected()
        assert isinstance(result, bool), f"Expected bool, got {type(result).__name__}"
