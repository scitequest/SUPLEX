import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.ui.pages.module_selection_page import ModuleSelectionPage
from suplex.ui.ui_constants import PAGE


class TestModuleSelectionFlow:
    """Integration tests for ModuleSelectionPage and its interaction with
    Navigator, module viability checking, tile creation, and launching.
    """

    # -------------------------------------------------------------------------
    # Module Selection UI
    # -------------------------------------------------------------------------
    def test_get_ui_with_viable_modules(self, module_selection_page, mock_modules, mock_datasets):
        """get_ui() builds a tabbed interface with viable module tiles and updates the info field."""
        result = module_selection_page.get_ui(mock_datasets)

        assert isinstance(result, widgets.Widget)
        module_selection_page._navigator.set_info_field_state.assert_called_once()
        call_kwargs = module_selection_page._navigator.set_info_field_state.call_args[1]
        assert "modules are available" in call_kwargs["message"]

    def test_get_ui_no_viable_modules(self, module_selection_page, mock_modules, mock_datasets):
        """When no modules are viable, shows warning in info field."""
        for module in mock_modules:
            module.check_if_viable.return_value = False

        result = module_selection_page.get_ui(mock_datasets)

        assert isinstance(result, widgets.Widget)
        module_selection_page._navigator.set_info_field_state.assert_called_once()
        call_kwargs = module_selection_page._navigator.set_info_field_state.call_args[1]
        assert "No modules are compatible" in call_kwargs["message"]

    # -------------------------------------------------------------------------
    # Module Tile Creation & Events
    # -------------------------------------------------------------------------
    @patch("suplex.ui.pages.module_selection_page.Event")
    def test_create_module_tile_viable_with_click(
        self, mock_event, module_selection_page, mock_modules
    ):
        """Viable module tiles get click handlers that call navigate_to_module."""
        module = mock_modules[0]
        mock_html = Mock()

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory") as mock_factory:
            mock_factory.html_widget.return_value = mock_html

            mock_click_event = Mock()
            mock_event.side_effect = [Mock(), Mock(), mock_click_event]

            module_selection_page.get_tile_html = Mock(return_value="<div>Tile</div>")
            module_selection_page.get_module_icon = Mock(return_value="🔧")

            result = module_selection_page.create_module_tile(module, is_viable=True)

            assert isinstance(result, widgets.HTML)
            mock_click_event.on_dom_event.assert_called_once()

    # -------------------------------------------------------------------------
    # Navigation to Module
    # -------------------------------------------------------------------------
    def test_navigate_to_module_from_tile(self, navigator, mock_modules):
        """Clicking a viable module tile correctly launches the module."""
        mock_module = mock_modules[0]
        mock_module.reset_module.return_value = mock_module
        mock_module.initiate_module.return_value = Mock()

        navigator._dataset_selection_page = Mock()
        navigator._dataset_selection_page.get_selected_datasets.return_value = [Mock()]

        # Use the real method (bypass fixture mocking)
        real_method = type(navigator).navigate_to_module.__get__(navigator, type(navigator))
        real_method(mock_module)

        assert navigator._current_module == mock_module
        assert navigator._current_step is PAGE.MODULE
        mock_module.initiate_module.assert_called_once()
        navigator.update_navigation_state.assert_called_once()

    # -------------------------------------------------------------------------
    # Scheme Update Propagation
    # -------------------------------------------------------------------------
    def test_scheme_update_in_module_selection(self, module_selection_page, alt_mock_scheme):
        """Scheme updates refresh module tiles and icons."""
        module_selection_page._module_tiles = [Mock(), Mock()]

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory"):
            module_selection_page.get_ui = Mock()

            module_selection_page._navigator.update_scheme = Mock()

            module_selection_page._navigator.update_scheme(alt_mock_scheme)

            assert module_selection_page._navigator.update_scheme.called

    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------
    def test_get_ui_with_group_sorting(self, module_selection_page, mock_modules):
        """Modules are correctly grouped and sorted into tabs (Vanilla first, then alphabetical)."""
        mock_modules[0].group_name = "Vanilla"
        mock_modules[1].group_name = "Analysis"
        mock_modules[2].group_name = ""

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory") as mock_factory:
            mock_tab = Mock()
            mock_factory.tab.return_value = mock_tab
            mock_factory.grid_container.return_value = Mock()

            module_selection_page.create_module_tile = Mock(return_value=Mock())

            module_selection_page.get_ui([])

            mock_factory.tab.assert_called_once()

    def test_empty_modules_list(self, mock_navigator):
        """Empty modules list returns fallback UI."""
        page = ModuleSelectionPage(navigator=mock_navigator, modules=[])

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory") as mock_factory:
            mock_vbox = Mock()
            mock_factory.vbox.return_value = mock_vbox
            result = page.get_ui([])

            assert result == mock_vbox
            assert "No modules available" in mock_factory.html_widget.call_args[1]["value"]
