import ipywidgets as widgets

from suplex.suplex_modules.submodules.settings.boxplot_settings import BoxplotSettings
from suplex.suplex_modules.submodules.settings.submodule_settings_constants import WHISKER_MODE


class TestBoxplotSettings:
    """Tests for the BoxplotSettings class (widget creation, dynamic behaviour, UI)."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def test_init_default_values(self):
        """Default constructor should enable all options with sensible defaults."""
        settings = BoxplotSettings()
        assert settings.show_boxplot is True
        assert settings.show_outliers is True
        assert settings.whisker_mode == WHISKER_MODE.IQR
        assert settings.iqr_factor == 1.5
        assert settings.percentile_min == 5
        assert settings.percentile_max == 95
        assert settings.box_alpha == 0.7
        assert settings.box_width == 0.5

    def test_init_custom_values(self):
        """Custom parameters should be respected."""
        settings = BoxplotSettings(
            show_boxplot=False,
            show_outliers=False,
            whisker_mode=WHISKER_MODE.PERCENTILES,
            iqr_factor=2.0,
            percentile_min=10,
            percentile_max=90,
            box_alpha=0.3,
            box_width=0.8,
        )
        assert settings.show_boxplot is False
        assert settings.show_outliers is False
        assert settings.whisker_mode == WHISKER_MODE.PERCENTILES
        assert settings.iqr_factor == 2.0
        assert settings.percentile_min == 10
        assert settings.percentile_max == 90
        assert settings.box_alpha == 0.3
        assert settings.box_width == 0.8

    # -------------------------------------------------------------------------
    # Widget creation
    # -------------------------------------------------------------------------

    def test_create_widgets_generates_all_widgets(self, boxplot_settings):
        """All relevant widgets should be created."""
        assert hasattr(boxplot_settings, "_show_boxplot_widget")
        assert hasattr(boxplot_settings, "_show_outliers_widget")
        assert hasattr(boxplot_settings, "_whisker_mode_radio")
        assert hasattr(boxplot_settings, "_iqr_factor_widget")
        assert hasattr(boxplot_settings, "_percentile_min_widget")
        assert hasattr(boxplot_settings, "_percentile_max_widget")
        assert hasattr(boxplot_settings, "_box_alpha_widget")
        assert hasattr(boxplot_settings, "_box_width_widget")

    def test_whisker_mode_radio_buttons_exist(self, boxplot_settings):
        """Whisker mode uses custom radio buttons (styled Button widgets)."""
        radios = boxplot_settings.get_whisker_mode_radio()
        assert len(radios) == len(WHISKER_MODE)
        assert len(radios) > 0
        assert all(isinstance(rb, widgets.Button) for rb in radios)

    # -------------------------------------------------------------------------
    # Dynamic behaviour
    # -------------------------------------------------------------------------

    def test_update_whisker_display_iqr(self, boxplot_settings):
        """Switching to IQR mode should show only the IQR factor widget."""
        boxplot_settings.update_whisker_display(WHISKER_MODE.IQR.value)
        children = boxplot_settings._whisker_inputs_vbox.children
        assert len(children) == 1
        assert "IQR Factor" in str(children[0])

    def test_update_whisker_display_percentiles(self, boxplot_settings):
        """Switching to PERCENTILES mode should show min/max percentile widgets."""
        boxplot_settings.update_whisker_display(WHISKER_MODE.PERCENTILES.value)
        children = boxplot_settings._whisker_inputs_vbox.children
        assert len(children) == 1
        assert "Min Percentile" in str(children[0])
        assert "Max Percentile" in str(children[0])

    # -------------------------------------------------------------------------
    # UI and properties
    # -------------------------------------------------------------------------

    def test_get_active_widgets(self, boxplot_settings):
        """get_active_widgets returns only the currently relevant widgets."""
        active = boxplot_settings.get_active_widgets()
        assert len(active) >= 6  # most widgets are enabled with show_all_options=True

    def test_get_ui_returns_valid_vbox(self, boxplot_settings):
        """get_ui should always return a VBox."""
        ui = boxplot_settings.get_ui()
        assert isinstance(ui, widgets.VBox)
        assert len(ui.children) > 0

    def test_properties_return_current_widget_values(self, boxplot_settings):
        """All @property getters should reflect the current widget state."""
        boxplot_settings._show_boxplot_widget.value = False
        boxplot_settings._show_outliers_widget.value = False
        boxplot_settings._box_alpha_widget.value = 0.9

        assert boxplot_settings.show_boxplot is False
        assert boxplot_settings.show_outliers is False
        assert boxplot_settings.box_alpha == 0.9

    # -------------------------------------------------------------------------
    # Minimal settings
    # -------------------------------------------------------------------------

    def test_minimal_settings_only_shows_essential_widgets(self, minimal_boxplot_settings):
        """When show_all_options=False only explicitly enabled widgets appear."""
        active = minimal_boxplot_settings.get_active_widgets()
        descriptions = [w.description if hasattr(w, "description") else str(w) for w in active]
        assert any("Show Boxplot" in d for d in descriptions)
        assert any("Show Outliers" in d for d in descriptions)
