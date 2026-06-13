import pytest
from unittest.mock import patch, MagicMock, Mock
import ipywidgets as widgets
import tempfile
import os
from pathlib import Path

from suplex_modules.vanilla.overview_heatmap import OverviewHeatmapModule
from martin_interface.dataset import Dataset
from suplex_modules.submodules.submodule_constants import DATASET_ATTRIBUTE


class TestOverviewHeatmapModule:
    """Integration tests for the OverviewHeatmapModule (heatmap collage)."""

    # -------------------------------------------------------------------------
    # Viability checks
    # -------------------------------------------------------------------------
    def test_check_if_viable_with_valid_datasets(self, viable_datasets):
        """Module is viable when valid datasets are provided."""
        module = OverviewHeatmapModule()
        assert module.check_if_viable(viable_datasets) is True
        assert "cannot initiate" not in module.get_module_hover_text().lower()

    def test_check_if_viable_with_no_datasets(self, mock_datasets):
        """Module is not viable and shows correct hover text when no datasets are selected."""
        module = OverviewHeatmapModule()
        empty_list = []
        assert module.check_if_viable(empty_list) is False
        assert "no datasets have been selected" in module.get_module_hover_text().lower()

    def test_check_if_viable_with_negative_values(self, datasets_with_issues):
        """Module is not viable when datasets contain negative values."""
        module = OverviewHeatmapModule()
        assert module.check_if_viable(datasets_with_issues) is False
        assert "negative value" in module.get_module_hover_text().lower()

    # -------------------------------------------------------------------------
    # Module initialization
    # -------------------------------------------------------------------------
    def test_initiate_module_creates_ui_and_internal_components(
        self, viable_datasets, mock_color_scheme
    ):
        """initiate_module successfully creates the full UI and initializes all sub-components."""
        module = OverviewHeatmapModule()
        ui = module.initiate_module(viable_datasets, mock_color_scheme)

        assert isinstance(ui, widgets.Box)
        assert module._datasets == viable_datasets
        assert module._value_extractor is not None
        assert module._collage is not None
        assert module._heatmap_settings is not None
        assert module._general_graph_settings is not None
        assert module._dataset_sorter is not None
        assert module._dataset_filter is not None
        assert module._sample_spot_filter is not None
        assert module._tabs is not None

    # -------------------------------------------------------------------------
    # Filter propagation and analysis update
    # -------------------------------------------------------------------------
    def test_value_extractor_change_triggers_analysis_update(
        self, viable_datasets, mock_color_scheme, mock_dataset_for_extractor
    ):
        """Changing value extractor settings triggers filter update and analysis refresh."""
        module = OverviewHeatmapModule()
        module.initiate_module([mock_dataset_for_extractor], mock_color_scheme)

        # Mock the update method to verify it gets called
        with patch.object(module, "update_analysis") as mock_update:
            # Simulate value extractor change (the observer is wired in initiate_module)
            module._value_extractor.get_attribute_widget().value = (
                DATASET_ATTRIBUTE.MEAN.value
            )
            mock_update.assert_called()

    # -------------------------------------------------------------------------
    # Plot / collage generation
    # -------------------------------------------------------------------------
    def test_update_analysis_generates_heatmap_collage(
        self, viable_datasets, mock_color_scheme, mock_matplotlib_figure, mock_svg_figure
    ):
        """update_analysis successfully generates the collage and places it in the plot box."""
        module = OverviewHeatmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        # Mock heavy dependencies
        with patch(
            "suplex_modules.vanilla.overview_heatmap.OverviewHeatmapModule.generate_heatmap",
            return_value=mock_matplotlib_figure,
        ), patch(
            "suplex_modules.submodules.collage.create_collage",
            return_value=mock_svg_figure,
        ), patch(
            "suplex_modules.vanilla.overview_heatmap.OverviewHeatmapModule.add_global_colorbar",
            return_value=mock_svg_figure,
        ):
            module.update_analysis()

            # Plot box should now contain the HTML widget with SVG
            assert len(module._plot_box.children) == 1
            assert isinstance(module._plot_box.children[0], widgets.HTML)

    # -------------------------------------------------------------------------
    # Export functionality
    # -------------------------------------------------------------------------
    @patch("tkinter.Tk")
    @patch("tkinter.filedialog.asksaveasfilename")
    def test_on_export_csv_success(
        self,
        mock_asksaveasfilename,
        mock_tk,
        viable_datasets,
        mock_color_scheme,
        tmp_path,
    ):
        """CSV export works and writes the expected file."""
        mock_asksaveasfilename.return_value = str(tmp_path / "test_export.csv")
        module = OverviewHeatmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        # Trigger export
        module.on_export_csv()

        assert (tmp_path / "test_export.csv").exists()

    # -------------------------------------------------------------------------
    # Reset and scheme update
    # -------------------------------------------------------------------------
    def test_reset_module_returns_new_instance(self, viable_datasets, mock_color_scheme):
        """reset_module returns a fresh instance of the module."""
        module = OverviewHeatmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        reset_module = module.reset_module()
        assert isinstance(reset_module, OverviewHeatmapModule)
        assert reset_module is not module

    def test_update_scheme_refreshes_analysis(self, viable_datasets, mock_color_scheme):
        """update_scheme calls update_analysis to refresh colors."""
        module = OverviewHeatmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------
    def test_initiate_module_with_reference_normalization(
        self, viable_datasets, mock_color_scheme
    ):
        """Module initializes correctly when reference-point normalization is active."""
        module = OverviewHeatmapModule()
        ui = module.initiate_module(viable_datasets, mock_color_scheme)

        # Reference selector should be present and functional
        assert module._value_extractor is not None
        assert module._value_extractor._references_enabled is True