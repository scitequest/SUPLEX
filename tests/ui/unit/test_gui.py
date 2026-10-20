import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.ui.gui import GUI


class TestGUI:
    """Tests for the main GUI orchestrator that manages header, navigator, content area,
    info field, and overall layout/scheme handling.
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def test_gui_initialization(self, mock_modules, mock_schemes, mock_content, mock_popup_logger):
        """GUI initializes correctly with all dependencies and sensible defaults."""
        gui = GUI(mock_modules, mock_schemes, mock_content, mock_popup_logger)

        assert gui._modules == mock_modules
        assert gui._schemes == mock_schemes
        assert gui._current_scheme == mock_schemes["Default"]
        assert gui._content == mock_content
        assert gui._popup_logger == mock_popup_logger

        # UI components start uninitialized
        assert gui._header is None
        assert gui._navigator is None
        assert gui._content_area is None
        assert gui._content_holder is None
        assert gui._info_field is None
        assert gui._current_page is None

        # Info field state has proper defaults
        assert gui._info_field_state["message"] == ""
        assert (
            gui._info_field_state["info_color"]
            == gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT
        )
        assert gui._info_field_state["info_icon"] == gui._current_scheme.ICON.DEFAULT

    # -------------------------------------------------------------------------
    # Building the GUI
    # -------------------------------------------------------------------------
    @patch("suplex.ui.gui.Header")
    @patch("suplex.ui.gui.Navigator")
    @patch("suplex.ui.gui.get_widget_styles")
    @patch("suplex.ui.gui.get_gui_styles")
    @patch("suplex.ui.gui.widgets")
    def test_build_gui(
        self,
        mock_widgets,
        mock_gui_styles,
        mock_widget_styles,
        mock_navigator_class,
        mock_header_class,
        gui,
    ):
        """build_gui() successfully creates all major UI components."""
        gui.build_gui()

        assert gui._header is not None
        assert gui._navigator is not None
        assert gui._content_area is not None
        assert gui._content_holder is not None
        assert gui._info_field is not None
        assert gui._info_container is not None

    # -------------------------------------------------------------------------
    # Content management
    # -------------------------------------------------------------------------
    def test_update_content_holder(self, gui):
        """Content holder correctly replaces its children with new content."""
        mock_widget = Mock(spec=widgets.Widget)
        gui._content_holder = Mock()
        gui._content_holder.children = []

        gui.update_content_holder(mock_widget)

        assert gui._content_holder.children == [mock_widget]

    def test_update_content_holder_error(self, gui):
        """Exceptions during content update are logged and re-raised."""
        gui._content_holder = Mock()
        # Force the children assignment to raise the expected exception
        type(gui._content_holder).children = property(
            fget=lambda self: [],
            fset=lambda self, val: (_ for _ in ()).throw(Exception("Test error")),
        )

        with pytest.raises(Exception, match="Test error"):
            gui.update_content_holder(Mock())

    # -------------------------------------------------------------------------
    # Info field management
    # -------------------------------------------------------------------------
    def test_set_info_field_state_default(self, gui):
        """set_info_field_state() uses default color/icon when only a message is given."""
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

    def test_set_info_field_state_icon_mapping(self, gui):
        """Correct icon is chosen for each info field status color."""
        gui._info_field = Mock()
        gui._info_field_state = {}
        gui.update_info_field = Mock()

        test_cases = [
            (gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO, gui._current_scheme.ICON.INFO),
            (gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS, gui._current_scheme.ICON.SUCCESS),
            (gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING, gui._current_scheme.ICON.WARNING),
            (gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR, gui._current_scheme.ICON.ERROR),
            (
                gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL,
                gui._current_scheme.ICON.CRITICAL,
            ),
            (gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG, gui._current_scheme.ICON.DEBUG),
        ]

        for color, expected_icon in test_cases:
            gui.set_info_field_state("Test", info_color=color)
            assert gui._info_field_state["info_icon"] == expected_icon

    def test_set_info_field_state_custom_icon(self, gui):
        """Custom icon overrides the default mapping."""
        gui._info_field = Mock()
        gui._info_field_state = {}
        gui.update_info_field = Mock()

        gui.set_info_field_state("Custom message", info_icon="🎯")

        assert gui._info_field_state["info_icon"] == "🎯"

    def test_update_info_field(self, gui):
        """update_info_field() correctly sets HTML value and applies the right CSS class."""
        gui.build_gui()  # ensure _info_field exists

        color = gui._current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS
        icon = gui._current_scheme.ICON.SUCCESS

        gui.update_info_field("Success message", color, icon)

        assert gui._info_field.value == f"{icon} Success message"

    def test_clear_hover_text(self, gui):
        """clear_hover_text() restores the persistent info field state."""
        gui._info_field_state = {
            "message": "Persistent message",
            "info_color": "#FF0000",
            "info_icon": "📌",
        }
        gui.update_info_field = Mock()

        gui.clear_hover_text()

        gui.update_info_field.assert_called_once_with("Persistent message", "#FF0000", "📌")

    # -------------------------------------------------------------------------
    # Scheme & layout
    # -------------------------------------------------------------------------
    def test_current_scheme_property(self, gui):
        """current_scheme property returns the active scheme."""
        assert gui.current_scheme == gui._current_scheme

    @patch("suplex.ui.gui.get_gui_styles")
    @patch("suplex.ui.gui.widgets")
    def test_update_layout(self, mock_widgets, mock_gui_styles, gui):
        """update_layout() assembles the complete GUI layout."""
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

        gui.update_layout()

        mock_widgets.VBox.assert_called()
        assert len(gui._content.children) == 3  # styles, main_layout, logger_box
        gui.set_info_field_state.assert_called_once_with("")

    @patch("suplex.ui.gui.get_gui_styles")
    @patch("suplex.ui.gui.get_widget_styles")
    def test_update_scheme(self, mock_widget_styles, mock_gui_styles, gui):
        """update_scheme() refreshes all components with the new color scheme."""
        gui._navigator = Mock()
        gui._popup_logger = Mock()
        gui._content_area = Mock()
        gui._content_area.children = (Mock(), Mock())
        gui._content = Mock()
        gui._content.children = (Mock(), Mock(), Mock())

        # Mock side-effect methods that expect a fully built GUI (header, etc.)
        gui.update_layout = Mock()
        gui.update_info_field = Mock()

        new_scheme = Mock()
        new_scheme.NAME = "NewScheme"
        new_scheme.LAYOUT_COLOR = Mock()
        new_scheme.LAYOUT_COLOR.INFO_FIELD = Mock()
        new_scheme.LAYOUT_COLOR.INFO_FIELD.INFO = "#00FF00"
        new_scheme.ICON = Mock()
        new_scheme.ICON.INFO = "ℹ️"

        mock_widget_styles.return_value = Mock()
        mock_gui_styles.return_value = Mock()

        gui.update_scheme(new_scheme)

        assert gui._current_scheme == new_scheme
        gui._navigator.update_scheme.assert_called_once_with(new_scheme=new_scheme)
        gui._popup_logger.update_scheme.assert_called_once_with(new_scheme=new_scheme)
        gui.update_layout.assert_called_once()
        gui.update_info_field.assert_called_once()
