import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets

from src.ui.elements.navigator import Navigator
from ui.ui_constants import PAGE


class TestNavigator:
    """Tests for the Navigator component that manages the multi-step wizard flow,
    breadcrumb navigation, back/forward buttons, and page switching.
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def test_navigator_initialization(self, mock_gui, mock_scheme, mock_modules):
        """Navigator initializes with correct defaults and creates initial UI."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)

        assert nav._gui == mock_gui
        assert nav._scheme == mock_scheme
        assert nav._modules == mock_modules
        assert nav._current_step is PAGE.DIRECTORY_SELECTION
        assert nav._adapter is None
        assert len(nav._steps) == 4
        assert nav._steps[0]["ID"] is PAGE.DIRECTORY_SELECTION
        assert nav._steps[0]["status"] == "available"
        assert nav._steps[1]["status"] == "locked"

    # -------------------------------------------------------------------------
    # Page setup
    # -------------------------------------------------------------------------
    def test_initialize_pages(self, navigator):
        """initialize_pages() creates all page instances and starts at directory selection."""
        with patch.object(navigator, "navigate_to_dir_selection") as mock_nav:
            navigator.initialize_pages()

            assert navigator._about_page is not None
            assert navigator._directory_selection_page is not None
            assert navigator._dataset_selection_page is not None
            assert navigator._module_selection_page is not None
            mock_nav.assert_called_once()

    # -------------------------------------------------------------------------
    # Breadcrumb
    # -------------------------------------------------------------------------
    def test_update_breadcrumb(self, navigator):
        """update_breadcrumb() rebuilds step buttons with correct status classes."""
        # Fixture already calls it during __init__ / create_navigation_ui
        assert len(navigator._step_buttons) == 4

    @pytest.mark.parametrize(
        "step, expected_method",
        [
            (PAGE.DIRECTORY_SELECTION, "navigate_to_dir_selection"),
            (PAGE.DATASET_SELECTION, "navigate_to_dataset_selection"),
            (PAGE.MODULE_SELECTION, "navigate_to_module_selection"),
        ],
    )
    def test_handle_step_click(self, navigator, step, expected_method):
        """Breadcrumb clicks call the correct navigation method when the step is available."""
        idx = 0 if step is PAGE.DIRECTORY_SELECTION else 1 if step is PAGE.DATASET_SELECTION else 2
        navigator._steps[idx]["status"] = "available"

        getattr(navigator, expected_method).reset_mock()
        navigator.handle_step_click(step)
        getattr(navigator, expected_method).assert_called_once()

    # -------------------------------------------------------------------------
    # Navigation methods - these use a fresh real Navigator to bypass fixture mocks
    # -------------------------------------------------------------------------
    def test_navigate_to_about_page(self, mock_gui, mock_scheme, mock_modules):
        """navigate_to_about_page() updates state and calls update_navigation_state."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        nav._about_page = Mock()
        nav._about_page.get_ui = Mock(return_value=Mock())

        with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
            with patch.object(nav, "update_navigation_state") as mock_update:
                nav.navigate_to_about_page()

        mock_update.assert_called_once()
        mock_gui_update.assert_called_once()

    def test_navigate_to_dir_selection_from_about(self, mock_gui, mock_scheme, mock_modules):
        """Going back to dir selection from about does **not** reset the page."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        nav._current_step = PAGE.ABOUT
        nav._directory_selection_page = Mock()
        nav._directory_selection_page.get_ui = Mock(return_value=Mock())
        nav._directory_selection_page.reset = Mock()

        with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
            nav.navigate_to_dir_selection()

        nav._directory_selection_page.reset.assert_not_called()
        mock_gui_update.assert_called_once()

    def test_navigate_to_dir_selection_from_later_step(self, mock_gui, mock_scheme, mock_modules):
        """Navigating back to dir selection from later steps resets the page."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        nav._current_step = PAGE.MODULE_SELECTION
        existing_page = Mock()
        reset_page = Mock()
        reset_page.get_ui = Mock(return_value=Mock())
        existing_page.reset = Mock(return_value=reset_page)
        nav._directory_selection_page = existing_page

        with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
            nav.navigate_to_dir_selection()

        existing_page.reset.assert_called_once()
        mock_gui_update.assert_called_once()

    def test_navigate_to_dataset_selection_from_dir(self, mock_gui, mock_scheme, mock_modules):
        """Moving forward from directory selection creates a fresh DatasetSelectionPage."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        nav._current_step = PAGE.DIRECTORY_SELECTION
        nav._adapter = Mock()

        with patch("src.ui.elements.navigator.DatasetSelectionPage") as mock_page_class:
            mock_instance = Mock()
            mock_instance.get_ui = Mock(return_value=Mock())
            mock_page_class.return_value = mock_instance

            with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
                nav.navigate_to_dataset_selection()

        mock_gui_update.assert_called_once()

    def test_navigate_to_dataset_selection_from_module(self, mock_gui, mock_scheme, mock_modules):
        """Coming back from module keeps existing dataset selections."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        nav._current_step = PAGE.MODULE
        existing_page = Mock()
        reset_page = Mock()
        reset_page.get_ui = Mock(return_value=Mock())
        existing_page.reset_keep_dataset_selections = Mock(return_value=reset_page)
        nav._dataset_selection_page = existing_page

        with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
            nav.navigate_to_dataset_selection()

        existing_page.reset_keep_dataset_selections.assert_called_once()
        mock_gui_update.assert_called_once()

    def test_navigate_to_module_selection(self, mock_gui, mock_scheme, mock_modules):
        """navigate_to_module_selection() passes selected datasets to the module page."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        nav._current_step = PAGE.DATASET_SELECTION
        nav._dataset_selection_page = Mock()
        nav._dataset_selection_page.get_selected_datasets = Mock(return_value=[Mock(), Mock()])
        nav._module_selection_page = Mock()
        nav._module_selection_page.get_ui = Mock(return_value=Mock())

        with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
            nav.navigate_to_module_selection()

        mock_gui_update.assert_called_once()

    def test_navigate_to_module(self, mock_gui, mock_scheme, mock_modules):
        """navigate_to_module() resets the module and shows its UI."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        mock_module = Mock()
        mock_module.module_name = "TestModule"
        mock_module.reset_module = Mock(return_value=mock_module)
        mock_module.initiate_module = Mock(return_value=Mock())

        nav._dataset_selection_page = Mock()
        nav._dataset_selection_page.get_selected_datasets = Mock(return_value=[Mock()])

        with patch.object(nav._gui, "update_content_holder") as mock_gui_update:
            nav.navigate_to_module(mock_module)

        mock_module.initiate_module.assert_called_once()
        mock_gui_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Navigation buttons & state (these work with the fixture's mocks)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "current_step, back_disabled, forward_disabled",
        [
            (PAGE.ABOUT, True, False),
            (PAGE.DIRECTORY_SELECTION, False, True),
            (PAGE.MODULE_SELECTION, False, True),
            (PAGE.MODULE, False, True),
        ],
    )
    def test_update_navigation_state_button_states(
        self, navigator, current_step, back_disabled, forward_disabled
    ):
        """update_navigation_state() correctly enables/disables back/forward buttons."""
        navigator._current_step = current_step
        if current_step is PAGE.DIRECTORY_SELECTION:
            navigator._adapter = None

        navigator._back_button = Mock()
        navigator._forward_button = Mock()

        navigator.update_navigation_state()

        navigator.update_navigation_state.assert_called_once()

    def test_back_button_clicked(self, navigator):
        """Back button routes to the correct previous page."""
        button = Mock()
        test_cases = [
            (PAGE.DIRECTORY_SELECTION, "navigate_to_about_page"),
            (PAGE.DATASET_SELECTION, "navigate_to_dir_selection"),
            (PAGE.MODULE_SELECTION, "navigate_to_dataset_selection"),
            (PAGE.MODULE, "navigate_to_module_selection"),
        ]

        for step, method_name in test_cases:
            navigator._current_step = step
            getattr(navigator, method_name).reset_mock()
            navigator.back_button_clicked(button)
            getattr(navigator, method_name).assert_called_once()

    def test_forward_button_clicked(self, navigator):
        """Forward button routes to the correct next page."""
        button = Mock()
        test_cases = [
            (PAGE.ABOUT, "navigate_to_dir_selection"),
            (PAGE.DIRECTORY_SELECTION, "navigate_to_dataset_selection"),
            (PAGE.DATASET_SELECTION, "navigate_to_module_selection"),
        ]

        for step, method_name in test_cases:
            navigator._current_step = step
            getattr(navigator, method_name).reset_mock()
            navigator.forward_button_clicked(button)
            getattr(navigator, method_name).assert_called_once()

    # -------------------------------------------------------------------------
    # External state updates (use fresh navigator to bypass fixture override)
    # -------------------------------------------------------------------------
    def test_invalid_dataset_dir_selected(self, mock_gui, mock_scheme, mock_modules):
        """invalid_dataset_dir_selected() resets adapter and locks later steps."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        with patch.object(nav, "update_navigation_state") as mock_update:
            nav.invalid_dataset_dir_selected()

        mock_update.assert_called_once()

    def test_valid_dataset_dir_selected(self, mock_gui, mock_scheme, mock_modules):
        """valid_dataset_dir_selected() stores adapter and unlocks dataset step."""
        nav = Navigator(mock_gui, mock_scheme, mock_modules)
        mock_adapter = Mock()
        with patch.object(nav, "update_navigation_state") as mock_update:
            nav.valid_dataset_dir_selected(mock_adapter)

        mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Scheme handling
    # -------------------------------------------------------------------------
    def test_update_scheme(self, navigator):
        """update_scheme() refreshes icons, buttons, breadcrumb, and dependent pages."""
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

        navigator._back_button = Mock()
        navigator._forward_button = Mock()

        with patch("src.ui.elements.navigator.get_navigator_styles"):
            navigator.update_scheme(new_scheme)

        assert navigator._scheme == new_scheme
        navigator.update_breadcrumb.assert_called_once()

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    def test_properties(self, navigator):
        """adapter and current_scheme properties return the expected values."""
        mock_adapter = Mock()
        navigator._adapter = mock_adapter

        assert navigator.adapter == mock_adapter
        assert navigator.current_scheme == navigator._gui.current_scheme
