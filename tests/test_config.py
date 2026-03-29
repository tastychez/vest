"""
test_config.py
==============
Tests for:
  - config.json  – file structure, key presence, value types and ranges
  - config.py    – runtime exports match the JSON file
  - Edge cases   – missing keys, malformed JSON, unexpected value types
"""

import importlib
import json
import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Load the real config.json once for structure-level tests
# (conftest.py already set CWD → project root, so the path is stable)
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(_ROOT, "config.json")

with open(CONFIG_PATH) as _f:
    RAW_CONFIG = json.load(_f)

# Keys we expect to always be present
REQUIRED_KEYS = [
    "fc22_pin",
    "flying_fish_pin",
    "cnt5_pin",
    "matrix_clk_pin",
    "matrix_mosi_pin",
    "matrix_cs_pin",
    "matrix_brightness",
]

# Subset of keys whose values must be non-empty strings (pin names)
PIN_KEYS = [k for k in REQUIRED_KEYS if k != "matrix_brightness"]


# ===========================================================================
# 1.  config.json – file structure
# ===========================================================================


class TestConfigJsonStructure:
    """Validate the raw JSON file independently of the Python config module."""

    def test_file_is_valid_json(self):
        """config.json must parse without errors."""
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_no_empty_string_keys(self):
        """Stray empty-string keys (e.g. from sloppy editing) must not exist."""
        assert "" not in RAW_CONFIG

    @pytest.mark.parametrize("key", REQUIRED_KEYS)
    def test_required_key_present(self, key):
        """Every required configuration key must be present in config.json."""
        assert key in RAW_CONFIG, f"Missing required key: {key!r}"

    @pytest.mark.parametrize("key", PIN_KEYS)
    def test_pin_value_is_non_empty_string(self, key):
        """Pin values must be non-empty strings (e.g. 'D4', 'SCK')."""
        value = RAW_CONFIG[key]
        assert isinstance(value, str), (
            f"{key!r} must be a str, got {type(value).__name__}"
        )
        assert value.strip() != "", f"{key!r} must not be blank"

    def test_matrix_brightness_is_integer(self):
        """Brightness must be stored as a JSON integer, not a float or string."""
        assert isinstance(RAW_CONFIG["matrix_brightness"], int)

    def test_matrix_brightness_minimum_bound(self):
        """Brightness must be >= 0 (MAX7219 range: 0-15)."""
        assert RAW_CONFIG["matrix_brightness"] >= 0

    def test_matrix_brightness_maximum_bound(self):
        """Brightness must be <= 15 (MAX7219 range: 0-15)."""
        assert RAW_CONFIG["matrix_brightness"] <= 15

    def test_no_unexpected_keys(self):
        """config.json should not contain keys outside the expected set."""
        extra = set(RAW_CONFIG.keys()) - set(REQUIRED_KEYS)
        assert extra == set(), f"Unexpected keys found: {extra}"


# ===========================================================================
# 2.  config.py – runtime exports
# ===========================================================================


class TestConfigModuleExports:
    """
    Import config.py fresh for every test so that monkeypatching CWD or
    builtins.open in edge-case tests doesn't bleed through.
    """

    @pytest.fixture(autouse=True)
    def fresh_config(self):
        """Evict cached module, re-import, expose as `self.cfg`."""
        sys.modules.pop("config", None)
        self.cfg = importlib.import_module("config")
        yield
        sys.modules.pop("config", None)

    def test_fc22_pin_matches_json(self):
        assert self.cfg.fc22_pin == RAW_CONFIG["fc22_pin"]

    def test_flying_fish_pin_matches_json(self):
        assert self.cfg.flying_fish_pin == RAW_CONFIG["flying_fish_pin"]

    def test_cnt5_pin_matches_json(self):
        assert self.cfg.cnt5_pin == RAW_CONFIG["cnt5_pin"]

    def test_matrix_clk_pin_matches_json(self):
        assert self.cfg.matrix_clk_pin == RAW_CONFIG["matrix_clk_pin"]

    def test_matrix_mosi_pin_matches_json(self):
        assert self.cfg.matrix_mosi_pin == RAW_CONFIG["matrix_mosi_pin"]

    def test_matrix_cs_pin_matches_json(self):
        assert self.cfg.matrix_cs_pin == RAW_CONFIG["matrix_cs_pin"]

    def test_matrix_brightness_matches_json(self):
        assert self.cfg.matrix_brightness == RAW_CONFIG["matrix_brightness"]

    def test_all_pin_exports_are_strings(self):
        """Every pin export must resolve to a string at runtime."""
        for key in PIN_KEYS:
            value = getattr(self.cfg, key)
            assert isinstance(value, str), (
                f"config.{key} should be str, got {type(value).__name__}"
            )

    def test_brightness_export_is_int(self):
        assert isinstance(self.cfg.matrix_brightness, int)


# ===========================================================================
# 3.  Edge cases – bad or incomplete config files
# ===========================================================================


class TestConfigEdgeCases:
    """
    Each test writes a temporary config.json, redirects CWD to that
    directory, evicts the cached config module, and re-imports it.
    monkeypatch restores CWD automatically after every test.
    """

    @pytest.fixture(autouse=True)
    def _cleanup(self):
        yield
        sys.modules.pop("config", None)

    def _write_cfg(self, tmp_path, data: dict) -> None:
        (tmp_path / "config.json").write_text(json.dumps(data))

    # ── Missing required key ────────────────────────────────────────────────

    @pytest.mark.parametrize("missing_key", REQUIRED_KEYS)
    def test_missing_key_raises_key_error(self, missing_key, tmp_path, monkeypatch):
        """Removing any single required key must cause a KeyError on import."""
        cfg = {k: v for k, v in RAW_CONFIG.items() if k != missing_key}
        self._write_cfg(tmp_path, cfg)
        monkeypatch.chdir(tmp_path)
        sys.modules.pop("config", None)
        with pytest.raises(KeyError):
            importlib.import_module("config")

    def test_completely_empty_json_raises_key_error(self, tmp_path, monkeypatch):
        self._write_cfg(tmp_path, {})
        monkeypatch.chdir(tmp_path)
        sys.modules.pop("config", None)
        with pytest.raises(KeyError):
            importlib.import_module("config")

    # ── Malformed JSON ──────────────────────────────────────────────────────

    def test_invalid_json_raises_json_decode_error(self, tmp_path, monkeypatch):
        (tmp_path / "config.json").write_text("{ this is not : valid json }")
        monkeypatch.chdir(tmp_path)
        sys.modules.pop("config", None)
        with pytest.raises(json.JSONDecodeError):
            importlib.import_module("config")

    def test_empty_file_raises_json_decode_error(self, tmp_path, monkeypatch):
        (tmp_path / "config.json").write_text("")
        monkeypatch.chdir(tmp_path)
        sys.modules.pop("config", None)
        with pytest.raises(json.JSONDecodeError):
            importlib.import_module("config")

    # ── Missing file entirely ───────────────────────────────────────────────

    def test_missing_file_raises_file_not_found(self, tmp_path, monkeypatch):
        """If config.json does not exist at all, config.py must raise FileNotFoundError."""
        monkeypatch.chdir(tmp_path)  # tmp_path has no config.json
        sys.modules.pop("config", None)
        with pytest.raises(FileNotFoundError):
            importlib.import_module("config")

    # ── Wrong value types (loaded as-is; type checking is caller's job) ─────

    def test_brightness_as_string_is_loaded_verbatim(self, tmp_path, monkeypatch):
        """
        config.py does no type validation; a string brightness value is stored
        as-is.  Callers (led_matrix.py) are responsible for type safety.
        """
        cfg = {**RAW_CONFIG, "matrix_brightness": "five"}
        self._write_cfg(tmp_path, cfg)
        monkeypatch.chdir(tmp_path)
        sys.modules.pop("config", None)
        c = importlib.import_module("config")
        assert c.matrix_brightness == "five"

    def test_pin_as_integer_is_loaded_verbatim(self, tmp_path, monkeypatch):
        """An integer where a string pin name is expected is stored as-is."""
        cfg = {**RAW_CONFIG, "fc22_pin": 4}
        self._write_cfg(tmp_path, cfg)
        monkeypatch.chdir(tmp_path)
        sys.modules.pop("config", None)
        c = importlib.import_module("config")
        assert c.fc22_pin == 4
