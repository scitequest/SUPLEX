import pytest
from unittest.mock import Mock, MagicMock, patch, call
import ipywidgets as widgets

from src.ui.gui import GUI
from ui.ui_constants import PAGE


class TestGUI:
    def test_gui_initialization(
        self, mock_modules, mock_schemes, mock_content, mock_popup_logger
    ):
        gui = GUI(mock_modules, mock_schemes, mock_content, mock_popup_logger)

        assert gui._modules == mock_modules
        assert gui._schemes == mock_schemes
        assert gui._current_scheme == mock_schemes["Default"]
        assert gui._content == mock_content
        assert gui._popup_logger == mock_popup_logger
        assert gui._header is None
        assert gui._navigator is None
        assert gui._content_area is None
        assert gui._content_holder is None
        assert gui._info_field is None
        assert gui._current_page is None

    @patch("src.ui.gui.Header")
    @patch("src.ui.gui.Navigator")
    @patch("src.ui.gui.get_widget_styles")
    @patch("src.ui.gui.get_gui_styles")
    @patch("src.ui.gui.widgets")
    def test_build_gui(
        self,
        mock_widgets,
        gui_styles,
        mock_widget_styles,
        mock_navigator_class,
        mock_header_class,
        gui,
    ):
        gui.build_gui()
        assert gui._header is not None
        assert gui._navigator is not None
        assert gui._content_area is not None
        assert gui._content_holder is not None
        assert gui._info_field is not None
        assert gui._info_container is not None

    def test_update_content_holder(self, gui):
        mock_widget = Mock()
        gui._content_holder = Mock()
        gui._content_holder.children = []

        gui.update_content_holder(mock_widget)

        assert gui._content_holder.children == [mock_widget]

    def test_set_info_field_state_default(self, gui):
        gui._info_field = Mock()
        gui._info_field_state = {}
        gui.update_info_field = Mock()

        gui.set_info_field_state("Test message")

        assert gui._info_field_state["message"] == "Test message"
        assert (
            gui._info_field_state["info_color"]
            == gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT
        )
        assert gui._info_field_state["info_icon"] == gui._current_scheme.ICON.DEFAULT

        gui.update_info_field.assert_called_once_with(
            "Test message",
            gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT,
            gui._current_scheme.ICON.DEFAULT,
        )

    def test_set_info_field_state_with_color(self, gui):
        gui._info_field = Mock()
        gui._info_field_state = {}
        gui.update_info_field = Mock()

        error_color = gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR
        gui.set_info_field_state("Error message", info_color=error_color)

        assert gui._info_field_state["message"] == "Error message"
        assert gui._info_field_state["info_color"] == error_color
        assert gui._info_field_state["info_icon"] == gui._current_scheme.ICON.ERROR

    def test_set_info_field_state_with_custom_icon(self, gui):
        gui._info_field = Mock()
        gui._info_field_state = {}
        gui.update_info_field = Mock()

        gui.set_info_field_state("Custom message", info_icon="🎯")

        assert gui._info_field_state["info_icon"] == "🎯"

    def test_update_info_field(self, gui):
        gui.build_gui()  # Needed to initialize info field
        gui.update_info_field(
            "Test message",
            gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS,
            gui._current_scheme.ICON.SUCCESS,
        )
        expected_value = f"{gui._current_scheme.ICON.SUCCESS} Test message"
        assert gui._info_field.value == expected_value

    def test_clear_hover_text(self, gui):
        gui._info_field_state = {
            "message": "Persistent message",
            "info_color": "#FF0000",
            "info_icon": "📌",
        }
        gui.update_info_field = Mock()

        gui.clear_hover_text()

        gui.update_info_field.assert_called_once_with(
            "Persistent message", "#FF0000", "📌"
        )

    def test_current_scheme_property(self, gui):
        assert gui.current_scheme == gui._current_scheme

    @patch("src.ui.gui.get_gui_styles")
    @patch("src.ui.gui.widgets")
    def test_update_layout(self, mock_widgets, gui_styles, gui):
        gui._header = Mock()
        gui._header.ui = Mock()
        gui._navigator = Mock()
        gui._navigator.get_ui_element.return_value = Mock()
        gui._content_area = Mock()
        gui._info_container = Mock()
        gui._popup_logger = Mock()
        gui._popup_logger.popup_panel = Mock()
        gui.set_info_field_state = Mock()

        mock_vbox = Mock()
        mock_box = Mock()
        mock_widgets.VBox.return_value = mock_vbox
        mock_widgets.Box.return_value = mock_box
        mock_widgets.Layout.return_value = Mock()

        gui.update_layout()

        mock_widgets.VBox.assert_called()
        assert len(gui._content.children) == 3  # styles, main_layout, logger_box
        gui.set_info_field_state.assert_called_once_with("")

    def test_update_content_holder_error(self, gui):
        gui._content_holder = Mock()
        gui._content_holder.children = Mock(side_effect=Exception("Test error"))

        gui.update_content_holder(Mock())

    def test_set_info_field_state_icon_mapping(self, gui):
        gui._info_field = Mock()
        gui._info_field_state = {}
        gui.update_info_field = Mock()

        test_cases = [
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
                gui._current_scheme.ICON.INFO,
            ),
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS,
                gui._current_scheme.ICON.SUCCESS,
            ),
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING,
                gui._current_scheme.ICON.WARNING,
            ),
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
                gui._current_scheme.ICON.ERROR,
            ),
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL,
                gui._current_scheme.ICON.CRITICAL,
            ),
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG,
                gui._current_scheme.ICON.DEBUG,
            ),
        ]

        for color, expected_icon in test_cases:
            gui.set_info_field_state("Test", info_color=color)
            assert gui._info_field_state["info_icon"] == expected_icon
