import pytest
import logging
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
import tempfile
import os

from src.ui.elements.popup_log_system import PopupLogger, PopupLogHandler
from src.ui.gui import GUI
from src.ui.pages.directory_selection_page import DirectorySelectionPage
from src.martin_interface.martin_adapter import Adapter

class TestLoggingSystemIntegration:
    """
    Integration tests for the logging system across multiple components.
    Tests log generation, capture, display, and persistence.
    """
    def test_log_capture_from_multiple_components(self, gui_with_logging):
        """Test that logs from different components are captured."""
        gui, popup_logger, test_logger = gui_with_logging
        
        # Clear any existing logs
        popup_logger._log_messages.clear()
        
        # Generate logs from different "components"
        test_logger.info("GUI initialized")
        test_logger.debug("Navigator state changed")
        test_logger.warning("Dataset validation warning")
        test_logger.error("Module loading error")
        
        # Verify all logs were captured
        assert len(popup_logger._log_messages) == 4
        
        # Verify log levels
        log_levels = [msg["level"] for msg in popup_logger._log_messages]
        assert logging.INFO in log_levels
        assert logging.DEBUG in log_levels
        assert logging.WARNING in log_levels
        assert logging.ERROR in log_levels
    
    def test_log_filtering_integration(self, integrated_logging_setup):
        """Test log level filtering across the system."""
        popup_logger, log_handler, test_logger = integrated_logging_setup
        
        # Set minimum level to WARNING - this filters at message addition time
        popup_logger._min_log_level = logging.WARNING
        popup_logger._log_messages.clear()
        
        # Generate logs of different levels
        test_logger.debug("Debug message - should be captured but not displayed")
        test_logger.info("Info message - should be captured but not displayed")
        test_logger.warning("Warning message - should be displayed")
        test_logger.error("Error message - should be displayed")
        
        # Only WARNING and ERROR should be captured due to min_log_level filtering
        assert len(popup_logger._log_messages) == 2
        
        # Verify only WARNING and above were captured
        captured_levels = [msg["level"] for msg in popup_logger._log_messages]
        assert logging.WARNING in captured_levels
        assert logging.ERROR in captured_levels
        assert logging.DEBUG not in captured_levels
        assert logging.INFO not in captured_levels
        
        # Verify the messages are correct
        captured_messages = [msg["message"] for msg in popup_logger._log_messages]
        assert "Warning message - should be displayed" in captured_messages
        assert "Error message - should be displayed" in captured_messages
    
    def test_log_persistence_to_file(self, integrated_logging_setup):
        """Test saving logs to file."""
        popup_logger, log_handler, test_logger = integrated_logging_setup
        
        # Generate some logs
        test_logger.info("Test log 1")
        test_logger.error("Test error")
        test_logger.warning("Test warning")
        
        # Mock file dialog and file operations
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            with patch("src.ui.elements.popup_log_system.filedialog.asksaveasfilename", return_value=tmp_filename):
                with patch("src.ui.elements.popup_log_system.tk"):
                    popup_logger.save_logs()
            
            # Verify file was created and contains logs
            with open(tmp_filename, "r") as f:
                content = f.read()
                assert "Test log 1" in content
                assert "Test error" in content
                assert "Test warning" in content
                assert "INFO" in content
                assert "ERROR" in content
                assert "WARNING" in content
        
        finally:
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)
    
    def test_unread_message_tracking(self, integrated_logging_setup):
        """Test unread message tracking and notification."""
        popup_logger, log_handler, test_logger = integrated_logging_setup
        
        # Ensure popup is hidden
        popup_logger._is_visible = False
        popup_logger._unread_count = 0
        popup_logger.update_button_appearance = Mock()
        
        # Generate logs while hidden
        test_logger.info("Message 1")
        test_logger.info("Message 2")
        test_logger.warning("Message 3")
        
        # Check unread count
        assert popup_logger._unread_count == 3
        assert popup_logger.update_button_appearance.call_count == 3
        
        # Show popup - should reset unread count
        popup_logger.show_popup()
        assert popup_logger._unread_count == 0
    
    def test_real_time_log_updates(self, integrated_logging_setup):
        """Test that logs update in real-time when popup is visible."""
        popup_logger, log_handler, test_logger = integrated_logging_setup
        
        # Show popup
        popup_logger._is_visible = True
        popup_logger.refresh_log_display = Mock()
        
        # Generate log
        test_logger.info("Real-time update test")
        
        # Verify display was refreshed
        popup_logger.refresh_log_display.assert_called()
    
    def test_log_overflow_handling(self, integrated_logging_setup):
        """Test handling of log overflow when max messages is reached."""
        popup_logger, log_handler, test_logger = integrated_logging_setup
        
        # Set low max messages for testing
        popup_logger._max_messages = 5
        popup_logger._log_messages.clear()
        
        # Generate more logs than max
        for i in range(10):
            test_logger.info(f"Log message {i}")
        
        # Should only keep last 5 messages
        assert len(popup_logger._log_messages) == 5
        assert popup_logger._log_messages[0]["message"] == "Log message 5"
        assert popup_logger._log_messages[-1]["message"] == "Log message 9"
    
    @patch("src.ui.pages.directory_selection_page.os.path.exists")
    @patch("src.ui.pages.directory_selection_page.os.path.isdir")
    def test_logging_during_directory_search(self, mock_isdir, mock_exists, gui_with_logging):
        """Test logging during directory search operations."""
        gui, popup_logger, test_logger = gui_with_logging
        
        # Create a simple mock navigator instead of using the complex GUI navigator
        mock_navigator = Mock()
        mock_navigator.current_scheme = Mock()
        mock_navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING = "#FFF3E6"
        mock_navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR = "#FFE6E6"
        mock_navigator.set_info_field_state = Mock()
        mock_navigator.invalid_dataset_dir_selected = Mock()
        
        # Setup directory selection page with mock navigator
        dir_page = DirectorySelectionPage(navigator=mock_navigator, n_modules=3)
        dir_page._selected_path = "/test/path"
        
        # Create mock widgets for dropdown and spinner
        mock_dropdown = Mock()
        mock_dropdown.value = Mock()
        mock_spinner = Mock()
        mock_spinner.value = 5
        
        dir_page._search_mode_dropdown = mock_dropdown
        dir_page._search_depth_spinner = mock_spinner
        
        # Mock file system checks to trigger error condition
        mock_exists.return_value = False
        mock_isdir.return_value = False
        
        popup_logger._log_messages.clear()
        
        # Perform directory search - should generate warning log about invalid path
        dir_page.search_dir()
        
        # Verify that the navigator methods were called appropriately
        # The search_dir method should call set_info_field_state and invalid_dataset_dir_selected
        mock_navigator.set_info_field_state.assert_called()
        mock_navigator.invalid_dataset_dir_selected.assert_called()
    
    def test_log_copy_to_clipboard(self, integrated_logging_setup):
        """Test copying logs to clipboard."""
        popup_logger, log_handler, test_logger = integrated_logging_setup
        
        # Generate logs
        test_logger.info("Copy test 1")
        test_logger.error("Copy test error")
        
        # Mock clipboard
        with patch("src.ui.elements.popup_log_system.pyperclip.copy") as mock_copy:
            popup_logger.copy_logs()
            
            # Verify clipboard received formatted logs
            mock_copy.assert_called_once()
            clipboard_content = mock_copy.call_args[0][0]
            assert "Copy test 1" in clipboard_content
            assert "Copy test error" in clipboard_content
            assert "INFO" in clipboard_content
            assert "ERROR" in clipboard_content