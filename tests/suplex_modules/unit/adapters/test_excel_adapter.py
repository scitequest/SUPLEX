import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import ipywidgets as widgets
from pathlib import Path

from suplex.suplex_modules.adapters.excel_adapter import ExcelAdapter
from suplex.martin_interface.dataset import Dataset


class TestExcelAdapter:
    """Unit tests for ExcelAdapter – exports MARTin datasets to Microsoft Excel with overview sheet and per-dataset sheets."""

    # -------------------------------------------------------------------------
    # Module Properties and Initialization
    # -------------------------------------------------------------------------
    def test_module_properties(self):
        """Verify all public SuplexModuleInterface properties return expected values."""
        module = ExcelAdapter()

        assert module.module_name == "MS Excel"
        assert module.module_version == "0.1.0"
        assert module.group_name == "Adapters"

        style = module.button_style
        assert style["font_color"] == "#FFFFFF"
        assert style["button_color"] == "#107C41"
        assert style["button_icon"] == "E"
        
    def test_init_defaults(self):
        """Module initializes with sensible default state (empty datasets, default hover text, etc.)."""
        module = ExcelAdapter()

        assert module._datasets == []
        assert module._module_hover_text == module._DEFAULT_HOVER_TEXT
        assert module._value_extractor is None

    # -------------------------------------------------------------------------
    # Viability Checks
    # -------------------------------------------------------------------------
    def test_check_if_viable_valid_datasets(self, viable_datasets):
        """Module is viable when provided with clean datasets."""
        module = ExcelAdapter()
        assert module.check_if_viable(viable_datasets) is True
        assert module.get_module_hover_text() == module._DEFAULT_HOVER_TEXT

    def test_check_if_viable_no_datasets_selected(self):
        """Module is NOT viable and updates hover text when no datasets are selected."""
        module = ExcelAdapter()
        with patch(
            "suplex.suplex_modules.submodules.viability_rules.no_datasets_selected", return_value=True
        ):
            assert module.check_if_viable([]) is False
            assert "no datasets" in module.get_module_hover_text().lower()

    # -------------------------------------------------------------------------
    # Reset and Scheme Updates
    # -------------------------------------------------------------------------
    def test_reset_module(self):
        """reset_module() returns a fresh instance of the module."""
        module = ExcelAdapter()
        reset_module = module.reset_module()

        assert isinstance(reset_module, ExcelAdapter)
        assert reset_module is not module  # must be a new object

    def test_update_scheme(self, mock_color_scheme):
        """update_scheme() is a no-op for ExcelAdapter (no visual elements depend on color scheme)."""
        module = ExcelAdapter()
        # Should not raise and do nothing
        module.update_scheme(mock_color_scheme)

    # -------------------------------------------------------------------------
    # UI / Initiate Smoke Test
    # -------------------------------------------------------------------------
    @patch("suplex.suplex_modules.adapters.excel_adapter.WidgetFactory")
    @patch("suplex.suplex_modules.adapters.excel_adapter.ValueExtractor")
    def test_initiate_module_smoke(
        self,
        mock_value_extractor,
        mock_widget_factory,
        mock_datasets,
        mock_color_scheme,
    ):
        """Smoke test: initiate_module runs without crashing and sets up core internal objects and UI sections."""
        module = ExcelAdapter()

        # Minimal mock setup for sub-components
        mock_value_extractor.return_value = Mock()
        mock_value_extractor.return_value.get_attribute_widget.return_value = Mock()
        mock_value_extractor.return_value.attribute = Mock()

        mock_widget_factory.html_widget.return_value = Mock()
        mock_widget_factory.vbox.return_value = Mock()
        mock_widget_factory.hbox.return_value = Mock()
        mock_widget_factory.button_success.return_value = Mock()
        mock_widget_factory.checkbox.return_value = Mock()
        mock_widget_factory.label.return_value = Mock()

        ui = module.initiate_module(mock_datasets, mock_color_scheme)

        assert ui is not None
        assert module._datasets == mock_datasets
        assert module._value_extractor is not None
        # UI sections were created
        assert hasattr(module, "_conditional_formatting_overview_sheet")
        assert hasattr(module, "_id_checkbox")
        assert hasattr(module, "_data_checkboxes")
        assert hasattr(module, "_data_statistics_checkboxes")

    # -------------------------------------------------------------------------
    # Export Helpers
    # -------------------------------------------------------------------------
    def test_export_overview_sheet_no_conditional_formatting(self, mock_datasets):
        """export_overview_sheet runs without crashing when conditional formatting is disabled."""
        module = ExcelAdapter()
        module._datasets = mock_datasets
        module._conditional_formatting_overview_sheet = Mock(value=False)
        module._value_extractor = Mock()
        module._value_extractor.attribute = Mock(value="mean_val")
    
        with (
            patch("suplex.suplex_modules.adapters.excel_adapter.Workbook") as mock_wb,
            patch("suplex.suplex_modules.adapters.excel_adapter.filedialog") as mock_filedialog,
            patch("suplex.suplex_modules.adapters.excel_adapter.get_shortened_label") as mock_shorten,
            patch("builtins.open") as mock_open,
        ):
            mock_filedialog.asksaveasfilename.return_value = "/tmp/test.xlsx"
            mock_shorten.return_value = "test_sheet"
    
            # Minimal mocks for openpyxl
            mock_ws = Mock()
            mock_wb.return_value.active = mock_ws
            mock_wb.return_value.remove.return_value = None
            mock_ws.columns = []
    
            module.export_overview_sheet(attribute=module._value_extractor.attribute)
    
            # Should reach file dialog and not crash
            mock_filedialog.asksaveasfilename.assert_called_once()
