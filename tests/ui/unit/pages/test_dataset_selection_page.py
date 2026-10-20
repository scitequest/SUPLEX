import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets
from datetime import date

from suplex.ui.pages.dataset_selection_page import DatasetSelectionPage, ProjectCard
from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_SELECTOR_MODE,
    DATASET_LABEL,
    SELECTION_MODE,
)


class TestDatasetSelectionPage:
    """Tests for DatasetSelectionPage – the page that displays projects in an accordion
    and allows dataset selection with filters (date range, tags).
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def test_initialization(self, mock_navigator):
        """DatasetSelectionPage initializes with navigator reference and empty project cards."""
        page = DatasetSelectionPage(navigator=mock_navigator)

        assert page._navigator == mock_navigator
        assert page._project_cards == []

    # -------------------------------------------------------------------------
    # UI rendering (get_ui)
    # -------------------------------------------------------------------------
    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    def test_get_ui_no_adapter(self, mock_factory, dataset_selection_page):
        """When no adapter exists, returns a helpful error HTML widget."""
        dataset_selection_page._navigator.adapter = None
        mock_html = Mock()
        mock_factory.html_widget.return_value = mock_html

        result = dataset_selection_page.get_ui()

        assert result == mock_html
        mock_factory.html_widget.assert_called_once()
        assert "No adapter available" in mock_factory.html_widget.call_args[1]["value"]

    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    def test_get_ui_no_projects(self, mock_factory, dataset_selection_page):
        """When adapter has no projects, shows a clear message."""
        dataset_selection_page._navigator.adapter.projects = []
        mock_html = Mock()
        mock_factory.html_widget.return_value = mock_html

        result = dataset_selection_page.get_ui()

        assert result == mock_html
        assert "No projects found" in mock_factory.html_widget.call_args[1]["value"]

    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    @patch("suplex.ui.pages.dataset_selection_page.ProjectCard")
    def test_get_ui_with_projects(
        self, mock_project_card_class, mock_factory, dataset_selection_page, mock_project
    ):
        """With valid projects, creates ProjectCard instances and builds an accordion."""
        dataset_selection_page._navigator.adapter.projects = [mock_project]

        mock_project_card = Mock()
        mock_project_card.title = "Test Project"
        mock_project_card_class.return_value = mock_project_card

        mock_accordion = Mock()
        mock_accordion.children = [Mock()]
        mock_factory.accordion.return_value = mock_accordion
        mock_factory.vbox.return_value = Mock()

        result = dataset_selection_page.get_ui()

        mock_project_card_class.assert_called_once_with(
            page=dataset_selection_page, project=mock_project
        )
        assert len(dataset_selection_page._project_cards) == 1
        mock_factory.accordion.assert_called_once()
        assert mock_accordion.selected_index is None  # all projects start closed

    # -------------------------------------------------------------------------
    # Dataset selection helpers
    # -------------------------------------------------------------------------
    def test_get_selected_datasets(self, dataset_selection_page):
        """get_selected_datasets() aggregates selections from all project cards."""
        card1 = Mock()
        card1.get_selected_datasets.return_value = [Mock(), Mock()]
        card2 = Mock()
        card2.get_selected_datasets.return_value = [Mock()]

        dataset_selection_page._project_cards = [card1, card2]

        result = dataset_selection_page.get_selected_datasets()

        assert len(result) == 3
        card1.get_selected_datasets.assert_called_once()
        card2.get_selected_datasets.assert_called_once()

    def test_handle_dataset_selection_changed_no_selection(self, dataset_selection_page):
        """With no datasets selected, shows default info field message."""
        card1 = Mock()
        card1.get_selected_datasets.return_value = []
        dataset_selection_page._project_cards = [card1]

        dataset_selection_page.handle_dataset_selection_changed()

        dataset_selection_page._navigator.set_info_field_state.assert_called_with(
            message="No datasets selected.",
            info_color=dataset_selection_page._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT,
        )

    def test_handle_dataset_selection_changed_with_selections(self, dataset_selection_page):
        """With selections, shows count of datasets and projects in info field."""
        card1 = Mock()
        card1.get_selected_datasets.return_value = [Mock(), Mock()]
        card2 = Mock()
        card2.get_selected_datasets.return_value = [Mock()]
        dataset_selection_page._project_cards = [card1, card2]

        dataset_selection_page.handle_dataset_selection_changed()

        expected_message = "You have selected 3 datasets from 2 projects."
        dataset_selection_page._navigator.set_info_field_state.assert_called_with(
            message=expected_message,
            info_color=dataset_selection_page._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
        )

    # -------------------------------------------------------------------------
    # Scheme & reset
    # -------------------------------------------------------------------------
    def test_update_scheme(self, dataset_selection_page):
        """update_scheme() forwards the new scheme to every project card."""
        card1 = Mock()
        card2 = Mock()
        dataset_selection_page._project_cards = [card1, card2]

        new_scheme = Mock()
        dataset_selection_page.update_scheme(new_scheme)

        card1.update_scheme.assert_called_once_with(new_scheme)
        card2.update_scheme.assert_called_once_with(new_scheme)

    def test_reset_keep_dataset_selections(self, dataset_selection_page):
        """reset_keep_dataset_selections() creates a new page preserving selections."""
        card = Mock()
        card.reset_keep_dataset_selection.return_value = Mock()
        dataset_selection_page._project_cards = [card]

        new_page = dataset_selection_page.reset_keep_dataset_selections()

        assert isinstance(new_page, DatasetSelectionPage)
        assert new_page is not dataset_selection_page
        card.reset_keep_dataset_selection.assert_called_once()

    def test_reset(self, dataset_selection_page):
        """reset() returns a completely fresh page (no selections preserved)."""
        new_page = dataset_selection_page.reset()

        assert isinstance(new_page, DatasetSelectionPage)
        assert new_page is not dataset_selection_page
        assert new_page._project_cards == []

class TestProjectCard:
    """Tests for the individual ProjectCard component used inside DatasetSelectionPage."""

    # -------------------------------------------------------------------------
    # Initialization & basic properties
    # -------------------------------------------------------------------------
    def test_initialization(self, mock_page, mock_project_with_datasets):
        """ProjectCard initializes lazily (DatasetSelector/TagSelector created in generate_ui)."""
        with patch("suplex.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            with patch("suplex.ui.pages.dataset_selection_page.TagSelector") as mock_ts:
                card = ProjectCard(page=mock_page, project=mock_project_with_datasets)

                assert card._page == mock_page
                assert card._project == mock_project_with_datasets
                assert card._borders == []
                assert card._current_date_format == DATASET_LABEL.CREATED_DATE
                assert card._tag_selection_mode == SELECTION_MODE.ANY
                assert card._dataset_selector is None
                assert card._tag_selector is None
                assert not card.is_created

                # Selectors are created lazily only when generate_ui() is called
                mock_ds.assert_not_called()
                mock_ts.assert_not_called()

    def test_title_property(self, project_card):
        """title property returns the project name."""
        assert project_card.title == "Test Project"

    # -------------------------------------------------------------------------
    # UI building
    # -------------------------------------------------------------------------
    @patch("suplex.ui.pages.dataset_selection_page.DatasetSelector")
    @patch("suplex.ui.pages.dataset_selection_page.TagSelector")
    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    def test_generate_ui(self, mock_factory, mock_ts, mock_ds, project_card):
        """generate_ui() builds a two-column HBox, lazily creating DatasetSelector and TagSelector."""
        project_card.create_left_column = Mock(return_value=Mock())
        project_card.create_right_column = Mock(return_value=Mock())
        mock_hbox = Mock()
        mock_factory.hbox.return_value = mock_hbox

        # Prevent issues with checkbox iteration in generate_ui
        mock_ds.return_value.get_checkboxes.return_value = []

        result = project_card.generate_ui()

        assert result == mock_hbox
        mock_ds.assert_called_once()
        mock_ts.assert_called_once()
        project_card.create_left_column.assert_called_once()
        project_card.create_right_column.assert_called_once()

    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    def test_create_left_column(self, mock_factory, project_card):
        """Left column contains ID/Name toggle, select/deselect all, and dataset selector."""
        mock_button = Mock()
        mock_factory.custom_radio_buttons.return_value = [mock_button, mock_button]
        mock_factory.button_success.return_value = mock_button
        mock_factory.button_danger.return_value = mock_button
        mock_factory.hbox.return_value = Mock()
        mock_factory.vbox.return_value = Mock()

        project_card._dataset_selector = Mock()
        project_card._dataset_selector.get_checkboxes.return_value = [Mock(), Mock()]
        project_card._dataset_selector.get_ui_element.return_value = Mock()

        result = project_card.create_left_column()

        assert mock_factory.custom_radio_buttons.called
        assert mock_factory.button_success.called
        assert mock_factory.button_danger.called

    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    def test_create_right_column(self, mock_factory, project_card):
        """Right column contains date filter and tag filter sections."""
        project_card.create_date_filter_box = Mock(return_value=Mock())
        project_card.create_tag_box = Mock(return_value=Mock())
        mock_factory.hbox.return_value = Mock()
        mock_factory.vbox.return_value = Mock()

        result = project_card.create_right_column()

        project_card.create_date_filter_box.assert_called_once()
        project_card.create_tag_box.assert_called_once()

    # -------------------------------------------------------------------------
    # Date filter helpers
    # -------------------------------------------------------------------------
    def test_get_earliest_date(self, project_card):
        """get_earliest_date() returns the earliest date for the chosen mode."""
        assert project_card.get_earliest_date(DATASET_LABEL.CREATED_DATE) == date(2023, 1, 1)
        assert project_card.get_earliest_date(DATASET_LABEL.MEASURE_DATE) == date(2023, 1, 2)

    def test_get_latest_date(self, project_card):
        """get_latest_date() returns the latest date for the chosen mode."""
        assert project_card.get_latest_date(DATASET_LABEL.CREATED_DATE) == date(2023, 1, 5)
        assert project_card.get_latest_date(DATASET_LABEL.MEASURE_DATE) == date(2023, 1, 6)

    # -------------------------------------------------------------------------
    # Dataset selection
    # -------------------------------------------------------------------------
    def test_get_selected_datasets(self, project_card):
        """get_selected_datasets() delegates to the DatasetSelector."""
        mock_datasets = [Mock(), Mock()]
        project_card._dataset_selector = Mock()
        project_card._dataset_selector.get_selected_datasets.return_value = mock_datasets

        result = project_card.get_selected_datasets()

        assert result == mock_datasets
        project_card._dataset_selector.get_selected_datasets.assert_called_once()

    def test_select_datasets(self, project_card):
        """select_datasets() delegates to the DatasetSelector."""
        mock_datasets = [Mock(), Mock()]
        project_card._dataset_selector = Mock()
        project_card.select_datasets(mock_datasets)
        project_card._dataset_selector.select_datasets.assert_called_once_with(
            datasets=mock_datasets
        )

    # -------------------------------------------------------------------------
    # Scheme & reset
    # -------------------------------------------------------------------------
    def test_update_scheme(self, project_card):
        """update_scheme() updates border colors on all tracked elements."""
        new_scheme = Mock()
        new_scheme.LAYOUT_COLOR = Mock()
        new_scheme.LAYOUT_COLOR.WIDGET = Mock()
        new_scheme.LAYOUT_COLOR.WIDGET.ACCORDION = Mock()
        new_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#000000"

        border1 = Mock()
        border2 = Mock()
        project_card._borders = [border1, border2]

        project_card.update_scheme(new_scheme)

        assert border1.border == "1px solid #000000"
        assert border2.border == "1px solid #000000"

    def test_reset(self, project_card):
        """reset() returns a fresh ProjectCard."""
        new_card = project_card.reset()
        assert isinstance(new_card, ProjectCard)
        assert new_card is not project_card

    def test_reset_keep_dataset_selection(self, project_card, mock_page):
        """reset_keep_dataset_selection() preserves selected datasets in _pending_selections (applied later in generate_ui)."""
        mock_datasets = [Mock(), Mock()]
        # Simulate that UI was generated and some datasets were selected
        project_card._is_created = True
        project_card._dataset_selector = Mock()
        project_card._dataset_selector.get_selected_datasets.return_value = mock_datasets

        new_card = project_card.reset_keep_dataset_selection(page=mock_page)

        assert isinstance(new_card, ProjectCard)
        assert new_card is not project_card
        assert new_card._pending_selections == mock_datasets
        assert not new_card.is_created
        # Note: select_datasets() on the new selector happens lazily inside generate_ui(), not during reset_keep

    # -------------------------------------------------------------------------
    # ID / Name toggle handlers (detailed behavior test)
    # -------------------------------------------------------------------------
    @patch("suplex.ui.pages.dataset_selection_page.WidgetFactory")
    def test_id_name_toggle_handlers(self, mock_factory, project_card):
        """ID/Name radio buttons correctly update the dataset label format."""
        button1 = Mock()  # ID button
        button2 = Mock()  # Name button
        mock_factory.custom_radio_buttons.return_value = [button1, button2]
        mock_factory.button_success.return_value = Mock()
        mock_factory.button_danger.return_value = Mock()
        mock_factory.hbox.return_value = Mock()
        mock_factory.vbox.return_value = Mock()

        project_card._dataset_selector = Mock()
        project_card._dataset_selector.get_checkboxes.return_value = []
        project_card._dataset_selector.get_ui_element.return_value = Mock()
        project_card._dataset_selector.get_dataset_label_format.return_value = [
            DATASET_LABEL.NAME,
            DATASET_LABEL.CREATED_DATE,
        ]

        project_card.create_left_column()

        id_handler = button1.on_click.call_args[0][0]
        name_handler = button2.on_click.call_args[0][0]

        # Switch to ID
        id_handler(button1)
        update_call = project_card._dataset_selector.update_dataset_labels.call_args
        assert DATASET_LABEL.ID in update_call[1]["label_parts"]
        assert DATASET_LABEL.NAME not in update_call[1]["label_parts"]

        # Switch to Name
        name_handler(button2)
        update_call = project_card._dataset_selector.update_dataset_labels.call_args
        assert DATASET_LABEL.NAME in update_call[1]["label_parts"]
        assert DATASET_LABEL.ID not in update_call[1]["label_parts"]