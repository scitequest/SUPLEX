import pytest

from suplex.ui.styles.color_utils import (
    hex_to_rgb,
    rgb_to_hex,
    get_luminance,
    darken_hex_color,
    lighten_hex_color,
    get_emphasized_hex_color,
    hex_to_rgba,
)


class TestColorUtils:
    """Tests for color utility functions used throughout the UI for consistent
    hex/RGB/RGBA conversion, luminance calculation, and emphasis adjustments.
    """

    # -------------------------------------------------------------------------
    # hex_to_rgb
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "hex_color, expected",
        [
            ("#FF0000", (255, 0, 0)),
            ("#00FF00", (0, 255, 0)),
            ("#0000FF", (0, 0, 255)),
            ("#FFFFFF", (255, 255, 255)),
            ("#000000", (0, 0, 0)),
            ("#808080", (128, 128, 128)),
            ("#F00", (255, 0, 0)),  # 3-char
            ("#0F0", (0, 255, 0)),
            ("FF0000", (255, 0, 0)),  # no hash
            ("ff0000", (255, 0, 0)),  # lowercase
            ("aabbcc", (170, 187, 204)),
        ],
    )
    def test_hex_to_rgb_valid(self, hex_color, expected):
        """hex_to_rgb() correctly parses 3-char, 6-char, with/without #, and lowercase."""
        assert hex_to_rgb(hex_color) == expected

    @pytest.mark.parametrize(
        "invalid_color",
        ["", "#GGGGGG", "#FF", "#FFFFFFF", "not-a-color", "#12345"],
    )
    def test_hex_to_rgb_invalid(self, invalid_color):
        """hex_to_rgb() returns None for malformed or invalid hex strings."""
        assert hex_to_rgb(invalid_color) is None

    # -------------------------------------------------------------------------
    # rgb_to_hex
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "r, g, b, expected",
        [
            (255, 0, 0, "#FF0000"),
            (0, 255, 0, "#00FF00"),
            (0, 0, 255, "#0000FF"),
            (255, 255, 255, "#FFFFFF"),
            (0, 0, 0, "#000000"),
            (128, 128, 128, "#808080"),
        ],
    )
    def test_rgb_to_hex(self, r, g, b, expected):
        """rgb_to_hex() converts RGB tuples to uppercase hex with # prefix."""
        assert rgb_to_hex(r, g, b) == expected

    def test_rgb_to_hex_clamping_and_floats(self):
        """rgb_to_hex() clamps values and handles float inputs correctly."""
        assert rgb_to_hex(-10, 300, 128) == "#00FF80"
        assert rgb_to_hex(256, 256, 256) == "#FFFFFF"
        assert rgb_to_hex(-1, -1, -1) == "#000000"
        assert rgb_to_hex(127.7, 128.2, 128.9) == "#7F8080"

    # -------------------------------------------------------------------------
    # Luminance
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "r, g, b, expected",
        [
            (255, 0, 0, 0.299),
            (0, 255, 0, 0.587),
            (0, 0, 255, 0.114),
            (0, 0, 0, 0.0),
            (255, 255, 255, 1.0),
            (128, 128, 128, 0.502),
        ],
    )
    def test_get_luminance(self, r, g, b, expected):
        """get_luminance() returns correct perceived brightness using BT.601 formula."""
        assert get_luminance(r, g, b) == pytest.approx(expected, rel=1e-3)

    def test_get_luminance_clamping(self):
        """get_luminance() clamps out-of-range values."""
        assert get_luminance(-10, 300, 128) == get_luminance(0, 255, 128)

    # -------------------------------------------------------------------------
    # Darken / Lighten
    # -------------------------------------------------------------------------
    def test_darken_hex_color(self):
        """darken_hex_color() reduces brightness by the given factor."""
        assert darken_hex_color("#FF0000", 0.15) == "#D80000"
        assert darken_hex_color("#FFFFFF", 0.5) == "#7F7F7F"
        assert darken_hex_color("#000000", 0.5) == "#000000"

    def test_darken_hex_color_clamping(self):
        """Factor is clamped between 0.0 and 1.0."""
        assert darken_hex_color("#FF0000", 1.5) == "#000000"
        assert darken_hex_color("#FF0000", -0.5) == "#FF0000"

    def test_darken_hex_color_invalid(self):
        """Invalid color is returned unchanged."""
        assert darken_hex_color("not-a-color", 0.5) == "not-a-color"

    def test_lighten_hex_color(self):
        """lighten_hex_color() increases brightness toward white."""
        assert lighten_hex_color("#FF0000", 0.15) == "#FF2626"
        assert lighten_hex_color("#404040", 0.5) == "#9F9F9F"
        assert lighten_hex_color("#000000", 0.5) == "#7F7F7F"
        assert lighten_hex_color("#FFFFFF", 0.5) == "#FFFFFF"

    def test_lighten_hex_color_clamping(self):
        """Factor is clamped between 0.0 and 1.0."""
        assert lighten_hex_color("#000000", 1.5) == "#FFFFFF"
        assert lighten_hex_color("#808080", -0.5) == "#808080"

    # -------------------------------------------------------------------------
    # Emphasized color
    # -------------------------------------------------------------------------
    def test_get_emphasized_hex_color_dark(self):
        """Dark colors are lightened for emphasis."""
        result = get_emphasized_hex_color("#202020", 0.15)
        original_lum = get_luminance(32, 32, 32)
        result_rgb = hex_to_rgb(result)
        result_lum = get_luminance(*result_rgb)
        assert result_lum > original_lum

    def test_get_emphasized_hex_color_light(self):
        """Light colors are darkened for emphasis."""
        result = get_emphasized_hex_color("#E0E0E0", 0.15)
        original_lum = get_luminance(224, 224, 224)
        result_rgb = hex_to_rgb(result)
        result_lum = get_luminance(*result_rgb)
        assert result_lum < original_lum

    def test_get_emphasized_hex_color_invalid(self):
        """Invalid color is returned unchanged."""
        assert get_emphasized_hex_color("not-a-color", 0.15) == "not-a-color"

    # -------------------------------------------------------------------------
    # hex_to_rgba
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "hex_color, alpha, expected",
        [
            ("#FF0000", 0.5, "rgba(255, 0, 0, 0.5)"),
            ("#00FF00", 1.0, "rgba(0, 255, 0, 1.0)"),
            ("#0000FF", 0.0, "rgba(0, 0, 255, 0.0)"),
            ("#FFFFFF", 0.75, "rgba(255, 255, 255, 0.75)"),
        ],
    )
    def test_hex_to_rgba(self, hex_color, alpha, expected):
        """hex_to_rgba() produces valid CSS RGBA strings."""
        assert hex_to_rgba(hex_color, alpha) == expected

    def test_hex_to_rgba_alpha_clamping(self):
        """Alpha value is clamped to [0.0, 1.0]."""
        assert hex_to_rgba("#FF0000", 1.5) == "rgba(255, 0, 0, 1.0)"
        assert hex_to_rgba("#FF0000", -0.5) == "rgba(255, 0, 0, 0.0)"

    def test_hex_to_rgba_invalid(self):
        """Invalid hex falls back to black with given alpha."""
        assert hex_to_rgba("not-a-color", 0.5) == "rgba(0, 0, 0, 0.5)"

    # -------------------------------------------------------------------------
    # Round-trip & edge cases
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("color", ["#FF0000", "#00FF00", "#0000FF", "#ABCDEF", "#123456"])
    def test_color_conversion_round_trip(self, color):
        """hex → rgb → hex round-trip returns original color (uppercase)."""
        rgb = hex_to_rgb(color)
        hex_again = rgb_to_hex(*rgb)
        assert hex_again == color.upper()

    def test_emphasis_factor_edge_cases(self):
        """Edge cases for get_emphasized_hex_color (factor 0.0 and 1.0)."""
        assert get_emphasized_hex_color("#808080", 0.0) == "#808080"
        assert get_emphasized_hex_color("#000000", 1.0) == "#FFFFFF"
        assert get_emphasized_hex_color("#FFFFFF", 1.0) == "#000000"
