import pytest
from unittest.mock import Mock, patch, mock_open
import base64

import ipywidgets as widgets

from suplex.ui.pages.module_selection_page import ModuleSelectionPage
from suplex.suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE


class TestModuleSelectionPage:
    """Tests for ModuleSelectionPage – the page that displays modules grouped by category
    as interactive tiles, with viability checking against selected datasets.
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def test_initialization(self, mock_navigator, mock_modules):
        """ModuleSelectionPage initializes with navigator and modules."""
        page = ModuleSelectionPage(navigator=mock_navigator, modules=mock_modules)

        assert page._navigator == mock_navigator
        assert page._modules == mock_modules
        assert page._module_tiles == []
        assert page._tile_events == []

    # -------------------------------------------------------------------------
    # Main UI (get_ui)
    # -------------------------------------------------------------------------
    @patch("suplex.ui.pages.module_selection_page.WidgetFactory")
    def test_get_ui_success(self, mock_factory, module_selection_page, mock_modules):
        """get_ui() builds a tabbed interface with grouped module tiles."""
        mock_datasets = [Mock(), Mock()]
        mock_tab_widget = Mock()
        mock_tab_widget.children = []
        mock_tab_widget.add_class = Mock()
        mock_tab_widget.set_title = Mock()
        mock_factory.tab.return_value = mock_tab_widget

        module_selection_page.create_module_tile = Mock(side_effect=[Mock(), Mock(), Mock()])
        mock_factory.grid_container.return_value = Mock()

        result = module_selection_page.get_ui(mock_datasets)

        assert result == mock_tab_widget

        for module in mock_modules:
            module.check_if_viable.assert_called_once_with(mock_datasets)

        assert module_selection_page.create_module_tile.call_count == 3

        module_selection_page._navigator.set_info_field_state.assert_called_once()
        call_kwargs = module_selection_page._navigator.set_info_field_state.call_args[1]
        assert "2 of 3 modules are available" in call_kwargs["message"]

    def test_get_ui_no_viable_modules(self, module_selection_page, mock_modules):
        """When no modules are viable, shows a warning in the info field."""
        for module in mock_modules:
            module.check_if_viable.return_value = False

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory"):
            module_selection_page.create_module_tile = Mock(return_value=Mock())
            module_selection_page.get_ui([])

        module_selection_page._navigator.set_info_field_state.assert_called_once()
        call_kwargs = module_selection_page._navigator.set_info_field_state.call_args[1]
        assert "No modules are compatible" in call_kwargs["message"]

    def test_get_ui_empty_modules(self, mock_navigator):
        """With no modules at all, shows a fallback message."""
        page = ModuleSelectionPage(navigator=mock_navigator, modules=[])

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory") as mock_factory:
            mock_vbox = Mock()
            mock_factory.vbox.return_value = mock_vbox
            mock_factory.html_widget.return_value = Mock()
            result = page.get_ui([])

        assert result == mock_vbox
        assert "No modules available" in mock_factory.html_widget.call_args[1]["value"]

    def test_get_ui_module_without_group(self, module_selection_page, mock_modules):
        """Modules without a group_name are placed in the 'No group' tab."""
        mock_modules[0].group_name = ""

        with patch("suplex.ui.pages.module_selection_page.WidgetFactory"):
            module_selection_page.create_module_tile = Mock(return_value=Mock())
            module_selection_page.get_ui([])

    # -------------------------------------------------------------------------
    # Module Tile Creation
    # -------------------------------------------------------------------------
    @patch("suplex.ui.pages.module_selection_page.widgets.HTML")
    @patch("suplex.ui.pages.module_selection_page.Event")
    def test_create_module_tile_viable(
        self, mock_event_class, mock_html_class, module_selection_page, mock_modules
    ):
        """create_module_tile() for viable modules adds hover + click handlers."""
        module = mock_modules[0]
        mock_html = Mock()
        mock_html_class.return_value = mock_html

        mock_hover_event = Mock()
        mock_hover_release = Mock()
        mock_click_event = Mock()
        mock_event_class.side_effect = [
            mock_hover_event,
            mock_hover_release,
            mock_click_event,
        ]

        module_selection_page.get_tile_html = Mock(return_value="<div>Tile HTML</div>")
        module_selection_page.get_module_icon = Mock(return_value="🎯")

        result = module_selection_page.create_module_tile(module, is_viable=True)

        assert result == mock_html
        assert mock_event_class.call_count == 3
        mock_hover_event.on_dom_event.assert_called_once()
        mock_hover_release.on_dom_event.assert_called_once()
        mock_click_event.on_dom_event.assert_called_once()
        assert len(module_selection_page._tile_events) == 3

    @patch("suplex.ui.pages.module_selection_page.widgets.HTML")
    @patch("suplex.ui.pages.module_selection_page.Event")
    def test_create_module_tile_not_viable(
        self, mock_event_class, mock_html_class, module_selection_page, mock_modules
    ):
        """Non-viable modules only get hover handlers (no click)."""
        module = mock_modules[1]
        mock_html = Mock()
        mock_html_class.return_value = mock_html

        mock_hover_event = Mock()
        mock_hover_release = Mock()
        mock_event_class.side_effect = [mock_hover_event, mock_hover_release]

        module_selection_page.get_tile_html = Mock(return_value="<div>Tile HTML</div>")
        module_selection_page.get_module_icon = Mock(return_value="🎯")

        result = module_selection_page.create_module_tile(module, is_viable=False)

        assert mock_event_class.call_count == 2

    # -------------------------------------------------------------------------
    # Icon Handling
    # -------------------------------------------------------------------------
    def test_get_module_icon_text(self, module_selection_page):
        """Text/emoji icons are returned as-is."""
        module = Mock()
        module.button_style = {"button_icon": "🎯"}

        result = module_selection_page.get_module_icon(module)
        assert result == "🎯"

    def test_get_module_icon_no_icon(self, module_selection_page):
        """Missing button_icon falls back to default emoji."""
        module = Mock()
        module.button_style = {}

        result = module_selection_page.get_module_icon(module)
        assert result == "📦"

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_get_module_icon_image(self, mock_getsize, mock_exists, module_selection_page):
        """Valid image file is converted to base64 data URL."""
        module = Mock()
        module.button_style = {"button_icon": "/path/to/icon.png"}

        mock_exists.return_value = True
        mock_getsize.return_value = 10000

        image_data = b"fake_image_data"
        with patch("builtins.open", mock_open(read_data=image_data)):
            result = module_selection_page.get_module_icon(module)

        expected_base64 = base64.b64encode(image_data).decode("utf-8")
        assert f"data:image/png;base64,{expected_base64}" in result

    @patch("os.path.exists")
    def test_get_module_icon_file_not_found(self, mock_exists, module_selection_page):
        """Missing icon file falls back to default."""
        module = Mock()
        module.button_style = {"button_icon": "/missing/icon.png"}

        mock_exists.return_value = False

        result = module_selection_page.get_module_icon(module)
        assert result == "📦"

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_get_module_icon_file_too_large(self, mock_getsize, mock_exists, module_selection_page):
        """Icons larger than 500KB are rejected."""
        module = Mock()
        module.button_style = {"button_icon": "/path/to/large.png"}

        mock_exists.return_value = True
        mock_getsize.return_value = 600 * 1024

        result = module_selection_page.get_module_icon(module)
        assert result == "📦"

    def test_is_text_or_emoji(self, module_selection_page):
        """is_text_or_emoji correctly distinguishes text/emoji from file paths."""
        assert module_selection_page.is_text_or_emoji("🎯") is True
        assert module_selection_page.is_text_or_emoji("ABC") is True
        assert module_selection_page.is_text_or_emoji("") is False
        assert module_selection_page.is_text_or_emoji("very_long_string") is False

        with patch("os.path.isfile", return_value=True):
            assert module_selection_page.is_text_or_emoji("/path/to/file") is False

    # -------------------------------------------------------------------------
    # Tile HTML Generation
    # -------------------------------------------------------------------------
    def test_get_tile_html_viable(self, module_selection_page):
        """get_tile_html() for viable modules includes hover effects and pointer cursor."""
        module = Mock()
        module.module_name = "Test Module"
        module.module_version = "1.0.0"
        module.button_style = {}

        result = module_selection_page.get_tile_html(module, "#FF0000", "#FFFFFF", is_viable=True)

        assert "Test Module" in result
        assert "1.0.0" in result
        assert "cursor: pointer" in result
        assert "opacity: 1.0" in result
        assert "onmouseover" in result
        assert "onmouseout" in result

    def test_get_tile_html_not_viable(self, module_selection_page):
        """Non-viable modules show DISABLED and not-allowed cursor."""
        module = Mock()
        module.module_name = "Test Module"
        module.module_version = "1.0.0"
        module.button_style = {}

        result = module_selection_page.get_tile_html(module, "#FF0000", "#FFFFFF", is_viable=False)

        assert "DISABLED" in result
        assert "cursor: not-allowed" in result
        assert "opacity: 0.6" in result
        assert "onmouseover" not in result

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------
    def test_hover_event_handlers(self, module_selection_page, mock_modules):
        """Hover events correctly call update_info_field / clear_hover_text."""
        with patch("suplex.ui.pages.module_selection_page.widgets.HTML"):
            with patch("suplex.ui.pages.module_selection_page.Event") as mock_event:
                mock_hover_event = Mock()
                mock_hover_release = Mock()
                mock_event.side_effect = [mock_hover_event, mock_hover_release, Mock()]

                module_selection_page.get_tile_html = Mock(return_value="<div></div>")
                module_selection_page.get_module_icon = Mock(return_value="🎯")

                module_selection_page.create_module_tile(mock_modules[0], is_viable=True)

                hover_handler = mock_hover_event.on_dom_event.call_args[0][0]

                mock_event_obj = {}
                hover_handler(mock_event_obj)

                mock_modules[0].get_module_hover_text.assert_called_once()
                module_selection_page._navigator.update_info_field.assert_called_once()
