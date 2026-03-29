import json

# Load configuration from config.json
with open("config.json") as f:
    _config = json.load(f)

# Digital input sensor pins (resolved as strings, e.g. "D4")
fc22_pin = _config["fc22_pin"]
flying_fish_pin = _config["flying_fish_pin"]
cnt5_pin = _config["cnt5_pin"]

# MAX7219 dot matrix SPI pins
matrix_clk_pin = _config["matrix_clk_pin"]
matrix_mosi_pin = _config["matrix_mosi_pin"]
matrix_cs_pin = _config["matrix_cs_pin"]

# MAX7219 brightness (0 = dimmest, 15 = brightest)
matrix_brightness = _config["matrix_brightness"]
