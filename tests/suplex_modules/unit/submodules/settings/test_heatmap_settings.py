import pytest
import ipywidgets as widgets

from suplex_modules.submodules.settings.heatmap_settings import HeatmapSettings
from suplex_modules.submodules.settings.submodule_settings_constants import (
    ANNOTATION_COLOR,
    LINE_COLOR,
    CBAR_ORIENTATION,
    CBAR_TICK_MODE,
)


class TestHeatmapSettings:
    """Tests for the HeatmapSettings class (initialization, widgets, dynamic display, UI)."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def test_init_default_values(self):
        """Default constructor should set sensible defaults for all options."""
        settings = HeatmapSettings()

        assert settings.square is False
        assert settings.symmetric_scaling is True
        assert settings.annot is False
        assert settings.annot_fontsize == 10.0
        assert settings.annot_digits == 2
        assert settings.annot_color == ANNOTATION_COLOR.BLACK
        assert settings.linewidths == 0
        assert settings.linecolor == LINE_COLOR.WHITE.value
        assert settings.robust is False
        assert settings.start_at_index_0 is True
        assert settings.n_cols == 10
        assert settings.use_custom_col_labels is False
        assert settings.use_custom_row_labels is False
        assert settings.highlight_reference_points is False
        assert settings.cell_size == 0.1

    def test_init_custom_values(self):
        """Custom parameters should be respected."""
        settings = HeatmapSettings(
            square=True,
            symmetric_scaling=False,
            annot=True,
            annot_fontsize=14.0,
            annot_digits=3,
            annot_color=ANNOTATION_COLOR.WHITE.value,
            linewidths=0.5,
            linecolor=LINE_COLOR.BLACK.value,
            robust=True,
            n_cols=8,
            highlight_reference_points=True,
            show_all_options=False,
        )

        assert settings.square is True
        assert settings.symmetric_scaling is False
        assert settings.annot is True
        assert settings.annot_fontsize == 14.0
        assert settings.annot_digits == 3
        assert settings.annot_color == ANNOTATION_COLOR.WHITE
        assert settings.linewidths == 0.5
        assert settings.linecolor == LINE_COLOR.BLACK.value
        assert settings.robust is True
        assert settings.n_cols == 8
        assert settings.highlight_reference_points is True

    # -------------------------------------------------------------------------
    # Widget creation
    # -------------------------------------------------------------------------

    def test_create_widgets_generates_all_widgets(self, heatmap_settings):
        """All relevant widgets should be created."""
        assert hasattr(heatmap_settings, "_square_widget")
        assert hasattr(heatmap_settings, "_annot_widget")
        assert hasattr(heatmap_settings, "_annot_fontsize_widget")
        assert hasattr(heatmap_settings, "_cbar_mode_widget")
        assert hasattr(heatmap_settings, "_highlight_reference_points_widget")
        assert hasattr(heatmap_settings, "_col_labels_widget")
        assert hasattr(heatmap_settings, "_cell_size_widget")

    def test_cbar_and_tick_mode_widgets_exist(self, heatmap_settings):
        """Colorbar and tick mode dropdowns should be present."""
        assert hasattr(heatmap_settings, "_cbar_mode_widget")
        assert hasattr(heatmap_settings, "_cbar_tick_mode_widget")
        assert len(heatmap_settings._cbar_mode_widget.options) > 0
        assert len(heatmap_settings._cbar_tick_mode_widget.options) > 0

    # -------------------------------------------------------------------------
    # Dynamic display updates
    # -------------------------------------------------------------------------

    def test_update_heatmap_settings_display_annotation(self, heatmap_settings):
        """Annotation widgets should be disabled when annot=False."""
        heatmap_settings._annot_widget.value = False
        heatmap_settings.update_heatmap_settings_display()
        assert heatmap_settings._annot_fontsize_widget.disabled is True
        assert heatmap_settings._annot_digits_widget.disabled is True
        assert heatmap_settings._annot_color_widget.disabled is True

        heatmap_settings._annot_widget.value = True
        heatmap_settings.update_heatmap_settings_display()
        assert heatmap_settings._annot_fontsize_widget.disabled is False

    def test_update_heatmap_settings_display_custom_labels(self, heatmap_settings):
        """Custom label widgets should be disabled when use_custom_*_labels=False."""
        heatmap_settings._use_custom_col_labels_widget.value = False
        heatmap_settings.update_heatmap_settings_display()
        assert heatmap_settings._col_labels_widget.disabled is True

        heatmap_settings._use_custom_col_labels_widget.value = True
        heatmap_settings.update_heatmap_settings_display()
        assert heatmap_settings._col_labels_widget.disabled is False

    def test_update_heatmap_settings_display_highlight(self, heatmap_settings):
        """Highlight color widget should be disabled when highlight_reference_points=False."""
        heatmap_settings._highlight_reference_points_widget.value = False
        heatmap_settings.update_heatmap_settings_display()
        assert heatmap_settings._highlight_color_widget.disabled is True

    # -------------------------------------------------------------------------
    # UI and properties
    # -------------------------------------------------------------------------

    def test_get_active_widgets(self, heatmap_settings):
        """get_active_widgets should return a large list when show_all_options=True."""
        active = heatmap_settings.get_active_widgets()
        assert len(active) >= 15  # most options are enabled

    def test_get_ui_returns_valid_vbox(self, heatmap_settings):
        """get_ui must always return a VBox."""
        ui = heatmap_settings.get_ui()
        assert isinstance(ui, widgets.VBox)
        assert len(ui.children) > 0

    def test_properties_return_current_widget_values(self, heatmap_settings):
        """All @property getters should reflect the live widget state."""
        heatmap_settings._square_widget.value = True
        heatmap_settings._annot_widget.value = True
        heatmap_settings._cell_size_widget.value = 0.8
        heatmap_settings._n_cols_widget.value = 12

        assert heatmap_settings.square is True
        assert heatmap_settings.annot is True
        assert heatmap_settings.cell_size == 0.8
        assert heatmap_settings.n_cols == 12

    # -------------------------------------------------------------------------
    # Minimal settings
    # -------------------------------------------------------------------------

    def test_minimal_settings_only_includes_enabled_widgets(self, minimal_heatmap_settings):
        """When show_all_options=False, only explicitly enabled widgets appear."""
        active = minimal_heatmap_settings.get_active_widgets()
        descriptions = [getattr(w, "description", str(w)) for w in active]

        assert any("Square Cells" in d for d in descriptions)
        assert any("Annotate Values" in d for d in descriptions)
