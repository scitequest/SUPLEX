import pytest
from unittest.mock import patch, MagicMock, Mock
import ipywidgets as widgets
import tempfile
import os
from pathlib import Path

from suplex_modules.vanilla.hitmap import HitmapModule
from martin_interface.dataset import Dataset
from suplex_modules.submodules.submodule_constants import DATASET_ATTRIBUTE


class TestHitmapModule:
    """Integration tests for the HitmapModule (static + dynamic hitmaps with compound map)."""

    # -------------------------------------------------------------------------
    # Viability checks
    # -------------------------------------------------------------------------
    def test_check_if_viable_with_valid_datasets(self, viable_datasets):
        """Module is viable when valid, uniform datasets with sufficient samples are provided."""
        module = HitmapModule()
        assert module.check_if_viable(viable_datasets) is True
        assert "cannot initiate" not in module.get_module_hover_text().lower()

    def test_check_if_viable_with_no_datasets(self, mock_datasets):
        """Module is not viable when no datasets are selected."""
        module = HitmapModule()
        empty_list = []
        assert module.check_if_viable(empty_list) is False
        assert "no datasets have been selected" in module.get_module_hover_text().lower()

    def test_check_if_viable_with_non_uniform_samples(self, datasets_with_issues):
        """Module is not viable when sample count is not uniform."""
        module = HitmapModule()
        assert module.check_if_viable(datasets_with_issues) is False
        assert "sample count is not uniform" in module.get_module_hover_text().lower()

    def test_check_if_viable_with_non_uniform_spots(self, datasets_with_issues):
        """Module is not viable when spot count per sample is not uniform."""
        module = HitmapModule()
        # datasets_with_issues already contains cases with inconsistent spots
        assert module.check_if_viable(datasets_with_issues) is False
        assert "spot count is not uniform" in module.get_module_hover_text().lower()

    def test_check_if_viable_with_insufficient_samples(self, datasets_with_issues):
        """Module is not viable when any dataset has fewer than 3 samples."""
        module = HitmapModule()
        assert module.check_if_viable(datasets_with_issues) is False
        assert "sample count is below three" in module.get_module_hover_text().lower()

    def test_check_if_viable_with_negative_values(self, datasets_with_issues):
        """Module is not viable when datasets contain negative values."""
        module = HitmapModule()
        assert module.check_if_viable(datasets_with_issues) is False
        assert "negative value" in module.get_module_hover_text().lower()

    # -------------------------------------------------------------------------
    # Module initialization
    # -------------------------------------------------------------------------
    def test_initiate_module_creates_ui_and_internal_components(
        self, viable_datasets, mock_color_scheme
    ):
        """initiate_module successfully creates the full UI and initializes all sub-components."""
        module = HitmapModule()
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
        module = HitmapModule()
        module.initiate_module([mock_dataset_for_extractor], mock_color_scheme)

        with patch.object(module, "update_analysis") as mock_update:
            # Simulate value extractor change
            module._value_extractor.get_attribute_widget().value = (
                DATASET_ATTRIBUTE.MEAN.value
            )
            mock_update.assert_called()

    # -------------------------------------------------------------------------
    # Plot / collage generation
    # -------------------------------------------------------------------------
    def test_update_analysis_generates_hitmaps_and_compound_map(
        self, viable_datasets, mock_color_scheme, mock_matplotlib_figure, mock_svg_figure
    ):
        """update_analysis successfully generates individual hitmaps, compound map, and places SVGs in plot boxes."""
        module = HitmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        with patch(
            "suplex_modules.vanilla.hitmap.HitmapModule._generate_heatmap_for_dataset",
            return_value=mock_matplotlib_figure,
        ), patch(
            "suplex_modules.submodules.collage.create_collage",
            return_value=mock_svg_figure,
        ):
            module.update_analysis()

            # Both collage and compound plot boxes should contain content
            assert len(module._collage_plot_box.children) >= 1
            assert len(module._compound_plot_box.children) >= 1

    # -------------------------------------------------------------------------
    # Export functionality
    # -------------------------------------------------------------------------
    @patch("tkinter.Tk")
    @patch("tkinter.filedialog.asksaveasfilename")
    def test_on_export_overview_csv_success(
        self,
        mock_asksaveasfilename,
        mock_tk,
        viable_datasets,
        mock_color_scheme,
        tmp_path,
    ):
        """Overview CSV export works and writes the expected file."""
        mock_asksaveasfilename.return_value = str(tmp_path / "overview.csv")
        module = HitmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        module.on_export_overview_csv()

        assert (tmp_path / "overview.csv").exists()

    @patch("tkinter.Tk")
    @patch("tkinter.filedialog.asksaveasfilename")
    def test_on_export_compound_csv_success(
        self,
        mock_asksaveasfilename,
        mock_tk,
        viable_datasets,
        mock_color_scheme,
        tmp_path,
    ):
        """Compound CSV export works and writes the expected file."""
        mock_asksaveasfilename.return_value = str(tmp_path / "compound.csv")
        module = HitmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        module.on_export_compound_csv()

        assert (tmp_path / "compound.csv").exists()

    # -------------------------------------------------------------------------
    # Reset and scheme update
    # -------------------------------------------------------------------------
    def test_reset_module_returns_new_instance(self, viable_datasets, mock_color_scheme):
        """reset_module returns a fresh instance of the module."""
        module = HitmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        reset_module = module.reset_module()
        assert isinstance(reset_module, HitmapModule)
        assert reset_module is not module

    def test_update_scheme_refreshes_analysis(self, viable_datasets, mock_color_scheme):
        """update_scheme calls update_analysis to refresh colors."""
        module = HitmapModule()
        module.initiate_module(viable_datasets, mock_color_scheme)

        with patch.object(module, "update_analysis") as mock_update:
            module.update_scheme(mock_color_scheme)
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------
    def test_initiate_module_with_dynamic_filtering(
        self, viable_datasets, mock_color_scheme
    ):
        """Module initializes correctly when dynamic filtering (sparsity) is active."""
        module = HitmapModule()
        ui = module.initiate_module(viable_datasets, mock_color_scheme)

        assert module._sparsity_sider is not None
        assert module._apply_dynamic_filter_checkbox is not None