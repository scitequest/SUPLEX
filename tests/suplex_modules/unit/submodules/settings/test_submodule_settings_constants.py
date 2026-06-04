import pytest
import math
from enum import Enum

from suplex_modules.submodules.settings.submodule_settings_constants import (
    OPTION_INSET,
    SCALE_TYPE,
    INTERPOLATION_TYPE,
    GRID_STYLE,
    LEGEND_POSITION,
    ASPECT_RATIO,
    get_aspect_ratio_value,
    SEQUENTIAL_COLOR_SCHEME,
    DIVERGENT_COLOR_SCHEME,
    WHISKER_MODE,
    JITTER_TYPE,
    ANNOTATION_COLOR,
    LINE_COLOR,
    CBAR_ORIENTATION,
    CBAR_TICK_MODE,
)


class TestSubmoduleSettingsConstants:
    """Tests for all constants and enums defined in submodule_settings_constants.py."""

    # -------------------------------------------------------------------------
    # Custom classes / helpers
    # -------------------------------------------------------------------------

    def test_option_inset_class(self):
        """OPTION_INSET should be a class with the correct inset strings."""
        assert OPTION_INSET.BASELINE == "0px 0px 0px 0px"
        assert OPTION_INSET.PRIMARY == "0px 0px 0px 10px"
        assert OPTION_INSET.SECONDARY == "0px 0px 0px 20px"
        assert OPTION_INSET.TERTIARY == "0px 0px 0px 30px"
        assert OPTION_INSET.QUATERNARY == "0px 0px 0px 40px"

    def test_get_aspect_ratio_value(self):
        """Helper function should correctly convert aspect ratios."""
        assert get_aspect_ratio_value(ASPECT_RATIO.AUTO) is None
        assert get_aspect_ratio_value(ASPECT_RATIO.EQUAL) == 1.0
        assert get_aspect_ratio_value(ASPECT_RATIO.FOUR_THREE) == pytest.approx(4 / 3)
        assert get_aspect_ratio_value(ASPECT_RATIO.SIXTEEN_NINE) == pytest.approx(16 / 9)
        assert get_aspect_ratio_value(ASPECT_RATIO.GOLDEN) == pytest.approx(1.618)
        assert get_aspect_ratio_value(ASPECT_RATIO.NINE_SIXTEEN) == pytest.approx(9 / 16)

    # -------------------------------------------------------------------------
    # Enum tests
    # -------------------------------------------------------------------------

    def test_scale_type_enum(self):
        """Test SCALE_TYPE enum."""
        assert issubclass(SCALE_TYPE, Enum)
        assert len(SCALE_TYPE) == 3
        assert SCALE_TYPE.LINEAR.value == "linear"
        assert SCALE_TYPE.LOG.value == "log"
        assert SCALE_TYPE.SYMLOG.value == "symlog"

    def test_interpolation_type_enum(self):
        """Test INTERPOLATION_TYPE enum."""
        assert issubclass(INTERPOLATION_TYPE, Enum)
        assert len(INTERPOLATION_TYPE) == 5
        assert INTERPOLATION_TYPE.NEAREST.value == "nearest"

    def test_grid_style_enum(self):
        """Test GRID_STYLE enum."""
        assert issubclass(GRID_STYLE, Enum)
        assert len(GRID_STYLE) == 3
        assert GRID_STYLE.DARKGRID.value == "darkgrid"

    def test_legend_position_enum(self):
        """Test LEGEND_POSITION enum."""
        assert issubclass(LEGEND_POSITION, Enum)
        assert len(LEGEND_POSITION) == 12
        assert LEGEND_POSITION.BEST.value == "best"

    def test_aspect_ratio_enum(self):
        """Test ASPECT_RATIO enum."""
        assert issubclass(ASPECT_RATIO, Enum)
        assert len(ASPECT_RATIO) == 11
        assert ASPECT_RATIO.AUTO.value == "auto"
        assert ASPECT_RATIO.EQUAL.value == "equal"

    def test_sequential_color_scheme_enum(self):
        """Test SEQUENTIAL_COLOR_SCHEME enum (many schemes + reversed variants)."""
        assert issubclass(SEQUENTIAL_COLOR_SCHEME, Enum)
        assert len(SEQUENTIAL_COLOR_SCHEME) > 30
        assert SEQUENTIAL_COLOR_SCHEME.VIRIDIS.value == "viridis"
        assert SEQUENTIAL_COLOR_SCHEME.VIRIDIS_R.value == "viridis_r"

    def test_divergent_color_scheme_enum(self):
        """Test DIVERGENT_COLOR_SCHEME enum."""
        assert issubclass(DIVERGENT_COLOR_SCHEME, Enum)
        assert len(DIVERGENT_COLOR_SCHEME) > 10
        assert DIVERGENT_COLOR_SCHEME.COOLWARM.value == "coolwarm"

    def test_whisker_mode_enum(self):
        """Test WHISKER_MODE enum."""
        assert issubclass(WHISKER_MODE, Enum)
        assert len(WHISKER_MODE) == 4
        assert WHISKER_MODE.IQR.value == "IQR"

    def test_jitter_type_enum(self):
        """Test JITTER_TYPE enum."""
        assert issubclass(JITTER_TYPE, Enum)
        assert len(JITTER_TYPE) == 2
        assert JITTER_TYPE.UNIFORM.value == "uniform"

    def test_annotation_color_enum(self):
        """Test ANNOTATION_COLOR enum."""
        assert issubclass(ANNOTATION_COLOR, Enum)
        assert len(ANNOTATION_COLOR) == 10
        assert ANNOTATION_COLOR.BLACK.value == "black"

    def test_line_color_enum(self):
        """Test LINE_COLOR enum."""
        assert issubclass(LINE_COLOR, Enum)
        assert len(LINE_COLOR) == 4
        assert LINE_COLOR.WHITE.value == "white"

    def test_cbar_orientation_enum(self):
        """Test CBAR_ORIENTATION enum."""
        assert issubclass(CBAR_ORIENTATION, Enum)
        assert len(CBAR_ORIENTATION) == 3
        assert CBAR_ORIENTATION.VERTICAL.value == "vertical"

    def test_cbar_tick_mode_enum(self):
        """Test CBAR_TICK_MODE enum."""
        assert issubclass(CBAR_TICK_MODE, Enum)
        assert len(CBAR_TICK_MODE) == 7
        assert CBAR_TICK_MODE.AUTO.value == "auto"
