import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.ui.elements.navigator import Navigator
from suplex.ui.ui_constants import PAGE


class TestNavigationFlow:
    """Integration tests for the Navigator component and its full multi-step flow:
    About → Directory Selection → Dataset Selection → Module Selection → Module.
    """

    # -------------------------------------------------------------------------
    # Initial Navigation State
    # -------------------------------------------------------------------------
    def test_initial_navigation_state(self, navigator):
        """Navigator starts at DIRECTORY_SELECTION with correct step statuses."""
        assert navigator._current_step is PAGE.DIRECTORY_SELECTION
        assert navigator._steps[0]["status"] == "available"
        assert navigator._steps[1]["status"] == "locked"
        assert navigator._steps[2]["status"] == "locked"
        assert navigator._steps[3]["status"] == "locked"

    # -------------------------------------------------------------------------
    # Full Happy Path Flow (up to dataset selection - module selection is tested elsewhere)
    # -------------------------------------------------------------------------
    def test_full_navigation_flow(self, navigator, mock_adapter_with_data):
        """Happy path up to dataset selection."""
        real_valid_dir = type(navigator).valid_dataset_dir_selected.__get__(
            navigator, type(navigator)
        )
        real_nav_to_dataset = type(navigator).navigate_to_dataset_selection.__get__(
            navigator, type(navigator)
        )

        navigator.navigate_to_dir_selection()
        assert navigator._current_step is PAGE.DIRECTORY_SELECTION

        real_valid_dir(mock_adapter_with_data)
        assert navigator._adapter == mock_adapter_with_data
        assert navigator._steps[1]["status"] == "available"

        real_nav_to_dataset()
        assert navigator._current_step is PAGE.DATASET_SELECTION
        assert navigator._steps[0]["status"] == "completed"
        assert navigator._steps[1]["status"] == "active"

    # -------------------------------------------------------------------------
    # Breadcrumb & Step Clicks
    # -------------------------------------------------------------------------
    def test_breadcrumb_click_navigation(self, navigator):
        """Clicking breadcrumb steps correctly navigates to the right page."""
        navigator.navigate_to_dataset_selection = Mock()
        navigator.navigate_to_module_selection = Mock()

        navigator._steps[1]["status"] = "available"
        navigator._steps[2]["status"] = "available"

        navigator.handle_step_click(PAGE.DATASET_SELECTION)
        navigator.navigate_to_dataset_selection.assert_called_once()

        navigator.handle_step_click(PAGE.MODULE_SELECTION)
        navigator.navigate_to_module_selection.assert_called_once()

    # -------------------------------------------------------------------------
    # Back / Forward Buttons
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "current_step, expected_back_target, expected_forward_target",
        [
            (PAGE.DIRECTORY_SELECTION, "navigate_to_about_page", "navigate_to_dataset_selection"),
            (PAGE.DATASET_SELECTION, "navigate_to_dir_selection", "navigate_to_module_selection"),
            (PAGE.MODULE_SELECTION, "navigate_to_dataset_selection", None),
            (PAGE.MODULE, "navigate_to_module_selection", None),
        ],
    )
    def test_back_and_forward_buttons(
        self, navigator, current_step, expected_back_target, expected_forward_target
    ):
        """Back and forward buttons call the correct navigation methods."""
        navigator._current_step = current_step

        if expected_back_target:
            with patch.object(navigator, expected_back_target) as mock_back:
                navigator.back_button_clicked(Mock())
                mock_back.assert_called_once()

        if expected_forward_target:
            with patch.object(navigator, expected_forward_target) as mock_forward:
                navigator.forward_button_clicked(Mock())
                mock_forward.assert_called_once()

    # -------------------------------------------------------------------------
    # Dataset Directory Handling
    # -------------------------------------------------------------------------
    def test_valid_dataset_dir_selected(self, navigator, mock_adapter_with_data):
        """Valid directory updates adapter and unlocks next step."""
        real_method = type(navigator).valid_dataset_dir_selected.__get__(navigator, type(navigator))
        real_method(mock_adapter_with_data)

        assert navigator._adapter == mock_adapter_with_data
        assert navigator._steps[1]["status"] == "available"
        navigator.update_navigation_state.assert_called_once()

    def test_invalid_dataset_dir_selected(self, navigator):
        """Invalid directory clears adapter and locks later steps."""
        real_method = type(navigator).invalid_dataset_dir_selected.__get__(
            navigator, type(navigator)
        )
        real_method()

        assert navigator._adapter is None
        assert all(step["status"] == "locked" for step in navigator._steps[1:])
        navigator.update_navigation_state.assert_called_once()

    # -------------------------------------------------------------------------
    # Scheme Propagation
    # -------------------------------------------------------------------------
    def test_scheme_update_affects_navigator(self, navigator, alt_mock_scheme):
        """Scheme updates propagate to icons, buttons, and breadcrumb."""
        navigator._back_button = Mock()
        navigator._forward_button = Mock()

        with patch("suplex.ui.elements.navigator.get_navigator_styles"):
            navigator.update_scheme(alt_mock_scheme)

        assert navigator._scheme == alt_mock_scheme
        assert navigator._back_button.description == alt_mock_scheme.ICON.BACKWARD
        assert navigator._forward_button.description == alt_mock_scheme.ICON.FORWARD
        navigator.update_breadcrumb.assert_called_once()
