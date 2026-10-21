import ipywidgets as widgets

from suplex.suplex_modules.submodules.settings.jitterplot_settings import JitterplotSettings
from suplex.suplex_modules.submodules.settings.submodule_settings_constants import JITTER_TYPE


class TestJitterplotSettings:
    """Tests for the JitterplotSettings class (initialization, widgets, UI, properties)."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def test_init_default_values(self):
        """Default constructor should set sensible defaults for all options."""
        settings = JitterplotSettings()

        assert settings.show_jitterplot is True
        assert settings.apply_jitter is False
        assert settings.jitter_type == JITTER_TYPE.UNIFORM
        assert settings.jitter_strength == 0.2
        assert settings.point_size == 10
        assert settings.point_alpha == 0.6

    def test_init_custom_values(self):
        """Custom parameters should be respected."""
        settings = JitterplotSettings(
            show_jitterplot=False,
            apply_jitter=True,
            jitter_type=JITTER_TYPE.GAUSSIAN,
            jitter_strength=0.5,
            point_size=15,
            point_alpha=0.8,
        )

        assert settings.show_jitterplot is False
        assert settings.apply_jitter is True
        assert settings.jitter_type == JITTER_TYPE.GAUSSIAN
        assert settings.jitter_strength == 0.5
        assert settings.point_size == 15
        assert settings.point_alpha == 0.8

    # -------------------------------------------------------------------------
    # Widget creation
    # -------------------------------------------------------------------------

    def test_create_widgets_generates_all_widgets(self, jitterplot_settings):
        """All relevant widgets should be created."""
        assert hasattr(jitterplot_settings, "_show_jitterplot_widget")
        assert hasattr(jitterplot_settings, "_apply_jitter_widget")
        assert hasattr(jitterplot_settings, "_jitter_type_radio")
        assert hasattr(jitterplot_settings, "_jitter_strength_widget")
        assert hasattr(jitterplot_settings, "_point_size_widget")
        assert hasattr(jitterplot_settings, "_point_alpha_widget")

    def test_jitter_type_radio_buttons_exist(self, jitterplot_settings):
        """Jitter type radio buttons should be present."""
        radios = jitterplot_settings.get_jitter_type_radio()
        assert len(radios) == len(JITTER_TYPE)
        # WidgetFactory.custom_radio_buttons returns a list of custom buttons
        assert len(radios) > 0

    # -------------------------------------------------------------------------
    # UI and properties
    # -------------------------------------------------------------------------

    def test_get_active_widgets(self, jitterplot_settings):
        """get_active_widgets returns a substantial list when show_all_options=True."""
        active = jitterplot_settings.get_active_widgets()
        assert len(active) >= 5  # most widgets are enabled

    def test_get_ui_returns_valid_vbox(self, jitterplot_settings):
        """get_ui must always return a VBox."""
        ui = jitterplot_settings.get_ui()
        assert isinstance(ui, widgets.VBox)
        assert len(ui.children) > 0

    def test_properties_return_current_widget_values(self, jitterplot_settings):
        """All @property getters should reflect the live widget state."""
        jitterplot_settings._show_jitterplot_widget.value = False
        jitterplot_settings._apply_jitter_widget.value = True
        jitterplot_settings._point_size_widget.value = 25
        jitterplot_settings._point_alpha_widget.value = 0.9

        assert jitterplot_settings.show_jitterplot is False
        assert jitterplot_settings.apply_jitter is True
        assert jitterplot_settings.point_size == 25
        assert jitterplot_settings.point_alpha == 0.9

    # -------------------------------------------------------------------------
    # Minimal settings
    # -------------------------------------------------------------------------

    def test_minimal_settings_only_includes_enabled_widgets(self, minimal_jitterplot_settings):
        """When show_all_options=False, only explicitly enabled widgets appear."""
        active = minimal_jitterplot_settings.get_active_widgets()
        descriptions = [getattr(w, "description", str(w)) for w in active]

        assert any("Show Jitterplot" in d for d in descriptions)
        assert any("Apply Jitter" in d for d in descriptions)
