from unittest.mock import Mock, PropertyMock, patch

import numpy as np

from suplex.martin_interface.dataset import Dataset
from suplex.suplex_modules.submodules.submodule_constants import NORMALIZATION
from suplex.suplex_modules.vanilla.overview_heatmap import OverviewHeatmapModule


class TestOverviewHeatmap:
    """Unit tests for OverviewHeatmap – generates a seaborn heatmap overview of dataset values with flexible normalization and filtering."""

    # -------------------------------------------------------------------------
    # Module Properties and Initialization
    # -------------------------------------------------------------------------
    def test_module_properties(self):
        """Verify all public SuplexModuleInterface properties return expected values."""
        module = OverviewHeatmapModule()

        assert module.module_name == "Overview Heatmap"
        assert module.module_version == "0.2.0"
        assert module.group_name == "Vanilla"

        style = module.button_style
        assert style["font_color"] == "#FFFFFF"
        assert style["button_color"] == "#87CEEB"
        assert style["button_icon"] == "🌡️"

    def test_init_defaults(self):
        """Module initializes with sensible default state (empty lists, default hover text, HeatmapSettings, etc.)."""
        module = OverviewHeatmapModule()

        assert module._datasets == []
        assert module._included_datasets == []
        assert module._excluded_datasets == []
        assert module._module_hover_text == module._DEFAULT_HOVER_TEXT
        assert module._value_extractor is None
        assert module._dataset_sorter is None
        assert module._dataset_filter is None
        assert module._sample_spot_filter is None
        assert module._heatmap_settings is not None

    # -------------------------------------------------------------------------
    # Viability Checks
    # -------------------------------------------------------------------------
    def test_check_if_viable_valid_datasets(self, viable_datasets):
        """Module is viable when provided with clean datasets (no negative values, samples present)."""
        module = OverviewHeatmapModule()
        with (
            patch(
                "suplex.suplex_modules.vanilla.overview_heatmap.no_datasets_selected",
                return_value=False,
            ),
            patch(
                "suplex.suplex_modules.vanilla.overview_heatmap.has_negative_values",
                return_value=False,
            ),
        ):
            assert module.check_if_viable(viable_datasets) is True
            assert module.get_module_hover_text() == module._DEFAULT_HOVER_TEXT

    def test_check_if_viable_no_datasets_selected(self):
        """Module is NOT viable and updates hover text when no datasets are selected."""
        module = OverviewHeatmapModule()
        with patch(
            "suplex.suplex_modules.vanilla.overview_heatmap.no_datasets_selected", return_value=True
        ):
            assert module.check_if_viable([]) is False
            assert "no datasets" in module.get_module_hover_text().lower()

    def test_check_if_viable_negative_values(self, datasets_with_issues):
        """Module is NOT viable and updates hover text when any dataset contains negative values."""
        module = OverviewHeatmapModule()
        # datasets_with_issues[2] contains a negative mean_minus_min value
        bad_datasets = [datasets_with_issues[2]]
        with patch(
            "suplex.suplex_modules.vanilla.overview_heatmap.has_negative_values", return_value=True
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
        assert reset_module is not module  # must be a new object

    def test_update_scheme(self, mock_color_scheme):
        """update_scheme() updates the internal color scheme.

        Note: update_analysis() is only called if the module has been initiated
        (i.e. _dataset_sorter is not None). This test verifies the color scheme
        update without requiring full initiation.
        """
        module = OverviewHeatmapModule()
        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            assert module._color_scheme == mock_color_scheme
            # update_analysis is intentionally not called on a fresh (non-initiated) module
            # because of the defensive guard in update_scheme()
            mock_update.assert_not_called()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def test_filter_empty_datasets_includes_all_when_enabled(self, mock_datasets):
        """When include_empty_datasets=True, all datasets (even empty/NaN) are kept."""
        module = OverviewHeatmapModule()
        ds_good = Mock(spec=Dataset)
        ds_nan = Mock(spec=Dataset)
        plot_data = {
            ds_good: [1.0, 2.0],
            ds_nan: [np.nan, np.nan],
        }
        with patch.object(
            type(module._general_graph_settings),
            "include_empty_datasets",
            new_callable=PropertyMock,
        ) as mock_prop:
            mock_prop.return_value = True
            result = module.filter_empty_datasets(plot_data)
        assert len(result) == 2
        assert ds_good in result
        assert ds_nan in result

    def test_filter_empty_datasets_excludes_empty_when_disabled(self, mock_datasets):
        """When include_empty_datasets=False, datasets that are empty or contain only NaNs are removed."""
        module = OverviewHeatmapModule()
        ds_good = Mock(spec=Dataset)
        ds_nan = Mock(spec=Dataset)
        ds_empty = Mock(spec=Dataset)
        plot_data = {
            ds_good: [1.0, 2.0],
            ds_nan: [np.nan, np.nan],
            ds_empty: [],
        }
        result = module.filter_empty_datasets(plot_data)
        assert len(result) == 1
        assert ds_good in result

    def test_get_data_matrix(self, mock_datasets):
        """get_data_matrix() creates a properly padded NaN-filled matrix from uneven value lists."""
        module = OverviewHeatmapModule()
        ds1 = Mock(spec=Dataset)
        ds2 = Mock(spec=Dataset)
        plot_data = {
            ds1: [10.0, 20.0],
            ds2: [30.0],
        }
        matrix = module.get_data_matrix(plot_data)

        assert matrix.shape == (2, 2)
        assert np.isnan(matrix).all()

    # -------------------------------------------------------------------------
    # UI / Initiate Smoke Test
    # -------------------------------------------------------------------------
    @patch("suplex.suplex_modules.vanilla.overview_heatmap.WidgetFactory")
    @patch("suplex.suplex_modules.vanilla.overview_heatmap.ValueExtractor")
    @patch("suplex.suplex_modules.vanilla.overview_heatmap.DatasetSorter")
    @patch("suplex.suplex_modules.vanilla.overview_heatmap.DatasetFilter")
    @patch("suplex.suplex_modules.vanilla.overview_heatmap.SampleSpotFilter")
    def test_initiate_module_smoke(
        self,
        mock_sample_spot_filter,
        mock_dataset_filter,
        mock_dataset_sorter,
        mock_value_extractor,
        mock_widget_factory,
        mock_datasets,
        mock_color_scheme,
    ):
        """Smoke test: initiate_module runs without crashing and sets up core internal objects (including reference selector)."""
        module = OverviewHeatmapModule()

        # Setup mocks with required attributes to prevent TypeErrors in initiate_module
        for ds in mock_datasets:
            ds.tags = []
            ds.suplex_tags = []

        # Minimal mock setup for sub-components
        mock_value_extractor.return_value = Mock()
        mock_value_extractor.return_value.get_ui.return_value = Mock()
        mock_value_extractor.return_value.get_reference_selector.return_value.get_ref_container.return_value = Mock()
        mock_value_extractor.return_value.get_active_widgets.return_value = [Mock()]
        mock_value_extractor.return_value.normalize_values.return_value = {}

        mock_dataset_sorter.return_value = Mock()
        mock_dataset_sorter.return_value.get_ui.return_value = Mock()
        mock_dataset_sorter.return_value.get_sorted_datasets.return_value = mock_datasets

        mock_dataset_filter.return_value = Mock()
        mock_dataset_filter.return_value.get_ui.return_value = Mock()
        mock_dataset_filter.return_value.get_threshold_slider.return_value = Mock()

        mock_sample_spot_filter.return_value = Mock()
        mock_sample_spot_filter.return_value.get_ui.return_value = Mock()
        mock_sample_spot_filter.return_value.get_default_sample_map.return_value = {}
        mock_sample_spot_filter.return_value.get_default_spot_map.return_value = {}
        mock_sample_spot_filter.return_value.on_filter_params_changed.return_value = None

        mock_widget_factory.vbox.return_value = Mock()
        mock_widget_factory.hbox.return_value = Mock()
        mock_widget_factory.tab.return_value = Mock()

        # Prevent full execution of heavy methods triggered by initiate_module
        with patch.object(module, "update_analysis"):
            ui = module.initiate_module(mock_datasets, mock_color_scheme)

        assert ui is not None
        assert module._datasets == mock_datasets
        assert module._color_scheme == mock_color_scheme
        assert module._value_extractor is not None
        assert module._dataset_sorter is not None
        assert module._dataset_filter is not None
        assert module._sample_spot_filter is not None
        assert module._tabs is not None

    # -------------------------------------------------------------------------
    # Export Helpers
    # -------------------------------------------------------------------------
    def test_on_export_plot_no_data_or_no_references(self):
        """Export plot gracefully handles no data or missing reference points for reference normalization."""
        module = OverviewHeatmapModule()
        module._value_extractor = Mock()
        module._value_extractor.normalization = NORMALIZATION.BY_POSITION
        module._value_extractor.references = []  # no references

        with patch.object(module, "generate_heatmap") as mock_generate:
            module.on_export_plot()
            mock_generate.assert_not_called()  # early return for missing references
