from unittest.mock import Mock, patch

from suplex.suplex_modules.submodules.submodule_constants import (
    NORMALIZATION,
)
from suplex.suplex_modules.vanilla.hitmap import HitmapModule


class TestHitmap:
    """Unit tests for Hitmap – generates static/dynamic threshold hitmaps with collage and compound map views."""

    # -------------------------------------------------------------------------
    # Module Properties and Initialization
    # -------------------------------------------------------------------------
    def test_module_properties(self):
        """Verify all public SuplexModuleInterface properties return expected values."""
        module = HitmapModule()

        assert module.module_name == "Hitmap"
        assert module.module_version == "0.1.0"
        assert module.group_name == "Vanilla"

        style = module.button_style
        assert style["font_color"] == "#FFFFFF"
        assert style["button_color"] == "#ff3333"
        assert style["button_icon"] == "🎯"

    def test_init_defaults(self):
        """Module initializes with sensible default state (empty lists, default hover text, etc.)."""
        module = HitmapModule()

        assert module._datasets == []
        assert module._included_datasets == []
        assert module._excluded_datasets == []
        assert module._module_hover_text == module._DEFAULT_HOVER_TEXT
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
        """Module is viable when provided with clean, uniform datasets meeting all rules."""
        module = HitmapModule()
        with (
            patch(
                "suplex.suplex_modules.vanilla.hitmap.sample_count_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.spot_count_is_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.has_insufficient_number_of_samples",
                return_value=False,
            ),
            patch("suplex.suplex_modules.vanilla.hitmap.has_negative_values", return_value=False),
        ):
            assert module.check_if_viable(viable_datasets) is True
            assert module.get_module_hover_text() == module._DEFAULT_HOVER_TEXT

    def test_check_if_viable_no_datasets_selected(self):
        """Module is NOT viable and updates hover text when no datasets are selected."""
        module = HitmapModule()
        with patch("suplex.suplex_modules.vanilla.hitmap.no_datasets_selected", return_value=True):
            assert module.check_if_viable([]) is False
            assert "no datasets" in module.get_module_hover_text().lower()

    def test_check_if_viable_non_uniform_samples(self, mock_datasets):
        """Module is NOT viable when sample counts are not uniform across datasets."""
        module = HitmapModule()
        with (
            patch(
                "suplex.suplex_modules.vanilla.hitmap.sample_count_not_uniform", return_value=True
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.spot_count_is_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.has_insufficient_number_of_samples",
                return_value=False,
            ),
            patch("suplex.suplex_modules.vanilla.hitmap.has_negative_values", return_value=False),
        ):
            assert module.check_if_viable(mock_datasets) is False
            assert "sample count is not uniform" in module.get_module_hover_text().lower()

    def test_check_if_viable_non_uniform_spots(self, mock_datasets):
        """Module is NOT viable when spot counts are not uniform across datasets."""
        module = HitmapModule()
        with (
            patch(
                "suplex.suplex_modules.vanilla.hitmap.sample_count_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.spot_count_is_not_uniform", return_value=True
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.has_insufficient_number_of_samples",
                return_value=False,
            ),
            patch("suplex.suplex_modules.vanilla.hitmap.has_negative_values", return_value=False),
        ):
            assert module.check_if_viable(mock_datasets) is False
            assert "sample count is not uniform" in module.get_module_hover_text().lower()

    def test_check_if_viable_insufficient_samples(self, mock_datasets):
        """Module is NOT viable when any dataset has fewer than 3 samples."""
        module = HitmapModule()
        with (
            patch(
                "suplex.suplex_modules.vanilla.hitmap.sample_count_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.spot_count_is_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.has_insufficient_number_of_samples",
                return_value=True,
            ),
        ):
            assert module.check_if_viable(mock_datasets) is False
            assert "sample count is below three" in module.get_module_hover_text().lower()

    def test_check_if_viable_negative_values(self, datasets_with_issues):
        """Module is NOT viable and updates hover text when any dataset contains negative values."""
        module = HitmapModule()
        bad_datasets = [datasets_with_issues[2]]
        with (
            patch(
                "suplex.suplex_modules.vanilla.hitmap.sample_count_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.spot_count_is_not_uniform", return_value=False
            ),
            patch(
                "suplex.suplex_modules.vanilla.hitmap.has_insufficient_number_of_samples",
                return_value=False,
            ),
            patch("suplex.suplex_modules.vanilla.hitmap.has_negative_values", return_value=True),
        ):
            assert module.check_if_viable(bad_datasets) is False
            assert "negative value" in module.get_module_hover_text().lower()

    # -------------------------------------------------------------------------
    # Reset and Scheme Updates
    # -------------------------------------------------------------------------
    def test_reset_module(self):
        """reset_module() returns a fresh instance of the module."""
        module = HitmapModule()
        reset_module = module.reset_module()

        assert isinstance(reset_module, HitmapModule)
        assert reset_module is not module  # must be a new object

    def test_update_scheme(self, mock_color_scheme):
        """update_scheme() updates the internal color scheme and triggers analysis refresh."""
        module = HitmapModule()
        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            assert module._color_scheme == mock_color_scheme
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def test_auto_update_respects_checkbox(self):
        """auto_update() only calls the method when the auto-update checkbox is checked."""
        module = HitmapModule()
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
    @patch("suplex.suplex_modules.vanilla.hitmap.WidgetFactory")
    @patch("suplex.suplex_modules.vanilla.hitmap.ValueExtractor")
    @patch("suplex.suplex_modules.vanilla.hitmap.DatasetSorter")
    @patch("suplex.suplex_modules.vanilla.hitmap.DatasetFilter")
    @patch("suplex.suplex_modules.vanilla.hitmap.SampleSpotFilter")
    @patch("suplex.suplex_modules.vanilla.hitmap.Collage")
    @patch("suplex.suplex_modules.vanilla.hitmap.HeatmapSettings")
    @patch("suplex.suplex_modules.vanilla.hitmap.GeneralGraphSettings")
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
        """Smoke test: initiate_module runs without crashing and sets up core internal objects (including collage, filters, and dynamic UI)."""
        module = HitmapModule()

        # Setup mock datasets with all required attributes
        for ds in mock_datasets:
            ds.general_parameters = Mock()
            ds.general_parameters.columns_per_spotfield = 5
            ds.general_parameters.number_of_spotfields = 5
            ds.tags = []
            ds.suplex_tags = []
            ds.id = "mock_ds"
            ds.name = "Mock Dataset"

        # Critical mocks for apply_all_filters -> apply_dataset_filter
        mock_dataset_filter.return_value.get_filtered_datasets.return_value = (mock_datasets, [])

        # Minimal mock setup for sub-components
        mock_value_extractor.return_value = Mock()
        mock_value_extractor.return_value.get_ui.return_value = Mock()
        mock_value_extractor.return_value.get_active_widgets.return_value = [Mock()]
        mock_value_extractor.return_value.get_attribute_widget.return_value = Mock()
        mock_value_extractor.return_value.attribute = Mock()
        mock_value_extractor.return_value.normalization = NORMALIZATION.RAW
        mock_value_extractor.return_value.custom_factor = 2**16

        mock_dataset_sorter.return_value = Mock()
        mock_dataset_sorter.return_value.get_ui.return_value = Mock()
        mock_dataset_sorter.return_value.get_sorted_datasets.return_value = mock_datasets

        mock_dataset_filter.return_value.get_ui.return_value = Mock()
        mock_dataset_filter.return_value.get_method_dropdown.return_value = Mock()
        mock_dataset_filter.return_value.get_attribute_dropdown.return_value = Mock()

        mock_sample_spot_filter.return_value = Mock()
        mock_sample_spot_filter.return_value.get_ui.return_value = Mock()
        mock_sample_spot_filter.return_value.get_threshold_range_slider.return_value = Mock()
        mock_sample_spot_filter.return_value.get_invert_checkbox.return_value = Mock()
        mock_sample_spot_filter.return_value.on_filter_params_changed.return_value = None
        mock_sample_spot_filter.return_value.get_filter_maps.return_value = ({}, {})
        mock_sample_spot_filter.return_value.extract_filtered_values_from_datasets.return_value = {}

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

        with patch.object(module, "update_analysis"):
            ui = module.initiate_module(mock_datasets, mock_color_scheme)

        assert ui is not None
        assert module._datasets == mock_datasets
        assert module._color_scheme == mock_color_scheme
        assert module._value_extractor is not None
        assert module._dataset_sorter is not None
        assert module._dataset_filter is not None
        assert module._sample_spot_filter is not None
        assert module._collage is not None
        assert module._tabs is not None
        assert module._heatmap_settings is not None
        assert module._general_graph_settings is not None

    # -------------------------------------------------------------------------
    # Export Helpers
    # -------------------------------------------------------------------------
    def test_on_export_overview_plot_no_filters(self):
        """Export overview plot gracefully handles case when no static or dynamic filter is active."""
        module = HitmapModule()
        module._apply_static_filter_checkbox = Mock(value=False)
        module._apply_dynamic_filter_checkbox = Mock(value=False)

        with patch.object(module, "get_collage") as mock_get_collage:
            module.on_export_overview_plot()
            mock_get_collage.assert_not_called()  # early return
