import pytest
from unittest.mock import Mock, patch
import logging

import ipywidgets as widgets

from src.ui.elements.popup_log_system import PopupLogger, PopupLogHandler


class TestPopupLoggerIntegration:
    """Integration tests for PopupLogger and its tight integration with GUI,
    real Python logging via PopupLogHandler, toggle behavior, copy/save/clear,
    and scheme updates.
    """

    # -------------------------------------------------------------------------
    # GUI + PopupLogger Integration
    # -------------------------------------------------------------------------
    def test_popup_logger_is_properly_attached_to_gui(self, gui_with_logging):
        """GUI correctly receives and wires the PopupLogger."""
        gui, popup_logger, _ = gui_with_logging

        # Ensure full GUI layout is built (fixes _info_container being None)
        gui.build_gui()

        assert gui._popup_logger == popup_logger
        assert popup_logger.toggle_button is not None
        assert popup_logger.popup_panel is not None

        # Toggle button is part of the info container in the GUI layout
        assert popup_logger.toggle_button in gui._info_container.children

    # -------------------------------------------------------------------------
    # Toggle Behavior
    # -------------------------------------------------------------------------
    def test_toggle_button_shows_and_hides_popup(self, gui_with_logging):
        """Clicking the toggle button correctly shows/hides the popup panel."""
        gui, popup_logger, _ = gui_with_logging
        gui.build_gui()

        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.layout = Mock()
        popup_logger._is_visible = False

        # Manually trigger the toggle logic
        if not popup_logger._is_visible:
            popup_logger.show_popup()

        assert popup_logger._is_visible is True
        assert popup_logger._popup_panel.layout.display == "flex"

        # Toggle again → hide
        popup_logger.close_popup()
        assert popup_logger._is_visible is False
        assert popup_logger._popup_panel.layout.display == "none"

    # -------------------------------------------------------------------------
    # Real Logging Integration via PopupLogHandler
    # -------------------------------------------------------------------------
    def test_popup_log_handler_forwards_logs(self, integrated_logging_setup):
        """PopupLogHandler correctly forwards real logging records to PopupLogger."""
        popup_logger, log_handler, test_logger = integrated_logging_setup

        test_logger.info("Integration test info message")
        test_logger.error("Integration test error message")

        # Verify messages were added
        assert len(popup_logger._log_messages) >= 2
        messages = [msg["message"] for msg in popup_logger._log_messages]
        assert "Integration test info message" in messages
        assert "Integration test error message" in messages

    # -------------------------------------------------------------------------
    # Copy / Save / Clear Actions
    # -------------------------------------------------------------------------
    @patch("src.ui.elements.popup_log_system.pyperclip")
    def test_copy_logs_integration(self, mock_pyperclip, popup_logger):
        """Copy action formats logs and puts them on the clipboard."""
        popup_logger._log_messages = [
            {"message": "Test log 1", "level": logging.INFO, "timestamp": "12:00:00"},
            {"message": "Test log 2", "level": logging.ERROR, "timestamp": "12:00:01"},
        ]
        popup_logger.format_logs_as_text = Mock(return_value="Formatted logs")

        with patch.object(popup_logger, "add_log_message") as mock_add:
            popup_logger.copy_logs()

            mock_pyperclip.copy.assert_called_once_with("Formatted logs")
            mock_add.assert_called_with("Logs copied to clipboard.", logging.INFO)

    @patch("src.ui.elements.popup_log_system.tk")
    @patch("src.ui.elements.popup_log_system.filedialog")
    @patch("builtins.open", create=True)
    def test_save_logs_integration(self, mock_open, mock_filedialog, mock_tk, popup_logger):
        """Save action opens dialog and writes logs to file."""
        mock_root = Mock()
        mock_tk.Tk.return_value = mock_root
        mock_filedialog.asksaveasfilename.return_value = "/tmp/test_logs.log"

        popup_logger._log_messages = [
            {"message": "Test log", "level": logging.INFO, "timestamp": "12:00:00"}
        ]
        popup_logger.format_logs_as_text = Mock(return_value="Formatted logs")

        with patch.object(popup_logger, "add_log_message") as mock_add:
            popup_logger.save_logs()

            mock_filedialog.asksaveasfilename.assert_called_once()
            mock_open.assert_called_once_with("/tmp/test_logs.log", "w", encoding="utf-8")
            mock_open().__enter__().write.assert_called_once_with("Formatted logs")
            mock_add.assert_called_with("Logs saved to: /tmp/test_logs.log", logging.INFO)

    def test_clear_logs_integration(self, popup_logger):
        """Clear action empties logs and resets UI state."""
        popup_logger._log_messages = [Mock()]
        popup_logger._unread_count = 5
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        popup_logger.clear_logs()

        assert popup_logger._log_messages == []
        assert popup_logger._unread_count == 0
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    # -------------------------------------------------------------------------
    # Scheme Updates
    # -------------------------------------------------------------------------
    def test_scheme_update_propagates_to_popup_logger(self, popup_logger, alt_mock_scheme):
        """Scheme changes update all icons and refresh the display."""
        popup_logger._close_button = Mock()
        popup_logger._clear_button = Mock()
        popup_logger._copy_button = Mock()
        popup_logger._save_button = Mock()
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.children = [Mock(), Mock()]

        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        with patch("src.ui.elements.popup_log_system.get_popup_logger_styles"):
            popup_logger.update_scheme(alt_mock_scheme)

        assert popup_logger._scheme == alt_mock_scheme
        assert popup_logger._close_button.description == alt_mock_scheme.ICON.CLOSE
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    # -------------------------------------------------------------------------
    # Unread Badge & Appearance
    # -------------------------------------------------------------------------
    def test_unread_badge_updates_on_new_logs(self, popup_logger):
        """New logs while popup is hidden increment unread count and update badge."""
        popup_logger._is_visible = False
        popup_logger.update_button_appearance = Mock()

        popup_logger.add_log_message("Hidden log message", logging.INFO)

        assert popup_logger._unread_count == 1
        popup_logger.update_button_appearance.assert_called_once()
