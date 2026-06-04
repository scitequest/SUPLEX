import logging
import os
import base64
from typing import TYPE_CHECKING, List, Optional, Any

import ipywidgets as widgets
from ipyevents import Event

from ui.widget_factory import WidgetFactory

if TYPE_CHECKING:
    from ui.elements.navigator import Navigator

logger = logging.getLogger(__name__)


class ModuleSelectionPage:
    """
    This page organizes modules by groups and displays them as interactive tiles.
    Each module tile shows information about the module and indicates whether it's
    viable for the selected datasets. Users can click on viable modules to launch them.
    """

    def __init__(self, navigator: "Navigator", modules: List[Any]) -> None:
        """
        Initialize the module selection page.

        Args:
            navigator: Reference to the navigator component
            modules: List of available module instances
        """
        logger.debug("Initializing module selection page with %d modules", len(modules))

        self._navigator = navigator
        self._modules = modules
        self._module_tiles: List[widgets.Widget] = []
        self._tile_events: List[Event] = []

        logger.debug("Module selection page initialized successfully")

    def get_ui(self, datasets: List[Any]) -> widgets.Widget:
        """
        Generate the user interface for the module selection page.

        Creates a tabbed interface where modules are grouped by their group_name.
        Each module is displayed as a tile with styling based on viability for
        the provided datasets.

        Args:
            datasets: List of selected datasets to check module viability against

        Returns:
            Widget containing the complete module selection interface
        """
        logger.debug("Building module selection UI for %d datasets", len(datasets))

        try:
            # Clean reset for new dataset selection
            self._module_tiles = []
            # Store module names for tile sorting
            module_names = {}
            self._tile_events = []

            tabs = {}
            viable_count = 0
            total_count = 0

            logger.debug("Processing %d modules for UI generation", len(self._modules))

            # Process each module and organize by groups
            for i, module in enumerate(self._modules):
                try:
                    group_name = module.group_name
                    module_name = module.module_name

                    logger.debug(
                        "Processing module %d: %s (group: %s)",
                        i,
                        module_name,
                        group_name,
                    )

                    if not group_name or str(group_name).strip() == "":
                        group_name = "No group"
                        logger.debug("Assigned default group to module %s", module_name)

                    # Check if module is viable for the selected datasets
                    is_viable = module.check_if_viable(datasets)
                    logger.debug("Module %s viability check: %s", module_name, is_viable)

                    total_count += 1
                    if is_viable:
                        viable_count += 1

                    # Create module tile
                    tile_widget = self.create_module_tile(module, is_viable)
                    if tile_widget is not None:
                        self._module_tiles.append(tile_widget)

                        # Organize tiles by group
                        if group_name not in tabs:
                            tabs[group_name] = []
                            module_names[group_name] = []
                            logger.debug("Created new tab group: %s", group_name)
                        tabs[group_name].append(tile_widget)
                        module_names[group_name].append(module_name.lower())
                    else:
                        logger.warning("Failed to create tile for module %s", module_name)

                except Exception as e:
                    logger.error("Error processing module %d: %s", i, e, exc_info=True)
                    continue

            # Set initial info field state based on module availability
            if viable_count == 0:
                self._navigator.set_info_field_state(
                    message="No modules are compatible with the selected datasets.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING,
                )
            else:
                self._navigator.set_info_field_state(
                    message=f"{viable_count} of {total_count} modules are available for your datasets.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
                )

            # Handle case where no valid modules were found
            if not tabs:
                logger.warning("No valid modules found after processing")
                return WidgetFactory.vbox(
                    children=[WidgetFactory.html_widget(value="<h3>No modules available</h3>")],
                    width="100%",
                    height="100%",
                )

            # Apply sorting to tabs - case insensitive
            tabs = dict(sorted(tabs.items(), key=lambda item: item[0].lower()))
            if "Adapters" in tabs:
                tabs = {"Adapters": tabs.pop("Adapters")} | tabs  # second

            if "Vanilla" in tabs:
                tabs = {"Vanilla": tabs.pop("Vanilla")} | tabs  # first

            if "No group" in tabs:
                tabs = tabs | {"No group": tabs.pop("No group")}  # last

            module_names[group_name].append(module_name)

            # Sort Modules per tab alphabetically
            for key in module_names:
                if key in tabs:
                    paired_sorted = sorted(zip(module_names[key], tabs[key]), key=lambda x: x[0])
                    module_names[key], tabs[key] = zip(*paired_sorted)
                    tabs[key] = list(tabs[key])

            # Create tab structure
            tab_children = []
            tab_titles = []

            for group_name, tiles in tabs.items():
                logger.debug("Creating tab content for %s with %d tiles", group_name, len(tiles))

                # Create grid container for module tiles
                group_content = WidgetFactory.grid_container(
                    children=list(tiles),
                    padding="10px",
                    width="100%",
                    height="100%",
                    overflow_y="auto",
                    overflow_x="hidden",
                )

                tab_children.append(group_content)
                tab_titles.append(group_name)

            logger.debug("Creating tab widget with %d tabs: %s", len(tab_children), tab_titles)

            # Create main tab widget
            tab_widget = WidgetFactory.tab(
                children=list(tab_children),
                layout=widgets.Layout(
                    width="100%", height="100%", overflow="hidden", padding="5px"
                ),
            )

            # Apply styling and set titles
            tab_widget.add_class("styled-widget")
            tab_widget.add_class("styled-tab")

            for i, title in enumerate(tab_titles):
                if i < len(tab_children):
                    tab_widget.set_title(i, title)

            logger.debug("Module selection UI built successfully with %d groups", len(tab_titles))
            return tab_widget

        except Exception as e:
            logger.error("Failed to build module selection UI: %s", e, exc_info=True)
            return WidgetFactory.html_widget(
                value="<div style='text-align: center; padding: 40px;'>Error loading module selection page</div>",
                width="100%",
                height="100%",
            )

    def create_module_tile(self, module: Any, is_viable: bool) -> Optional[widgets.Widget]:
        """
        Creates a styled HTML widget representing the module with hover effects,
        click handlers, and visual indicators for viability status.

        Args:
            module: Module instance to create tile for
            is_viable: Whether the module is viable for current datasets

        Returns:
            Widget containing the module tile, or None if creation fails
        """
        logger.debug("Creating tile for module: %s (viable: %s)", module.module_name, is_viable)

        try:
            # Get module styling
            button_style = module.button_style
            background_color = button_style.get("button_color", "#FFFFFF")
            text_color = button_style.get("font_color", "#000000")

            # Create HTML tile widget

            # Current implementation ignores widget factory. Might change this later to be more responsive to desing schemes
            tile_html = widgets.HTML(
                value=self.get_tile_html(module, background_color, text_color, is_viable),
                layout=widgets.Layout(width="280px", height="160px"),
            )

            # Set up event handlers
            events = []

            # Hover events for info display - show module details temporarily
            hover_event = Event(source=tile_html, watched_events=["mouseenter"])
            hover_event.on_dom_event(
                lambda event, mod=module: self._navigator.update_info_field(
                    mod.get_module_hover_text(),
                    self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT,
                    self._navigator.current_scheme.ICON.DEFAULT,
                )
            )

            hover_release = Event(source=tile_html, watched_events=["mouseleave"])
            hover_release.on_dom_event(lambda event: self._navigator.clear_hover_text())

            events.extend([hover_event, hover_release])

            # Click event for viable modules
            if is_viable:
                click_event = Event(source=tile_html, watched_events=["click"])
                click_event.on_dom_event(
                    lambda event, mod=module: self._navigator.navigate_to_module(mod)
                )
                events.append(click_event)
                logger.debug("Added click handler for viable module: %s", module.module_name)

            # Store events for cleanup
            self._tile_events.extend(events)

            logger.debug("Successfully created tile for module: %s", module.module_name)
            return tile_html

        except Exception as e:
            logger.error(
                "Error creating tile for module %s: %s",
                module.module_name,
                e,
                exc_info=True,
            )
            return None

    def get_module_icon(self, module: Any) -> str:
        """
        Get the icon for a module, handling various icon types.
        Supports text/emoji icons and image files. Validates file existence,
        size limits, and supported formats for image icons.

        Args:
            module: Module instance to get icon for

        Returns:
            HTML string for the icon (text/emoji or img tag)
        """
        default_icon = "📦"

        try:
            button_style = module.button_style
            if "button_icon" not in button_style:
                logger.debug("No button_icon found in module.button_style")
                return default_icon

            icon = button_style["button_icon"]

            if not icon or not isinstance(icon, str):
                logger.debug("Icon is empty or not a string")
                return default_icon

            # Check if it's a text/emoji icon
            if self.is_text_or_emoji(icon):
                logger.debug("Using text/emoji icon: %s", icon)
                return icon

            # Validate image file format
            allowed_icon_formats = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp"]
            if not any(icon.lower().endswith(ext) for ext in allowed_icon_formats):
                logger.debug("Icon format not allowed: %s", icon)
                return default_icon

            if not os.path.exists(icon):
                logger.warning("Icon file does not exist: %s", icon)
                return default_icon

            # Load and encode image file
            try:
                # Check file size to avoid huge Base64 strings
                file_size = os.path.getsize(icon)
                if file_size > 500 * 1024:  # 500KB limit
                    logger.warning("Icon file too large (%d bytes): %s", file_size, icon)
                    return default_icon

                with open(icon, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode("utf-8")

                logger.debug("Successfully loaded icon from file: %s", icon)
                return f'<img src="data:image/png;base64,{img_data}" style="width: 32px; height: 32px; object-fit: contain;">'

            except Exception as e:
                logger.error("Error loading icon file %s: %s", icon, e, exc_info=True)
                return default_icon

        except Exception as e:
            logger.error("Error processing module icon: %s", e, exc_info=True)
            return default_icon

    def is_text_or_emoji(self, icon: str, max_length: int = 4) -> bool:
        """
        Check if an icon string represents text/emoji rather than a file path.

        Args:
            icon: Icon string to check
            max_length: Maximum length for text/emoji icons

        Returns:
            True if the icon is text/emoji, False if it's likely a file path
        """
        if not isinstance(icon, str) or len(icon) == 0:
            return False

        if len(icon) > max_length:
            return False

        if os.path.isfile(icon) or os.path.isdir(icon):
            return False

        return True

    def get_tile_html(
        self, module: Any, background_color: str, text_color: str, is_viable: bool
    ) -> str:
        """
        Creates a styled HTML representation of the module with gradients,
        hover effects, and status indicators.

        Args:
            module: Module instance
            background_color: Background color for the tile
            text_color: Text color for the tile
            is_viable: Whether the module is viable for current datasets

        Returns:
            HTML string for the module tile
        """
        try:
            module_name = module.module_name
            module_version = module.module_version

            background_gradient = (
                f"linear-gradient(135deg, {background_color} 0%, {background_color}CC 100%)"
            )
            icon = self.get_module_icon(module)

            # Configure hover effects and cursor based on viability
            hover_effects = ""
            cursor = "pointer"

            if is_viable:
                hover_effects = """
                onmouseover="
                    this.style.transform='translateY(-8px) scale(1.02)'; 
                    this.style.boxShadow='0 12px 30px rgba(0,0,0,0.2)';
                "
                onmouseout="
                    this.style.transform='translateY(0px) scale(1)'; 
                    this.style.boxShadow='0 4px 15px rgba(0,0,0,0.1)';
                "
                """
            else:
                cursor = "not-allowed"

            # Generate complete tile HTML
            tile_html = f"""
            <div id="module-tile-{module_name}" style="
                width: 100%;
                height: 100%;
                background: {background_gradient};
                border-radius: 15px;
                padding: 20px;
                color: {text_color};
                cursor: {cursor};
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                position: relative;
                overflow: hidden;
                opacity: {"1.0" if is_viable else "0.6"};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            " {hover_effects}>
                
                <!-- Background icon -->
                <div style="
                    position: absolute;
                    top: -10px;
                    right: -10px;
                    font-size: 60px;
                    opacity: 0.1;
                    z-index: 1;
                ">{icon}</div>
                
                <!-- Icon and title -->
                <div style="z-index: 2;">
                    <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
                    <h3 style="
                        margin: 0;
                        font-size: 16px;
                        font-weight: 600;
                        line-height: 1.3;
                        word-wrap: break-word;
                    ">{module_name}</h3>
                </div>
                
                <!-- Status indicator -->
                <div style="
                    position: absolute;
                    bottom: 15px;
                    right: 15px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 20px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: 500;
                    z-index: 2;
                ">{module_version if is_viable else "DISABLED"}</div>
                
            </div>
            """

            logger.debug("Generated tile HTML for module: %s", module_name)
            return tile_html

        except Exception as e:
            logger.error(
                "Error generating tile HTML for module %s: %s",
                module.module_name,
                e,
                exc_info=True,
            )
            return f"<div>Error loading module {module.module_name}</div>"
