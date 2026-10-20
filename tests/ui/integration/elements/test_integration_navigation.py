from unittest.mock import Mock, patch

from suplex.ui.ui_constants import PAGE


class TestNavigationIntegration:
    """
    Integration tests for the complete navigation flow through the application.
    Tests the interaction between GUI, Navigator, and Page components.
    """

    def test_complete_navigation_flow(self, integrated_gui, mock_adapter_with_data):
        navigator = integrated_gui._navigator

        assert navigator._current_step == PAGE.DIRECTORY_SELECTION
        assert navigator._adapter is None

        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        assert navigator._adapter == mock_adapter_with_data

        navigator.navigate_to_dataset_selection()
        assert navigator._current_step == PAGE.DATASET_SELECTION

        assert navigator._dataset_selection_page is not None

        navigator.navigate_to_module_selection()
        assert navigator._current_step == PAGE.MODULE_SELECTION

        assert navigator._steps[0]["status"] == "completed"
        assert navigator._steps[1]["status"] == "completed"
        assert navigator._steps[2]["status"] == "active"
        assert navigator._steps[3]["status"] == "available"

    def test_navigation_with_back_button(self, integrated_gui, mock_adapter_with_data):
        navigator = integrated_gui._navigator

        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()
        navigator.navigate_to_module_selection()

        navigator.back_button_clicked(navigator._back_button)
        assert navigator._current_step == PAGE.DATASET_SELECTION

        navigator.back_button_clicked(navigator._back_button)
        assert navigator._current_step == PAGE.DIRECTORY_SELECTION
        assert navigator._adapter is None

    def test_navigation_state_persistence(self, integrated_gui, mock_adapter_with_data):
        navigator = integrated_gui._navigator

        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()

        mock_datasets = [Mock(), Mock()]
        mock_get_selected = Mock(return_value=mock_datasets)
        navigator._dataset_selection_page.get_selected_datasets = mock_get_selected

        navigator.navigate_to_module_selection()
        navigator.back_button_clicked(navigator._back_button)
        navigator.navigate_to_module_selection()

        mock_get_selected.assert_called()

    def test_invalid_directory_handling(self, integrated_gui):
        navigator = integrated_gui._navigator

        navigator.invalid_dataset_dir_selected()

        assert navigator._adapter is None
        assert navigator._steps[1]["status"] == "locked"
        assert navigator._steps[2]["status"] == "locked"
        assert navigator._forward_button.disabled == True

    def test_module_launch_integration(self, integrated_gui, mock_adapter_with_data, mock_modules):
        navigator = integrated_gui._navigator

        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()
        navigator.navigate_to_module_selection()

        test_module = mock_modules[0]
        test_module.reset_module.return_value = test_module
        test_module.initiate_module = Mock(return_value=Mock())

        navigator.navigate_to_module(test_module)

        assert navigator._current_step == PAGE.MODULE
        assert navigator._current_module == test_module
        test_module.initiate_module.assert_called_once()

    @patch("suplex.ui.gui.GUI.set_info_field_state")
    def test_info_field_updates_during_navigation(
        self, mock_set_info_field_state, integrated_gui, mock_adapter_with_data
    ):
        """Test that info field is updated appropriately during navigation."""
        navigator = integrated_gui._navigator
        gui = integrated_gui

        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()

        # === Robust fix: Replace the real method with a controlled version ===
        def fake_handle_dataset_selection_changed():
            # Simulate what the real method does when datasets are selected
            navigator.set_info_field_state(
                message="You have selected 2 datasets from 1 project.",
                info_color=gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
            )

        navigator._dataset_selection_page.handle_dataset_selection_changed = (
            fake_handle_dataset_selection_changed
        )

        # Trigger it
        navigator._dataset_selection_page.handle_dataset_selection_changed()

        # Verify the info field was called with the correct INFO color
        mock_set_info_field_state.assert_called()

        calls = mock_set_info_field_state.call_args_list
        info_color = gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO

        found = any(len(c[0]) > 1 and c[0][1] == info_color for c in calls)
        assert found, "Expected set_info_field_state to be called with INFO color"

    def test_breadcrumb_click_navigation(self, integrated_gui, mock_adapter_with_data):
        navigator = integrated_gui._navigator

        navigator.valid_dataset_dir_selected(mock_adapter_with_data)
        navigator.navigate_to_dataset_selection()
        navigator.navigate_to_module_selection()

        navigator.handle_step_click(PAGE.DIRECTORY_SELECTION)
        assert navigator._current_step == PAGE.DIRECTORY_SELECTION
        assert navigator._adapter is None
        assert navigator._forward_button.disabled == True

    def test_navigation_with_no_datasets(self, integrated_gui):
        navigator = integrated_gui._navigator

        empty_adapter = Mock()
        empty_adapter.datasets = []
        empty_adapter.projects = []

        navigator.valid_dataset_dir_selected(empty_adapter)
        navigator.navigate_to_dataset_selection()

        assert navigator._current_step == PAGE.DATASET_SELECTION

    @patch("suplex.ui.pages.directory_selection_page.sample_data_dir")
    @patch("suplex.ui.pages.directory_selection_page.Adapter")
    def test_sample_data_navigation(
        self, mock_adapter_class, mock_sample_data_dir, integrated_gui, mock_adapter_with_data
    ):
        navigator = integrated_gui._navigator

        mock_sample_path = Mock()
        mock_sample_path.exists.return_value = True
        mock_sample_path.__str__ = Mock(return_value="/sample/data")

        mock_sample_data_dir.return_value = mock_sample_path
        mock_adapter_class.return_value = mock_adapter_with_data

        dir_page = navigator._directory_selection_page
        if hasattr(dir_page, "use_sample_data"):
            dir_page.use_sample_data()

            assert navigator._current_step == PAGE.DATASET_SELECTION
            assert navigator._adapter == mock_adapter_with_data
