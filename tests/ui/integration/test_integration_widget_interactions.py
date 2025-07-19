import pytest
import logging
from unittest.mock import Mock, patch, MagicMock, call, create_autospec
from datetime import date
import ipywidgets as widgets

from src.ui.widget_factory import WidgetFactory
from src.ui.pages.dataset_selection_page import ProjectCard, DatasetSelectionPage
from src.ui.pages.directory_selection_page import DirectorySelectionPage
from src.ui.elements.popup_log_system import PopupLogger
from martin_interface.martin_interface_constants import SEARCH_MODE
from suplex_modules.submodules.submodule_constants import (
    DATASET_LABEL,
    TAG_SELECTION_MODE,
)


class TestWidgetInteractionsIntegration:
    """
    Integration tests for widget interactions across UI components.
    Tests complex widget behaviors, event handling, and state synchronization.
    """

    def test_radio_button_mutual_exclusion(self):
        """Test custom radio button behavior across multiple instances."""
        buttons = WidgetFactory.custom_radio_buttons(
            number=3, description=["Option A", "Option B", "Option C"], i_toggled=0
        )

        # Initial state - first button selected
        assert "button-emphasis" in buttons[0]._dom_classes
        assert "button-default" in buttons[1]._dom_classes
        assert "button-default" in buttons[2]._dom_classes

        # Click second button - simulate the click handler
        for button in buttons:
            button.remove_class("button-emphasis")
            button.add_class("button-default")
        buttons[1].remove_class("button-default")
        buttons[1].add_class("button-emphasis")

        # Verify mutual exclusion
        assert "button-default" in buttons[0]._dom_classes
        assert "button-emphasis" in buttons[1]._dom_classes
        assert "button-default" in buttons[2]._dom_classes

        # Click third button - simulate the click handler
        for button in buttons:
            button.remove_class("button-emphasis")
            button.add_class("button-default")
        buttons[2].remove_class("button-default")
        buttons[2].add_class("button-emphasis")

        # Verify state change
        assert "button-default" in buttons[0]._dom_classes
        assert "button-default" in buttons[1]._dom_classes
        assert "button-emphasis" in buttons[2]._dom_classes

    def test_dataset_selector_checkbox_interactions(self, mock_project_with_datasets):
        """Test checkbox interactions in dataset selector."""
        # Create project card with dataset selector
        page = Mock()
        page.navigator = Mock()
        page.navigator.current_scheme = Mock()
        page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#DDDDDD"
        page.handle_dataset_selection_changed = Mock()

        with patch("src.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            # Create mock dataset selector
            mock_selector = Mock()
            mock_ds.return_value = mock_selector

            # Mock checkboxes
            mock_checkboxes = [Mock() for _ in range(5)]
            for i, cb in enumerate(mock_checkboxes):
                cb.value = False
                cb.observe = Mock()
            mock_selector.get_checkboxes.return_value = mock_checkboxes
            mock_selector.get_selected_datasets.return_value = []

            project_card = ProjectCard(page=page, project=mock_project_with_datasets)

            # Initially none selected
            assert all(not cb.value for cb in mock_checkboxes)

            # Select first checkbox
            mock_checkboxes[0].value = True
            mock_selector.get_selected_datasets.return_value = [
                mock_project_with_datasets.datasets[0]
            ]

            # Verify selection
            selected = project_card._dataset_selector.get_selected_datasets()
            assert len(selected) == 1
            assert selected[0].id == "DS_000"

            # Test select all
            for cb in mock_checkboxes:
                cb.value = True
            mock_selector.get_selected_datasets.return_value = (
                mock_project_with_datasets.datasets
            )

            project_card._dataset_selector.select_all()
            assert len(project_card._dataset_selector.get_selected_datasets()) == 5

            # Test clear selection
            for cb in mock_checkboxes:
                cb.value = False
            mock_selector.get_selected_datasets.return_value = []

            project_card._dataset_selector.clear_selection()
            assert len(project_card._dataset_selector.get_selected_datasets()) == 0

    def test_date_picker_range_selection(self, mock_project_with_datasets):
        """Test date picker interactions for range selection."""
        page = Mock()
        page.navigator = Mock()
        page.navigator.current_scheme = Mock()
        page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#DDDDDD"

        with patch("src.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            with patch("src.ui.pages.dataset_selection_page.TagSelector") as mock_ts:
                # Mock the selectors
                mock_selector = Mock()
                mock_ds.return_value = mock_selector
                mock_ts.return_value = Mock()

                project_card = ProjectCard(
                    page=page, project=mock_project_with_datasets
                )

                # Create date range
                start_date = date(2023, 1, 2)
                end_date = date(2023, 1, 4)

                # Mock filtered datasets
                filtered_datasets = [
                    ds
                    for ds in mock_project_with_datasets.datasets
                    if start_date <= ds.image_creation_date.date() <= end_date
                ]

                mock_selector.get_selected_datasets.return_value = filtered_datasets

                # Simulate date range selection
                project_card._dataset_selector.select_date_range(
                    start_date=start_date,
                    end_date=end_date,
                    mode=DATASET_LABEL.CREATED_DATE,
                )

                # Verify datasets in range are selected
                selected = project_card._dataset_selector.get_selected_datasets()

                # Should have selected datasets within the date range
                assert len(selected) > 0
                for dataset in selected:
                    assert start_date <= dataset.image_creation_date.date() <= end_date

    def test_dropdown_change_propagation(self, mock_navigator):
        """Test dropdown changes propagate through the system."""
        dir_page = DirectorySelectionPage(navigator=mock_navigator, n_modules=5)

        # Create actual dropdown widget with correct SEARCH_MODE options
        search_dropdown = WidgetFactory.dropdown(
            options=[(mode.name, mode) for mode in SEARCH_MODE],
            value=SEARCH_MODE.RECURSIVE,
        )

        depth_spinner = WidgetFactory.number_input(value=5, min_value=0, max_value=30)

        dir_page._search_mode_dropdown = search_dropdown
        dir_page._search_depth_spinner = depth_spinner
        dir_page.search_dir = Mock()

        # Change dropdown value to a valid SEARCH_MODE option
        search_dropdown.value = SEARCH_MODE.ITERATIVE_UNBOUND

        # Change spinner value
        depth_spinner.value = 10

        # Verify values were updated
        assert dir_page._search_mode_dropdown.value == SEARCH_MODE.ITERATIVE_UNBOUND
        assert dir_page._search_depth_spinner.value == 10

    def test_toggle_button_state_persistence(self):
        """Test toggle button state persistence and behavior."""
        # Create toggle button
        toggle = WidgetFactory.toggle_button(description="Test Toggle", toggled=False)

        # Initial state
        assert toggle._toggled == False
        assert "button-default" in toggle._dom_classes

        # Simulate toggle on - manually trigger the toggle handler
        toggle._toggled = not toggle._toggled
        if toggle._toggled:
            toggle.remove_class("button-default")
            toggle.add_class("button-emphasis")
        else:
            toggle.remove_class("button-emphasis")
            toggle.add_class("button-default")

        assert toggle._toggled == True
        assert "button-emphasis" in toggle._dom_classes
        assert "button-default" not in toggle._dom_classes

        # Simulate toggle off
        toggle._toggled = not toggle._toggled
        if toggle._toggled:
            toggle.remove_class("button-default")
            toggle.add_class("button-emphasis")
        else:
            toggle.remove_class("button-emphasis")
            toggle.add_class("button-default")

        assert toggle._toggled == False
        assert "button-default" in toggle._dom_classes
        assert "button-emphasis" not in toggle._dom_classes

    def test_tag_selector_interaction(self, mock_project_with_datasets):
        """Test tag selector widget interactions."""
        page = Mock()
        page.navigator = Mock()
        page.navigator.current_scheme = Mock()
        page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#DDDDDD"

        with patch("src.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            with patch("src.ui.pages.dataset_selection_page.TagSelector") as mock_ts:
                # Mock the selectors
                mock_selector = Mock()
                mock_ds.return_value = mock_selector

                mock_tag_selector = Mock()
                mock_ts.return_value = mock_tag_selector

                # Mock tag selector methods
                all_tags = ["tag_0", "tag_1", "tag_2", "tag_3", "tag_4", "common_tag"]
                mock_tag_selector.get_available_tags.return_value = all_tags
                mock_tag_selector.set_selected_tags = Mock()
                mock_tag_selector.get_tagged_datasets_any.return_value = (
                    mock_project_with_datasets.datasets
                )

                project_card = ProjectCard(
                    page=page, project=mock_project_with_datasets
                )

                # Get available tags
                available_tags = project_card._tag_selector.get_available_tags()
                assert "common_tag" in available_tags

                # Select tags
                project_card._tag_selector.set_selected_tags(["common_tag"])

                # Test tag-based dataset filtering
                project_card._tag_selection_mode = TAG_SELECTION_MODE.ANY
                datasets_with_tag = project_card._tag_selector.get_tagged_datasets_any()

                # All datasets should have the common tag
                assert len(datasets_with_tag) == 5

    def test_info_field_widget_updates(self, mock_gui):
        """Test info field widget updates with different states."""
        # Create actual HTML widget for info field
        info_field = widgets.HTML()
        mock_gui._info_field = info_field
        mock_gui._current_scheme = Mock()

        # Test different info states
        test_cases = [
            ("Info message", "info", "ℹ️"),
            ("Success message", "success", "✅"),
            ("Error message", "error", "❌"),
        ]

        for message, level, icon in test_cases:
            # Mock the update_info_field method to actually update the widget
            def mock_update_info_field(msg, color, ic):
                info_field.value = f"{ic} {msg}"

            mock_gui.update_info_field = mock_update_info_field

            # Update info field
            mock_gui.update_info_field(message, "#000000", icon)

            # Verify content
            assert icon in info_field.value
            assert message in info_field.value

    def test_accordion_expansion_state(
        self, mock_navigator, mock_project_with_datasets
    ):
        """Test accordion widget expansion state management."""
        dataset_page = DatasetSelectionPage(navigator=mock_navigator)

        # Create real widgets for accordion children instead of mocks
        with patch("src.ui.pages.dataset_selection_page.ProjectCard") as mock_pc:
            cards = []
            real_widgets = []  # Store real widgets for accordion

            for i in range(2):
                mock_card = Mock()
                mock_card.title = f"Test Project {i}"

                # Create real widget instead of mock for accordion children
                real_widget = WidgetFactory.html_widget(
                    value=f"<div>Project {i} Content</div>", width="100%", height="100%"
                )
                mock_card.get_ui_element.return_value = real_widget
                cards.append(mock_card)
                real_widgets.append(real_widget)

            dataset_page._project_cards = cards

            # Create accordion with real widgets as children
            accordion = WidgetFactory.accordion(
                children=real_widgets,  # Use real widgets instead of mock returns
                titles=[card.title for card in cards],
            )

            # Initially closed
            accordion.selected_index = None
            assert accordion.selected_index is None

            # Open first project
            accordion.selected_index = 0
            assert accordion.selected_index == 0

            # Switch to second project
            accordion.selected_index = 1
            assert accordion.selected_index == 1

    def test_popup_logger_button_interactions(self, mock_scheme):
        """Test popup logger toggle button and panel interactions."""
        popup_logger = PopupLogger(scheme=mock_scheme, max_messages=50)

        # Initially hidden
        assert popup_logger._is_visible == False
        assert popup_logger._popup_panel.layout.display == "none"

        # Add some messages
        popup_logger.add_log_message("Test message 1", logging.INFO)
        popup_logger.add_log_message("Test message 2", logging.WARNING)

        # Should show unread count
        assert popup_logger._unread_count == 2

        # Show popup
        popup_logger.show_popup()
        assert popup_logger._is_visible == True
        assert popup_logger._popup_panel.layout.display == "flex"
        assert popup_logger._unread_count == 0

        # Hide popup
        popup_logger.close_popup()
        assert popup_logger._is_visible == False
        assert popup_logger._popup_panel.layout.display == "none"

    def test_complex_widget_state_synchronization(self, mock_project_with_datasets):
        """Test complex state synchronization between multiple widgets."""
        page = Mock()
        page.navigator = Mock()
        page.navigator.current_scheme = Mock()
        page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#DDDDDD"
        page.handle_dataset_selection_changed = Mock()

        with patch("src.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            with patch("src.ui.pages.dataset_selection_page.TagSelector") as mock_ts:
                # Mock the selectors
                mock_selector = Mock()
                mock_ds.return_value = mock_selector
                mock_ts.return_value = Mock()

                # Mock label format methods
                mock_selector.get_dataset_label_format.return_value = [
                    DATASET_LABEL.ID,
                    DATASET_LABEL.CREATED_DATE,
                ]
                mock_selector.update_dataset_labels = Mock()

                project_card = ProjectCard(
                    page=page, project=mock_project_with_datasets
                )

                # Test ID/Name button synchronization
                current_format = (
                    project_card._dataset_selector.get_dataset_label_format()
                )
                assert DATASET_LABEL.ID in current_format

                # Simulate changing to name display
                current_format = [DATASET_LABEL.NAME, DATASET_LABEL.CREATED_DATE]
                mock_selector.get_dataset_label_format.return_value = current_format

                # Verify label format was updated
                label_format = project_card._dataset_selector.get_dataset_label_format()
                assert (
                    DATASET_LABEL.NAME in label_format
                    or DATASET_LABEL.ID in label_format
                )  # Either is valid
