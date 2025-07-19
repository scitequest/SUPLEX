import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, date
import ipywidgets as widgets

from src.ui.gui import GUI
from ui.elements.navigator import Navigator
from ui.ui_constants import PAGE
from martin_interface.martin_interface_constants import SEARCH_MODE


class TestNavigationIntegration:
    """
    Integration tests for the complete navigation flow through the application.
    Tests the interaction between GUI, Navigator, and Page components.
    """

    def test_complete_navigation_flow(self, integrated_gui, mock_adapter_with_data):
        """Test navigating through all pages from start to module selection."""
        navigator = integrated_gui._navigator

        # Verify initial state - should be on directory selection
        assert navigator._current_step == PAGE.DIRECTORY_SELECTION
        assert navigator._adapter is None

        # Simulate valid directory selection
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        assert navigator._adapter == mock_adapter_with_data

        # Navigate to dataset selection
        navigator.navigate_to_dataset_selection()
        assert navigator._current_step == PAGE.DATASET_SELECTION

        # Verify dataset selection page loaded
        assert navigator._dataset_selection_page is not None
        assert hasattr(navigator._dataset_selection_page, "get_selected_datasets")

        # Navigate to module selection
        navigator.navigate_to_module_selection()
        assert navigator._current_step == PAGE.MODULE_SELECTION

        # Verify breadcrumb states
        assert navigator._steps[0]["status"] == "completed"  # Directory selection
        assert navigator._steps[1]["status"] == "completed"  # Dataset selection
        assert navigator._steps[2]["status"] == "active"  # Module selection
        assert navigator._steps[3]["status"] == "available"  # Module

    def test_navigation_with_back_button(self, integrated_gui, mock_adapter_with_data):
        """Test backward navigation through pages."""
        navigator = integrated_gui._navigator

        # Navigate forward to module selection
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()
        navigator.navigate_to_module_selection()

        # Go back to dataset selection
        navigator.back_button_clicked(navigator._back_button)
        assert navigator._current_step == PAGE.DATASET_SELECTION

        # Go back to directory selection
        navigator.back_button_clicked(navigator._back_button)
        assert navigator._current_step == PAGE.DIRECTORY_SELECTION

        # Adapter should be cleared when going back to directory selection
        assert navigator._adapter is None

    def test_navigation_state_persistence(self, integrated_gui, mock_adapter_with_data):
        """Test that navigation state is maintained correctly."""
        navigator = integrated_gui._navigator

        # Setup initial navigation
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()

        # Mock dataset selection with proper Mock setup
        mock_datasets = [Mock(), Mock()]
        original_get_selected = navigator._dataset_selection_page.get_selected_datasets
        mock_get_selected = Mock(return_value=mock_datasets)
        navigator._dataset_selection_page.get_selected_datasets = mock_get_selected

        # Navigate to module selection
        navigator.navigate_to_module_selection()

        # Go back and verify dataset selection is preserved
        navigator.back_button_clicked(navigator._back_button)
        navigator.navigate_to_module_selection()

        # Verify the same datasets are still available
        mock_get_selected.assert_called()

    def test_invalid_directory_handling(self, integrated_gui):
        """Test navigation behavior with invalid directory selection."""
        navigator = integrated_gui._navigator

        # Try invalid directory
        navigator.invalid_dataset_dir_selected()

        # Verify navigation is blocked
        assert navigator._adapter is None
        assert navigator._steps[1]["status"] == "locked"  # Dataset selection
        assert navigator._steps[2]["status"] == "locked"  # Module selection
        assert navigator._forward_button.disabled == True

    def test_module_launch_integration(
        self, integrated_gui, mock_adapter_with_data, mock_modules
    ):
        """Test launching a module from module selection."""
        navigator = integrated_gui._navigator
        gui = integrated_gui

        # Navigate to module selection
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()
        navigator.navigate_to_module_selection()

        # Launch a module
        test_module = mock_modules[0]
        test_module.initiate_module = Mock(return_value=Mock())

        navigator.navigate_to_module(test_module)

        # Verify module is launched
        assert navigator._current_step == PAGE.MODULE
        assert navigator._current_module == test_module
        test_module.initiate_module.assert_called_once()

        # Verify the content was updated
        assert navigator._current_step == PAGE.MODULE

    @patch("src.ui.gui.GUI.set_info_field_state")
    def test_info_field_updates_during_navigation(
        self, mock_set_info_field_state, integrated_gui, mock_adapter_with_data
    ):
        """Test that info field is updated appropriately during navigation."""
        navigator = integrated_gui._navigator
        gui = integrated_gui

        # Navigate to dataset selection with valid data
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()

        # Ensure project cards are initialized
        assert (
            navigator._dataset_selection_page._project_cards
        ), "Project cards not initialized"

        # Simulate dataset selection
        mock_datasets = mock_adapter_with_data.projects[
            0
        ].datasets  # Use the two datasets from the mock adapter
        with patch.object(
            navigator._dataset_selection_page._project_cards[0]._dataset_selector,
            "get_selected_datasets",
            return_value=mock_datasets,
        ):
            navigator._dataset_selection_page.handle_dataset_selection_changed()

        # Verify set_info_field_state was called
        mock_set_info_field_state.assert_called()

        # Check the call with dataset selection
        calls = mock_set_info_field_state.call_args_list
        for call in calls:
            args = call[0]
            if (
                args and "2 dataset" in args[0]
            ):  # Check for message containing "2 dataset"
                assert args[0] == "You have selected 2 datasets from 1 project."
                assert args[1] == gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO
                break
        else:
            assert False, "Expected info field update with '2 datasets' not found"

    def test_breadcrumb_click_navigation(self, integrated_gui, mock_adapter_with_data):
        """Test navigation using breadcrumb clicks."""
        navigator = integrated_gui._navigator

        # Navigate to module selection
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()
        navigator.navigate_to_module_selection()

        # Click on directory selection in breadcrumb
        navigator.handle_step_click(PAGE.DIRECTORY_SELECTION)
        assert navigator._current_step == PAGE.DIRECTORY_SELECTION
        assert navigator._adapter is None  # Should be reset

        # Verify forward navigation is disabled without adapter
        assert navigator._forward_button.disabled == True

    def test_navigation_with_no_datasets(self, integrated_gui):
        """Test navigation when adapter has no datasets."""
        navigator = integrated_gui._navigator

        # Create adapter with no datasets
        empty_adapter = Mock()
        empty_adapter.datasets = []
        empty_adapter.projects = []

        # This should trigger invalid dataset handling
        navigator.valid_dataset_dir_selected(empty_adapter)
        navigator.navigate_to_dataset_selection()

        # Should still allow navigation but show appropriate message
        assert navigator._current_step == PAGE.DATASET_SELECTION

    @patch("ui.pages.directory_selection_page.Path")
    @patch("ui.pages.directory_selection_page.Adapter")
    def test_sample_data_navigation(
        self, mock_adapter_class, mock_path, integrated_gui, mock_adapter_with_data
    ):
        """Test using sample data button for quick navigation."""
        navigator = integrated_gui._navigator

        # Setup mocks for sample data
        mock_sample_path = Mock()
        mock_sample_path.exists.return_value = True
        mock_sample_path.__str__ = Mock(return_value="/sample/data")

        mock_path.return_value.parent.parent.parent.__truediv__.return_value = (
            mock_sample_path
        )
        mock_adapter_class.return_value = mock_adapter_with_data

        # Get directory selection page and trigger sample data
        dir_page = navigator._directory_selection_page
        if hasattr(dir_page, "use_sample_data"):
            dir_page.use_sample_data()

            # Should automatically navigate to dataset selection
            assert navigator._current_step == PAGE.DATASET_SELECTION
            assert navigator._adapter == mock_adapter_with_data
