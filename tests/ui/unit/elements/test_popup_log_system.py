import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
import logging
import ipywidgets as widgets

from src.ui.elements.popup_log_system import PopupLogger, PopupLogHandler


class TestPopupLogger:
    def test_popup_logger_initialization(self, mock_scheme):
        with patch("src.ui.elements.popup_log_system.widgets"):
            with patch("src.ui.elements.popup_log_system.get_popup_logger_styles"):
                logger = PopupLogger(
                    scheme=mock_scheme, max_messages=50, min_log_level=logging.DEBUG
                )

        assert logger._scheme == mock_scheme
        assert logger._max_messages == 50
        assert logger._min_log_level == logging.DEBUG
        assert logger._is_visible == False
        assert logger._log_messages == []
        assert logger._unread_count == 0

    def test_create_popup_log_widget(self, popup_logger):
        with patch("src.ui.elements.popup_log_system.widgets.Button") as mock_button:
            with patch.object(popup_logger, "create_popup_panel") as mock_panel:
                mock_panel.return_value = Mock()
                popup_logger._toggle_button = None
                popup_logger._popup_panel = None

                popup_logger.create_popup_log_widget()

                assert popup_logger._toggle_button is not None
                assert popup_logger._popup_panel is not None
                mock_button.assert_called_once()

    def test_show_popup(self, popup_logger):
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.layout = Mock()
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        popup_logger.show_popup()

        assert popup_logger._popup_panel.layout.display == "flex"
        assert popup_logger._is_visible == True
        assert popup_logger._unread_count == 0
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    def test_close_popup(self, popup_logger):
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.layout = Mock()
        popup_logger._is_visible = True
        popup_logger.update_button_appearance = Mock()

        popup_logger.close_popup()

        assert popup_logger._popup_panel.layout.display == "none"
        assert popup_logger._is_visible == False
        popup_logger.update_button_appearance.assert_called_once()

    def test_update_button_appearance_no_unread(self, popup_logger):
        popup_logger._toggle_button = Mock()
        popup_logger._unread_count = 0

        popup_logger.update_button_appearance()

        assert (
            popup_logger._toggle_button.description == popup_logger._scheme.ICON.STORE
        )
        popup_logger._toggle_button.remove_class.assert_called_with(
            "popup-toggle-button-unread"
        )
        popup_logger._toggle_button.add_class.assert_called_with(
            "popup-toggle-button-normal"
        )

    def test_update_button_appearance_with_unread(self, popup_logger):
        popup_logger._toggle_button = Mock()
        popup_logger._unread_count = 5

        popup_logger.update_button_appearance()

        assert (
            popup_logger._toggle_button.description
            == f"{popup_logger._scheme.ICON.STORE} 5"
        )
        popup_logger._toggle_button.remove_class.assert_called_with(
            "popup-toggle-button-normal"
        )
        popup_logger._toggle_button.add_class.assert_called_with(
            "popup-toggle-button-unread"
        )

    def test_update_button_appearance_many_unread(self, popup_logger):
        popup_logger._toggle_button = Mock()
        popup_logger._unread_count = 150

        popup_logger.update_button_appearance()

        assert (
            popup_logger._toggle_button.description
            == f"{popup_logger._scheme.ICON.STORE} 99+"
        )

    def test_add_log_message(self, popup_logger):
        popup_logger._is_visible = False
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        with patch("src.ui.elements.popup_log_system.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "12:34:56"

            popup_logger.add_log_message("Test message", logging.INFO)

        assert len(popup_logger._log_messages) == 1
        assert popup_logger._log_messages[0]["message"] == "Test message"
        assert popup_logger._log_messages[0]["level"] == logging.INFO
        assert popup_logger._log_messages[0]["timestamp"] == "12:34:56"
        assert popup_logger._unread_count == 1
        popup_logger.update_button_appearance.assert_called_once()

    def test_add_log_message_below_min_level(self, popup_logger):
        popup_logger._min_log_level = logging.WARNING

        popup_logger.add_log_message("Debug message", logging.DEBUG)
        assert len(popup_logger._log_messages) == 0

    def test_add_log_message_max_messages(self, popup_logger):
        popup_logger._max_messages = 3
        popup_logger._is_visible = True
        popup_logger.refresh_log_display = Mock()

        for i in range(5):
            popup_logger.add_log_message(f"Message {i}", logging.INFO)

        assert len(popup_logger._log_messages) == 3
        assert popup_logger._log_messages[0]["message"] == "Message 2"
        assert popup_logger._log_messages[-1]["message"] == "Message 4"

    def test_get_level_info(self, popup_logger):
        test_cases = [
            (
                logging.DEBUG,
                popup_logger._scheme.ICON.DEBUG,
                "popup-log-debug",
                "Debug",
            ),
            (logging.INFO, popup_logger._scheme.ICON.INFO, "popup-log-info", "Info"),
            (
                logging.WARNING,
                popup_logger._scheme.ICON.WARNING,
                "popup-log-warning",
                "Warning",
            ),
            (
                logging.ERROR,
                popup_logger._scheme.ICON.ERROR,
                "popup-log-error",
                "Error",
            ),
            (
                logging.CRITICAL,
                popup_logger._scheme.ICON.CRITICAL,
                "popup-log-critical",
                "Critical",
            ),
            (
                999,
                popup_logger._scheme.ICON.DEFAULT,
                "popup-log-default",
                "Unspecified",
            ),
        ]

        for level, expected_icon, expected_class, expected_name in test_cases:
            icon, css_class, name = popup_logger.get_level_info(level)
            assert icon == expected_icon
            assert css_class == expected_class
            assert name == expected_name

    def test_refresh_log_display_empty(self, popup_logger):
        popup_logger._log_output = Mock()
        popup_logger._message_counter = Mock()

        popup_logger.refresh_log_display()

        assert popup_logger._scheme.ICON.STORE in popup_logger._log_output.value
        assert "No logged messages yet" in popup_logger._log_output.value
        assert popup_logger._message_counter.value == "0 messages"

    def test_refresh_log_display_with_messages(self, popup_logger):
        popup_logger._log_output = Mock()
        popup_logger._message_counter = Mock()
        popup_logger._log_messages = [
            {"message": "Test 1", "level": logging.INFO, "timestamp": "12:00:00"},
            {"message": "Test 2", "level": logging.ERROR, "timestamp": "12:00:01"},
        ]

        popup_logger.refresh_log_display()

        assert "Test 1" in popup_logger._log_output.value
        assert "Test 2" in popup_logger._log_output.value
        assert "12:00:00" in popup_logger._log_output.value
        assert "12:00:01" in popup_logger._log_output.value
        assert popup_logger._message_counter.value == "2 messages"

    def test_refresh_log_display_filtering(self, popup_logger):
        popup_logger._log_output = Mock()
        popup_logger._message_counter = Mock()
        popup_logger._min_log_level = logging.WARNING
        popup_logger._log_messages = [
            {"message": "Debug", "level": logging.DEBUG, "timestamp": "12:00:00"},
            {"message": "Info", "level": logging.INFO, "timestamp": "12:00:01"},
            {"message": "Warning", "level": logging.WARNING, "timestamp": "12:00:02"},
            {"message": "Error", "level": logging.ERROR, "timestamp": "12:00:03"},
        ]

        popup_logger.refresh_log_display()

        assert "Debug" not in popup_logger._log_output.value
        assert "Info" not in popup_logger._log_output.value
        assert "Warning" in popup_logger._log_output.value
        assert "Error" in popup_logger._log_output.value

    def test_clear_logs(self, popup_logger):
        popup_logger._log_messages = [{"message": "Test", "level": logging.INFO}]
        popup_logger._unread_count = 5
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        popup_logger.clear_logs()

        assert popup_logger._log_messages == []
        assert popup_logger._unread_count == 0
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    @patch("src.ui.elements.popup_log_system.pyperclip")
    def test_copy_logs_success(self, mock_pyperclip, popup_logger):
        popup_logger._log_messages = [
            {"message": "Test 1", "level": logging.INFO, "timestamp": "12:00:00"},
            {"message": "Test 2", "level": logging.ERROR, "timestamp": "12:00:01"},
        ]
        popup_logger.format_logs_as_text = Mock(return_value="Formatted logs")
        popup_logger.add_log_message = Mock()

        popup_logger.copy_logs()

        mock_pyperclip.copy.assert_called_once_with("Formatted logs")
        popup_logger.add_log_message.assert_called_with(
            "Logs copied to clipboard.", logging.INFO
        )

    def test_copy_logs_empty(self, popup_logger):
        popup_logger._log_messages = []
        popup_logger.add_log_message = Mock()

        popup_logger.copy_logs()

        popup_logger.add_log_message.assert_called_with(
            "No logs to copy.", logging.INFO
        )

    @patch("src.ui.elements.popup_log_system.pyperclip")
    def test_copy_logs_error(self, mock_pyperclip, popup_logger):
        popup_logger._log_messages = [{"message": "Test", "level": logging.INFO}]
        mock_pyperclip.copy.side_effect = Exception("Clipboard error")
        popup_logger.add_log_message = Mock()

        popup_logger.copy_logs()

        popup_logger.add_log_message.assert_called()
        assert "Error copying logs" in popup_logger.add_log_message.call_args[0][0]

    @patch("src.ui.elements.popup_log_system.tk")
    @patch("src.ui.elements.popup_log_system.filedialog")
    @patch("builtins.open", create=True)
    def test_save_logs_success(self, mock_open, mock_filedialog, mock_tk, popup_logger):
        mock_root = Mock()
        mock_tk.Tk.return_value = mock_root
        mock_filedialog.asksaveasfilename.return_value = "/test/logs.log"
        popup_logger._log_messages = [{"message": "Test", "level": logging.INFO}]
        popup_logger.format_logs_as_text = Mock(return_value="Formatted logs")
        popup_logger.add_log_message = Mock()

        popup_logger.save_logs()

        mock_filedialog.asksaveasfilename.assert_called_once()
        mock_open.assert_called_once_with("/test/logs.log", "w", encoding="utf-8")
        mock_open().__enter__().write.assert_called_once_with("Formatted logs")
        popup_logger.add_log_message.assert_called_with(
            "Logs saved to: /test/logs.log", logging.INFO
        )
        mock_root.destroy.assert_called_once()

    @patch("src.ui.elements.popup_log_system.tk")
    @patch("src.ui.elements.popup_log_system.filedialog")
    def test_save_logs_cancelled(self, mock_filedialog, mock_tk, popup_logger):
        mock_root = Mock()
        mock_tk.Tk.return_value = mock_root
        mock_filedialog.asksaveasfilename.return_value = ""
        popup_logger._log_messages = [{"message": "Test"}]
        popup_logger.add_log_message = Mock()

        popup_logger.save_logs()

        popup_logger.add_log_message.assert_called_with(
            "Log save cancelled", logging.INFO
        )

    def test_save_logs_empty(self, popup_logger):
        popup_logger._log_messages = []
        popup_logger.add_log_message = Mock()
        popup_logger.save_logs()

        popup_logger.add_log_message.assert_called_with(
            "No logs to save.", logging.INFO
        )

    def test_format_logs_as_text(self, popup_logger):
        popup_logger._log_messages = [
            {"message": "Info message", "level": logging.INFO, "timestamp": "12:00:00"},
            {
                "message": "Error message",
                "level": logging.ERROR,
                "timestamp": "12:00:01",
            },
        ]

        result = popup_logger.format_logs_as_text()

        assert "INFO - 12:00:00: Info message" in result
        assert "ERROR - 12:00:01: Error message" in result

    def test_update_scheme(self, popup_logger):
        new_scheme = Mock()
        new_scheme.ICON = Mock()
        new_scheme.ICON.CLOSE = "X"
        new_scheme.ICON.CLEAR = "C"
        new_scheme.ICON.STORE = "S"
        new_scheme.ICON.SAVE = "V"

        popup_logger._close_button = Mock()
        popup_logger._clear_button = Mock()
        popup_logger._copy_button = Mock()
        popup_logger._save_button = Mock()
        popup_logger._popup_panel = Mock()
        popup_logger._popup_panel.children = [Mock(), Mock()]
        popup_logger.update_button_appearance = Mock()
        popup_logger.refresh_log_display = Mock()

        with patch("src.ui.elements.popup_log_system.get_popup_logger_styles"):
            popup_logger.update_scheme(new_scheme)

        assert popup_logger._scheme == new_scheme
        assert popup_logger._close_button.description == "X"
        assert popup_logger._clear_button.description == "C"
        assert popup_logger._copy_button.description == "S"
        assert popup_logger._save_button.description == "V"
        popup_logger.update_button_appearance.assert_called_once()
        popup_logger.refresh_log_display.assert_called_once()

    def test_create_popup_panel_dropdown_change(self, popup_logger):
        with patch(
            "src.ui.elements.popup_log_system.widgets.Dropdown"
        ) as mock_dropdown:
            with patch("src.ui.elements.popup_log_system.widgets.Button"):
                with patch("src.ui.elements.popup_log_system.widgets.HTML"):
                    with patch("src.ui.elements.popup_log_system.widgets.HBox"):
                        with patch("src.ui.elements.popup_log_system.widgets.VBox"):
                            dropdown_instance = Mock()
                            dropdown_instance.value = logging.WARNING
                            mock_dropdown.return_value = dropdown_instance

                            popup_logger._min_log_level = logging.INFO
                            popup_logger.refresh_log_display = Mock()

                            popup_logger.create_popup_panel()

                            observe_call = dropdown_instance.observe.call_args
                            handler = observe_call[0][0]

                            handler({"new": logging.WARNING})

                            assert popup_logger._min_log_level == logging.WARNING
                            popup_logger.refresh_log_display.assert_called()


class TestPopupLogHandler:
    def test_popup_log_handler_initialization(self):
        mock_popup_logger = Mock()
        handler = PopupLogHandler(mock_popup_logger)

        assert handler._popup_logger == mock_popup_logger

    def test_popup_log_handler_emit(self):
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
        call_args = mock_popup_logger.add_log_message.call_args
        assert "Test message" in call_args[0][0]
        assert call_args[0][1] == logging.INFO

    def test_popup_log_handler_emit_error(self):
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

        handler.emit(record)
