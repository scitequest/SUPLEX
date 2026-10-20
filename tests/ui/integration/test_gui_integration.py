import pytest
from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.ui.gui import GUI


class TestGUIIntegration:
    """Integration tests for the main GUI class and its interactions with
    Header, Navigator, PopupLogger, and scheme switching.
    """

    # -------------------------------------------------------------------------
    # Full GUI Build
    # -------------------------------------------------------------------------
    def test_gui_builds_all_components(self, integrated_gui):
        """Full GUI build successfully creates Header, Navigator, content areas,
        and info container.
        """
        assert integrated_gui._header is not None
        assert integrated_gui._navigator is not None
        assert integrated_gui._content_area is not None
        assert integrated_gui._content_holder is not None
        assert integrated_gui._info_field is not None
        assert integrated_gui._info_container is not None

    # -------------------------------------------------------------------------
    # Content Management
    # -------------------------------------------------------------------------
    def test_update_content_holder(self, integrated_gui):
        """Content holder correctly replaces its children when pages/modules change."""
        mock_content = Mock(spec=widgets.Widget)
        integrated_gui._content_holder = Mock()
        integrated_gui._content_holder.children = []

        integrated_gui.update_content_holder(mock_content)

        assert integrated_gui._content_holder.children == [mock_content]

    # -------------------------------------------------------------------------
    # Info Field Integration
    # -------------------------------------------------------------------------
    def test_info_field_state_updates(self, integrated_gui):
        """set_info_field_state correctly updates the HTML widget."""
        integrated_gui.build_gui()

        integrated_gui.set_info_field_state(
            message="Test info message",
            info_color=integrated_gui.current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS,
            info_icon=integrated_gui.current_scheme.ICON.SUCCESS,
        )

        assert "Test info message" in integrated_gui._info_field.value

    def test_clear_hover_text_restores_state(self, integrated_gui):
        """clear_hover_text restores the persistent info field state after hover."""
        integrated_gui._info_field_state = {
            "message": "Persistent message",
            "info_color": "#FF0000",
            "info_icon": "📌",
        }
        integrated_gui.update_info_field = Mock()

        integrated_gui.clear_hover_text()

        integrated_gui.update_info_field.assert_called_once_with(
            "Persistent message", "#FF0000", "📌"
        )

    # -------------------------------------------------------------------------
    # Popup Logger Integration
    # -------------------------------------------------------------------------
    def test_popup_logger_toggle_integration(self, gui_with_logging):
        """GUI correctly integrates with PopupLogger toggle button and panel."""
        gui, popup_logger, _ = gui_with_logging
        gui.build_gui()  # ensure GUI is fully built

        assert gui._popup_logger == popup_logger
        assert popup_logger.toggle_button is not None
        assert popup_logger.popup_panel is not None

        assert popup_logger.toggle_button in gui._info_container.children

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    def test_gui_build_failure_is_handled(self, mock_modules, mock_schemes, mock_popup_logger):
        """GUI gracefully handles build failures."""
        content = Mock()
        gui = GUI(mock_modules, mock_schemes, content, mock_popup_logger)

        with patch.object(gui, "build_gui", side_effect=Exception("Build failed")):
            with pytest.raises(Exception, match="Build failed"):
                gui.build_gui()
