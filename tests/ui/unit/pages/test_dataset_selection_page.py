import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, date
import ipywidgets as widgets

from src.ui.pages.dataset_selection_page import DatasetSelectionPage, ProjectCard
from suplex_modules.submodules.submodule_constants import (
    DATASET_SELECTOR_MODE,
    DATASET_LABEL,
    TAG_SELECTION_MODE,
)

class TestDatasetSelectionPage:
    def test_initialization(self, mock_navigator):
        page = DatasetSelectionPage(navigator=mock_navigator)

        assert page._navigator == mock_navigator
        assert page._project_cards == []

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_get_ui_no_adapter(self, mock_factory, dataset_selection_page):
        dataset_selection_page._navigator.adapter = None
        mock_html = Mock()
        mock_factory.html_widget.return_value = mock_html

        result = dataset_selection_page.get_ui()

        assert result == mock_html
        mock_factory.html_widget.assert_called_once()
        assert "No adapter available" in mock_factory.html_widget.call_args[1]["value"]

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_get_ui_no_projects(self, mock_factory, dataset_selection_page):
        dataset_selection_page._navigator.adapter.projects = []
        mock_html = Mock()
        mock_factory.html_widget.return_value = mock_html

        result = dataset_selection_page.get_ui()

        assert result == mock_html
        assert "No projects found" in mock_factory.html_widget.call_args[1]["value"]

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    @patch("src.ui.pages.dataset_selection_page.ProjectCard")
    def test_get_ui_with_projects(
        self,
        mock_project_card_class,
        mock_factory,
        dataset_selection_page,
        mock_project,
    ):
        dataset_selection_page._navigator.adapter.projects = [mock_project]

        mock_project_card = Mock()
        mock_project_card.title = "Test Project"
        mock_project_card.get_ui_element.return_value = Mock()
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
        assert mock_accordion.selected_index is None

    def test_get_selected_datasets(self, dataset_selection_page):
        card1 = Mock()
        card1.get_selected_datasets.return_value = [Mock(), Mock()]
        card2 = Mock()
        card2.get_selected_datasets.return_value = [Mock()]

        dataset_selection_page._project_cards = [card1, card2]

        result = dataset_selection_page.get_selected_datasets()

        assert len(result) == 3
        card1.get_selected_datasets.assert_called_once()
        card2.get_selected_datasets.assert_called_once()

    def test_handle_dataset_selection_changed_no_selection(
        self, dataset_selection_page
    ):
        card1 = Mock()
        card1.get_selected_datasets.return_value = []
        dataset_selection_page._project_cards = [card1]

        dataset_selection_page.handle_dataset_selection_changed()

        dataset_selection_page._navigator.set_info_field_state.assert_called_with(
            message="No datasets selected.",
            info_color=dataset_selection_page._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT,
        )

    def test_handle_dataset_selection_changed_with_selections(
        self, dataset_selection_page
    ):
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

    def test_update_scheme(self, dataset_selection_page):
        card1 = Mock()
        card2 = Mock()
        dataset_selection_page._project_cards = [card1, card2]

        new_scheme = Mock()
        dataset_selection_page.update_scheme(new_scheme)

        card1.update_scheme.assert_called_once_with(new_scheme)
        card2.update_scheme.assert_called_once_with(new_scheme)

    def test_reset_keep_dataset_selections(self, dataset_selection_page):
        card = Mock()
        card.reset_keep_dataset_selection.return_value = Mock()
        dataset_selection_page._project_cards = [card]

        new_page = dataset_selection_page.reset_keep_dataset_selections()

        assert isinstance(new_page, DatasetSelectionPage)
        assert new_page is not dataset_selection_page
        card.reset_keep_dataset_selection.assert_called_once()

    def test_reset(self, dataset_selection_page):
        new_page = dataset_selection_page.reset()

        assert isinstance(new_page, DatasetSelectionPage)
        assert new_page is not dataset_selection_page
        assert new_page._project_cards == []


class TestProjectCard:
    def test_initialization(self, mock_page, mock_project_with_datasets):
        with patch("src.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            with patch("src.ui.pages.dataset_selection_page.TagSelector") as mock_ts:
                card = ProjectCard(page=mock_page, project=mock_project_with_datasets)

                assert card._page == mock_page
                assert card._project == mock_project_with_datasets
                assert card._borders == []
                assert card._current_date_format == DATASET_LABEL.CREATED_DATE
                assert card._tag_selection_mode == TAG_SELECTION_MODE.ANY

                # Verify selectors created
                mock_ds.assert_called_once()
                mock_ts.assert_called_once()

    def test_title_property(self, project_card):
        assert project_card.title == "Test Project"

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_get_ui_element(self, mock_factory, project_card):
        project_card.create_left_column = Mock(return_value=Mock())
        project_card.create_right_column = Mock(return_value=Mock())
        mock_hbox = Mock()
        mock_factory.hbox.return_value = mock_hbox

        result = project_card.get_ui_element()

        assert result == mock_hbox
        project_card.create_left_column.assert_called_once()
        project_card.create_right_column.assert_called_once()

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_create_left_column(self, mock_factory, project_card):
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

        success_button = mock_factory.button_success.return_value
        danger_button = mock_factory.button_danger.return_value
        success_button.on_click.assert_called()
        danger_button.on_click.assert_called()

    def test_get_earliest_date(self, project_card):
        result = project_card.get_earliest_date(DATASET_LABEL.CREATED_DATE)
        assert result == date(2023, 1, 1)

        # Test with MEASURE_DATE
        result = project_card.get_earliest_date(DATASET_LABEL.MEASURE_DATE)
        assert result == date(2023, 1, 2)

    def test_get_latest_date(self, project_card):
        result = project_card.get_latest_date(DATASET_LABEL.CREATED_DATE)
        assert result == date(2023, 1, 5)

        result = project_card.get_latest_date(DATASET_LABEL.MEASURE_DATE)
        assert result == date(2023, 1, 6)

    def test_get_earliest_date_no_dates(self, mock_page):
        project = Mock()
        project.name = "Empty Project"
        project.datasets = []

        with patch("src.ui.pages.dataset_selection_page.DatasetSelector"):
            with patch("src.ui.pages.dataset_selection_page.TagSelector"):
                card = ProjectCard(page=mock_page, project=project)

        with patch("src.ui.pages.dataset_selection_page.date") as mock_date:
            mock_date.today.return_value = date(2024, 1, 1)
            result = card.get_earliest_date(DATASET_LABEL.CREATED_DATE)
            assert result == date(2024, 1, 1)

    def test_get_selected_datasets(self, project_card):
        mock_datasets = [Mock(), Mock()]
        project_card._dataset_selector.get_selected_datasets.return_value = (
            mock_datasets
        )

        result = project_card.get_selected_datasets()

        assert result == mock_datasets
        project_card._dataset_selector.get_selected_datasets.assert_called_once()

    def test_select_datasets(self, project_card):
        mock_datasets = [Mock(), Mock()]

        project_card.select_datasets(mock_datasets)
        project_card._dataset_selector.select_datasets.assert_called_once_with(
            datasets=mock_datasets
        )

    def test_update_scheme(self, project_card):
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
        new_card = project_card.reset()

        assert isinstance(new_card, ProjectCard)
        assert new_card is not project_card
        assert new_card._project == project_card._project

    def test_reset_keep_dataset_selection(self, project_card, mock_page):
        mock_datasets = [Mock(), Mock()]
        project_card._dataset_selector.get_selected_datasets.return_value = (
            mock_datasets
        )

        with patch("src.ui.pages.dataset_selection_page.DatasetSelector") as mock_ds:
            with patch("src.ui.pages.dataset_selection_page.TagSelector"):
                new_selector = Mock()
                mock_ds.return_value = new_selector

                new_card = project_card.reset_keep_dataset_selection(page=mock_page)

        assert isinstance(new_card, ProjectCard)
        assert new_card is not project_card
        new_selector.select_datasets.assert_called_once_with(mock_datasets)

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_create_date_filter_box(self, mock_factory, project_card):
        mock_radio = Mock()
        mock_factory.radio_buttons.return_value = [mock_radio, mock_radio]
        mock_factory.label.return_value = Mock()
        mock_factory.date_picker.return_value = Mock()
        mock_factory.button_success.return_value = Mock()
        mock_factory.button_danger.return_value = Mock()
        mock_factory.hbox.return_value = Mock()
        mock_factory.vbox.return_value = Mock()

        result = project_card.create_date_filter_box()

        radio_call = mock_factory.radio_buttons.call_args
        assert radio_call[1]["options"] == [
            DATASET_LABEL.CREATED_DATE.value,
            DATASET_LABEL.MEASURE_DATE.value,
        ]

        assert mock_factory.date_picker.call_count == 2

        assert mock_factory.button_success.called
        assert mock_factory.button_danger.called

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_create_tag_box(self, mock_factory, project_card):
        mock_button = Mock()
        mock_factory.custom_radio_buttons.return_value = [mock_button, mock_button]
        mock_factory.button_success.return_value = mock_button
        mock_factory.button_danger.return_value = mock_button
        mock_factory.hbox.return_value = Mock()
        mock_factory.vbox.return_value = Mock()

        project_card._tag_selector = Mock()
        project_card._tag_selector.get_ui_element.return_value = Mock()

        result = project_card.create_tag_box()

        radio_call = mock_factory.custom_radio_buttons.call_args
        assert radio_call[1]["description"] == ["If Any", "If All"]

        assert mock_factory.button_success.called
        assert mock_factory.button_danger.called

    @patch("src.ui.pages.dataset_selection_page.WidgetFactory")
    def test_id_name_toggle_handlers(self, mock_factory, project_card):
        button1 = Mock()
        button2 = Mock()
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

        id_handler(button1)
        update_call = project_card._dataset_selector.update_dataset_labels.call_args
        assert DATASET_LABEL.ID in update_call[1]["label_parts"]
        assert DATASET_LABEL.NAME not in update_call[1]["label_parts"]

        name_handler(button2)
        update_call = project_card._dataset_selector.update_dataset_labels.call_args
        assert DATASET_LABEL.NAME in update_call[1]["label_parts"]
        assert DATASET_LABEL.ID not in update_call[1]["label_parts"]

        # Testing back and forth
        id_handler(button1)
        update_call = project_card._dataset_selector.update_dataset_labels.call_args
        assert DATASET_LABEL.ID in update_call[1]["label_parts"]
        assert DATASET_LABEL.NAME not in update_call[1]["label_parts"]

        # Testing if state unchanged
        id_handler(button1)
        assert (
            update_call
            == project_card._dataset_selector.update_dataset_labels.call_args
        )

        # Testing back and forth
        name_handler(button2)
        update_call = project_card._dataset_selector.update_dataset_labels.call_args
        assert DATASET_LABEL.NAME in update_call[1]["label_parts"]
        assert DATASET_LABEL.ID not in update_call[1]["label_parts"]

        # Testing if state unchanged
        name_handler(button2)
        assert (
            update_call
            == project_card._dataset_selector.update_dataset_labels.call_args
        )
