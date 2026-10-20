import logging
from typing import TYPE_CHECKING, Dict, Any, List, Optional

import ipywidgets as widgets

from suplex.ui.pages.about_page import AboutPage
from suplex.ui.pages.directory_selection_page import DirectorySelectionPage
from suplex.ui.pages.dataset_selection_page import DatasetSelectionPage
from suplex.ui.pages.module_selection_page import ModuleSelectionPage

from suplex.martin_interface.martin_adapter import Adapter
from suplex.ui.ui_constants import PAGE
from suplex.ui.styles.navigator_styles import get_navigator_styles

if TYPE_CHECKING:
    from .gui import GUI

logger = logging.getLogger(__name__)


class Navigator:
    """
    This class handles the navigation flow between different pages in the application,
    maintains navigation state, and provides a breadcrumb interface for users to
    understand their current position and navigate between steps.
    """

    def __init__(self, gui: "GUI", scheme: Any, modules: List[Any]) -> None:
        """
        Initialize the navigator component.

        Args:
            gui: Reference to the main GUI instance
            scheme: Current color scheme
            modules: List of available modules
        """
        logger.debug("Initializing navigator with %d modules", len(modules))

        self._gui = gui
        self._scheme = scheme
        self._modules = modules
        self._current_module: Optional[Any] = None
        self._adapter: Optional[Adapter] = None

        # Navigation state
        self._current_step = PAGE.DIRECTORY_SELECTION
        self._steps = [
            {
                "ID": PAGE.DIRECTORY_SELECTION,
                "label": "Select Directory",
                "icon": self._scheme.ICON.PAGE.DIRECTORY_SELECTION,
                "status": "available",
            },
            {
                "ID": PAGE.DATASET_SELECTION,
                "label": "Select Datasets",
                "icon": self._scheme.ICON.PAGE.DATASET_SELECTION,
                "status": "locked",
            },
            {
                "ID": PAGE.MODULE_SELECTION,
                "label": "Select Module",
                "icon": self._scheme.ICON.PAGE.MODULE_SELECTION,
                "status": "locked",
            },
            {
                "ID": PAGE.MODULE,
                "label": "Module",
                "icon": self._scheme.ICON.PAGE.MODULE,
                "status": "locked",
            },
        ]

        # UI Components
        self._breadcrumb_container: Optional[widgets.HBox] = None
        self._nav_container: Optional[widgets.HBox] = None
        self._step_buttons: List[widgets.Button] = []
        self._back_button: Optional[widgets.Button] = None
        self._forward_button: Optional[widgets.Button] = None

        # Page instances
        self._about_page: Optional[AboutPage] = None
        self._directory_selection_page: Optional[DirectorySelectionPage] = None
        self._dataset_selection_page: Optional[DatasetSelectionPage] = None
        self._module_selection_page: Optional[ModuleSelectionPage] = None

        try:
            self.create_navigation_ui()
            logger.debug("Navigator initialization completed successfully")
        except Exception as e:
            logger.error("Failed to initialize navigator: %s", e, exc_info=True)
            raise

    def create_navigation_ui(self) -> None:
        """
        Create the navigation UI components including breadcrumb and navigation buttons.
        """
        logger.debug("Creating navigation UI components")

        try:
            # Create back button
            self._back_button = widgets.Button(
                description=self._scheme.ICON.BACKWARD,
                button_style="",
                layout=widgets.Layout(width="30px", height="30px", margin="0px"),
                disabled=True,
            )
            self._back_button.add_class("nav-arrow")
            self._back_button.add_class("nav-back")
            self._back_button.on_click(self.back_button_clicked)

            # Create forward button
            self._forward_button = widgets.Button(
                description=self._scheme.ICON.FORWARD,
                button_style="",
                layout=widgets.Layout(width="30px", height="30px", margin="0px"),
                disabled=False,
            )
            self._forward_button.add_class("nav-arrow")
            self._forward_button.add_class("nav-forward")
            self._forward_button.on_click(self.forward_button_clicked)

            # Create breadcrumb navigator
            self.update_breadcrumb()

            # Create main navigation container
            self._nav_container = widgets.HBox(
                [
                    get_navigator_styles(self._scheme),
                    self._back_button,
                    self._breadcrumb_container,
                    self._forward_button,
                ],
                layout=widgets.Layout(
                    justify_content="space-between",
                    align_items="center",
                    margin="0px",
                ),
            )
            self._nav_container.add_class("slim-breadcrumb-container")

            logger.debug("Navigation UI components created successfully")

        except Exception as e:
            logger.error("Failed to create navigation UI: %s", e, exc_info=True)
            raise

    def initialize_pages(self) -> None:
        """
        Initialize all page instances and set up initial navigation state.
        Doing this separately from the actual initialization is done to make easier to establish the bidirectional association between the navigator and its pages.
        """
        logger.debug("Initializing navigator pages")

        try:
            self._about_page = AboutPage()
            self._directory_selection_page = DirectorySelectionPage(
                navigator=self, n_modules=len(self._modules)
            )
            self._dataset_selection_page = DatasetSelectionPage(navigator=self)
            self._module_selection_page = ModuleSelectionPage(navigator=self, modules=self._modules)

            self.navigate_to_dir_selection()
            logger.debug("Navigator pages initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize navigator pages: %s", e, exc_info=True)
            raise

    def update_breadcrumb(self) -> None:
        """
        Update the breadcrumb navigation based on current navigation state.

        Rebuilds the breadcrumb display to reflect current step status and availability.
        """
        logger.debug("Updating breadcrumb navigation")

        try:
            breadcrumb_items = []
            self._step_buttons = []

            for i, step in enumerate(self._steps):
                step_text = f"{step['icon']} {step['label']}"
                step_button = widgets.Button(
                    description=step_text,
                    button_style="",
                    layout=widgets.Layout(
                        width="150px",
                        height="30px",
                        padding="0px",
                        margin="0px",
                        border="none",
                    ),
                )
                step_button.add_class("step-item")
                step_button.add_class(f"step-{step['status']}")

                # Add click handler if step is clickable
                if step["status"] in ["available", "completed"]:

                    def create_click_handler(step_id):
                        return lambda button: self.handle_step_click(step_id)

                    step_button.on_click(create_click_handler(step["ID"]))

                elif step["status"] != "active":
                    step_button.disabled = True

                self._step_buttons.append(step_button)
                breadcrumb_items.append(step_button)

                # Add separators between step buttons
                if i < len(self._steps) - 1:
                    separator = widgets.HTML(value="<div class='step-separator'>▶</div>")
                    breadcrumb_items.append(separator)

            self._breadcrumb_container = widgets.HBox(
                breadcrumb_items,
                layout=widgets.Layout(
                    justify_content="center",
                    align_items="center",
                    flex="1",
                    overflow="hidden",
                ),
            )
            self._breadcrumb_container.add_class("step-breadcrumb-container")

            # Update nav container if it exists
            if self._nav_container is not None:
                self._nav_container.children = [
                    get_navigator_styles(self._scheme),
                    self._back_button,
                    self._breadcrumb_container,
                    self._forward_button,
                ]

            logger.debug("Breadcrumb navigation updated successfully")

        except Exception as e:
            logger.error("Failed to update breadcrumb: %s", e, exc_info=True)

    def handle_step_click(self, step: str) -> None:
        """
        Handle breadcrumb step click events.

        Args:
            step: The page constant representing the clicked step
        """
        logger.debug("Handling breadcrumb step click: %s", step)
        try:
            if step == PAGE.DIRECTORY_SELECTION:
                self.navigate_to_dir_selection()
            elif step == PAGE.DATASET_SELECTION:
                self.navigate_to_dataset_selection()
            elif step == PAGE.MODULE_SELECTION:
                self.navigate_to_module_selection()
            # Module step can never be clicked since modules are loaded by the MODULE_SELECTION and not the navigator

        except Exception as e:
            logger.error("Failed to handle step click: %s", e, exc_info=True)

    def navigate_to_about_page(self) -> None:
        """
        Navigate to the about page and update navigation state.
        """
        logger.debug("Navigating to about page")

        try:
            self._current_step = PAGE.ABOUT
            for step in self._steps:
                step["status"] = "locked"
            self._steps[0]["status"] = "available"
            self.update_navigation_state()
            self._gui.update_content_holder(self._about_page.get_ui(self._scheme))

        except Exception as e:
            logger.error("Failed to navigate to about page: %s", e, exc_info=True)

    def navigate_to_dir_selection(self) -> None:
        """
        Navigate to the directory selection page and update navigation state.
        """
        logger.debug("Navigating to directory selection page")

        try:
            if self._current_step in [
                PAGE.DATASET_SELECTION,
                PAGE.MODULE_SELECTION,
                PAGE.MODULE,
            ]:
                self._adapter = None
                self._directory_selection_page = self._directory_selection_page.reset()

            # No reset when going from about page to dir_selection

            self._gui.update_content_holder(self._directory_selection_page.get_ui())

            self._current_step = PAGE.DIRECTORY_SELECTION
            for i in range(len(self._steps)):
                self._steps[i]["status"] = "locked"
            self._steps[0]["status"] = "active"

            if self._adapter:
                self._steps[1]["status"] = "available"

            self.update_navigation_state()

        except Exception as e:
            logger.error("Failed to navigate to directory selection: %s", e, exc_info=True)

    def navigate_to_dataset_selection(self) -> None:
        """
        Navigate to the dataset selection page and update navigation state.
        """
        logger.debug("Navigating to dataset selection page")

        try:
            # Reset module selection but keep dataset selections
            if self._current_step in [PAGE.MODULE_SELECTION, PAGE.MODULE]:
                self._dataset_selection_page = (
                    self._dataset_selection_page.reset_keep_dataset_selections()
                )

            # Moving forward from dir selection
            elif self._current_step is PAGE.DIRECTORY_SELECTION:
                self._dataset_selection_page = DatasetSelectionPage(navigator=self)

            # This should never be the case
            else:
                logger.warning(
                    "Invalid navigation path to dataset selection from step: %s",
                    self._current_step,
                )
                return

            self._gui.update_content_holder(self._dataset_selection_page.get_ui())

            self._current_step = PAGE.DATASET_SELECTION
            self._steps[0]["status"] = "completed"
            self._steps[1]["status"] = "active"
            self._steps[2]["status"] = "available"
            self._steps[3]["status"] = "locked"
            self.update_navigation_state()

        except Exception as e:
            logger.error("Failed to navigate to dataset selection: %s", e, exc_info=True)

    def navigate_to_module_selection(self) -> None:
        """
        Navigate to the module selection page and update navigation state.
        The module selection page may be called without any datasets selected.
        """
        try:
            selected_datasets = self._dataset_selection_page.get_selected_datasets()
            logger.debug(
                "Navigating to module selection with %d selected datasets",
                len(selected_datasets),
            )

            self._gui.update_content_holder(self._module_selection_page.get_ui(selected_datasets))

            self._current_step = PAGE.MODULE_SELECTION
            self._steps[0]["status"] = "completed"
            self._steps[1]["status"] = "completed"
            self._steps[2]["status"] = "active"
            self._steps[3]["status"] = "available"
            self.update_navigation_state()

        except Exception as e:
            logger.error("Failed to navigate to module selection: %s", e, exc_info=True)

    def navigate_to_module(self, module: Any) -> None:
        """
        Navigate to a specific module page and update navigation state.

        Args:
            module: The module instance to navigate to
        """
        try:
            logger.debug("Navigating to module: %s", module.module_name)
            self._current_module = module.reset_module()  # Always returns a fresh module instance
            selected_datasets = self._dataset_selection_page.get_selected_datasets()

            module_ui = self._current_module.initiate_module(
                datasets=selected_datasets, color_scheme=self._scheme
            )
            self._gui.update_content_holder(module_ui)

            self._current_step = PAGE.MODULE
            self._steps[0]["status"] = "completed"
            self._steps[1]["status"] = "completed"
            self._steps[2]["status"] = "completed"
            self._steps[3]["status"] = "active"
            self.update_navigation_state()

        except Exception as e:
            logger.error("Failed to navigate to module: %s", e, exc_info=True)

    def update_navigation_state(self) -> None:
        """
        Update the navigation button states based on current step and available options.
        """
        logger.debug("Updating navigation state for step: %s", self._current_step)

        try:
            if self._current_step is PAGE.ABOUT:
                self._back_button.disabled = True
                self._forward_button.disabled = False
            # Dir selection without a dir selected
            elif self._current_step is PAGE.DIRECTORY_SELECTION and self._adapter is None:
                self._back_button.disabled = False
                self._forward_button.disabled = True
            elif self._current_step is PAGE.MODULE_SELECTION or self._current_step == PAGE.MODULE:
                self._back_button.disabled = False
                self._forward_button.disabled = True
            else:
                self._back_button.disabled = False
                self._forward_button.disabled = False

            logger.debug(
                "Navigation buttons updated - Back: %s, Forward: %s",
                not self._back_button.disabled,
                not self._forward_button.disabled,
            )

            self.update_breadcrumb()

        except Exception as e:
            logger.error("Failed to update navigation state: %s", e, exc_info=True)

    def back_button_clicked(self, button: widgets.Button) -> None:
        """
        Handle back button click events.

        Args:
            button: The clicked button widget
        """
        logger.debug("Back button clicked from step: %s", self._current_step)

        try:
            if self._current_step is PAGE.DIRECTORY_SELECTION:
                self.navigate_to_about_page()
            elif self._current_step == PAGE.DATASET_SELECTION:
                self.navigate_to_dir_selection()
            elif self._current_step == PAGE.MODULE_SELECTION:
                self.navigate_to_dataset_selection()
            elif self._current_step == PAGE.MODULE:
                self.navigate_to_module_selection()

        except Exception as e:
            logger.error("Failed to handle back button click: %s", e, exc_info=True)

    def forward_button_clicked(self, button: widgets.Button) -> None:
        """
        Handle forward button click events.

        Args:
            button: The clicked button widget
        """
        logger.debug("Forward button clicked from step: %s", self._current_step)

        try:
            if self._current_step is PAGE.ABOUT:
                self.navigate_to_dir_selection()
            elif self._current_step is PAGE.DIRECTORY_SELECTION:
                self.navigate_to_dataset_selection()
            elif self._current_step == PAGE.DATASET_SELECTION:
                self.navigate_to_module_selection()

        except Exception as e:
            logger.error("Failed to handle forward button click: %s", e, exc_info=True)

    def get_ui_element(self) -> Optional[widgets.HBox]:
        """
        Get the main navigation UI container.

        Returns:
            The navigation container widget
        """
        return self._nav_container

    # External state updates
    def invalid_dataset_dir_selected(self) -> None:
        """
        Handle invalid dataset directory selection by resetting navigation state.
        """
        logger.warning("Invalid dataset directory selected")

        self._adapter = None
        for i in range(1, len(self._steps)):
            self._steps[i]["status"] = "locked"
        self.update_navigation_state()

    def valid_dataset_dir_selected(self, adapter: Adapter) -> None:
        """
        Handle valid dataset directory selection by enabling next steps.

        Args:
            adapter: The Martin adapter instance for the selected directory
        """
        logger.info("Valid dataset directory selected")

        self._adapter = adapter
        self._steps[1]["status"] = "available"
        self.update_navigation_state()

    def set_info_field_state(
        self,
        message: str = "",
        info_color: Optional[str] = None,
        info_icon: Optional[str] = None,
    ) -> None:
        """
        Calls gui.set_info_field_state with all its attributes.

        Args:
            text: The text to display in the info field
            info_color: The color scheme for the info field (default: scheme default)
            info_icon: The icon to display (default: scheme default)
        """
        self._gui.set_info_field_state(message, info_color, info_icon)

    def clear_hover_text(self) -> None:
        """
        Calls gui.clear_hover_text
        """
        self._gui.clear_hover_text()

    def update_scheme(self, new_scheme: Any) -> None:
        """
        Update the navigator's color scheme and refresh UI elements.

        Args:
            new_scheme: The new color scheme to apply
        """
        logger.debug("Updating navigator color scheme to: %s", new_scheme.NAME)

        try:
            self._scheme = new_scheme
            page_icon_list = [
                self._scheme.ICON.PAGE.DIRECTORY_SELECTION,
                self._scheme.ICON.PAGE.DATASET_SELECTION,
                self._scheme.ICON.PAGE.MODULE_SELECTION,
                self._scheme.ICON.PAGE.MODULE,
            ]

            for i, step in enumerate(self._steps):
                step["icon"] = page_icon_list[i]

            self._back_button.description = self._scheme.ICON.BACKWARD
            self._forward_button.description = self._scheme.ICON.FORWARD

            self.update_breadcrumb()

            new_navigator = (get_navigator_styles(self._scheme),) + self._nav_container.children[1:]
            self._nav_container.children = new_navigator

            # Non-standard style updates.
            # Most styling is handled automatically via GUI.
            # The following are only exceptions.
            if self._current_step == PAGE.ABOUT and self._about_page:
                self._gui.update_content_holder(self._about_page.get_ui(self._scheme))
            elif self._current_step == PAGE.DATASET_SELECTION and self._dataset_selection_page:
                self._dataset_selection_page.update_scheme(self._scheme)
            elif self._current_step == PAGE.MODULE and self._current_module:
                self._current_module.update_scheme(self._scheme)

            logger.debug("Navigator color scheme updated successfully")

        except Exception as e:
            logger.error("Failed to update navigator color scheme: %s", e, exc_info=True)

    @property
    def adapter(self) -> Optional[Adapter]:
        """
        Get the current Martin adapter instance.

        Returns:
            The current adapter or None if no valid directory is selected
        """
        return self._adapter

    @property
    def current_scheme(self) -> Any:
        """
        Get the current color scheme from the GUI.

        Returns:
            The current color scheme object
        """
        return self._gui.current_scheme
