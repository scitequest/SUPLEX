import pytest
from unittest.mock import Mock, MagicMock, patch, call
import ipywidgets as widgets

from src.ui.elements.navigator import Navigator
from ui.ui_constants import PAGE


class TestNavigator:
    def test_navigator_initialization(self, mock_gui, mock_scheme, mock_modules):
        nav = Navigator(mock_gui, mock_scheme, mock_modules)

        assert nav._gui == mock_gui
        assert nav._scheme == mock_scheme
        assert nav._modules == mock_modules
        assert nav._current_step.value == PAGE.DIRECTORY_SELECTION.value
        assert nav._adapter is None
        assert len(nav._steps) == 4
        assert nav._steps[0]["ID"].value == PAGE.DIRECTORY_SELECTION.value
        assert nav._steps[0]["status"] == "available"
        assert nav._steps[1]["ID"].value == PAGE.DATASET_SELECTION.value
        assert nav._steps[1]["status"] == "locked"
        assert nav._steps[2]["ID"].value == PAGE.MODULE_SELECTION.value
        assert nav._steps[2]["status"] == "locked"
        assert nav._steps[3]["ID"].value == PAGE.MODULE.value
        assert nav._steps[3]["status"] == "locked"

    def test_initialize_pages(self, navigator):
        assert isinstance(navigator.navigate_to_dir_selection, Mock)

        with patch("src.ui.elements.navigator.AboutPage") as mock_about:
            with patch("src.ui.elements.navigator.DirectorySelectionPage") as mock_dir:
                with patch(
                    "src.ui.elements.navigator.DatasetSelectionPage"
                ) as mock_dataset:
                    with patch(
                        "src.ui.elements.navigator.ModuleSelectionPage"
                    ) as mock_module:
                        navigator.initialize_pages()

                        assert navigator._about_page is not None
                        assert navigator._directory_selection_page is not None
                        assert navigator._dataset_selection_page is not None
                        assert navigator._module_selection_page is not None
                        navigator.navigate_to_dir_selection.assert_called_once()

    def test_update_breadcrumb(self, navigator):
        navigator._steps[0]["status"] = "completed"
        navigator._steps[1]["status"] = "active"
        navigator._steps[2]["status"] = "available"
        navigator._steps[3]["status"] = "locked"

        mock_update = navigator.update_breadcrumb
        navigator.update_breadcrumb = Navigator.update_breadcrumb.__get__(navigator)

        button_mocks = []

        def create_button(*args, **kwargs):
            btn = Mock()
            btn.add_class = Mock()
            btn.on_click = Mock()
            btn.disabled = False
            button_mocks.append(btn)
            return btn

        with patch(
            "src.ui.elements.navigator.widgets.Button", side_effect=create_button
        ):
            with patch("src.ui.elements.navigator.widgets.HBox", return_value=Mock()):
                with patch(
                    "src.ui.elements.navigator.widgets.HTML", return_value=Mock()
                ):
                    navigator.update_breadcrumb()

        assert len(button_mocks) == 4
        assert len(navigator._step_buttons) == 4
        navigator.update_breadcrumb = mock_update

    def test_handle_step_click_directory_selection(self, navigator):
        navigator.handle_step_click = Navigator.handle_step_click.__get__(navigator)
        navigator._steps[0]["status"] = "available"
        navigator.navigate_to_dir_selection.reset_mock()
        navigator.handle_step_click(PAGE.DIRECTORY_SELECTION)
        navigator.navigate_to_dir_selection.assert_called_once()

    def test_handle_step_click_dataset_selection(self, navigator):
        navigator.handle_step_click = Navigator.handle_step_click.__get__(navigator)
        navigator._steps[1]["status"] = "available"
        navigator.navigate_to_dataset_selection.reset_mock()
        navigator.handle_step_click(PAGE.DATASET_SELECTION)
        navigator.navigate_to_dataset_selection.assert_called_once()

    def test_handle_step_click_module_selection(self, navigator):
        navigator.handle_step_click = Navigator.handle_step_click.__get__(navigator)
        navigator._steps[2]["status"] = "available"
        navigator.navigate_to_module_selection.reset_mock()
        navigator.handle_step_click(PAGE.MODULE_SELECTION)
        navigator.navigate_to_module_selection.assert_called_once()

    def test_navigate_to_about_page(self, navigator):
        navigator.navigate_to_about_page = Navigator.navigate_to_about_page.__get__(
            navigator
        )

        navigator._about_page = Mock()
        navigator._about_page.get_ui = Mock(return_value=Mock())

        navigator.navigate_to_about_page()

        assert navigator._current_step.value == PAGE.ABOUT.value
        assert navigator._steps[0]["status"] == "available"
        assert all(step["status"] == "locked" for step in navigator._steps[1:])
        navigator.update_navigation_state.assert_called_once()

    def test_navigate_to_dir_selection_from_about(self, navigator):
        navigator.navigate_to_dir_selection = (
            Navigator.navigate_to_dir_selection.__get__(navigator)
        )

        navigator._current_step = PAGE.ABOUT
        navigator._directory_selection_page = Mock()
        navigator._directory_selection_page.get_ui = Mock(return_value=Mock())
        navigator._directory_selection_page.reset = Mock()

        navigator.navigate_to_dir_selection()

        assert navigator._current_step.value == PAGE.DIRECTORY_SELECTION.value
        assert navigator._steps[0]["status"] == "active"
        navigator._directory_selection_page.reset.assert_not_called()
        navigator.update_navigation_state.assert_called_once()

    def test_navigate_to_dir_selection_from_later_step(self, navigator):
        navigator.navigate_to_dir_selection = (
            Navigator.navigate_to_dir_selection.__get__(navigator)
        )

        navigator._current_step = PAGE.MODULE_SELECTION

        existing_page = Mock()
        reset_page = Mock()
        reset_page.get_ui = Mock(return_value=Mock())
        existing_page.reset = Mock(return_value=reset_page)

        navigator._directory_selection_page = existing_page

        navigator.navigate_to_dir_selection()

        existing_page.reset.assert_called_once()
        assert navigator._directory_selection_page == reset_page
        assert navigator._adapter is None
        navigator.update_navigation_state.assert_called_once()

    def test_navigate_to_dataset_selection_from_dir(self, navigator):
        navigator.navigate_to_dataset_selection = (
            Navigator.navigate_to_dataset_selection.__get__(navigator)
        )

        navigator._current_step = PAGE.DIRECTORY_SELECTION
        navigator._adapter = Mock()

        with patch("src.ui.elements.navigator.DatasetSelectionPage") as mock_page:
            mock_instance = Mock()
            mock_instance.get_ui = Mock(return_value=Mock())
            mock_page.return_value = mock_instance

            navigator.navigate_to_dataset_selection()

        assert navigator._current_step.value == PAGE.DATASET_SELECTION.value
        assert navigator._steps[0]["status"] == "completed"
        assert navigator._steps[1]["status"] == "active"
        assert navigator._steps[2]["status"] == "available"
        navigator.update_navigation_state.assert_called_once()

    def test_navigate_to_dataset_selection_from_module(self, navigator):
        navigator.navigate_to_dataset_selection = (
            Navigator.navigate_to_dataset_selection.__get__(navigator)
        )

        navigator._current_step = PAGE.MODULE
        navigator._adapter = Mock()

        existing_page = Mock()
        reset_page = Mock()
        reset_page.get_ui = Mock(return_value=Mock())
        existing_page.reset_keep_dataset_selections = Mock(return_value=reset_page)

        navigator._dataset_selection_page = existing_page

        navigator.navigate_to_dataset_selection()

        existing_page.reset_keep_dataset_selections.assert_called_once()
        assert navigator._dataset_selection_page == reset_page
        navigator.update_navigation_state.assert_called_once()

    def test_navigate_to_module_selection(self, navigator):
        navigator.navigate_to_module_selection = (
            Navigator.navigate_to_module_selection.__get__(navigator)
        )

        navigator._current_step = PAGE.DATASET_SELECTION
        navigator._adapter = Mock()
        navigator._dataset_selection_page = Mock()
        navigator._dataset_selection_page.get_selected_datasets = Mock(
            return_value=[Mock(), Mock()]
        )
        navigator._module_selection_page = Mock()
        navigator._module_selection_page.get_ui = Mock(return_value=Mock())

        navigator.navigate_to_module_selection()

        assert navigator._current_step.value == PAGE.MODULE_SELECTION.value
        assert navigator._steps[0]["status"] == "completed"
        assert navigator._steps[1]["status"] == "completed"
        assert navigator._steps[2]["status"] == "active"
        assert navigator._steps[3]["status"] == "available"
        navigator.update_navigation_state.assert_called_once()

    def test_navigate_to_module(self, navigator):
        navigator.navigate_to_module = Navigator.navigate_to_module.__get__(navigator)

        mock_module = Mock()
        mock_module.module_name = "TestModule"
        mock_module.initiate_module = Mock(return_value=Mock())

        navigator._dataset_selection_page = Mock()
        navigator._dataset_selection_page.get_selected_datasets = Mock(
            return_value=[Mock()]
        )

        navigator.navigate_to_module(mock_module)

        assert navigator._current_module == mock_module
        assert navigator._current_step.value == PAGE.MODULE.value
        assert all(step["status"] == "completed" for step in navigator._steps[:-1])
        assert navigator._steps[3]["status"] == "active"
        mock_module.initiate_module.assert_called_once()
        navigator.update_navigation_state.assert_called_once()

    def test_update_navigation_state_about_page(self, navigator):
        navigator.update_navigation_state = Navigator.update_navigation_state.__get__(
            navigator
        )

        navigator._current_step = PAGE.ABOUT

        back_button = Mock()
        back_button.disabled = False
        forward_button = Mock()
        forward_button.disabled = True

        navigator._back_button = back_button
        navigator._forward_button = forward_button

        navigator.update_navigation_state()

        assert navigator._back_button.disabled is True
        assert navigator._forward_button.disabled is False
        navigator.update_breadcrumb.assert_called_once()

    def test_update_navigation_state_dir_no_adapter(self, navigator):
        navigator.update_navigation_state = Navigator.update_navigation_state.__get__(
            navigator
        )

        navigator._current_step = PAGE.DIRECTORY_SELECTION
        navigator._adapter = None

        back_button = Mock()
        back_button.disabled = True
        forward_button = Mock()
        forward_button.disabled = False

        navigator._back_button = back_button
        navigator._forward_button = forward_button

        navigator.update_navigation_state()

        assert navigator._back_button.disabled is False
        assert navigator._forward_button.disabled is True
        navigator.update_breadcrumb.assert_called_once()

    def test_update_navigation_state_dir_with_adapter(self, navigator):
        navigator.update_navigation_state = Navigator.update_navigation_state.__get__(
            navigator
        )

        navigator._current_step = PAGE.DIRECTORY_SELECTION
        navigator._adapter = Mock()

        back_button = Mock()
        back_button.disabled = True
        forward_button = Mock()
        forward_button.disabled = True

        navigator._back_button = back_button
        navigator._forward_button = forward_button

        navigator.update_navigation_state()

        assert navigator._back_button.disabled is False
        assert navigator._forward_button.disabled is False
        navigator.update_breadcrumb.assert_called_once()

    def test_update_navigation_state_module(self, navigator):
        navigator.update_navigation_state = Navigator.update_navigation_state.__get__(
            navigator
        )

        navigator._current_step = PAGE.MODULE

        back_button = Mock()
        back_button.disabled = True
        forward_button = Mock()
        forward_button.disabled = False

        navigator._back_button = back_button
        navigator._forward_button = forward_button

        navigator.update_navigation_state()

        assert navigator._back_button.disabled is False
        assert navigator._forward_button.disabled is True
        navigator.update_breadcrumb.assert_called_once()

    def test_back_button_clicked(self, navigator):
        navigator.back_button_clicked = Navigator.back_button_clicked.__get__(navigator)

        button = Mock()

        test_cases = [
            (PAGE.DIRECTORY_SELECTION, "navigate_to_about_page"),
            (PAGE.DATASET_SELECTION, "navigate_to_dir_selection"),
            (PAGE.MODULE_SELECTION, "navigate_to_dataset_selection"),
            (PAGE.MODULE, "navigate_to_module_selection"),
        ]

        for current_step, method_name in test_cases:
            navigator._current_step = current_step
            navigator._adapter = Mock()
            mock_method = getattr(navigator, method_name)
            mock_method.reset_mock()

            navigator.back_button_clicked(button)

            mock_method.assert_called_once()

    def test_forward_button_clicked(self, navigator):
        navigator.forward_button_clicked = Navigator.forward_button_clicked.__get__(
            navigator
        )

        button = Mock()

        test_cases = [
            (PAGE.ABOUT, "navigate_to_dir_selection"),
            (PAGE.DIRECTORY_SELECTION, "navigate_to_dataset_selection"),
            (PAGE.DATASET_SELECTION, "navigate_to_module_selection"),
        ]

        for current_step, method_name in test_cases:
            navigator._current_step = current_step
            navigator._adapter = Mock()
            mock_method = getattr(navigator, method_name)
            mock_method.reset_mock()

            navigator.forward_button_clicked(button)

            mock_method.assert_called_once()

    def test_invalid_dataset_dir_selected(self, navigator):
        navigator.invalid_dataset_dir_selected = (
            Navigator.invalid_dataset_dir_selected.__get__(navigator)
        )

        navigator.invalid_dataset_dir_selected()

        assert navigator._adapter is None
        assert all(step["status"] == "locked" for step in navigator._steps[1:])
        navigator.update_navigation_state.assert_called_once()

    def test_valid_dataset_dir_selected(self, navigator):
        navigator.valid_dataset_dir_selected = (
            Navigator.valid_dataset_dir_selected.__get__(navigator)
        )

        mock_adapter = Mock()

        navigator.valid_dataset_dir_selected(mock_adapter)

        assert navigator._adapter == mock_adapter
        assert navigator._steps[1]["status"] == "available"
        navigator.update_navigation_state.assert_called_once()

    def test_update_scheme(self, navigator):
        navigator.update_scheme = Navigator.update_scheme.__get__(navigator)

        new_scheme = Mock()
        new_scheme.NAME = "NewScheme"
        new_scheme.ICON = Mock()
        new_scheme.ICON.BACKWARD = "⬅"
        new_scheme.ICON.FORWARD = "➡"
        new_scheme.ICON.PAGE = Mock()
        new_scheme.ICON.PAGE.DIRECTORY_SELECTION = "📂"
        new_scheme.ICON.PAGE.DATASET_SELECTION = "📈"
        new_scheme.ICON.PAGE.MODULE_SELECTION = "📦"
        new_scheme.ICON.PAGE.MODULE = "⚙"

        with patch("src.ui.elements.navigator.get_navigator_styles"):
            navigator.update_scheme(new_scheme)

        assert navigator._scheme == new_scheme
        assert navigator._back_button.description == "⬅"
        assert navigator._forward_button.description == "➡"
        navigator.update_breadcrumb.assert_called_once()

    def test_properties(self, navigator):
        mock_adapter = Mock()
        navigator._adapter = mock_adapter

        assert navigator.adapter == mock_adapter
        assert navigator.current_scheme == navigator._gui.current_scheme
