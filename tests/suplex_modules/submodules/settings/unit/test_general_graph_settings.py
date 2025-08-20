import pytest
import ipywidgets as widgets
from suplex_modules.submodules.settings.general_graph_settings import (
    GeneralGraphSettings,
)
from suplex_modules.submodules.settings.submodule_settings_constants import (
    SCALE_TYPE,
    ASPECT_RATIO,
    SEQUENTIAL_COLOR_SCHEME,
)


class TestGeneralGraphSettings:
    def test_init_defaults(self):
        """Test init."""
        settings = GeneralGraphSettings()
        assert settings.col_descriptor == "Column"
        assert settings.show_axis_ticks is True
        assert settings.x_scale == SCALE_TYPE.LINEAR

    def test_get_ui(self):
        """Test UI."""
        settings = GeneralGraphSettings()
        ui = settings.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_properties(self):
        """Test properties."""
        settings = GeneralGraphSettings(
            aspect_ratio=ASPECT_RATIO.EQUAL,
            sequential_color_scheme=SEQUENTIAL_COLOR_SCHEME.VIRIDIS,
        )
        assert settings.aspect_ratio == ASPECT_RATIO.EQUAL
        assert settings.sequential_color_scheme == SEQUENTIAL_COLOR_SCHEME.VIRIDIS

    def test_get_aspect_ratio_value(self):
        """Test helper function."""
        from suplex_modules.submodules.settings.submodule_settings_constants import (
            get_aspect_ratio_value,
        )

        assert get_aspect_ratio_value(ASPECT_RATIO.EQUAL) == 1.0
        assert get_aspect_ratio_value(ASPECT_RATIO.AUTO) is None
        assert get_aspect_ratio_value(ASPECT_RATIO.GOLDEN) == pytest.approx(
            1.618, 0.001
        )
