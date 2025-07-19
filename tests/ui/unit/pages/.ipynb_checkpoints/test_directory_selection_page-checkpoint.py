import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import os
import ipywidgets as widgets

from src.ui.pages.directory_selection_page import DirectorySelectionPage
from martin_interface.martin_interface_constants import (
    SEARCH_MODE,
    MARTIN_MEASURE_DIR_DEPTH,
)


class TestDirectorySelectionPage:
    def test_initialization(self, mock_navigator):
        page = DirectorySelectionPage(
            navigator=mock_navigator,
            n_modules=5,
            search_mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL,
            search_depth=5,
            selected_path="/custom/path",
            n_datasets=15,
            n_projects=3,
        )

        assert page._navigator == mock_navigator
        assert page._search_mode == SEARCH_MODE.ITERATIVE_BOUNDED_ALL
        assert page._search_depth == 5
        assert page._selected_path == "/custom/path"
        assert page._n_datasets == 15
        assert page._n_projects == 3
        assert page._n_modules == 5

    def test_initialization_defaults(self, mock_navigator):
        page = DirectorySelectionPage(navigator=mock_navigator, n_modules=3)

        assert page._search_mode == SEARCH_MODE.RECURSIVE
        assert page._search_depth == MARTIN_MEASURE_DIR_DEPTH
        assert page._selected_path == ""
        assert page._n_datasets == 0
        assert page._n_projects == 0

    @patch("src.ui.pages.directory_selection_page.WidgetFactory")
    def test_get_ui_success(self, mock_factory, dir_selection_page):
        mock_vbox = Mock()
        mock_hbox = Mock()
        mock_factory.vbox.return_value = mock_vbox
        mock_factory.hbox.return_value = mock_hbox

        dir_selection_page.create_header = Mock(return_value=Mock())
        dir_selection_page.create_main_content = Mock(return_value=Mock())
        dir_selection_page.get_updated_stats_box = Mock(return_value=Mock())

        result = dir_selection_page.get_ui()

        assert result == mock_vbox
        dir_selection_page.create_header.assert_called_once()
        dir_selection_page.create_main_content.assert_called_once()
        dir_selection_page.get_updated_stats_box.assert_called_once()

    @patch("src.ui.pages.directory_selection_page.WidgetFactory")
    def test_create_header(self, mock_factory, dir_selection_page):
        mock_html = Mock()
        mock_vbox = Mock()
        mock_factory.html_widget.return_value = mock_html
        mock_factory.vbox.return_value = mock_vbox

        result = dir_selection_page.create_header()

        assert result == mock_vbox
        assert mock_factory.html_widget.call_count == 2

        subtitle_call = mock_factory.html_widget.call_args_list[1]
        assert "@keyframes fadeInOut" in subtitle_call[1]["value"]

    @patch("src.ui.pages.directory_selection_page.WidgetFactory")
    def test_create_path_section(self, mock_factory, dir_selection_page):
        dir_selection_page._selected_path = "/test/path"
        dir_selection_page.open_directory_dialog = Mock()

        mock_html = Mock()
        mock_button = Mock()
        mock_factory.html_widget.return_value = mock_html
        mock_factory.button_emphasis.return_value = mock_button
        mock_factory.info_field_default.return_value = Mock()
        mock_factory.hbox.return_value = Mock()

        result = dir_selection_page.create_path_section()

        mock_factory.html_widget.assert_called_with(
            value="/test/path", width="auto", height="auto"
        )

        mock_factory.button_emphasis.assert_called_once()
        assert (
            mock_factory.button_emphasis.call_args[1]["description"]
            == "Select Directory"
        )

        mock_button.on_click.assert_called_once()

    @patch("src.ui.pages.directory_selection_page.WidgetFactory")
    def test_create_search_options_section(self, mock_factory, dir_selection_page):
        mock_dropdown = Mock()
        mock_number = Mock()
        mock_factory.dropdown.return_value = mock_dropdown
        mock_factory.number_input.return_value = mock_number
        mock_factory.label.return_value = Mock()
        mock_factory.hbox.return_value = Mock()

        result = dir_selection_page.create_search_options_section()

        dropdown_call = mock_factory.dropdown.call_args
        assert dropdown_call[1]["value"] == dir_selection_page._search_mode
        assert len(dropdown_call[1]["options"]) == len(SEARCH_MODE)

        number_call = mock_factory.number_input.call_args
        assert number_call[1]["value"] == dir_selection_page._search_depth
        assert number_call[1]["min_value"] == 0
        assert number_call[1]["max_value"] == 30

    def test_get_updated_stats_box(self, dir_selection_page):
        with patch(
            "src.ui.pages.directory_selection_page.WidgetFactory"
        ) as mock_factory:
            mock_html = Mock()
            mock_hbox = Mock()
            mock_factory.html_widget.return_value = mock_html
            mock_factory.hbox.return_value = mock_hbox

            result = dir_selection_page.get_updated_stats_box()

            assert result == mock_hbox
            assert mock_factory.html_widget.call_count == 3

            html_calls = [
                call[1]["value"] for call in mock_factory.html_widget.call_args_list
            ]
            assert any("5" in html and "Modules Loaded" in html for html in html_calls)
            assert any(
                "10" in html and "Datasets Collected" in html for html in html_calls
            )
            assert any(
                "2" in html and "Projects Detected" in html for html in html_calls
            )

    @patch("src.ui.pages.directory_selection_page.tk")
    @patch("src.ui.pages.directory_selection_page.filedialog")
    def test_open_directory_dialog_success(
        self, mock_filedialog, mock_tk, dir_selection_page
    ):
        mock_root = Mock()
        mock_tk.Tk.return_value = mock_root
        mock_filedialog.askdirectory.return_value = "/new/selected/path"

        dir_selection_page._path_display = Mock()
        dir_selection_page.search_dir = Mock()

        dir_selection_page.open_directory_dialog()

        assert dir_selection_page._selected_path == "/new/selected/path"
        assert dir_selection_page._path_display.value == "/new/selected/path"
        dir_selection_page.search_dir.assert_called_once()
        mock_root.destroy.assert_called_once()

    @patch("src.ui.pages.directory_selection_page.tk")
    @patch("src.ui.pages.directory_selection_page.filedialog")
    def test_open_directory_dialog_cancelled(
        self, mock_filedialog, mock_tk, dir_selection_page
    ):
        mock_root = Mock()
        mock_tk.Tk.return_value = mock_root
        mock_filedialog.askdirectory.return_value = ""

        dir_selection_page.search_dir = Mock()
        dir_selection_page.open_directory_dialog()

        assert dir_selection_page._selected_path == "/test/path"
        dir_selection_page.search_dir.assert_not_called()

    @patch("src.ui.pages.directory_selection_page.os.path.exists")
    @patch("src.ui.pages.directory_selection_page.os.path.isdir")
    @patch("src.ui.pages.directory_selection_page.Adapter")
    def test_search_dir_success(
        self, mock_adapter_class, mock_isdir, mock_exists, dir_selection_page
    ):
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_adapter = Mock()
        mock_adapter.datasets = [Mock(), Mock(), Mock()]
        mock_adapter.projects = [Mock()]
        mock_adapter_class.return_value = mock_adapter

        dir_selection_page._search_mode_dropdown = Mock(value=SEARCH_MODE.RECURSIVE)
        dir_selection_page._search_depth_spinner = Mock(value=5)
        dir_selection_page._stats_box = Mock()

        dir_selection_page.search_dir()

        mock_adapter_class.assert_called_once_with(
            path="/test/path", mode=SEARCH_MODE.RECURSIVE, search_depth=5
        )

        assert dir_selection_page._n_datasets == 3
        assert dir_selection_page._n_projects == 1
        dir_selection_page._navigator.valid_dataset_dir_selected.assert_called_once_with(
            adapter=mock_adapter
        )

    def test_search_dir_no_path(self, dir_selection_page):
        dir_selection_page._selected_path = ""
        dir_selection_page._search_mode_dropdown = Mock(value=SEARCH_MODE.RECURSIVE)
        dir_selection_page._search_depth_spinner = Mock(value=5)

        dir_selection_page.search_dir()

        dir_selection_page._navigator.set_info_field_state.assert_called_with(
            message="No path selected.",
            info_color=dir_selection_page._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING,
        )

    @patch("src.ui.pages.directory_selection_page.os.path.exists")
    def test_search_dir_invalid_path(self, mock_exists, dir_selection_page):
        mock_exists.return_value = False
        dir_selection_page._search_mode_dropdown = Mock(value=SEARCH_MODE.RECURSIVE)
        dir_selection_page._search_depth_spinner = Mock(value=5)

        dir_selection_page.search_dir()

        dir_selection_page._navigator.set_info_field_state.assert_called_with(
            message="The selected path is invalid.",
            info_color=dir_selection_page._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
        )
        dir_selection_page._navigator.invalid_dataset_dir_selected.assert_called_once()

    @patch("src.ui.pages.directory_selection_page.Path")
    @patch("src.ui.pages.directory_selection_page.Adapter")
    def test_use_sample_data_success(
        self, mock_adapter_class, mock_path_class, dir_selection_page
    ):
        mock_sample_path = Mock()
        mock_sample_path.exists.return_value = True
        mock_sample_path.__str__ = Mock(return_value="/path/to/sample_data")

        mock_path_instance = Mock()

        parent1 = Mock()
        parent2 = Mock()
        parent3 = Mock()

        mock_path_instance.parent = parent1
        parent1.parent = parent2
        parent2.parent = parent3

        def truediv_side_effect(other):
            if other == "sample_data":
                return mock_sample_path
            return Mock()

        parent3.__truediv__ = Mock(side_effect=truediv_side_effect)
        mock_path_class.return_value = mock_path_instance

        mock_adapter = Mock()
        mock_adapter.datasets = [Mock(), Mock()]
        mock_adapter_class.return_value = mock_adapter

        dir_selection_page.use_sample_data()

        mock_adapter_class.assert_called_once_with(
            path="/path/to/sample_data", mode=SEARCH_MODE.RECURSIVE, search_depth=5
        )

        dir_selection_page._navigator.valid_dataset_dir_selected.assert_called_once_with(
            adapter=mock_adapter
        )
        dir_selection_page._navigator.navigate_to_dataset_selection.assert_called_once()

    def test_reset(self, dir_selection_page):
        new_page = dir_selection_page.reset()

        assert isinstance(new_page, DirectorySelectionPage)
        assert new_page is not dir_selection_page
        assert new_page._n_modules == 5
        assert new_page._selected_path == ""
        assert new_page._n_datasets == 0
        assert new_page._n_projects == 0
