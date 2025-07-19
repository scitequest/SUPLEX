import pytest
from src.ui.styles.color_utils import (
    hex_to_rgb, rgb_to_hex, get_luminance, 
    darken_hex_color, lighten_hex_color, 
    get_emphasized_hex_color, hex_to_rgba
)

class TestColorUtils:
    def test_hex_to_rgb_6_char(self):
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#000000") == (0, 0, 0)
        assert hex_to_rgb("#808080") == (128, 128, 128)
    
    def test_hex_to_rgb_3_char(self):
        assert hex_to_rgb("#F00") == (255, 0, 0)
        assert hex_to_rgb("#0F0") == (0, 255, 0)
        assert hex_to_rgb("#00F") == (0, 0, 255)
        assert hex_to_rgb("#FFF") == (255, 255, 255)
        assert hex_to_rgb("#000") == (0, 0, 0)
        assert hex_to_rgb("#888") == (136, 136, 136)
    
    def test_hex_to_rgb_without_hash(self):
        assert hex_to_rgb("FF0000") == (255, 0, 0)
        assert hex_to_rgb("F00") == (255, 0, 0)
    
    def test_hex_to_rgb_lowercase(self):
        assert hex_to_rgb("#ff0000") == (255, 0, 0)
        assert hex_to_rgb("aabbcc") == (170, 187, 204)
    
    def test_hex_to_rgb_invalid(self):
        assert hex_to_rgb("") is None
        assert hex_to_rgb("#GGGGGG") is None
        assert hex_to_rgb("#FF") is None
        assert hex_to_rgb("#FFFFFFF") is None
        assert hex_to_rgb("not-a-color") is None
    
    def test_rgb_to_hex(self):
        assert rgb_to_hex(255, 0, 0) == "#FF0000"
        assert rgb_to_hex(0, 255, 0) == "#00FF00"
        assert rgb_to_hex(0, 0, 255) == "#0000FF"
        assert rgb_to_hex(255, 255, 255) == "#FFFFFF"
        assert rgb_to_hex(0, 0, 0) == "#000000"
        assert rgb_to_hex(128, 128, 128) == "#808080"
    
    def test_rgb_to_hex_clamping(self):
        assert rgb_to_hex(-10, 300, 128) == "#00FF80"
        assert rgb_to_hex(256, 256, 256) == "#FFFFFF"
        assert rgb_to_hex(-1, -1, -1) == "#000000"
    
    def test_rgb_to_hex_float_input(self):
        assert rgb_to_hex(127.7, 128.2, 128.9) == "#7F8080"
    
    def test_get_luminance(self):
        assert get_luminance(255, 0, 0) == pytest.approx(0.299, rel=1e-3)
        assert get_luminance(0, 255, 0) == pytest.approx(0.587, rel=1e-3)
        assert get_luminance(0, 0, 255) == pytest.approx(0.114, rel=1e-3)
        
        assert get_luminance(0, 0, 0) == 0.0
        assert get_luminance(255, 255, 255) == 1.0
        
        assert get_luminance(128, 128, 128) == pytest.approx(0.502, rel=1e-3)
    
    def test_get_luminance_clamping(self):
        assert get_luminance(-10, 300, 128) == get_luminance(0, 255, 128)
    
    def test_darken_hex_color(self):
        result = darken_hex_color("#FF0000", 0.15)
        # 255 * (1 - 0.15) = 255 * 0.85 = 216.75 → 216 = 0xD8
        assert result == "#D80000"
        
        result = darken_hex_color("#FFFFFF", 0.5)
        # 255 * 0.5 = 127.5 → 127 = 0x7F
        assert result == "#7F7F7F"
        
        result = darken_hex_color("#000000", 0.5)
        assert result == "#000000"
    
    def test_darken_hex_color_factor_clamping(self):
        result = darken_hex_color("#FF0000", 1.5)
        assert result == "#000000"

        result = darken_hex_color("#FF0000", -0.5)
        assert result == "#FF0000"
    
    def test_darken_hex_color_invalid(self):
        result = darken_hex_color("not-a-color", 0.5)
        assert result == "not-a-color"
    
    def test_lighten_hex_color(self):
        result = lighten_hex_color("#FF0000", 0.15)
        # R: 255 + (255-255)*0.15 = 255 (no change)
        # G: 0 + (255-0)*0.15 = 38.25 → 38 = 0x26
        # B: 0 + (255-0)*0.15 = 38.25 → 38 = 0x26
        assert result == "#FF2626"
        
        result = lighten_hex_color("#404040", 0.5)
        # 64 + (255-64)*0.5 = 64 + 95.5 = 159.5 → 159 = 0x9F
        assert result == "#9F9F9F"
        
        result = lighten_hex_color("#000000", 0.5)
        # 0 + (255-0)*0.5 = 127.5 → 127 = 0x7F
        assert result == "#7F7F7F"
        
        result = lighten_hex_color("#FFFFFF", 0.5)
        assert result == "#FFFFFF"
    
    def test_lighten_hex_color_factor_clamping(self):
        result = lighten_hex_color("#000000", 1.5)
        assert result == "#FFFFFF"
        
        result = lighten_hex_color("#808080", -0.5)
        assert result == "#808080"
    
    def test_get_emphasized_hex_color_dark(self):
        result = get_emphasized_hex_color("#202020", 0.15)
        original_lum = get_luminance(32, 32, 32)
        result_rgb = hex_to_rgb(result)
        result_lum = get_luminance(*result_rgb)
        assert result_lum > original_lum
    
    def test_get_emphasized_hex_color_light(self):
        result = get_emphasized_hex_color("#E0E0E0", 0.15)
        original_lum = get_luminance(224, 224, 224)
        result_rgb = hex_to_rgb(result)
        result_lum = get_luminance(*result_rgb)
        assert result_lum < original_lum
    
    def test_get_emphasized_hex_color_invalid(self):
        result = get_emphasized_hex_color("not-a-color", 0.15)
        assert result == "not-a-color"
    
    def test_hex_to_rgba(self):
        assert hex_to_rgba("#FF0000", 0.5) == "rgba(255, 0, 0, 0.5)"
        assert hex_to_rgba("#00FF00", 1.0) == "rgba(0, 255, 0, 1.0)"
        assert hex_to_rgba("#0000FF", 0.0) == "rgba(0, 0, 255, 0.0)"
        assert hex_to_rgba("#FFFFFF", 0.75) == "rgba(255, 255, 255, 0.75)"
    
    def test_hex_to_rgba_alpha_clamping(self):
        assert hex_to_rgba("#FF0000", 1.5) == "rgba(255, 0, 0, 1.0)"
        assert hex_to_rgba("#FF0000", -0.5) == "rgba(255, 0, 0, 0.0)"
    
    def test_hex_to_rgba_invalid(self):
        assert hex_to_rgba("not-a-color", 0.5) == "rgba(0, 0, 0, 0.5)"
    
    def test_color_conversion_round_trip(self):
        colors = ["#FF0000", "#00FF00", "#0000FF", "#ABCDEF", "#123456"]
        
        for color in colors:
            rgb = hex_to_rgb(color)
            hex_again = rgb_to_hex(*rgb)
            assert hex_again == color.upper()
    
    def test_emphasis_factor_edge_cases(self):
        result = get_emphasized_hex_color("#808080", 0.0)
        assert result == "#808080"
        
        result = get_emphasized_hex_color("#000000", 1.0)
        assert result == "#FFFFFF"
        
        result = get_emphasized_hex_color("#FFFFFF", 1.0)
        assert result == "#000000"