import logging
from unittest.mock import Mock, patch

import pytest

from suplex.ui.elements.popup_log_system import PopupLogger, PopupLogHandler


class TestPopupLogger:
    """Tests for the PopupLogger – a toggleable popup panel that displays
    filtered log messages with copy/save/clear functionality.
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def test_popup_logger_initialization(self, mock_scheme):
        """PopupLogger initializes with correct defaults and creates UI components."""
        with patch("suplex.ui.elements.popup_log_system.widgets"):
            with patch("suplex.ui.elements.popup_log_system.get_popup_logger_styles"):
                logger_instance = PopupLogger(
                    scheme=mock_scheme, max_messages=50, min_log_level=logging.DEBUG
                )

        assert logger_instance._scheme == mock_scheme
        assert logger_instance._max_messages == 50
        assert logger_instance._min_log_level == logging.DEBUG
        assert logger_instance._is_visible is False
        assert logger_instance._log_messages == []
        assert logger_instance._unread_count == 0

    # -------------------------------------------------------------------------
    # UI creation
    # -------------------------------------------------------------------------
    def test_create_popup_log_widget(self, popup_logger):
        """create_popup_log_widget() sets up toggle button and popup panel."""
        with patch("suplex.ui.elements.popup_log_system.widgets.Button") as mock_button:
            with patch.object(popup_logger, "create_popup_panel") as mock_panel:
                mock_panel.return_value = Mock()
                popup_logger._toggle_button = None
                popup_logger._popup_panel = None

                popup_logger.create_popup_log_widget()

                assert popup_logger._toggle_button is not None
                assert popup_logger._popup_panel is not None
                mock_button.assert_called_once()

    # -------------------------------------------------------------------------
    # Show / hide popup
    # -------------------------------------------------------------------------
    def test_show_popup(self, popup_logger):
        """show_popup() makes the panel visible, resets unread count, and refreshes display."""
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.layout = Mock()
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        popup_logger.show_popup()

        assert popup_logger._popup_panel.layout.display == "flex"
        assert popup_logger._is_visible is True
        assert popup_logger._unread_count == 0
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    def test_close_popup(self, popup_logger):
        """close_popup() hides the panel and updates button appearance."""
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.layout = Mock()
        popup_logger._is_visible = True
        popup_logger.update_button_appearance = Mock()

        popup_logger.close_popup()

        assert popup_logger._popup_panel.layout.display == "none"
        assert popup_logger._is_visible is False
        popup_logger.update_button_appearance.assert_called_once()

    # -------------------------------------------------------------------------
    # Toggle button appearance
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "unread_count, expected_description, expected_class",
        [
            (0, "💾", "popup-toggle-button-normal"),  # no unread
            (5, "💾 5", "popup-toggle-button-unread"),  # small count
            (150, "💾 99+", "popup-toggle-button-unread"),  # capped at 99+
        ],
    )
    def test_update_button_appearance(
        self, popup_logger, unread_count, expected_description, expected_class
    ):
        """update_button_appearance() correctly sets badge and CSS classes."""
        popup_logger._toggle_button = Mock()
        popup_logger._unread_count = unread_count

        popup_logger.update_button_appearance()

        assert popup_logger._toggle_button.description == expected_description
        popup_logger._toggle_button.remove_class.assert_any_call(
            "popup-toggle-button-unread" if unread_count == 0 else "popup-toggle-button-normal"
        )
        popup_logger._toggle_button.add_class.assert_any_call(expected_class)

    # -------------------------------------------------------------------------
    # Log message handling
    # -------------------------------------------------------------------------
    def test_add_log_message(self, popup_logger):
        """add_log_message() stores message, updates unread count when hidden, and refreshes display when visible."""
        popup_logger._is_visible = False
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        with patch("suplex.ui.elements.popup_log_system.datetime") as mock_dt:
            mock_dt.now.return_value.strftime.return_value = "12:34:56"
            popup_logger.add_log_message("Test message", logging.INFO)

        assert len(popup_logger._log_messages) == 1
        assert popup_logger._log_messages[0]["message"] == "Test message"
        assert popup_logger._log_messages[0]["level"] == logging.INFO
        assert popup_logger._log_messages[0]["timestamp"] == "12:34:56"
        assert popup_logger._unread_count == 1
        popup_logger.update_button_appearance.assert_called_once()

    def test_add_log_message_below_min_level(self, popup_logger):
        """Messages below min_log_level are ignored."""
        popup_logger._min_log_level = logging.WARNING
        popup_logger.add_log_message("Debug message", logging.DEBUG)
        assert len(popup_logger._log_messages) == 0

    def test_add_log_message_respects_max_messages(self, popup_logger):
        """Oldest messages are dropped when max_messages limit is reached."""
        popup_logger._max_messages = 3
        popup_logger._is_visible = True
        popup_logger.refresh_log_display = Mock()

        for i in range(5):
            popup_logger.add_log_message(f"Message {i}", logging.INFO)

        assert len(popup_logger._log_messages) == 3
        assert popup_logger._log_messages[0]["message"] == "Message 2"

    # -------------------------------------------------------------------------
    # Log display & level info
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "level, expected_icon, expected_class, expected_name",
        [
            (logging.DEBUG, "🐛", "popup-log-debug", "Debug"),
            (logging.INFO, "ℹ️", "popup-log-info", "Info"),
            (logging.WARNING, "⚠️", "popup-log-warning", "Warning"),
            (logging.ERROR, "❌", "popup-log-error", "Error"),
            (logging.CRITICAL, "🚨", "popup-log-critical", "Critical"),
            (999, "📄", "popup-log-default", "Unspecified"),
        ],
    )
    def test_get_level_info(
        self, popup_logger, level, expected_icon, expected_class, expected_name
    ):
        """get_level_info() returns correct icon, CSS class, and name for every log level."""
        icon, css_class, name = popup_logger.get_level_info(level)
        assert icon == expected_icon
        assert css_class == expected_class
        assert name == expected_name

    def test_refresh_log_display_empty(self, popup_logger):
        """When there are no messages, a friendly empty state is shown."""
        popup_logger._log_output = Mock()
        popup_logger._message_counter = Mock()

        popup_logger.refresh_log_display()

        assert popup_logger._scheme.ICON.STORE in popup_logger._log_output.value
        assert "No logged messages yet" in popup_logger._log_output.value
        assert popup_logger._message_counter.value == "0 messages"

    def test_refresh_log_display_with_messages(self, popup_logger):
        """refresh_log_display() renders recent messages with proper formatting."""
        popup_logger._log_output = Mock()
        popup_logger._message_counter = Mock()
        popup_logger._log_messages = [
            {"message": "Test 1", "level": logging.INFO, "timestamp": "12:00:00"},
            {"message": "Test 2", "level": logging.ERROR, "timestamp": "12:00:01"},
        ]

        popup_logger.refresh_log_display()

        assert "Test 1" in popup_logger._log_output.value
        assert "Test 2" in popup_logger._log_output.value
        assert popup_logger._message_counter.value == "2 messages"

    def test_refresh_log_display_filtering(self, popup_logger):
        """Only messages >= min_log_level are shown."""
        popup_logger._log_output = Mock()
        popup_logger._message_counter = Mock()
        popup_logger._min_log_level = logging.WARNING
        popup_logger._log_messages = [
            {"message": "Debug", "level": logging.DEBUG, "timestamp": "12:00:00"},
            {"message": "Warning", "level": logging.WARNING, "timestamp": "12:00:02"},
            {"message": "Error", "level": logging.ERROR, "timestamp": "12:00:03"},
        ]

        popup_logger.refresh_log_display()

        assert "Debug" not in popup_logger._log_output.value
        assert "Warning" in popup_logger._log_output.value
        assert "Error" in popup_logger._log_output.value

    # -------------------------------------------------------------------------
    # Actions (clear, copy, save)
    # -------------------------------------------------------------------------
    def test_clear_logs(self, popup_logger):
        """clear_logs() empties the message list and resets UI."""
        popup_logger._log_messages = [{"message": "Test"}]
        popup_logger._unread_count = 5
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        popup_logger.clear_logs()

        assert popup_logger._log_messages == []
        assert popup_logger._unread_count == 0
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    @patch("suplex.ui.elements.popup_log_system.pyperclip")
    def test_copy_logs_success(self, mock_pyperclip, popup_logger):
        """copy_logs() formats and copies logs to clipboard."""
        popup_logger._log_messages = [
            {"message": "Test 1", "level": logging.INFO, "timestamp": "12:00:00"},
        ]
        popup_logger.format_logs_as_text = Mock(return_value="Formatted logs")
        popup_logger.add_log_message = Mock()

        popup_logger.copy_logs()

        mock_pyperclip.copy.assert_called_once_with("Formatted logs")
        popup_logger.add_log_message.assert_called_with("Logs copied to clipboard.", logging.INFO)

    def test_copy_logs_empty(self, popup_logger):
        """Empty log list shows a helpful message."""
        popup_logger._log_messages = []
        popup_logger.add_log_message = Mock()

        popup_logger.copy_logs()

        popup_logger.add_log_message.assert_called_with("No logs to copy.", logging.INFO)

    # -------------------------------------------------------------------------
    # Scheme update
    # -------------------------------------------------------------------------
    def test_update_scheme(self, popup_logger):
        """update_scheme() refreshes all icons and UI elements with the new scheme."""
        new_scheme = Mock()
        new_scheme.NAME = "Dark"
        new_scheme.ICON = Mock()
        new_scheme.ICON.CLOSE = "✖"
        new_scheme.ICON.CLEAR = "🗑️"
        new_scheme.ICON.STORE = "💾"
        new_scheme.ICON.SAVE = "📥"

        popup_logger._close_button = Mock()
        popup_logger._clear_button = Mock()
        popup_logger._copy_button = Mock()
        popup_logger._save_button = Mock()
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.children = [Mock(), Mock()]
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        with patch("suplex.ui.elements.popup_log_system.get_popup_logger_styles"):
            popup_logger.update_scheme(new_scheme)

        assert popup_logger._scheme == new_scheme
        assert popup_logger._close_button.description == "✖"
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()


class TestPopupLogHandler:
    """Tests for the custom logging handler that forwards records to PopupLogger."""

    def test_popup_log_handler_initialization(self):
        """PopupLogHandler stores reference to the PopupLogger instance."""
        mock_popup_logger = Mock()
        handler = PopupLogHandler(mock_popup_logger)

        assert handler._popup_logger == mock_popup_logger

    def test_popup_log_handler_emit(self):
        """emit() forwards formatted log record to add_log_message."""
        mock_popup_logger = Mock()
        handler = PopupLogHandler(mock_popup_logger)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        mock_popup_logger.add_log_message.assert_called_once()
        args, _ = mock_popup_logger.add_log_message.call_args
        assert "Test message" in args[0]
        assert args[1] == logging.INFO

    def test_popup_log_handler_emit_error_is_silent(self):
        """Errors in emit() are silently ignored to prevent recursion."""
        mock_popup_logger = Mock()
        mock_popup_logger.add_log_message.side_effect = Exception("Logger error")
        handler = PopupLogHandler(mock_popup_logger)

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)  # should not raise
