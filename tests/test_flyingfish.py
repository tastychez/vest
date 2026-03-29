"""
Tests for flyingfish.py – Flying Fish water/moisture sensor digital input.

Strategy
--------
A module-scoped fixture wipes the relevant sys.modules entries and resets
all hardware mock call-history before importing flyingfish, giving each
test run a clean, isolated view of exactly what the module did on load.
"""

import importlib
import sys

import pytest

# ── Hardware stubs (injected by conftest.py before this file is imported) ──────
mock_board = sys.modules["board"]
mock_digitalio = sys.modules["digitalio"]


# ── Module fixture ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module", autouse=True)
def flyingfish_module():
    """
    Import flyingfish.py in total isolation:
      - remove any cached copies of flyingfish + config
      - reset digitalio mock so call history is empty
      - import fresh, capturing module-level side-effects
    """
    for mod in ("flyingfish", "config"):
        sys.modules.pop(mod, None)

    # Clear call history on the hardware stubs
    mock_digitalio.reset_mock()
    mock_digitalio.Direction.INPUT = "INPUT"  # restore after recursive reset

    mod = importlib.import_module("flyingfish")
    yield mod

    # Teardown: leave sys.modules clean for other test files
    for mod_name in ("flyingfish", "config"):
        sys.modules.pop(mod_name, None)


# ── Tests ──────────────────────────────────────────────────────────────────────


class TestFlyingFishInitialisation:
    def test_flyingfish_object_exists(self, flyingfish_module):
        """Module must expose a top-level `flyingfish` sensor object."""
        assert hasattr(flyingfish_module, "flyingfish"), (
            "flyingfish.py should define a module-level `flyingfish` variable"
        )

    def test_correct_pin_passed_to_digital_in_out(self):
        """
        DigitalInOut must be called with board.D17, matching the
        `flying_fish_pin` value in config.json.
        """
        mock_digitalio.DigitalInOut.assert_called_once_with(mock_board.D17)

    def test_direction_set_to_input(self, flyingfish_module):
        """
        flyingfish.direction must equal digitalio.Direction.INPUT.
        The sensor only reads data; it must never be configured as OUTPUT.
        """
        assert flyingfish_module.flyingfish.direction == "INPUT"

    def test_only_one_pin_configured(self):
        """
        flyingfish.py should create exactly one DigitalInOut object —
        the Flying Fish sensor has a single digital output line.
        """
        assert mock_digitalio.DigitalInOut.call_count == 1
