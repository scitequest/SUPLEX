import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd
import ipywidgets as widgets
from PIL import Image

from suplex.suplex_modules.vanilla.heatmap_collage import OverviewHeatmapModule
from suplex.martin_interface.dataset import Dataset
from suplex.suplex_modules.submodules.submodule_constants import DATASET_LABEL, NORMALIZATION


class TestHeatmapCollage:
    """Unit tests for Heatmap Collage – generates collage of per-dataset heatmaps optionally combined with annotated/full images."""

    # -------------------------------------------------------------------------
    # Module Properties and Initialization
    # -------------------------------------------------------------------------
    def test_module_properties(self):
        """Verify all public SuplexModuleInterface properties return expected values."""
        module = OverviewHeatmapModule()

        assert module.module_name == "Heatmap Collage"
        assert module.module_version == "0.2.0"
        assert module.group_name == "Vanilla"

        style = module.button_style
        assert style["font_color"] == "#FFFFFF"
        assert style["button_color"] == "#ED9121"
        assert style["button_icon"] == "🗺️"

    def test_init_defaults(self):
        """Module initializes with sensible default state (empty lists, default hover text, etc.)."""
        module = OverviewHeatmapModule()

        assert module._datasets == []
        assert module._included_datasets == []
        assert module._excluded_datasets == []
        assert module._module_hover_text == module._DEFAULT_HOVER_TEXT
        assert module._color_scheme is None
        assert module._value_extractor is None
        assert module._dataset_sorter is None
        assert module._dataset_filter is None
        assert module._sample_spot_filter is None
        # These are set only in initiate_module
        assert not hasattr(module, "_collage") or module._collage is None
        assert not hasattr(module, "_heatmap_settings") or module._heatmap_settings is None
        assert (
            not hasattr(module, "_general_graph_settings") or module._general_graph_settings is None
        )

    # -------------------------------------------------------------------------
    # Viability Checks
    # -------------------------------------------------------------------------
    def test_check_if_viable_valid_datasets(self, viable_datasets):
        """Module is viable when provided with clean datasets (no negative values)."""
        module = OverviewHeatmapModule()
        with (
            patch(
                "suplex.suplex_modules.submodules.viability_rules.has_negative_values", return_value=False
            ),
            patch(
                "suplex.suplex_modules.submodules.viability_rules.has_negative_data_values",
                return_value=False,
            ),
            patch(
                "suplex.suplex_modules.submodules.viability_rules.has_negative_data_statistics_values",
                return_value=False,
            ),
            patch(
                "suplex.suplex_modules.submodules.viability_rules.has_negative_spot_coordinates",
                return_value=False,
            ),
        ):
            assert module.check_if_viable(viable_datasets) is True
            assert module.get_module_hover_text() == module._DEFAULT_HOVER_TEXT

    def test_check_if_viable_no_datasets_selected(self):
        """Module is NOT viable and updates hover text when no datasets are selected."""
        module = OverviewHeatmapModule()
        with patch(
            "suplex.suplex_modules.submodules.viability_rules.no_datasets_selected", return_value=True
        ):
            assert module.check_if_viable([]) is False
            assert "no datasets" in module.get_module_hover_text().lower()

    def test_check_if_viable_negative_values(self, datasets_with_issues):
        """Module is NOT viable and updates hover text when any dataset contains negative values."""
        module = OverviewHeatmapModule()
        bad_datasets = [datasets_with_issues[2]]
        with patch(
            "suplex.suplex_modules.submodules.viability_rules.has_negative_values", return_value=True
        ):
            assert module.check_if_viable(bad_datasets) is False
            assert "negative value" in module.get_module_hover_text().lower()

    # -------------------------------------------------------------------------
    # Reset and Scheme Updates
    # -------------------------------------------------------------------------
    def test_reset_module(self):
        """reset_module() returns a fresh instance of the module."""
        module = OverviewHeatmapModule()
        reset_module = module.reset_module()

        assert isinstance(reset_module, OverviewHeatmapModule)
        assert reset_module is not module

    def test_update_scheme(self, mock_color_scheme):
        """update_scheme() updates the internal color scheme and triggers analysis refresh."""
        module = OverviewHeatmapModule()
        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            assert module._color_scheme == mock_color_scheme
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def test_filter_empty_datasets_includes_all_when_enabled(self, mock_datasets):
        """When include_empty_datasets=True, all datasets (even empty/NaN) are kept."""
        module = OverviewHeatmapModule()
        module._general_graph_settings = Mock(include_empty_datasets=True)

        ds0 = Mock(spec=Dataset)
        ds1 = Mock(spec=Dataset)
        plot_data = {
            ds0: [1.0, 2.0],
            ds1: [np.nan, np.nan],
        }
        result = module.filter_empty_datasets(plot_data)
        assert len(result) == 2
        assert ds0 in result
        assert ds1 in result

    def test_filter_empty_datasets_excludes_empty_when_disabled(self, mock_datasets):
        """When include_empty_datasets=False, datasets that are empty or contain only NaNs are removed."""
        module = OverviewHeatmapModule()
        module._general_graph_settings = Mock(include_empty_datasets=False)

        ds0 = Mock(spec=Dataset)
        ds1 = Mock(spec=Dataset)
        plot_data = {
            ds0: [1.0, 2.0],
            ds1: [np.nan, np.nan],
            Mock(spec=Dataset): [],
        }
        result = module.filter_empty_datasets(plot_data)
        assert len(result) == 1
        assert ds0 in result

    def test_auto_update_respects_checkbox(self):
        """auto_update() only calls the method when the auto-update checkbox is checked."""
        module = OverviewHeatmapModule()
        module._auto_update_checkbox = Mock()
        module._auto_update_checkbox.value = False

        with patch.object(module, "update_analysis") as mock_update:
            module.auto_update(mock_update)
            mock_update.assert_not_called()

            module._auto_update_checkbox.value = True
            module.auto_update(mock_update)
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # UI / Initiate Smoke Test
    # -------------------------------------------------------------------------
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.WidgetFactory")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.ValueExtractor")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.DatasetSorter")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.DatasetFilter")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.SampleSpotFilter")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.Collage")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.HeatmapSettings")
    @patch("suplex.suplex_modules.vanilla.heatmap_collage.GeneralGraphSettings")
    def test_initiate_module_smoke(
        self,
        mock_general_graph_settings,
        mock_heatmap_settings,
        mock_collage,
        mock_sample_spot_filter,
        mock_dataset_filter,
        mock_dataset_sorter,
        mock_value_extractor,
        mock_widget_factory,
        mock_datasets,
        mock_color_scheme,
    ):
        """Smoke test: initiate_module runs without crashing and sets up core internal objects (collage, extra checkboxes, image options)."""
        module = OverviewHeatmapModule()

        # Setup mock datasets with all required attributes
        for ds in mock_datasets:
            ds.general_parameters = Mock()
            ds.general_parameters.columns_per_spotfield = 5
            ds.general_parameters.number_of_spotfields = 5
            ds.tags = []
            ds.suplex_tags = []
            ds.id = "mock_ds"
            ds.name = "Mock Dataset"

        # Critical mocks for apply_all_filters -> apply_dataset_filter and apply_value_filter
        mock_dataset_filter.return_value.get_filtered_datasets.return_value = (mock_datasets, [])
        mock_sample_spot_filter.return_value.get_filter_maps.return_value = ({}, {})

        # Minimal mock setup for sub-components
        mock_value_extractor.return_value = Mock()
        mock_value_extractor.return_value.get_ui.return_value = Mock()
        mock_value_extractor.return_value.get_active_widgets.return_value = [Mock()]
        mock_value_extractor.return_value.get_reference_selector.return_value.get_ref_container.return_value = (
            Mock()
        )
        mock_value_extractor.return_value.attribute = Mock()
        mock_value_extractor.return_value.normalization = NORMALIZATION.RAW
        mock_value_extractor.return_value.references = []

        mock_dataset_sorter.return_value = Mock()
        mock_dataset_sorter.return_value.get_ui.return_value = Mock()
        mock_dataset_sorter.return_value.get_sorted_datasets.return_value = mock_datasets

        mock_dataset_filter.return_value.get_ui.return_value = Mock()

        mock_sample_spot_filter.return_value.get_ui.return_value = Mock()
        mock_sample_spot_filter.return_value.get_default_sample_map.return_value = {}
        mock_sample_spot_filter.return_value.get_default_spot_map.return_value = {}
        mock_sample_spot_filter.return_value.on_filter_params_changed.return_value = None

        mock_collage.return_value = Mock()
        mock_collage.return_value.get_ui.return_value = Mock()
        mock_collage.return_value.get_columns_input.return_value = Mock()
        mock_collage.return_value.generate_collage.return_value = Mock()

        mock_heatmap_settings.return_value = Mock()
        mock_heatmap_settings.return_value.get_ui.return_value = Mock()
        mock_heatmap_settings.return_value.get_n_cols_widget.return_value = Mock()

        mock_general_graph_settings.return_value = Mock()

        mock_widget_factory.vbox.return_value = Mock()
        mock_widget_factory.hbox.return_value = Mock()
        mock_widget_factory.tab.return_value = Mock()

        # Prevent RuntimeWarning from np.nanmean / nanmin / nanmax on empty mock data in update_overview
        with (
            patch("suplex.suplex_modules.vanilla.heatmap_collage.np.nanmean", return_value=0.0),
            patch("suplex.suplex_modules.vanilla.heatmap_collage.np.nanmin", return_value=0.0),
            patch("suplex.suplex_modules.vanilla.heatmap_collage.np.nanmax", return_value=0.0),
        ):
            ui = module.initiate_module(mock_datasets, mock_color_scheme)

        assert ui is not None
        assert module._datasets == mock_datasets
        assert module._color_scheme == mock_color_scheme
        assert module._value_extractor is not None
        assert module._dataset_sorter is not None
        assert module._dataset_filter is not None
        assert module._sample_spot_filter is not None
        assert module._collage is not None
        assert module._heatmap_settings is not None
        assert module._general_graph_settings is not None
        assert module._tabs is not None
        # Collage-specific controls exist
        assert hasattr(module, "_add_heatmaps_checkbox")
        assert hasattr(module, "_add_annotated_images_checkbox")
        assert hasattr(module, "_add_full_images_checkbox")
        assert hasattr(module, "_dataset_cols_number_input")

    # -------------------------------------------------------------------------
    # Export Helpers
    # -------------------------------------------------------------------------
    def test_on_export_plot_no_data_or_no_elements(self):
        """Export plot gracefully handles no data or when no collage elements (heatmaps/images) are selected."""
        module = OverviewHeatmapModule()
        module._value_extractor = Mock()
        module._value_extractor.normalization = NORMALIZATION.RAW
        module._add_heatmaps_checkbox = Mock(value=False)
        module._add_annotated_images_checkbox = Mock(value=False)
        module._add_full_images_checkbox = Mock(value=False)

        with patch.object(module, "get_collage") as mock_get_collage:
            module.on_export_plot()
            mock_get_collage.assert_not_called()
