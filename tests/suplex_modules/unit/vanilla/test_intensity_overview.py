from unittest.mock import Mock, PropertyMock, patch

import numpy as np

from suplex.martin_interface.dataset import Dataset
from suplex.suplex_modules.vanilla.intensity_overview import IntensityOverviewModule


class TestIntensityOverview:
    """Unit tests for IntensityOverview module for intensity distribution visualization (boxplot + jitterplot overlay)."""

    # -------------------------------------------------------------------------
    # Module Properties and Initialization
    # -------------------------------------------------------------------------
    def test_module_properties(self):
        """Verify all public SuplexModuleInterface properties return expected values."""
        module = IntensityOverviewModule()

        assert module.module_name == "Intensity Overview"
        assert module.module_version == "0.6.0"
        assert module.group_name == "Vanilla"

        style = module.button_style
        assert style["font_color"] == "#FFFFFF"
        assert style["button_color"] == "#28A745"
        assert style["button_icon"] == "📊"

    def test_init_defaults(self):
        """Module initializes with sensible default state (empty lists, default hover text, etc.)."""
        module = IntensityOverviewModule()

        assert module._datasets == []
        assert module._included_datasets == []
        assert module._excluded_datasets == []
        assert module._module_hover_text == module._DEFAULT_HOVER_TEXT
        assert module._value_extractor is None
        assert module._dataset_sorter is None
        assert module._dataset_filter is None
        assert module._sample_spot_filter is None

    # -------------------------------------------------------------------------
    # Viability Checks
    # -------------------------------------------------------------------------
    def test_check_if_viable_valid_datasets(self, viable_datasets):
        """Module is viable when provided with clean datasets (no negative values, samples present)."""
        module = IntensityOverviewModule()
        with (
            patch(
                "suplex.suplex_modules.vanilla.intensity_overview.no_datasets_selected",
                return_value=False,
            ),
            patch(
                "suplex.suplex_modules.vanilla.intensity_overview.has_negative_values",
                return_value=False,
            ),
        ):
            assert module.check_if_viable(viable_datasets) is True
            assert module.get_module_hover_text() == module._DEFAULT_HOVER_TEXT

    def test_check_if_viable_no_datasets_selected(self):
        """Module is NOT viable and updates hover text when no datasets are selected."""
        module = IntensityOverviewModule()
        with patch(
            "suplex.suplex_modules.vanilla.intensity_overview.no_datasets_selected",
            return_value=True,
        ):
            assert module.check_if_viable([]) is False
            assert "no datasets" in module.get_module_hover_text().lower()

    def test_check_if_viable_negative_values(self, datasets_with_issues):
        """Module is NOT viable and updates hover text when any dataset contains negative values."""
        module = IntensityOverviewModule()
        bad_datasets = [datasets_with_issues[2]]
        with patch(
            "suplex.suplex_modules.vanilla.intensity_overview.has_negative_values",
            return_value=True,
        ):
            assert module.check_if_viable(bad_datasets) is False
            assert "negative value" in module.get_module_hover_text().lower()

    # -------------------------------------------------------------------------
    # Reset and Scheme Updates
    # -------------------------------------------------------------------------
    def test_reset_module(self):
        """reset_module() returns a fresh instance of the module."""
        module = IntensityOverviewModule()
        reset_module = module.reset_module()

        assert isinstance(reset_module, IntensityOverviewModule)
        assert reset_module is not module  # must be a new object

    def test_update_scheme(self, mock_color_scheme):
        """update_scheme() updates the internal color scheme and triggers analysis refresh."""
        module = IntensityOverviewModule()
        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            assert module._color_scheme == mock_color_scheme
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def test_get_shortened_label(self):
        """get_shortened_label() correctly truncates long labels while preserving readability."""
        module = IntensityOverviewModule()

        assert module.get_shortened_label("ShortName", 20) == "ShortName"
        assert (
            module.get_shortened_label("VeryLongDatasetNameThatNeedsShortening", 15)
            == "VeryLo...tening"
        )
        assert module.get_shortened_label("ABCDEF", 3) == "ABC"
        assert module.get_shortened_label("ABCDEF", 0) == ""

    def test_filter_empty_datasets_includes_all_when_enabled(self, mock_datasets):
        """When include_empty_datasets=True, all datasets (even empty/NaN) are kept."""
        module = IntensityOverviewModule()
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
        module = IntensityOverviewModule()
        # Default is already False
        ds_good = Mock(spec=Dataset)
        ds_nan = Mock(spec=Dataset)
        ds_empty = Mock(spec=Dataset)
        plot_data = {
            ds_good: [1.0, 2.0],
            ds_nan: [np.nan, np.nan],
            # Add a third mock to simulate a third dataset
            ds_empty: [],
        }
        result = module.filter_empty_datasets(plot_data)
        assert len(result) == 1
        assert ds_good in result

    # -------------------------------------------------------------------------
    # UI / Initiate Smoke Test
    # -------------------------------------------------------------------------
    @patch("suplex.suplex_modules.vanilla.intensity_overview.WidgetFactory")
    @patch("suplex.suplex_modules.vanilla.intensity_overview.ValueExtractor")
    @patch("suplex.suplex_modules.vanilla.intensity_overview.DatasetSorter")
    @patch("suplex.suplex_modules.vanilla.intensity_overview.DatasetFilter")
    @patch("suplex.suplex_modules.vanilla.intensity_overview.SampleSpotFilter")
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
        """Smoke test: initiate_module runs without crashing and sets up core internal objects."""
        module = IntensityOverviewModule()

        # Setup mocks with required attributes to prevent TypeErrors in initiate_module
        for ds in mock_datasets:
            ds.tags = []
            ds.suplex_tags = []

        # Critical mocks for on_selected_attribute_changed -> apply_dataset_filter
        mock_dataset_filter.return_value.get_filtered_datasets.return_value = (mock_datasets, [])

        # ValueExtractor mock
        mock_value_extractor.return_value = Mock()
        mock_value_extractor.return_value.get_active_widgets.return_value = [Mock()]
        mock_value_extractor.return_value.get_ui.return_value = Mock()
        mock_value_extractor.return_value.attribute = Mock()
        mock_value_extractor.return_value.normalization = Mock()
        mock_value_extractor.return_value.custom_factor = 65536

        mock_dataset_sorter.return_value = Mock()
        mock_dataset_sorter.return_value.get_sorted_datasets.return_value = mock_datasets
        mock_dataset_sorter.return_value.get_ui.return_value = Mock()

        mock_dataset_filter.return_value.get_ui.return_value = Mock()
        mock_dataset_filter.return_value.get_threshold_slider.return_value = Mock()
        mock_dataset_filter.return_value.get_attribute_dropdown.return_value = Mock()
        mock_dataset_filter.return_value.get_method_dropdown.return_value = Mock()
        mock_dataset_filter.return_value.get_invert_checkbox.return_value = Mock()

        mock_sample_spot_filter.return_value = Mock()
        mock_sample_spot_filter.return_value.get_default_sample_map.return_value = {}
        mock_sample_spot_filter.return_value.get_default_spot_map.return_value = {}
        mock_sample_spot_filter.return_value.get_ui.return_value = Mock()
        mock_sample_spot_filter.return_value.get_threshold_range_slider.return_value = Mock()
        mock_sample_spot_filter.return_value.get_attribute_dropdown.return_value = Mock()
        mock_sample_spot_filter.return_value.get_normalization_dropdown.return_value = Mock()
        mock_sample_spot_filter.return_value.get_normalization_factor_input.return_value = Mock()
        mock_sample_spot_filter.return_value.get_invert_checkbox.return_value = Mock()
        mock_sample_spot_filter.return_value.get_sample_affects_spots_checkbox.return_value = Mock()
        mock_sample_spot_filter.return_value.get_spots_affect_sample_checkbox.return_value = Mock()
        mock_sample_spot_filter.return_value.get_sample_filter_mode_dropdown.return_value = Mock()
        mock_sample_spot_filter.return_value.get_filter_maps.return_value = ({}, {})
        mock_sample_spot_filter.return_value.extract_filtered_values_from_datasets.return_value = {}

        mock_widget_factory.vbox.return_value = Mock()
        mock_widget_factory.hbox.return_value = Mock()
        mock_widget_factory.tab.return_value = Mock()

        # Prevent full execution of on_selected_attribute_changed (which triggers heavy filtering)
        with patch.object(module, "on_selected_attribute_changed"):
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
    def test_on_export_plot_no_data(self):
        """Export plot gracefully handles the case of no data after filtering."""
        module = IntensityOverviewModule()
        with patch.object(module, "generate_box_jitter_plot") as mock_plot:
            # Simulate no data
            module._unfiltered_values = {}
            module.on_export_plot()
            mock_plot.assert_not_called()  # should early-return
