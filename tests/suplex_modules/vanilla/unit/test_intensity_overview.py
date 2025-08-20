import pytest
from unittest.mock import Mock, patch, MagicMock, call
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import logging
from suplex_modules.vanilla.intensity_overview import IntensityOverviewModule
from suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    NORMALIZATION,
    DATASET_LABEL,
)
from suplex_modules.submodules.viability_rules import no_datasets_selected
from suplex_modules.submodules.sample_spot_filter import THRESHOLD_FILTER_STATE


class TestIntensityOverviewModule:
    def test_initialization(self):
        """Test module instantiation."""
        module = IntensityOverviewModule()
        assert module._datasets == []
        assert module._color_scheme is None
        assert module._sorted_datasets == []
        assert module._included_datasets == []
        assert module._spot_threshold_map == {}
        assert module._sample_threshold_map == {}
        assert module._filtered_values == {}
        assert module._unfiltered_values == {}
        assert module._attribute_selector is None
        assert module._dataset_sorter is None
        assert module._dataset_filter is None
        assert module._sample_spot_filter is None
        assert module._general_graph_settings is not None
        assert module._boxplot_settings is not None
        assert module._jitterplot_settings is not None
        assert module._overview_box is not None
        assert module._dataset_stats_box is not None
        assert module._plot_box is not None

    def test_properties(self):
        """Test module properties."""
        module = IntensityOverviewModule()
        assert module.module_name == "Intensity Overview"
        assert module.module_version == "0.5.0"
        assert module.group_name == "Vanilla"
        assert module.button_style == {
            "font_color": "#FFFFFF",
            "button_color": "#28A745",
            "button_icon": "📊",
        }

    def test_check_if_viable(self, mock_datasets):
        """Test viability check method."""
        module = IntensityOverviewModule()
        assert module.check_if_viable(mock_datasets) is True
        assert module.check_if_viable([]) is False  # No datasets

    def test_get_module_hover_text(self):
        """Test hover text method."""
        module = IntensityOverviewModule()
        assert (
            "Visualizes intensity distributions across datasets using an overlay of boxplots and jitterplots."
            == module.get_module_hover_text()
        )

    @patch(
        "src.suplex_modules.vanilla.intensity_overview.IntensityOverviewModule.create_settings_tab"
    )
    @patch(
        "src.suplex_modules.vanilla.intensity_overview.IntensityOverviewModule.create_sort_filter_tab"
    )
    @patch(
        "src.suplex_modules.vanilla.intensity_overview.IntensityOverviewModule.create_main_control_interface"
    )
    @patch(
        "src.suplex_modules.vanilla.intensity_overview.IntensityOverviewModule.update_analysis"
    )
    def test_initiate_module(
        self,
        mock_update,
        mock_control,
        mock_sort,
        mock_settings,
        mock_datasets,
        mock_color_scheme,
    ):
        """Test initiate module method."""
        for dataset in mock_datasets:
            dataset.tags = []
            dataset.suplex_tags = []
        mock_control.return_value = widgets.VBox()
        mock_sort.return_value = widgets.VBox()
        mock_settings.return_value = widgets.VBox()
        module = IntensityOverviewModule()
        module._attribute_dropdown = MagicMock(
            value=DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
        )  # Use Enum display value
        ui = module.initiate_module(
            mock_datasets, mock_color_scheme
        )  # Pass mock_color_scheme
        assert module._datasets == mock_datasets
        assert isinstance(ui, widgets.Box)
        mock_control.assert_called_once()
        mock_sort.assert_called_once()
        mock_settings.assert_called_once()

    def test_update_scheme(self, mock_color_scheme):
        """Test update scheme method."""
        module = IntensityOverviewModule()
        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            assert module._color_scheme == mock_color_scheme
            mock_update.assert_called_once()

    def test_reset_module(self):
        """Test reset module method."""
        module = IntensityOverviewModule()
        new_module = module.reset_module()
        assert isinstance(new_module, IntensityOverviewModule)
        assert new_module != module  # New instance

    @patch("matplotlib.pyplot.subplots")
    def test_update_analysis(self, mock_subplots, mock_datasets):
        """Test update analysis method."""
        module = IntensityOverviewModule()
        module._datasets = mock_datasets
        module._included_datasets = mock_datasets
        module._attribute_dropdown = MagicMock(
            value=DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
        )
        module._normalization_dropdown = MagicMock(value=NORMALIZATION.RAW.value)
        module._custom_normalization_input = MagicMock(value=1.0)
        module._dataset_descriptor = DATASET_LABEL.NAME
        module._apply_threshold_checkbox = MagicMock(value=False)
        module._show_threshold_checkbox = MagicMock(value=False)
        module._use_displayed_dataset_filter_checkbox = MagicMock(value=True)
        module._dataset_filter_checkbox = MagicMock(value=False)
        module._use_displayed_value_filter_checkbox = MagicMock(value=True)

        # Mocks for submodules
        module._attribute_selector = Mock()
        module._dataset_sorter = Mock(
            get_sorted_datasets=MagicMock(return_value=mock_datasets)
        )
        module._dataset_filter = Mock(
            get_filtered_datasets=MagicMock(return_value=(mock_datasets, []))
        )
        module._sample_spot_filter = Mock()
        module._sample_spot_filter.extract_filtered_values_from_datasets = MagicMock(
            return_value={d: [100, 200, 150] for d in mock_datasets}
        )
        module._sample_spot_filter.get_filter_maps = MagicMock(return_value=({}, {}))
        module._sample_spot_filter.get_threshold_range_slider = MagicMock(
            return_value=MagicMock(min=0, max=100, value=(0, 100))
        )

        # Mock Enum properties to support .value access
        x_scale_mock = MagicMock(value="linear")
        grid_style_mock = MagicMock(value="whitegrid")

        module._general_graph_settings = Mock(
            swap_axes=False,
            include_empty_datasets=True,
            x_range=(0, 100),
            x_scale=x_scale_mock,
            grid_style=grid_style_mock,
            max_label_length=20,
        )
        module._boxplot_settings = Mock(
            show_boxplot=True, show_outliers=True, box_width=0.5, box_alpha=0.5
        )
        module._jitterplot_settings = Mock(
            show_jitterplot=True,
            apply_jitter=True,
            point_size=10,
            jitter_strength=0.1,
            point_alpha=0.5,
        )

        # Simulate data to avoid "no data" warning
        module._unfiltered_values = {d: [100, 200, 150] for d in mock_datasets}
        module._filtered_values = {d: [100, 200, 150] for d in mock_datasets}

        # Set color scheme to avoid NoneType errors
        module._color_scheme = MagicMock()

        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        module.update_analysis()
        mock_subplots.assert_called()

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("builtins.open")
    @patch("csv.writer")
    def test_export_to_csv(self, mock_writer, mock_open, mock_asksave, mock_datasets):
        """Test export to CSV method."""
        mock_asksave.return_value = "/test.csv"
        module = IntensityOverviewModule()
        module._attribute_dropdown = MagicMock(
            value=DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
        )
        module._normalization_dropdown = MagicMock(value=NORMALIZATION.RAW.value)
        module._custom_normalization_input = MagicMock(value=1.0)
        module._dataset_descriptor = DATASET_LABEL.NAME
        module._apply_threshold_checkbox = MagicMock(value=False)
        module._spot_threshold_map = {
            mock_datasets[0]: [
                [THRESHOLD_FILTER_STATE.WITHIN_RANGE for _ in range(3)]
                for _ in range(2)
            ]
        }
        module._sample_spot_filter = Mock()
        module._sample_spot_filter.extract_filtered_values_from_datasets = MagicMock(
            return_value={mock_datasets[0]: [100, 200, 150, 50, 300, 250]}
        )
        module._included_datasets = mock_datasets

        module.on_export_csv()
        mock_writer.assert_called()
