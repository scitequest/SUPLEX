import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.ui.pages.directory_selection_page import DirectorySelectionPage
from suplex.ui.pages.dataset_selection_page import DatasetSelectionPage, ProjectCard
from suplex.martin_interface.martin_interface_constants import SEARCH_MODE
from suplex.ui.ui_constants import PAGE
from suplex.ui.elements.navigator import Navigator


class TestDirectoryDatasetFlow:
    """Integration tests for the DirectorySelectionPage → DatasetSelectionPage flow,
    including directory dialog, adapter creation, project cards, filtering, and
    selection state propagation to the Navigator.
    """

    # -------------------------------------------------------------------------
    # Directory Selection Flow
    # -------------------------------------------------------------------------
    def test_directory_selection_initial_state(self, mock_navigator):
        """DirectorySelectionPage starts with correct defaults when freshly created."""
        page = DirectorySelectionPage(navigator=mock_navigator, n_modules=5)

        assert page._search_mode == SEARCH_MODE.RECURSIVE
        assert page._selected_path == ""
        assert page._n_datasets == 0
        assert page._n_projects == 0

    def test_directory_chosen_and_search(self, dir_selection_page, mock_adapter_with_data):
        """Selecting a directory in the chooser triggers search and notifies Navigator."""
        chooser = Mock(selected_path="/valid/dataset/path")

        with patch("suplex.ui.pages.directory_selection_page.Adapter") as mock_adapter_class:
            mock_adapter_class.return_value = mock_adapter_with_data

            dir_selection_page._path_display = Mock()
            dir_selection_page.search_dir = Mock()

            dir_selection_page.on_directory_chosen(chooser)

            assert dir_selection_page._selected_path == "/valid/dataset/path"
            dir_selection_page.search_dir.assert_called_once()

    @patch("suplex.ui.pages.directory_selection_page.Adapter")
    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_search_dir_valid_path(
        self,
        mock_isdir,
        mock_exists,
        mock_adapter_class,
        dir_selection_page,
        mock_adapter_with_data,
    ):
        """Valid directory creates adapter and calls valid_dataset_dir_selected."""
        # Must call get_ui() first to initialize dropdowns and spinners
        dir_selection_page.get_ui()

        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_adapter_class.return_value = mock_adapter_with_data
        dir_selection_page._selected_path = "/valid/path"

        dir_selection_page.search_dir()

        mock_adapter_class.assert_called_once_with(
            path="/valid/path",
            mode=SEARCH_MODE.RECURSIVE,
            search_depth=dir_selection_page._search_depth,
        )
        dir_selection_page._navigator.valid_dataset_dir_selected.assert_called_once_with(
            adapter=mock_adapter_with_data
        )
        assert dir_selection_page._n_datasets == len(mock_adapter_with_data.datasets)

    @patch("os.path.exists")
    def test_search_dir_invalid_path(self, mock_exists, dir_selection_page):
        """Invalid path triggers error state and invalid_dataset_dir_selected."""
        dir_selection_page.get_ui()  # ensure dropdowns exist
        dir_selection_page._selected_path = "/invalid/path"
        mock_exists.return_value = False

        dir_selection_page.search_dir()

        dir_selection_page._navigator.set_info_field_state.assert_called_with(
            message="The selected path is invalid.",
            info_color=dir_selection_page._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
        )
        dir_selection_page._navigator.invalid_dataset_dir_selected.assert_called_once()

    def test_use_sample_data_success(self, dir_selection_page, mock_adapter_with_data):
        """use_sample_data() loads sample data and advances navigation."""
        with patch("suplex.ui.pages.directory_selection_page.sample_data_dir") as mock_sample_dir:
            mock_sample_path = Mock()
            mock_sample_path.exists.return_value = True
            mock_sample_dir.return_value = mock_sample_path

            with patch("suplex.ui.pages.directory_selection_page.Adapter") as mock_adapter_class:
                mock_adapter_class.return_value = mock_adapter_with_data

                dir_selection_page.use_sample_data()

                mock_adapter_class.assert_called_once()
                dir_selection_page._navigator.valid_dataset_dir_selected.assert_called_once_with(
                    adapter=mock_adapter_with_data
                )
                dir_selection_page._navigator.navigate_to_dataset_selection.assert_called_once()

    # -------------------------------------------------------------------------
    # Dataset Selection Flow
    # -------------------------------------------------------------------------
    def test_dataset_selection_page_integration(
        self, dataset_selection_page, mock_adapter_complex_data
    ):
        """DatasetSelectionPage correctly builds project cards from adapter data."""
        dataset_selection_page._navigator.adapter = mock_adapter_complex_data

        ui = dataset_selection_page.get_ui()

        assert isinstance(ui, widgets.VBox)
        assert len(dataset_selection_page._project_cards) == len(mock_adapter_complex_data.projects)

    def test_get_selected_datasets_aggregation(self, dataset_selection_page):
        """get_selected_datasets() correctly aggregates from all ProjectCards."""
        card1 = Mock()
        card1.get_selected_datasets.return_value = [Mock(), Mock()]
        card2 = Mock()
        card2.get_selected_datasets.return_value = [Mock()]

        dataset_selection_page._project_cards = [card1, card2]

        result = dataset_selection_page.get_selected_datasets()

        assert len(result) == 3
        card1.get_selected_datasets.assert_called_once()
        card2.get_selected_datasets.assert_called_once()

    def test_handle_dataset_selection_changed_updates_info_field(self, dataset_selection_page):
        """Selection changes correctly update the Navigator's info field."""
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
    # ProjectCard Integration
    # -------------------------------------------------------------------------
    def test_project_card_reset_keep_selection(self, project_card):
        """reset_keep_dataset_selection() preserves user selections via _pending_selections (lazy init compatible)."""
        selected = [Mock(), Mock()]
        project_card._is_created = True
        project_card._dataset_selector = Mock()
        project_card._dataset_selector.get_selected_datasets.return_value = selected

        new_card = project_card.reset_keep_dataset_selection(page=Mock())

        assert isinstance(new_card, ProjectCard)
        assert new_card._pending_selections == selected
        assert not new_card.is_created

    # -------------------------------------------------------------------------
    # Cross-component Flow
    # -------------------------------------------------------------------------
    def test_directory_to_dataset_flow(self, navigator, mock_adapter_with_data):
        """Full flow: valid directory selection → dataset selection page is shown."""
        # Simulate successful directory selection
        navigator.valid_dataset_dir_selected(mock_adapter_with_data)

        # Set adapter via private attribute (property is read-only)
        navigator._adapter = mock_adapter_with_data

        # Use the REAL navigate_to_dataset_selection method
        real_navigate = Navigator.navigate_to_dataset_selection.__get__(navigator, Navigator)
        real_navigate()

        assert navigator._current_step is PAGE.DATASET_SELECTION
        assert navigator._steps[0]["status"] == "completed"
        assert navigator._steps[1]["status"] == "active"