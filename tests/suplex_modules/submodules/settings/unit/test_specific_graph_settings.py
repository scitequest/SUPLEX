import pytest
import ipywidgets as widgets
from suplex_modules.submodules.settings.jitterplot_settings import JitterplotSettings
from suplex_modules.submodules.settings.submodule_settings_constants import JITTER_TYPE

class TestJitterplotSettings:
    def test_init_defaults(self):
        """Test init."""
        settings = JitterplotSettings()
        assert settings.apply_jitter is False
        assert settings.jitter_type == JITTER_TYPE.UNIFORM
        assert settings.jitter_strength == 0.2

    def test_get_ui(self):
        """Test UI."""
        settings = JitterplotSettings()
        ui = settings.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_properties(self):
        """Test properties."""
        settings = JitterplotSettings(apply_jitter=True, jitter_strength=0.2)
        assert settings.apply_jitter is True
        assert settings.jitter_strength == 0.2