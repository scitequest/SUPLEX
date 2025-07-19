import logging
from typing import Dict, Any, Optional
import ipywidgets as widgets

from ui.elements.popup_log_system import PopupLogger
from ui.elements.header import Header
from ui.elements.navigator import Navigator

from ui.styles.gui_styles import get_gui_styles
from ui.styles.widget_styles import get_widget_styles

logger = logging.getLogger(__name__)


class GUI:
    """
    Main GUI class that manages the user interface components and layout.

    This class orchestrates the overall GUI structure including header, navigation,
    content area, and info field. It handles scheme updates, content management,
    and layout rendering.
    """

    def __init__(
        self,
        modules: Dict[str, Any],
        schemes: Dict[str, Any],
        content: widgets.Box,
        popup_logger: PopupLogger,
    ) -> None:
        """
        Initialise the GUI with modules, schemes, content container, and logger.

        Args:
            modules: Dictionary containing available modules
            schemes: Dictionary of available colour schemes
            content: IPython widget Box to contain the GUI layout
            popup_logger: Logger instance for popup notifications
        """
        logger.debug(
            f"Initialising GUI with {len(modules)} modules and {len(schemes)} schemes"
        )

        self._modules = modules
        self._schemes = schemes
        self._current_scheme = schemes["Default"]
        self._content = content

        # UI Components
        self._header: Optional[Header] = None
        self._navigator: Optional[Navigator] = None
        self._content_area: Optional[widgets.VBox] = None
        self._content_holder: Optional[widgets.VBox] = None

        # Info field state management
        self._info_field: Optional[widgets.HTML] = None
        self._info_field_state: Dict[str, Any] = {
            "message": "",
            "info_color": self._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT,
            "info_icon": self._current_scheme.ICON.DEFAULT,
        }
        self._info_container: Optional[widgets.HBox] = None

        self._popup_logger = popup_logger
        self._current_page: Optional[Any] = None

        logger.debug("GUI initialization completed successfully")

    def build_gui(self) -> None:
        """
        Build and initialize all GUI components.
        Done separate from the regular initialization to make bidirectional associations easier.

        Creates the header, navigator, content areas, and info field.
        Sets up the initial layout and styling for the GUI.
        """
        logger.debug("Building GUI components")

        try:
            # Initialize header
            self._header = Header(gui=self, schemes=self._schemes)
            default_scheme = self._header.current_scheme

            # Create content holder with scrolling capability
            self._content_holder = widgets.VBox(
                layout=widgets.Layout(
                    width="100%",
                    height="100%",
                    min_height="0",
                    max_height="100%",
                    overflow="auto",
                    flex_shrink="1",
                    flex_grow="0",
                    padding="0",
                )
            )
            self._content_holder.add_class("gui-content-holder")

            logger.debug("Creating main content area")
            self._content_area = widgets.VBox(
                [get_widget_styles(self._current_scheme), self._content_holder],
                layout=widgets.Layout(
                    width="100%", flex="1 1 0", min_height="0", overflow="hidden"
                ),
            )
            self._content_area.add_class("gui-content-area")

            # Initialize navigator
            self._navigator = Navigator(
                gui=self, scheme=default_scheme, modules=self._modules
            )
            self._navigator.initialize_pages()

            # Create info field for status messages
            logger.debug("Creating info field")
            self._info_field = widgets.HTML(
                layout=widgets.Layout(
                    height="100%",
                    flex="0 1 100%",
                    padding="0px 5px 0px 0px",
                    margin="0px",
                    overflow_y="auto",
                )
            )
            self._info_field.add_class("gui-info-field")

            # Create info container with logger toggle
            logger.debug("Creating info container")
            self._info_container = widgets.HBox(
                [self._info_field, self._popup_logger.toggle_button],
                layout=widgets.Layout(
                    height="60px",
                    width="100%",
                    overflow_y="hidden",
                    overflow_x="hidden",
                ),
            )
            self._info_container.add_class("gui-info-container")

            self.update_layout()
            logger.debug("GUI build completed successfully")

        except Exception as e:
            logger.error("Failed to build GUI: %s", e, exc_info=True)
            raise

    def update_layout(self) -> None:
        """
        Update the main GUI layout with all components.

        Assembles the complete GUI layout including header, navigator, content area,
        and info container. Applies CSS classes and positioning.
        """
        logger.debug("Updating GUI layout")

        try:
            # Create main layout structure
            # TODO: solve main layout styling completeley via the css and force min and max size values.
            main_layout = widgets.VBox(
                [
                    get_gui_styles(self._current_scheme),
                    self._header.ui,
                    self._navigator.get_ui_element(),
                    self._content_area,
                    self._info_container,
                ],
                layout=widgets.Layout(
                    width="100%",
                    min_width="320px",
                    height="100%",
                    min_height="560px",
                    overflow="auto",
                    box_sizing="border-box",
                    display="flex",
                    flex_flow="column",
                    position="relative",
                    top="0",
                    left="0",
                    z_index="1",
                ),
            )
            main_layout.add_class("gui-main-layout")

            # Add CSS classes to components makes changing styles easier.
            if self._header and self._header.ui:
                self._header.ui.add_class("gui-header")
                logger.debug("Applied CSS class to header")

            if self._navigator:
                navigator_ui = self._navigator.get_ui_element()
                navigator_ui.add_class("gui-navigator")
                logger.debug("Applied CSS class to navigator")

            # Create logger overlay box
            logger_box = widgets.Box(
                [self._popup_logger.popup_panel],
                layout=widgets.Layout(
                    width="auto",
                    height="auto",
                    margin="auto 0 0 auto",
                    z_index="9999",  # top level
                ),
            )

            # Set up grid layout
            main_layout.layout.grid_area = "1 / 1 / 2 / 2"
            logger_box.layout.grid_area = "1 / 1 / 2 / 2"
            self._content.children = [
                get_gui_styles(self._current_scheme),
                main_layout,
                logger_box,
            ]

            self.set_info_field_state("")
            logger.debug("Layout update completed successfully")

        except Exception as e:
            logger.error("Failed to update layout: %s", e, exc_info=True)
            raise

    def update_content_holder(self, new_content: widgets.Widget) -> None:
        """
        Update the content holder with new content.
        This can either be a page or a module.

        Args:
            new_content: The new content to display in the content holder
        """
        logger.debug(
            "Updating content holder with new content: %s", type(new_content).__name__
        )

        try:
            self._content_holder.children = [new_content]
            logger.debug("Content holder updated successfully")
        except Exception as e:
            logger.error("Failed to update content holder: %s", e, exc_info=True)
            raise

    def set_info_field_state(
        self,
        message: str = "",
        info_color: Optional[str] = None,
        info_icon: Optional[str] = None,
    ) -> None:
        """
        Set the info field state and update the display.

        Args:
            message: The message text to display (default: empty string)
            info_color: The color scheme for the info field (default: scheme default)
            info_icon: The icon to display (default: scheme default)
        """
        logger.debug("Setting info field state: message='%s'", message)

        if info_color is None:
            info_color = self._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT

        # If icon is not specified use default icon of info level
        if info_icon is None:
            if info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT:
                info_icon = self._current_scheme.ICON.DEFAULT
            elif info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO:
                info_icon = self._current_scheme.ICON.INFO
            elif info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS:
                info_icon = self._current_scheme.ICON.SUCCESS
            elif info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING:
                info_icon = self._current_scheme.ICON.WARNING
            elif info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR:
                info_icon = self._current_scheme.ICON.ERROR
            elif info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL:
                info_icon = self._current_scheme.ICON.CRITICAL
            elif info_color == self._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG:
                info_icon = self._current_scheme.ICON.DEBUG

        self._info_field_state["message"] = message
        self._info_field_state["info_color"] = info_color
        self._info_field_state["info_icon"] = info_icon

        self.update_info_field(
            self._info_field_state["message"],
            self._info_field_state["info_color"],
            self._info_field_state["info_icon"],
        )

        logger.debug("Info field state set successfully")

    def update_info_field(self, message: str, info_color: str, info_icon: str) -> None:
        """
        Update the info field with a new message, color, and icon.

        Args:
            message: The message text to display
            info_color: The color scheme for the info field
            info_icon: The icon to display with the message
        """
        logger.debug("Updating info field: message='%s'", message)

        try:
            color_class_map = {
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT: "gui-info-field-default",
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO: "gui-info-field-info",
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS: "gui-info-field-success",
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING: "gui-info-field-warning",
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR: "gui-info-field-error",
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL: "gui-info-field-critical",
                self._current_scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG: "gui-info-field-debug",
            }

            # Remove all previous color classes
            for css_class in color_class_map.values():
                self._info_field.remove_class(css_class)

            # Apply new styling and content
            css_class = color_class_map.get(info_color, "gui-info-field-default")
            self._info_field.value = f"{info_icon} {message}"
            self._info_field.add_class(css_class)

            logger.debug("Info field updated with class: %s", css_class)

        except Exception as e:
            logger.error("Failed to update info field: %s", e, exc_info=True)

    def clear_hover_text(self) -> None:
        """
        Clear any hover text and restore the info field to its saved state.

        This method is typically called when mouse hover events end to restore
        the info field to its persistent state.
        """
        logger.debug("Clearing hover text and restoring info field state")

        self.update_info_field(
            self._info_field_state["message"],
            self._info_field_state["info_color"],
            self._info_field_state["info_icon"],
        )

    def update_scheme(self, scheme: Any) -> None:
        """
        Update the GUI color scheme and refresh all components.

        Args:
            scheme: The new color scheme to apply to the GUI
        """
        logger.info("Updating GUI color scheme to: %s", scheme.NAME)

        try:
            self._current_scheme = scheme

            # Update content area styles
            new_content_area = (
                get_widget_styles(self._current_scheme),
            ) + self._content_area.children[1:]
            self._content_area.children = new_content_area

            # Update main content styles
            new_content = (
                get_gui_styles(self._current_scheme),
            ) + self._content.children[1:]
            self._content.children = new_content

            # Update component schemes
            self._navigator.update_scheme(new_scheme=scheme)
            self._popup_logger.update_scheme(new_scheme=scheme)

            # Refresh layout and show confirmation message
            self.update_layout()
            self.update_info_field(
                message=f"Changed color scheme to: {scheme.NAME}.",
                info_color=scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
                info_icon=scheme.ICON.INFO,
            )
            logger.debug("Color scheme update completed successfully")

        except Exception as e:
            logger.error("Failed to update color scheme: %s", e, exc_info=True)
            raise

    @property
    def current_scheme(self) -> Any:
        """
        Get the currently active color scheme.

        Returns:
            The current color scheme object
        """
        return self._current_scheme
