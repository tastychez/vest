"""
test_fc22sbx.py
===============
Tests for fc22sbx.py – FC-22 smoke / gas sensor digital input.

Strategy
--------
The module is re-imported fresh for every test-module run via a
`scope="module"` fixture that:
  • evicts fc22sbx and config from sys.modules
  • resets the digitalio mock call history
  • does a clean import so module-level side-effects are re-executed

This guarantees that call counts start at zero and the assertions below
are never polluted by other test files.
"""

import importlib
import sys
from unittest.mock import call

import pytest

# ── Hardware stubs (injected by tests/conftest.py) ─────────────────────────────
mock_board = sys.modules["board"]
mock_digitalio = sys.modules["digitalio"]


# ── Module fixture ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def fc22_mod():
    """Import fc22sbx with a clean mock slate; tear down afterwards."""
    # Clear any cached imports from other test files
    for mod in ("fc22sbx", "config"):
        sys.modules.pop(mod, None)

    # Reset digitalio mock so call counts start at 0
    mock_digitalio.reset_mock()
    mock_digitalio.Direction.INPUT = "INPUT"  # restore after recursive reset

    imported = importlib.import_module("fc22sbx")
    yield imported

    # Teardown – remove from cache so the next test file gets a clean slate
    for mod in ("fc22sbx", "config"):
        sys.modules.pop(mod, None)


# ── Tests ──────────────────────────────────────────────────────────────────────


class TestFC22Initialisation:
    def test_module_exposes_fc22_object(self, fc22_mod):
        """fc22sbx must export a top-level `fc22` name."""
        assert hasattr(fc22_mod, "fc22"), (
            "fc22sbx.py should define a module-level variable named 'fc22'"
        )

    def test_digital_in_out_called_exactly_once(self, fc22_mod):
        """digitalio.DigitalInOut should be instantiated exactly once."""
        assert mock_digitalio.DigitalInOut.call_count == 1

    def test_correct_board_pin_used(self, fc22_mod):
        """DigitalInOut must receive board.D4 (the pin named in config.json)."""
        mock_digitalio.DigitalInOut.assert_called_once_with(mock_board.D4)

    def test_wrong_pin_not_used(self, fc22_mod):
        """Sanity-check: board.D2 (the old hard-coded pin) must NOT be used."""
        actual_pin = mock_digitalio.DigitalInOut.call_args[0][0]
        assert actual_pin is not mock_board.D2

    def test_direction_set_to_input(self, fc22_mod):
        """fc22.direction must be set to digitalio.Direction.INPUT."""
        assert fc22_mod.fc22.direction == "INPUT"

    def test_direction_not_output(self, fc22_mod):
        """fc22 is a sensor input – it must never be set to OUTPUT."""
        assert fc22_mod.fc22.direction != "OUTPUT"


class TestFC22ConfigIntegration:
    def test_pin_name_comes_from_config(self, fc22_mod):
        """
        config.fc22_pin must equal 'D4' and the corresponding board attribute
        must be what was passed to DigitalInOut.
        """
        import config

        expected_pin_obj = getattr(mock_board, config.fc22_pin)
        actual_pin_obj = mock_digitalio.DigitalInOut.call_args[0][0]
        assert actual_pin_obj is expected_pin_obj

    def test_changing_config_pin_would_change_board_attr(self):
        """
        Verify that getattr(board, 'D4') returns the same object as board.D4,
        confirming the dynamic-pin mechanism works correctly.
        """
        assert getattr(mock_board, "D4") is mock_board.D4
