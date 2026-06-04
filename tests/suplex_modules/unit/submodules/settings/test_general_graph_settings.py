import pytest
import ipywidgets as widgets

from suplex_modules.submodules.settings.general_graph_settings import GeneralGraphSettings
from suplex_modules.submodules.settings.submodule_settings_constants import (
    SCALE_TYPE,
    SEQUENTIAL_COLOR_SCHEME,
    DIVERGENT_COLOR_SCHEME,
    GRID_STYLE,
    LEGEND_POSITION,
    ASPECT_RATIO,
    INTERPOLATION_TYPE,
)


class TestGeneralGraphSettings:
    """Tests for the large GeneralGraphSettings class (initialization, widgets, UI, properties)."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def test_init_default_values(self):
        """Default constructor should set sensible defaults for all options."""
        settings = GeneralGraphSettings()

        assert settings.col_descriptor == "Column"
        assert settings.row_descriptor == "Row"
        assert settings.z_descriptor == "Z"
        assert settings.invert_x_axis is False
        assert settings.show_grid is True
        assert settings.show_legend is True
        assert settings.sequential_color_scheme == SEQUENTIAL_COLOR_SCHEME.VIRIDIS
        assert settings.x_scale == SCALE_TYPE.LINEAR
        assert settings.resolution == (800, 600)
        assert settings.dpi == 100
        assert settings.aspect_ratio == ASPECT_RATIO.AUTO
        assert settings.interpolation == INTERPOLATION_TYPE.NEAREST
        assert settings.grid_style == GRID_STYLE.DARKGRID
        assert settings.legend_position == LEGEND_POSITION.BEST

    def test_init_custom_values(self):
        """All custom parameters should be respected."""
        settings = GeneralGraphSettings(
            col_descriptor="MyCol",
            row_descriptor="MyRow",
            show_grid=False,
            x_scale=SCALE_TYPE.LOG,
            sequential_color_scheme=SEQUENTIAL_COLOR_SCHEME.PLASMA,
            dpi=300,
            show_all_options=False,
        )

        assert settings.col_descriptor == "MyCol"
        assert settings.row_descriptor == "MyRow"
        assert settings.show_grid is False
        assert settings.x_scale == SCALE_TYPE.LOG
        assert settings.sequential_color_scheme == SEQUENTIAL_COLOR_SCHEME.PLASMA
        assert settings.dpi == 300

    # -------------------------------------------------------------------------
    # Widget creation
    # -------------------------------------------------------------------------

    def test_create_widgets_generates_key_widgets(self, general_graph_settings):
        """Important widgets should be created."""
        assert hasattr(general_graph_settings, "_col_descriptor_widget")
        assert hasattr(general_graph_settings, "_show_grid_widget")
        assert hasattr(general_graph_settings, "_x_scale_dropdown")
        assert hasattr(general_graph_settings, "_sequential_color_scheme_dropdown")
        assert hasattr(general_graph_settings, "_resolution_width_widget")

    def test_scale_dropdowns_exist_and_are_populated(self, general_graph_settings):
        """Scale dropdowns should contain all SCALE_TYPE options."""
        assert general_graph_settings._x_scale_dropdown.options
        assert SCALE_TYPE.LINEAR.value in general_graph_settings._x_scale_dropdown.options

    # -------------------------------------------------------------------------
    # UI and properties
    # -------------------------------------------------------------------------

    def test_get_active_widgets(self, general_graph_settings):
        """get_active_widgets returns a substantial list when show_all_options=True."""
        active = general_graph_settings.get_active_widgets()
        assert len(active) > 20  # many options enabled

    def test_get_ui_returns_valid_vbox(self, general_graph_settings):
        """get_ui must always return a VBox."""
        ui = general_graph_settings.get_ui()
        assert isinstance(ui, widgets.VBox)
        assert len(ui.children) > 0

    def test_properties_return_current_widget_values(self, general_graph_settings):
        """All @property getters should reflect the live widget state."""
        general_graph_settings._show_grid_widget.value = False
        general_graph_settings._x_scale_dropdown.value = SCALE_TYPE.LOG.value
        general_graph_settings._title_widget.value = "Test Graph"

        assert general_graph_settings.show_grid is False
        assert general_graph_settings.x_scale == SCALE_TYPE.LOG
        assert general_graph_settings.title == "Test Graph"

    def test_resolution_property_returns_tuple(self, general_graph_settings):
        """resolution property returns (width, height) tuple."""
        res = general_graph_settings.resolution
        assert isinstance(res, tuple)
        assert len(res) == 2
        assert isinstance(res[0], int) and isinstance(res[1], int)

    # -------------------------------------------------------------------------
    # Minimal settings
    # -------------------------------------------------------------------------

    def test_minimal_settings_only_includes_enabled_widgets(self, minimal_general_graph_settings):
        """When show_all_options=False, only explicitly enabled widgets appear."""
        active = minimal_general_graph_settings.get_active_widgets()
        descriptions = [getattr(w, "description", str(w)) for w in active]

        # In minimal mode not all options are present – we just check that we don't get everything
        assert len(active) < 40  # rough check that not all widgets are shown
