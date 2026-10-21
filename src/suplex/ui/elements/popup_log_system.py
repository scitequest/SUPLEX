import logging
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from typing import Any

import ipywidgets as widgets
import pyperclip

from suplex.config import DEMO
from suplex.ui.styles.popup_logger_styles import get_popup_logger_styles
from suplex.ui.styles.schemes.default_scheme import DEFAULT_SCHEME

logger = logging.getLogger(__name__)


class PopupLogger:
    """
    This class provides a toggleable popup panel that displays log messages with different
    severity levels. It supports features like log filtering, copying to clipboard,
    saving to file, and real-time log display with unread message indicators.
    """

    def __init__(
        self,
        scheme: Any = DEFAULT_SCHEME,
        max_messages: int = 1000,
        min_log_level: int = logging.INFO,
    ) -> None:
        """
        Initialize the popup logger system.

        Args:
            scheme: Color scheme for styling the popup
            max_messages: Maximum number of log messages to retain
            min_log_level: Minimum log level to display (e.g., logging.INFO)
        """
        logger.debug(
            "Initializing popup logger with max_messages=%d, min_level=%s",
            max_messages,
            logging.getLevelName(min_log_level),
        )

        self._scheme = scheme
        self._max_messages = max_messages
        self._is_visible = False
        self._log_messages: list[dict[str, Any]] = []
        self._unread_count = 0
        self._min_log_level = min_log_level

        # UI Components
        self._toggle_button: widgets.Button | None = None
        self._popup_panel: widgets.VBox | None = None
        self._log_output: widgets.HTML | None = None
        self._message_counter: widgets.HTML | None = None

        # Used for scheme updates
        self._close_button: widgets.Button | None = None
        self._clear_button: widgets.Button | None = None
        self._copy_button: widgets.Button | None = None
        self._save_button: widgets.Button | None = None

        try:
            self.create_popup_log_widget()
            logger.debug("Popup logger initialization completed successfully")
        except Exception as e:
            logger.error("Failed to initialize popup logger: %s", e, exc_info=True)
            raise

    @property
    def toggle_button(self) -> widgets.Button | None:
        """
        Get the toggle button widget for showing/hiding the popup logger.

        Returns:
            The toggle button widget
        """
        return self._toggle_button

    @property
    def popup_panel(self) -> widgets.VBox | None:
        """
        Get the main popup panel widget.

        Returns:
            The popup panel widget
        """
        return self._popup_panel

    def create_popup_log_widget(self) -> None:
        """
        Create the main popup log widget components.

        Sets up the toggle button and popup panel with all necessary UI elements.
        """
        logger.debug("Creating popup log widget components")

        try:
            # Create toggle button
            self._toggle_button = widgets.Button(
                description=self._scheme.ICON.STORE,
                button_style="",
                tooltip="Toggle Logger",
                layout=widgets.Layout(
                    flex="0 1 100px",
                    height="100%",
                    overflow_y="hidden",
                    overflow_x="hidden",
                    margin="0px",
                ),
            )

            # Create popup panel
            self._popup_panel = self.create_popup_panel()

            def toggle_popup(button: widgets.Button) -> None:
                """Handle toggle button clicks."""
                if self._is_visible:
                    self.close_popup(button)
                else:
                    self.show_popup()

            self._toggle_button.on_click(toggle_popup)
            self.update_button_appearance()

            logger.debug("Popup log widget components created successfully")

        except Exception as e:
            logger.error("Failed to create popup log widget: %s", e, exc_info=True)
            raise

    def create_popup_panel(self) -> widgets.VBox:
        """
        Create the main popup panel with header, body, and footer sections.

        Returns:
            The complete popup panel widget
        """
        logger.debug("Creating popup panel components")

        try:
            # Header section
            header_text = widgets.HTML("System Logs")
            header_text.add_class("popup-header-title")

            self._close_button = widgets.Button(
                description=self._scheme.ICON.CLOSE,
                button_style="",
                layout=widgets.Layout(width="30px", height="30px", padding="5px"),
            )
            self._close_button.add_class("popup-close-button")
            self._close_button.on_click(self.close_popup)

            header = widgets.HBox(
                [header_text, self._close_button],
                layout=widgets.Layout(
                    justify_content="space-between",
                    align_items="center",
                    padding="0px 20px",
                    height="40px",
                    max_height="60px",
                    width="auto",
                    overflow="hidden",
                ),
            )
            header.add_class("popup-header-override")

            # Body section
            self._log_output = widgets.HTML(
                value="",
                layout=widgets.Layout(
                    width="100%",
                    height="auto",
                    border="none",
                ),
            )
            log_container = widgets.VBox(
                children=[self._log_output],
                layout=widgets.Layout(
                    height="auto",
                    width="100%",
                    overflow_y="auto",
                    overflow_x="hidden",
                    padding="10px",
                    border="none",
                    flex="1",
                ),
            )
            log_container.add_class("popup-log-container-override")

            # Footer section
            min_level_dropdown = widgets.Dropdown(
                options=[
                    ("Debug", logging.DEBUG),
                    ("Info", logging.INFO),
                    ("Warning", logging.WARNING),
                    ("Error", logging.ERROR),
                    ("Critical", logging.CRITICAL),
                ],
                value=self._min_log_level,
                description="",
                layout=widgets.Layout(width="auto", height="40%"),
            )

            def dropdown_changed(change: dict[str, Any]) -> None:
                """Handle log level filter changes."""
                old_level = self._min_log_level
                self._min_log_level = int(min_level_dropdown.value)
                logger.debug(
                    "Log level filter changed from %s to %s",
                    logging.getLevelName(old_level),
                    logging.getLevelName(self._min_log_level),
                )
                self.refresh_log_display()

            min_level_dropdown.observe(dropdown_changed, names="value")

            # Action buttons
            self._clear_button = widgets.Button(
                description=self._scheme.ICON.CLEAR,
                button_style="",
                tooltip="Clear all logs",
                layout=widgets.Layout(width="65px", height="30px"),
            )
            self._clear_button.add_class("popup-button-clear")
            self._clear_button.on_click(lambda b: self.clear_logs())

            self._copy_button = widgets.Button(
                description=self._scheme.ICON.STORE,
                button_style="",
                tooltip="Copy logs to clipboard",
                layout=widgets.Layout(width="65px", height="30px"),
            )
            self._copy_button.add_class("popup-button-copy")
            self._copy_button.on_click(lambda b: self.copy_logs())

            self._save_button = widgets.Button(
                description=self._scheme.ICON.SAVE,
                button_style="",
                tooltip="Save logs to file",
                disabled=DEMO,
                layout=widgets.Layout(width="65px", height="30px"),
            )
            self._save_button.add_class("popup-button-save")
            self._save_button.on_click(lambda b: self.save_logs())

            button_box = widgets.HBox([self._clear_button, self._copy_button, self._save_button])

            self._message_counter = widgets.HTML("0 messages")
            self._message_counter.add_class("popup-message-counter")

            bottom_box = widgets.HBox(
                [button_box, self._message_counter],
                layout=widgets.Layout(
                    justify_content="space-between",
                    align_items="center",
                    height="60%",
                    overflow_y="invisible",
                ),
            )

            footer = widgets.VBox(
                [min_level_dropdown, bottom_box],
                layout=widgets.Layout(
                    width="auto",
                    height="80px",
                    padding="5px 10px",
                ),
            )
            footer.add_class("popup-footer-override")

            # Create complete panel
            panel = widgets.VBox(
                [get_popup_logger_styles(self._scheme), header, log_container, footer],
                layout=widgets.Layout(
                    # 7:6 aspect ratio
                    height="408px",
                    width="350px",
                    z_index="10000",
                    display="none",
                    position="static",
                    margin="10px",
                    overflow="hidden",
                ),
            )

            panel.add_class("popup-panel-override")

            logger.debug("Popup panel components created successfully")
            return panel

        except Exception as e:
            logger.error("Failed to create popup panel: %s", e, exc_info=True)
            raise

    def show_popup(self) -> None:
        """
        Show the popup panel and mark all messages as read.
        """
        logger.debug("Showing popup logger panel")

        try:
            self._popup_panel.layout.display = "flex"
            self._is_visible = True
            self._unread_count = 0
            self.update_button_appearance()
            self.refresh_log_display()

        except Exception as e:
            logger.error("Failed to show popup: %s", e, exc_info=True)

    def close_popup(self, button: widgets.Button | None = None) -> None:
        """
        Hide the popup panel.

        Args:
            button: The button that triggered the close (optional)
        """
        logger.debug("Closing popup logger panel")

        try:
            self._popup_panel.layout.display = "none"
            self._is_visible = False
            self.update_button_appearance()

        except Exception as e:
            logger.error("Failed to close popup: %s", e, exc_info=True)

    def update_button_appearance(self) -> None:
        """
        Update the toggle button appearance based on unread message count.
        """
        try:
            if self._unread_count > 0:
                badge = "99+" if self._unread_count > 99 else str(self._unread_count)
                self._toggle_button.description = f"{self._scheme.ICON.STORE} {badge}"
                self._toggle_button.remove_class("popup-toggle-button-normal")
                self._toggle_button.add_class("popup-toggle-button-unread")
            else:
                self._toggle_button.description = self._scheme.ICON.STORE
                self._toggle_button.remove_class("popup-toggle-button-unread")
                self._toggle_button.add_class("popup-toggle-button-normal")

        except Exception as e:
            logger.error("Failed to update button appearance: %s", e, exc_info=True)

    def refresh_log_display(self) -> None:
        """
        Refresh the log display with current messages and filtering.
        """
        try:
            # Filter messages by current log level
            filtered_messages = [
                msg for msg in self._log_messages if msg["level"] >= self._min_log_level
            ]
            recent_messages = filtered_messages[-100:]  # Show last 100 filtered messages

            if not recent_messages:
                content = f"<div class='popup-log-empty'>{self._scheme.ICON.STORE} No logged messages yet</div>"
            else:
                log_entries = []

                for msg in recent_messages:
                    level_icon, level_class, level_name = self.get_level_info(msg["level"])

                    log_entry = f"""
                    <div class="popup-log-entry {level_class}">
                        <div class="popup-log-entry-header">
                            <span class="popup-log-level-icon">{level_icon}{level_name}</span>
                            <span class="popup-log-timestamp">[{msg["timestamp"]}]</span>
                        </div>
                        <div class="popup-log-message">{msg["message"]}</div>
                    </div>
                    """
                    log_entries.append(log_entry)

                content = "".join(log_entries)

            self._log_output.value = f'<div class="popup-log-display">{content}</div>'
            self._message_counter.value = f"{len(self._log_messages)} messages"

        except Exception as e:
            logger.error("Failed to refresh log display: %s", e, exc_info=True)

    def get_level_info(self, level: int) -> tuple[str, str, str]:
        """
        Get display information for a log level.

        Args:
            level: The logging level integer

        Returns:
            Tuple of (icon, css_class, display_name)
        """
        level_mapping = {
            logging.DEBUG: (self._scheme.ICON.DEBUG, "popup-log-debug", "Debug"),
            logging.INFO: (self._scheme.ICON.INFO, "popup-log-info", "Info"),
            logging.WARNING: (
                self._scheme.ICON.WARNING,
                "popup-log-warning",
                "Warning",
            ),
            logging.ERROR: (self._scheme.ICON.ERROR, "popup-log-error", "Error"),
            logging.CRITICAL: (
                self._scheme.ICON.CRITICAL,
                "popup-log-critical",
                "Critical",
            ),
        }

        return level_mapping.get(
            level, (self._scheme.ICON.DEFAULT, "popup-log-default", "Unspecified")
        )

    def clear_logs(self) -> None:
        """
        Clear all stored log messages and refresh the display.
        """
        logger.debug("Clearing all log messages")

        try:
            self._log_messages.clear()
            self._unread_count = 0
            self.update_button_appearance()
            self.refresh_log_display()

        except Exception as e:
            logger.error("Failed to clear logs: %s", e, exc_info=True)

    def copy_logs(self) -> None:
        """
        Copy all log messages to the system clipboard.
        """
        logger.debug("Copying logs to clipboard")

        if not self._log_messages:
            self.add_log_message("No logs to copy.", logging.INFO)
            return

        try:
            log_text = self.format_logs_as_text()
            pyperclip.copy(log_text)
            self.add_log_message("Logs copied to clipboard.", logging.INFO)
            logger.debug(
                "Successfully copied %d log messages to clipboard",
                len(self._log_messages),
            )

        except Exception as e:
            error_msg = f"Error copying logs: {str(e)}"
            self.add_log_message(error_msg, logging.ERROR)
            logger.error("Failed to copy logs to clipboard: %s", e, exc_info=True)

    def save_logs(self) -> None:
        """
        Save all log messages to a file using a file dialog.
        """
        logger.debug("Saving logs to file")

        if not self._log_messages:
            self.add_log_message("No logs to save.", logging.INFO)
            return

        root = None
        try:
            root = tk.Tk()
            root.withdraw()

            filepath = filedialog.asksaveasfilename(
                title="Save Logs",
                defaultextension=".log",
                filetypes=[
                    ("Log Files", "*.log"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*"),
                ],
                initialfile=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                initialdir=os.path.expanduser("~"),
            )

            if not filepath:
                self.add_log_message("Log save cancelled", logging.INFO)
                return

            log_text = self.format_logs_as_text()

            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(log_text)

            self.add_log_message(f"Logs saved to: {filepath}", logging.INFO)
            logger.info(
                "Successfully saved %d log messages to: %s",
                len(self._log_messages),
                filepath,
            )

        except Exception as e:
            error_msg = f"Error saving logs: {str(e)}"
            self.add_log_message(error_msg, logging.ERROR)
            logger.error("Failed to save logs to file: %s", e, exc_info=True)

        finally:
            if root:
                root.destroy()

    def format_logs_as_text(self) -> str:
        """
        Format all log messages as plain text.

        Returns:
            Formatted log text suitable for saving or copying
        """
        try:
            lines = []
            for log_entry in self._log_messages:
                level_name = logging.getLevelName(log_entry["level"])
                line = f"{level_name} - {log_entry['timestamp']}: {log_entry['message']}"
                lines.append(line)

            return "\n".join(lines)

        except Exception as e:
            logger.error("Failed to format logs as text: %s", e, exc_info=True)
            return "Error formatting logs"

    def add_log_message(self, message: str, level: int = logging.INFO) -> None:
        """
        Add a new log message to the system.

        Args:
            message: The log message text
            level: The logging level (e.g., logging.INFO, logging.ERROR)
        """
        if level < int(self._min_log_level):
            return

        try:
            timestamp = datetime.now().strftime("%H:%M:%S")

            log_entry = {
                "message": message,
                "level": level,  # Stored as an integer
                "timestamp": timestamp,
            }

            self._log_messages.append(log_entry)

            # Maintain maximum message count
            if len(self._log_messages) > self._max_messages:
                self._log_messages = self._log_messages[-self._max_messages :]

            # Update unread count if popup is not visible
            if not self._is_visible:
                self._unread_count += 1
                self.update_button_appearance()

            # Refresh display if popup is visible
            if self._is_visible:
                self.refresh_log_display()

        except Exception as e:
            # Avoid infinite recursion by not using logger here
            print(f"Error adding log message: {e}")

    def update_scheme(self, new_scheme: Any) -> None:
        """
        Update the popup logger's color scheme and refresh UI elements.

        Args:
            new_scheme: The new color scheme to apply
        """
        logger.debug("Updating popup logger color scheme to: %s", new_scheme.NAME)

        try:
            self._scheme = new_scheme

            # Update button icons
            if self._close_button:
                self._close_button.description = self._scheme.ICON.CLOSE
            if self._clear_button:
                self._clear_button.description = self._scheme.ICON.CLEAR
            if self._copy_button:
                self._copy_button.description = self._scheme.ICON.STORE
            if self._save_button:
                self._save_button.description = self._scheme.ICON.SAVE

            self.update_button_appearance()
            self.refresh_log_display()

            # Update panel styles
            if self._popup_panel:
                new_panel = (get_popup_logger_styles(self._scheme),) + self._popup_panel.children[
                    1:
                ]
                self._popup_panel.children = new_panel

            logger.debug("Popup logger color scheme updated successfully")

        except Exception as e:
            logger.error("Failed to update popup logger color scheme: %s", e, exc_info=True)


class PopupLogHandler(logging.Handler):
    """
    Custom logging handler that forwards log messages to the PopupLogger.

    This handler integrates with Python's logging system to automatically
    capture and display log messages in the popup logger interface.
    """

    def __init__(self, popup_logger: PopupLogger) -> None:
        """
        Initialize the popup log handler.

        Args:
            popup_logger: The PopupLogger instance to send messages to
        """
        super().__init__()
        self._popup_logger = popup_logger

    def emit(self, record: logging.LogRecord) -> None:
        """
        Handle a log record by forwarding it to the popup logger.

        Args:
            record: The log record to handle
        """
        try:
            message = self.format(record)
            self._popup_logger.add_log_message(message, record.levelno)

        except Exception:
            # Silently ignore errors to avoid infinite recursion
            pass
