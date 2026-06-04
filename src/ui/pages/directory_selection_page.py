import logging
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING, Optional

import ipywidgets as widgets

from martin_interface.martin_interface_constants import (
    SEARCH_MODE,
    MARTIN_MEASURE_DIR_DEPTH,
)
from martin_interface.martin_adapter import Adapter
from ui.widget_factory import WidgetFactory
from ui.styles.color_utils import hex_to_rgba

if TYPE_CHECKING:
    from ui.elements.navigator import Navigator

logger = logging.getLogger(__name__)


class DirectorySelectionPage:
    """
    This page allows users to select a directory containing MARTin datasets, configure
    search mode and depth, and view statistics about loaded modules and datasets.
    It also provides an option to load sample data for demonstration purposes.
    """

    def __init__(
        self,
        navigator: "Navigator",
        n_modules: int,
        search_mode: SEARCH_MODE = SEARCH_MODE.RECURSIVE,
        search_depth: int = MARTIN_MEASURE_DIR_DEPTH,
        selected_path: str = "",
        n_datasets: int = 0,
        n_projects: int = 0,
    ) -> None:
        """
        Initialize the directory selection page.

        Args:
            navigator: Reference to the navigator component
            n_modules: Number of available modules
            search_mode: Default search mode for directory scanning
            search_depth: Default search depth for directory scanning
            selected_path: Currently selected directory path
            n_datasets: Number of datasets found in selected directory
            n_projects: Number of projects found in selected directory
        """
        logger.debug("Initializing directory selection page with %d modules", n_modules)

        self._navigator = navigator
        self._search_mode = search_mode
        self._search_depth = search_depth
        self._selected_path = selected_path
        self._n_datasets = n_datasets
        self._n_projects = n_projects
        self._n_modules = n_modules

        # UI Components
        self._stats_box: Optional[widgets.Widget] = None
        self._path_display: Optional[widgets.HTML] = None
        self._search_mode_dropdown: Optional[widgets.Dropdown] = None
        self._search_depth_spinner: Optional[widgets.Widget] = None

        logger.debug("Directory selection page initialized successfully")

    def get_ui(self) -> widgets.Widget:
        """
        Generate the user interface for the directory selection page.

        Creates a welcome page with directory selection controls, search options,
        and statistics display. Includes animated elements and responsive layout.

        Returns:
            Widget containing the complete directory selection interface
        """
        logger.debug("Building directory selection page UI")

        try:
            # Create main sections
            title_container = self.create_title()
            controls_container = self.create_controls()

            # Create stats box
            self._stats_box = WidgetFactory.info_field_default(
                children=[self.get_updated_stats_box()],
                width="100%",
                height="100px",
                padding="10px",
                align_items="center",
                justify_content="center",
                overflow="hidden",
            )

            bottom_box = WidgetFactory.vbox(
                children=[controls_container, self._stats_box],
                layout=widgets.Layout(
                    width="100%",
                    height="50%",
                    min_height="250px",
                    justify_content="space-between",
                    align_items="center",
                ),
                overflow="visible",
            )

            # Main page layout
            page = WidgetFactory.vbox(
                children=[title_container, bottom_box],
                layout=widgets.Layout(
                    width="100%",
                    height="100%",
                    justify_content="space-between",
                    align_items="center",
                ),
                overflow="auto",
            )

            logger.debug("Directory selection page UI built successfully")
            return page

        except Exception as e:
            logger.error("Failed to build directory selection page UI: %s", e, exc_info=True)
            return WidgetFactory.html_widget(
                value="<div style='text-align: center; padding: 40px;'>Error loading directory selection page</div>",
                width="100%",
                height="100%",
            )

    def create_title(self) -> widgets.VBox:
        """
        Create the title section with title and animated subtitle.

        Returns:
            VBox widget containing the header elements
        """
        logger.debug("Creating header section")

        title = WidgetFactory.html_widget(
            value="""
            <div style="text-align: center; padding: 5px 0;">
                <h1 style="margin: 0;">
                    Welcome to SUPLEX!
                </h1>
            </div>
            """,
            width="100%",
        )

        # Animated subtitle with CSS keyframes
        subtitle = WidgetFactory.html_widget(
            value="""
            <div style="text-align: center; padding-bottom: 30px;">
                <style>
                    @keyframes fadeInOut {
                        0% { opacity: 0.4; }
                        50% { opacity: 1.0; }
                        100% { opacity: 0.4; }
                    }
                    .animated-subtitle {
                        animation: fadeInOut 3s ease-in-out infinite;
                        font-size: 18px;
                        color: #666;
                    }
                </style>
                <p class="animated-subtitle">
                    Please begin by selecting a directory to upload your datasets.
                </p>
            </div>
            """,
            width="100%",
        )

        return WidgetFactory.vbox(
            children=[title, subtitle],
            layout=widgets.Layout(width="100%", height="60%", justify_content="center"),
            overflow="visible",
        )

    def create_controls(self) -> widgets.HBox:
        """
        Create the controls section with path selection and search options.

        Returns:
            HBox widget containing the main content
        """
        logger.debug("Creating main content section")

        # Path display + button
        path_section = self.create_path_section()

        # Dropdowns for search mode and depth
        search_options_section = self.create_search_options_section()

        # Sample data button
        sample_data_button = WidgetFactory.button_default(
            description="Use Sample Data", layout=widgets.Layout(width="100%")
        )
        sample_data_button.on_click(lambda x: self.use_sample_data())

        content_block = WidgetFactory.vbox(
            children=[path_section, search_options_section, sample_data_button],
            layout=widgets.Layout(
                width="100%", max_width="600px", gap="5px", align_items="center", padding="5px"
            ),
            overflow="visible",
        )

        # Center the content block
        content_container = WidgetFactory.hbox(
            children=[content_block],
            width="100%",
            justify_content="center",
            overflow="hidden",
        )

        return content_container

    def create_path_section(self) -> widgets.HBox:
        """
        Create the path selection section with display and button.

        Returns:
            HBox widget containing the path selection controls
        """
        logger.debug("Creating path selection section")

        dir_path = "..." if not self._selected_path else self._selected_path

        self._path_display = WidgetFactory.html_widget(value=dir_path, width="auto", height="auto")

        path_container = WidgetFactory.info_field_default(
            children=[self._path_display],
            width="100%",
            height="100%",
            align_items="flex-start",
            justify_content="center",
            overflow_x="hidden",
            overflow_y="hidden",
            layout=widgets.Layout(padding="0px 0px 0px 12px"),
        )

        dir_selector_button = WidgetFactory.button_emphasis(
            description="Select Directory", width="150px", height="100%"
        )
        dir_selector_button.on_click(lambda x: self.open_directory_dialog())

        path_row = WidgetFactory.hbox(
            children=[path_container, dir_selector_button],
            align_items="stretch",
            justify_content="center",
            width="100%",
            height="50px",
            overflow="hidden",
        )

        return path_row

    def create_search_options_section(self) -> widgets.HBox:
        """
        Create the search options section with mode and depth controls.

        Returns:
            HBox widget containing the search options
        """
        logger.debug("Creating search options section")

        search_mode_label = WidgetFactory.label(value="Mode", width="30px")
        search_mode_dropdown = WidgetFactory.dropdown(
            options=[(mode.name, mode) for mode in SEARCH_MODE],
            value=self._search_mode,
            layout=widgets.Layout(width="100%"),
            on_change=lambda change: self.search_dir(),
        )

        search_depth_label = WidgetFactory.label(value="Depth", width="30px")
        search_depth_spinner = WidgetFactory.number_input(
            value=self._search_depth,
            min_value=0,
            max_value=30,
            step=1,
            layout=widgets.Layout(width="100%"),
            on_change=lambda change: self.search_dir(),
        )

        # Store references for later use
        self._search_mode_dropdown = search_mode_dropdown
        self._search_depth_spinner = search_depth_spinner

        search_mode_box = WidgetFactory.hbox(
            children=[search_mode_label, search_mode_dropdown],
            width="70%",
            justify_content="flex-start",
            overflow="visible",
        )

        search_depth_box = WidgetFactory.hbox(
            children=[search_depth_label, search_depth_spinner],
            width="30%",
            justify_content="flex-start",
            gap="5px",
            overflow="visible",
        )

        search_options_row = WidgetFactory.hbox(
            children=[search_mode_box, search_depth_box],
            justify_content="space-between",
            width="100%",
            gap="5px",
        )

        return search_options_row

    def get_updated_stats_box(self) -> widgets.HBox:
        """
        Create an updated statistics display box.

        Returns:
            HBox widget containing statistics information
        """
        logger.debug(
            "Creating stats box: modules=%d, datasets=%d, projects=%d",
            self._n_modules,
            self._n_datasets,
            self._n_projects,
        )

        scheme = self._navigator.current_scheme

        stats_widgets = []

        # Modules loaded
        stats_widgets.append(
            WidgetFactory.html_widget(
                value=f"""
            <div style="text-align: center;">
                <h3 style="color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT};">{self._n_modules}</h3>
                <p style="color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT};">Modules Loaded</p>
            </div>
            """
            )
        )

        # Datasets collected
        stats_widgets.append(
            WidgetFactory.html_widget(
                value=f"""
            <div style="text-align: center;">
                <h3 style="color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT};">{self._n_datasets}</h3>
                <p style="color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT};">Datasets Collected</p>
            </div>
            """
            )
        )

        # Projects detected
        stats_widgets.append(
            WidgetFactory.html_widget(
                value=f"""
            <div style="text-align: center;">
                <h3 style="color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT};">{self._n_projects}</h3>
                <p style="color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT};">Projects Detected</p>
            </div>
            """
            )
        )

        return WidgetFactory.hbox(
            children=stats_widgets,
            justify_content="space-between",
            width="100%",
            height="100%",
            align_items="center",
            overflow="hidden",
        )

    def open_directory_dialog(self) -> None:
        """
        Open a directory selection dialog and handle the result.

        Uses tkinter file dialog to allow users to select a directory.
        Updates the selected path and triggers directory search if successful.
        """
        logger.debug("Opening directory selection dialog")

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            initial_dir = (
                self._selected_path
                if self._selected_path and os.path.exists(self._selected_path)
                else os.path.expanduser("~")
            )

            selected_dir = filedialog.askdirectory(title="Select Directory", initialdir=initial_dir)

            root.destroy()

            if selected_dir:
                self._selected_path = selected_dir
                self._path_display.value = selected_dir
                logger.info("Directory selected via dialog: %s", selected_dir)
                self.search_dir()
            else:
                logger.debug("Directory selection cancelled by user")

        except Exception as e:
            logger.error("Error opening directory dialog: %s", e, exc_info=True)

    def search_dir(self) -> None:
        """
        Updates search mode and depth from UI controls, validates the selected path,
        and creates an adapter to scan for datasets. Updates navigation state and
        statistics based on the results.
        """
        logger.debug("Searching directory with current parameters")

        try:
            # Update search parameters from UI
            self._search_mode = self._search_mode_dropdown.value
            self._search_depth = self._search_depth_spinner.value
            path = self._selected_path

            if not path:
                logger.debug("No path selected for directory search")
                self._navigator.set_info_field_state(
                    message="No path selected.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING,
                )
                return

            if not os.path.exists(path) or not os.path.isdir(path):
                logger.warning("Invalid path selected: %s", path)
                self._navigator.set_info_field_state(
                    message="The selected path is invalid.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
                )
                self._navigator.invalid_dataset_dir_selected()
                return

            logger.info(
                "Creating adapter for path: %s (mode: %s, depth: %d)",
                path,
                self._search_mode.name,
                self._search_depth,
            )

            adapter = Adapter(path=path, mode=self._search_mode, search_depth=self._search_depth)

            if adapter.datasets:
                self._n_datasets = len(adapter.datasets)
                self._n_projects = len(adapter.projects)

                logger.info(
                    "Valid adapter created: %d datasets, %d projects",
                    self._n_datasets,
                    self._n_projects,
                )

                self._navigator.valid_dataset_dir_selected(adapter=adapter)
                self._navigator.set_info_field_state(
                    message=f"Found {self._n_datasets} datasets in {self._n_projects} projects.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
                )
            else:
                logger.warning("No valid datasets found in selected path: %s", path)
                self._n_datasets = 0
                self._n_projects = 0
                self._navigator.set_info_field_state(
                    message="The selected path does not contain any valid MARTin datasets.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.WARNING,
                )
                self._navigator.invalid_dataset_dir_selected()

            # Update statistics display
            self._stats_box.children = [self.get_updated_stats_box()]

        except Exception as e:
            logger.error("Error during directory search: %s", e, exc_info=True)
            self._navigator.set_info_field_state(
                message="Error occurred during directory search.",
                info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
            )

    def use_sample_data(self) -> None:
        """
        Attempts to load sample data from the sample_data directory relative to
        the application. If successful, navigates directly to dataset selection.
        """
        logger.info("Loading sample data")

        try:
            sample_data_path = Path(__file__).parent.parent.parent / "sample_data"

            if not sample_data_path.exists():
                logger.error("Sample data directory does not exist: %s", sample_data_path)
                self._navigator.set_info_field_state(
                    message="Sample data directory does not exist.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
                )
                return

            logger.debug("Creating adapter for sample data: %s", sample_data_path)
            adapter = Adapter(
                path=str(sample_data_path), mode=SEARCH_MODE.RECURSIVE, search_depth=5
            )

            if not adapter.datasets:
                logger.error("No valid data found in sample data directory")
                self._navigator.set_info_field_state(
                    message="Could not extract valid data from sample data directory.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
                )
                return

            logger.info("Sample data loaded successfully: %d datasets", len(adapter.datasets))
            self._navigator.set_info_field_state(
                message="Loaded sample data!",
                info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
            )
            self._navigator.valid_dataset_dir_selected(adapter=adapter)
            self._navigator.navigate_to_dataset_selection()

        except Exception as e:
            logger.error("Error loading sample data: %s", e, exc_info=True)
            self._navigator.set_info_field_state(
                message="Error loading sample data.",
                info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.ERROR,
            )

    def reset(self) -> "DirectorySelectionPage":
        """
        Reset the directory selection page to its initial state.

        Returns:
            New DirectorySelectionPage instance with default parameters
        """
        logger.debug("Resetting directory selection page")

        return DirectorySelectionPage(navigator=self._navigator, n_modules=self._n_modules)
