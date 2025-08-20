import pytest
import ipywidgets as widgets
from suplex_modules.submodules.settings.boxplot_settings import BoxplotSettings
from suplex_modules.submodules.settings.submodule_settings_constants import WHISKER_MODE


class TestBoxplotSettings:
    def test_init_defaults(self):
        """Test init with defaults."""
        settings = BoxplotSettings()
        assert settings.show_boxplot is True
        assert settings.show_outliers is True
        assert settings.whisker_mode == WHISKER_MODE.IQR
        assert settings.iqr_factor == 1.5

    def test_get_ui(self):
        """Test UI creation."""
        settings = BoxplotSettings()
        ui = settings.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_properties(self):
        """Test properties."""
        settings = BoxplotSettings(
            whisker_mode=WHISKER_MODE.PERCENTILES, percentile_min=5, percentile_max=95
        )
        assert settings.whisker_mode == WHISKER_MODE.PERCENTILES
        assert settings.percentile_min == 5
        assert settings.percentile_max == 95
