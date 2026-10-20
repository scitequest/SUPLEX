import logging
from unittest.mock import MagicMock, patch


class TestMocks:
    """Test suite for mocking external dependencies."""

    @patch("ipywidgets.VBox")
    @patch("ipywidgets.HTML")
    @patch("ipywidgets.Output")
    def test_gui_widget_mocking(self, mock_output, mock_html, mock_vbox):
        """Test mocking of ipywidgets for GUI testing."""
        # Setup mocks
        mock_vbox.return_value = MagicMock()
        mock_html.return_value = MagicMock()
        mock_output.return_value = MagicMock()

        # Create widgets
        content = mock_vbox()
        log_view = mock_html()
        output = mock_output()

        # Verify mocks were called
        mock_vbox.assert_called_once()
        mock_html.assert_called_once()
        mock_output.assert_called_once()

    @patch("logging.getLogger")
    def test_logging_mocking(self, mock_get_logger):
        """Test mocking of logging functionality."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Use logger
        logger = logging.getLogger(__name__)
        logger.info("Test message")
        logger.error("Error message")

        # Verify calls
        mock_logger.info.assert_called_once_with("Test message")
        mock_logger.error.assert_called_once_with("Error message")
