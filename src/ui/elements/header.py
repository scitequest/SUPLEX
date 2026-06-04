import logging
import base64
import os
from typing import TYPE_CHECKING, Dict, Any, Callable, List, Optional

import ipywidgets as widgets

if TYPE_CHECKING:
    from .gui import GUI

from general_constants import VERSION_NUMBER
from ui.styles.header_styles import get_header_styles

logger = logging.getLogger(__name__)


class Header:
    """
    This class manages the header section of the application which includes the SUPLEX logo,
    title, version information, social media links, and theme selection dropdown. It handles
    icon loading, theme switching, and triggers UI updates when schemes change.
    """

    def __init__(self, gui: "GUI", schemes: Dict[str, Any]) -> None:
        """
        Initialize the header component.

        Args:
            gui: Reference to the main GUI instance
            schemes: Dictionary of available color schemes
        """
        logger.debug("Initializing header component with %d schemes", len(schemes))

        self._gui = gui
        self._schemes = schemes
        self._selected_scheme = "Default"
        self._theme_dropdown: Optional[widgets.Dropdown] = None
        self._ui: Optional[widgets.VBox] = None

        try:
            self.update_ui_element()
            logger.debug("Header initialization completed successfully")
        except Exception as e:
            logger.error("Failed to initialize header: %s", e, exc_info=True)
            raise

    def update_ui_element(self) -> None:
        """
        Update and rebuild the header UI elements.

        Creates or recreates all header components including logo, title, version info,
        social media links, and theme dropdown. Applies current scheme styling.
        """
        logger.debug("Updating header UI elements")

        try:
            # Load icons with current scheme
            suplex_icon = self.load_icon(self.current_scheme.ICON.IMAGE_PATH.SUPLEX, 60)
            martin_icon = self.load_icon(self.current_scheme.ICON.IMAGE_PATH.MARTIN, 22)
            x_icon = self.current_scheme.ICON.SVG.X
            github_icon = self.current_scheme.ICON.SVG.GITHUB

            # Left-hand side components
            logo_widget = widgets.HTML(
                value=f"<div class='header-logo'>{suplex_icon}</div>",
                layout=widgets.Layout(width="auto"),
            )

            title_widget = widgets.HTML(
                value="<div class='header-title'>SUPLEX</div>",
                layout=widgets.Layout(width="auto", padding="0px 0px 0px 15px"),
            )

            # Right-hand side components
            version = widgets.HTML(
                value=f"<div class='header-version'>Version {VERSION_NUMBER}</div>",
                layout=widgets.Layout(width="auto", justify_content="flex-end"),
            )
            version_box = widgets.HBox(
                [version],
                layout=widgets.Layout(width="auto", justify_content="flex-end"),
            )
            version_box.add_class("version-box")

            link_icons = widgets.HTML(
                value=f"""
                <div class="header-social-icons">
                    <a href="https://x.com/scitequest" target="_blank" class="social-icon">
                        {x_icon}
                    </a>
                    <a href="https://github.com/scitequest/scitequest-SUPLEX" target="_blank" class="social-icon">
                        {github_icon}
                    </a>
                    <a href="https://github.com/scitequest/martin" target="_blank" class="social-icon">
                        {martin_icon}
                    </a>
                </div>
                """,
                layout=widgets.Layout(width="auto"),
            )
            icon_box = widgets.HBox(
                [link_icons],
                layout=widgets.Layout(
                    width="auto", height="auto", padding="0px 20px 0px 0px", overflow="visible"
                ),
            )
            icon_box.add_class("icon-box")

            self.update_theme_dropdown()

            # Create container sections
            left_section = widgets.HBox(
                [logo_widget, title_widget],
                layout=widgets.Layout(
                    width="auto",
                    height="100%",
                    align_items="center",
                    justify_content="flex-start",
                ),
            )
            left_section.add_class("header-left-section")

            right_bottom_section = widgets.HBox(
                [icon_box, self._theme_dropdown],
                layout=widgets.Layout(
                    width="auto",
                    height="40px",
                    align_items="center",
                    justify_content="flex-end",
                    overflow="visible",
                ),
            )
            right_bottom_section.add_class("header-right-bottom-section")

            right_section = widgets.VBox(
                [version_box, right_bottom_section],
                layout=widgets.Layout(
                    width="auto",
                    justify_content="space-between",
                    padding="10px 0px",  # Top and bottom padding
                ),
            )
            right_section.add_class("header-right-section")

            header_container = widgets.HBox(
                [left_section, right_section],
                layout=widgets.Layout(
                    width="100%",
                    height="100%",
                    justify_content="space-between",
                    margin="0px",
                    padding="0px 10px",  # left and right padding
                ),
            )
            header_container.add_class("suplex-header-container")

            # Create final header with styling
            header = widgets.VBox(
                [header_container, get_header_styles(self.current_scheme)],
                layout=widgets.Layout(width="100%", height="100px", margin="0px"),
            )

            self._ui = header
            logger.debug("Header UI elements updated successfully")

        except Exception as e:
            logger.error("Failed to update header UI elements: %s", e, exc_info=True)
            raise

    def load_icon(self, file_path: str, size: int) -> str:
        """
        Load an icon from file path and convert to base64 data URL.

        Args:
            file_path: Path to the icon image file
            size: Desired height of the icon in pixels

        Returns:
            HTML img tag with base64 encoded image data or fallback div
        """
        logger.debug("Loading icon: %s (size: %dpx)", file_path, size)

        try:
            if not os.path.exists(file_path):
                logger.warning("Icon file not found: %s", file_path)
                return f'<div style="width: {size}px; height: {size}px; background: #ddd; border-radius: 4px;"></div>'

            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()

            # Determine MIME type
            mime = "image/png" if file_path.endswith(".png") else "image/jpeg"

            logger.debug("Successfully loaded icon: %s", file_path)
            return f'<img src="data:{mime};base64,{encoded}" style="height: {size}px;">'

        except Exception as e:
            logger.error("Could not load header icon: %s - %s", file_path, e, exc_info=True)
            return f'<div style="width: {size}px; height: {size}px; background: #ddd; border-radius: 4px;"></div>'

    def update_theme_dropdown(self) -> None:
        """
        Create or update the theme selection dropdown widget.

        Sets up the dropdown with available themes and handles theme change events.
        """
        logger.debug("Updating theme dropdown with %d schemes", len(self._schemes))

        try:
            theme_options = [(name, name) for name in self._schemes.keys()]

            self._theme_dropdown = widgets.Dropdown(
                options=theme_options,
                value=self._selected_scheme,
                description="",
                layout=widgets.Layout(
                    width="22px", height="22px", margin="0px", overflow="visible"
                ),
            )
            self._theme_dropdown.add_class("header-theme-dropdown-widget")

            def on_theme_change() -> None:
                """Handle theme selection change."""
                old_scheme = self._selected_scheme
                new_scheme = self._theme_dropdown.value

                if old_scheme == new_scheme:
                    return

                logger.info("Theme changed from '%s' to '%s'", old_scheme, new_scheme)

                self._selected_scheme = new_scheme
                self.update_ui_element()
                self._gui.update_scheme(self.current_scheme)

            self._theme_dropdown.observe(lambda change: on_theme_change(), names="value")
            logger.debug("Theme dropdown updated successfully")

        except Exception as e:
            logger.error("Failed to update theme dropdown: %s", e, exc_info=True)
            raise

    @property
    def current_scheme(self) -> Any:
        """
        Get the currently selected color scheme.

        Returns:
            The current color scheme object
        """
        return self._schemes[self._selected_scheme]

    @property
    def ui(self) -> Optional[widgets.VBox]:
        """
        Get the header UI widget.

        Returns:
            The header widget container
        """
        return self._ui
