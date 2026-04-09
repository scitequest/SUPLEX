import logging
from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional, Any, Callable

import ipywidgets as widgets

if TYPE_CHECKING:
    from ui.elements.navigator import Navigator

from martin_interface.project import Project
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory

from suplex_modules.submodules.submodule_constants import (
    DATASET_SELECTOR_MODE,
    DATASET_LABEL,
    SELECTION_MODE,
)
from suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex_modules.submodules.tag_selector import TagSelector

logger = logging.getLogger(__name__)


class DatasetSelectionPage:
    """
    This page displays projects in an accordion layout, allowing users to select
    datasets from each project using various filtering options including date ranges
    and tags. Provides comprehensive dataset selection capabilities with visual feedback.
    """

    def __init__(self, navigator: "Navigator") -> None:
        """
        Initialize the dataset selection page.

        Args:
            navigator: Reference to the navigator component
        """
        logger.debug("Initializing dataset selection page")

        self._navigator = navigator
        self._project_cards: List["ProjectCard"] = []

        logger.debug("Dataset selection page initialized successfully")

    @property
    def navigator(self) -> "Navigator":
        """
        Get the navigator instance.

        Returns:
            Navigator component reference
        """
        return self._navigator

    def get_ui(self) -> Optional[widgets.Widget]:
        """
        Creates an accordion layout with project cards, each containing dataset
        selection controls and filtering options. Handles cases where no adapter
        or projects are available.

        Returns:
            Widget containing the complete dataset selection interface, or None if error
        """
        logger.debug("Building dataset selection page UI")

        try:
            # Stores references of layouts using borders to allow color scheme updates
            self._borders: List[Any] = []

            adapter = self._navigator.adapter
            if adapter is None:
                logger.error(
                    "Cannot load dataset selection page - no adapter initialized"
                )
                return WidgetFactory.html_widget(
                    value="<div style='text-align: center; padding: 40px;'><h3>No adapter available</h3></div>",
                    width="100%",
                    height="100%",
                )

            # Check if projects are available
            if not adapter.projects:
                logger.warning("No projects found in adapter")
                return WidgetFactory.html_widget(
                    value="<div style='text-align: center; padding: 40px;'><h3>No projects found in the selected directory.</h3></div>",
                    width="100%",
                    height="100%",
                )

            logger.info("Creating project cards for %d projects", len(adapter.projects))

            # Create project cards if not already existing
            if not self._project_cards:
                for i, project in enumerate(adapter.projects):
                    try:
                        project_card = ProjectCard(page=self, project=project)
                        self._project_cards.append(project_card)
                        logger.debug("Created project card %d: %s", i, project.name)
                    except Exception as e:
                        logger.error(
                            "Failed to create project card for project %s: %s",
                            getattr(project, "name", "Unknown"),
                            e,
                            exc_info=True,
                        )
                        continue

            # Sort project cards alphanumerically
            self._project_cards.sort(key=lambda x: x.title.lower())
            
            # Create accordion using WidgetFactory
            accordion = WidgetFactory.accordion(
                children=[
                    project_card.get_ui_element()
                    for project_card in self._project_cards
                ],
                titles=[project_card.title for project_card in self._project_cards],
                layout=widgets.Layout(width="100%", height="auto", padding="5px")
            )

            # Set fixed height for accordion items when opened
            for i, project_card in enumerate(self._project_cards):
                if i < len(accordion.children):
                    accordion.children[i].layout.height = "400px"

            # Initially all projects are closed
            accordion.selected_index = None

            main_container = WidgetFactory.vbox(
                children=[accordion],
                width="100%",
                height="100%",
                overflow_y="auto",
                box_sizing="border-box",
                padding="5px",
            )

            logger.debug("Dataset selection page UI built successfully")
            return main_container

        except Exception as e:
            logger.error(
                "Failed to build dataset selection page UI: %s", e, exc_info=True
            )
            return WidgetFactory.html_widget(
                value="<div style='text-align: center; padding: 40px;'>Error loading dataset selection page</div>",
                width="100%",
                height="100%",
            )

    def get_selected_datasets(self) -> List[Dataset]:
        """
        Get all currently selected datasets from all project cards.

        Returns:
            List of selected Dataset objects across all projects
        """
        logger.debug("Retrieving selected datasets from all project cards")

        datasets = []
        for project_card in self._project_cards:
            try:
                card_datasets = project_card.get_selected_datasets()
                datasets.extend(card_datasets)
            except Exception as e:
                logger.error(
                    "Error getting datasets from project card %s: %s",
                    project_card.title,
                    e,
                    exc_info=True,
                )

        logger.info("Retrieved %d selected datasets total", len(datasets))
        return datasets

    def handle_dataset_selection_changed(self) -> None:
        """
        Handle changes in dataset selection and update the info field.

        Counts selected datasets and projects, then updates the navigator's
        info field with current selection statistics.
        """
        logger.debug("Handling dataset selection change")

        try:
            n_projects = 0
            n_datasets = 0

            for project_card in self._project_cards:
                try:
                    n_sets = len(project_card.get_selected_datasets())
                    n_datasets += n_sets
                    if n_sets > 0:
                        n_projects += 1
                except Exception as e:
                    logger.error(
                        "Error counting datasets for project %s: %s",
                        project_card.title,
                        e,
                        exc_info=True,
                    )

            if n_datasets == 0:
                self._navigator.set_info_field_state(
                    message="No datasets selected.",
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT,
                )
            else:
                message = (
                    f"You have selected {n_datasets} dataset{'s' if n_datasets != 1 else ''} from "
                    f"{n_projects} project{'s' if n_projects != 1 else ''}."
                )
                self._navigator.set_info_field_state(
                    message=message,
                    info_color=self._navigator.current_scheme.LAYOUT_COLOR.INFO_FIELD.INFO,
                )

            logger.debug(
                "Updated selection info: %d datasets, %d projects",
                n_datasets,
                n_projects,
            )

        except Exception as e:
            logger.error(
                "Error handling dataset selection change: %s", e, exc_info=True
            )

    def update_scheme(self, new_scheme: Any) -> None:
        """
        Update the color scheme for the border elements of all project cards.

        Args:
            new_scheme: New color scheme to apply
        """
        for card in self._project_cards:
            card.update_scheme(new_scheme)

    def reset_keep_dataset_selections(self) -> "DatasetSelectionPage":
        """
        Creates a new page instance with the same dataset selections maintained
        across project cards. Useful for navigation without losing user choices.

        Returns:
            New DatasetSelectionPage instance with preserved selections
        """
        logger.debug("Resetting dataset selection page while keeping selections")

        try:
            new_page = DatasetSelectionPage(navigator=self._navigator)
            project_cards = []

            for project_card in self._project_cards:
                try:
                    reset_card = project_card.reset_keep_dataset_selection(
                        page=new_page
                    )
                    project_cards.append(reset_card)
                except Exception as e:
                    logger.error(
                        "Error resetting project card %s: %s",
                        project_card.title,
                        e,
                        exc_info=True,
                    )

            new_page._project_cards = project_cards
            logger.debug("Dataset selection page reset with preserved selections")
            return new_page

        except Exception as e:
            logger.error(
                "Error during reset with preserved selections: %s", e, exc_info=True
            )
            return DatasetSelectionPage(navigator=self._navigator)

    def reset(self) -> "DatasetSelectionPage":
        """
        Creates a fresh page instance with no preserved state or selections.

        Returns:
            New DatasetSelectionPage instance
        """
        logger.debug("Completely resetting dataset selection page")
        return DatasetSelectionPage(navigator=self._navigator)


class ProjectCard:
    """
    Individual project card component for dataset selection within a project.

    Manages dataset selection, filtering, and display for a single project.
    Provides controls for dataset selection, date filtering, and tag-based filtering.
    """

    def __init__(self, page: "DatasetSelectionPage", project: Project) -> None:
        """
        Initialize a project card for dataset selection.

        Args:
            page: Reference to the parent dataset selection page
            project: Project instance containing datasets
        """
        logger.debug("Initializing project card for project: %s", project.name)

        self._page = page
        self._project = project
        self._borders: List[Any] = []

        # Initialize dataset selector
        dataset_label_parts = [DATASET_LABEL.ID, DATASET_LABEL.CREATED_DATE]
        self._dataset_selector = DatasetSelector(
            datasets=self._project.datasets,
            mode=DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
            label_parts=dataset_label_parts,
        )

        self._current_date_format = DATASET_LABEL.CREATED_DATE

        # Initialize tag selector
        self._tag_selection_mode = SELECTION_MODE.ANY
        self._tag_selector = TagSelector(datasets=self._project.datasets)

        logger.debug(
            "Project card initialized for %s with %d datasets",
            project.name,
            len(project.datasets),
        )

    @property
    def title(self) -> str:
        """
        Get the project title for display.

        Returns:
            Project name string
        """
        return self._project.name

    def get_ui_element(self) -> widgets.HBox:
        """
        Generate the user interface for the project card which is a two-column layout with dataset selection on the left and
        filtering controls on the right.

        Returns:
            HBox widget containing the complete project card interface
        """
        logger.debug("Building UI for project card: %s", self.title)

        try:
            # Left column - Dataset selection
            dataset_col_box = self.create_left_column()

            # Right column - Filter controls, description and tags
            filter_col_box = self.create_right_column()

            # Main layout with two columns
            project_card = WidgetFactory.hbox(
                children=[dataset_col_box, filter_col_box],
                width="100%",
                height="100%",
                overflow_y="visible",
                overflow_x="visible",
            )

            logger.debug("Project card UI built successfully for: %s", self.title)
            return project_card

        except Exception as e:
            logger.error(
                "Failed to build project card UI for %s: %s",
                self.title,
                e,
                exc_info=True,
            )
            return WidgetFactory.html_widget(
                value=f"<div>Error loading project: {self.title}</div>",
                width="100%",
                height="100%",
            )

    def create_left_column(self) -> widgets.VBox:
        """
        Create the left column with dataset selection controls.

        Returns:
            VBox widget containing dataset selection interface
        """
        logger.debug("Creating left column for project: %s", self.title)

        # ID/Name toggle buttons
        description_buttons = WidgetFactory.custom_radio_buttons(
            number=2,
            description=["ID", "Name"],
            i_toggled=0,
            layout = widgets.Layout(width="100%", height="30px", margin = "0")
        )

        # Add click handlers for ID/Name buttons
        def on_id_clicked(b):
            set_format = self._dataset_selector.get_dataset_label_format()
            try:
                set_format.remove(DATASET_LABEL.NAME)
                set_format.append(DATASET_LABEL.ID)
                self._dataset_selector.update_dataset_labels(label_parts=set_format)
                logger.debug("Switched to ID display for project: %s", self.title)
            except ValueError:
                pass

        def on_name_clicked(b):
            set_format = self._dataset_selector.get_dataset_label_format()
            try:
                set_format.remove(DATASET_LABEL.ID)
                set_format.append(DATASET_LABEL.NAME)
                self._dataset_selector.update_dataset_labels(label_parts=set_format)
                logger.debug("Switched to Name display for project: %s", self.title)
            except ValueError:
                pass

        description_buttons[0].on_click(on_id_clicked)
        description_buttons[1].on_click(on_name_clicked)

        descriptor_buttons_box = WidgetFactory.hbox(
            children= description_buttons,
            width="100%",
            height="50px",
            gap="0px",
            overflow_y="visible",
            overflow_x="visible",
        )

        # Select/Deselect all buttons
        select_all_button = WidgetFactory.button_success(
            description="Select All",
            width="100%",
            height="30px",
            layout=widgets.Layout(margin="0"),
            on_click=lambda b: self._dataset_selector.select_all(),
        )

        deselect_all_button = WidgetFactory.button_danger(
            description="Deselect All",
            width="100%",
            height="30px",
            layout=widgets.Layout(margin="0"),
            on_click=lambda b: self._dataset_selector.clear_selection(),
        )

        mass_select_buttons_box = WidgetFactory.hbox(
            children=[select_all_button, deselect_all_button],
            width="100%",
            height="50px",
            gap="0px",
            overflow_y="visible",
            overflow_x="visible",
        )

        selector_buttons = WidgetFactory.vbox(
            children=[descriptor_buttons_box, mass_select_buttons_box],
            width="100%",
            height="auto",
            gap="0px",
            margin="0px",
            padding="0px",
            overflow_y="visible",
            overflow_x="visible",
        )

        # Add change listeners to checkboxes
        for checkbox in self._dataset_selector.get_checkboxes():
            checkbox.observe(lambda b: self._page.handle_dataset_selection_changed())

        # Dataset selector container with scrolling
        dataset_selector_container = WidgetFactory.vbox(
            children=[self._dataset_selector.get_ui_element()],
            width="100%",
            height="100%",
            overflow_y="auto",
            overflow_x="hidden",
        )
        dataset_selector_container.layout.border = f"1px solid {self._page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES}"
        self._borders.append(dataset_selector_container.layout)

        dataset_col_box = WidgetFactory.vbox(
            children=[selector_buttons, dataset_selector_container],
            width="300px",
            height="100%",
            padding="10px",
            overflow_y="visible",
        )

        return dataset_col_box

    def create_right_column(self) -> widgets.VBox:
        """
        Create the right column with filtering controls and project description.

        Returns:
            VBox widget containing filter controls and description
        """
        logger.debug("Creating right column for project: %s", self.title)

        # Date filter and description
        date_filter_box = self.create_date_filter_box()

        project_description_html = WidgetFactory.html_widget(
            value=f"<h3>Project Description</h3><p>{self._project.description}</p>",
            width="auto",
            height="auto",
        )
        project_description = WidgetFactory.info_field_default(
            children=[project_description_html],
            width="100%",
            height="100%",
            overflow_y="auto",
            overflow_x="visible",
            layout=widgets.Layout(padding="10px"),
        )

        top_row_box = WidgetFactory.hbox(
            children=[date_filter_box, project_description],
            width="100%",
            height="250px",
            gap ="5px",
        )

        # Tag selection box
        tag_box = self.create_tag_box()

        filter_col_box = WidgetFactory.vbox(
            children=[top_row_box, tag_box],
            width="100%",
            height="100%",
            overflow_x="visible",
            overflow_y="visible",
            gap = "5px",
        )

        return filter_col_box

    def create_date_filter_box(self) -> widgets.VBox:
        """
        Create the date filtering controls.

        Returns:
            VBox widget containing date filter interface
        """
        logger.debug("Creating date filter box for project: %s", self.title)

        def date_radio_button_changed(selected_format):
            """Handle date filter mode changes."""
            self._current_date_format = selected_format
            label_format = self._dataset_selector.get_dataset_label_format()

            # Remove old date labels
            for date_mode in [DATASET_LABEL.CREATED_DATE, DATASET_LABEL.MEASURE_DATE]:
                try:
                    label_format.remove(date_mode)
                except ValueError:
                    pass

            label_format.append(selected_format)
            start_date_picker.value = self.get_earliest_date(selected_format)
            end_date_picker.value = self.get_latest_date(selected_format)
            self._dataset_selector.update_dataset_labels(label_parts=label_format)

        # Date mode radio buttons
        date_radio_buttons = WidgetFactory.radio_buttons(
            options=[
                DATASET_LABEL.CREATED_DATE.value,
                DATASET_LABEL.MEASURE_DATE.value,
            ],
            i_selected=0,
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
        )
        date_radio_buttons[0].observe(
            lambda b: date_radio_button_changed(DATASET_LABEL.CREATED_DATE)
        )
        date_radio_buttons[1].observe(
            lambda b: date_radio_button_changed(DATASET_LABEL.MEASURE_DATE)
        )

        radio_buttons_box = WidgetFactory.vbox(
            children=[date_radio_buttons[0], date_radio_buttons[1]],
            width="auto",
            height="auto",
            overflow="visible",
            layout=widgets.Layout(margin="0px", padding="0px 0px 0px 10px"),
            gap="0px",
        )

        # Date picker controls
        start_date_label = WidgetFactory.label(
            value="Start Date:", layout=widgets.Layout(margin="0px")
        )

        start_date_picker = WidgetFactory.date_picker(
            value=self.get_earliest_date(DATASET_LABEL.CREATED_DATE),
            height="100%",
            width="100%",
            layout=widgets.Layout(margin="0px", max_width="100%"),
        )

        start_date_box = WidgetFactory.vbox(
            children=[start_date_label, start_date_picker],
            width="100%",
            height="auto",
            overflow="hidden",
            gap=None,
        )

        end_date_label = WidgetFactory.label(
            value="End Date:", layout=widgets.Layout(margin="0px")
        )

        end_date_picker = WidgetFactory.date_picker(
            value=self.get_latest_date(DATASET_LABEL.CREATED_DATE),
            height="100%",
            width="100%",
            layout=widgets.Layout(margin="0px", max_width="100%"),
        )

        end_date_box = WidgetFactory.vbox(
            children=[end_date_label, end_date_picker],
            width="100%",
            height="auto",
            overflow="hidden",
            layout=widgets.Layout(margin="0px", padding="0px"),
            gap=None,
        )

        date_picker_box = WidgetFactory.hbox(
            children=[start_date_box, end_date_box],
            width="100%",
            gap="5px",
            overflow="hidden",
            layout=widgets.Layout(margin="0px", padding="0px"),
        )

        # Range selection buttons
        select_range_button = WidgetFactory.button_success(
            description="Select Range", height="30px", width="100%"
        )
        select_range_button.on_click(
            lambda b: self._dataset_selector.select_date_range(
                start_date=start_date_picker.value,
                end_date=end_date_picker.value,
                mode=self._current_date_format,
            )
        )

        deselect_range_button = WidgetFactory.button_danger(
            description="Deselect Range", height="30px", width="100%"
        )
        deselect_range_button.on_click(
            lambda b: self._dataset_selector.deselect_date_range(
                start_date=start_date_picker.value,
                end_date=end_date_picker.value,
                mode=self._current_date_format,
            )
        )

        range_buttons_box = WidgetFactory.hbox(
            children=[select_range_button, deselect_range_button],
            width="100%",
            overflow="hidden",
            gap="5px",
        )

        return WidgetFactory.vbox(
            children=[date_picker_box, radio_buttons_box, range_buttons_box],
            width="400px",
            height="100%",
            overflow="hidden",
            justify_content="space-between",
        )

    def create_tag_box(self) -> widgets.VBox:
        """
        Create the tag-based filtering controls.

        Returns:
            VBox widget containing tag filter interface
        """
        logger.debug("Creating tag filter box for project: %s", self.title)

        # Tag selection mode buttons
        tag_mode_buttons = WidgetFactory.custom_radio_buttons(
            number=2,
            description=["If Any", "If All"],
            i_toggled=0,
            layout = widgets.Layout(width="100%", height="30px", padding = "0px", margin = "0px")
        )

        def on_tag_any_clicked(b):
            self._tag_selection_mode = SELECTION_MODE.ANY
            logger.debug("Tag mode set to ANY for project: %s", self.title)

        def on_tag_all_clicked(b):
            self._tag_selection_mode = SELECTION_MODE.ALL
            logger.debug("Tag mode set to ALL for project: %s", self.title)

        tag_mode_buttons[0].on_click(on_tag_any_clicked)
        tag_mode_buttons[1].on_click(on_tag_all_clicked)

        # Tag selection buttons
        select_tags_button = WidgetFactory.button_success(
            description="Select", width="100%", height="30px"
        )

        def on_select_tags_button_clicked(b):
            datasets = (
                self._tag_selector.get_tagged_datasets_any()
                if self._tag_selection_mode == SELECTION_MODE.ANY
                else self._tag_selector.get_tagged_datasets_all()
            )
            self._dataset_selector.select_datasets(datasets)
            logger.debug("Selected datasets by tags for project: %s", self.title)

        select_tags_button.on_click(on_select_tags_button_clicked)

        deselect_tags_button = WidgetFactory.button_danger(
            description="Deselect", width="100%", height="30px"
        )

        def on_deselect_tags_button_clicked(b):
            datasets = (
                self._tag_selector.get_tagged_datasets_any()
                if self._tag_selection_mode == SELECTION_MODE.ANY
                else self._tag_selector.get_tagged_datasets_all()
            )
            self._dataset_selector.deselect_datasets(datasets)
            logger.debug("Deselected datasets by tags for project: %s", self.title)

        deselect_tags_button.on_click(on_deselect_tags_button_clicked)

        tag_buttons_box = WidgetFactory.hbox(
            children=[
                tag_mode_buttons[0],
                tag_mode_buttons[1],
                select_tags_button,
                deselect_tags_button,
            ],
            width="100%",
            height="40px",
            gap="5px",
            overflow="visible",
        )

        # Tag selector container with scrolling
        tag_selector_container = WidgetFactory.vbox(
            children=[self._tag_selector.get_ui_element()],
            width="100%",
            height="100%",
            overflow_y="auto",
            overflow_x="hidden",
        )
        tag_selector_container.layout.border = f"1px solid {self._page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES}"
        self._borders.append(tag_selector_container.layout)

        tag_box = WidgetFactory.vbox(
            children=[tag_buttons_box, tag_selector_container],
            width="100%",
            height="340px",
            gap = "5px"
        )

        return tag_box

    def get_selected_datasets(self) -> List[Dataset]:
        """
        Get the currently selected datasets from this project card.

        Returns:
            List of selected Dataset objects
        """
        return self._dataset_selector.get_selected_datasets()

    def select_datasets(self, datasets: List[Dataset]) -> None:
        """
        Programmatically select specific datasets.

        Args:
            datasets: List of Dataset objects to select
        """
        self._dataset_selector.select_datasets(datasets=datasets)

    def get_earliest_date(self, mode: DATASET_LABEL) -> date:
        """
        Get the earliest date from datasets based on the specified mode.

        Args:
            mode: Date mode (CREATED_DATE or MEASURE_DATE)

        Returns:
            Earliest date found, or today's date if no dates available
        """
        dates = []
        for dataset in self._project.datasets:
            try:
                if mode == DATASET_LABEL.CREATED_DATE and dataset.image_creation_date:
                    dates.append(dataset.image_creation_date.date())
                elif mode == DATASET_LABEL.MEASURE_DATE and dataset.measure_date:
                    dates.append(dataset.measure_date.date())
            except Exception as e:
                logger.debug("Error getting date from dataset: %s", e)
                continue

        return min(dates) if dates else date.today()

    def get_latest_date(self, mode: DATASET_LABEL) -> date:
        """
        Get the latest date from datasets based on the specified mode.

        Args:
            mode: Date mode (CREATED_DATE or MEASURE_DATE)

        Returns:
            Latest date found, or today's date if no dates available
        """
        dates = []
        for dataset in self._project.datasets:
            try:
                if mode == DATASET_LABEL.CREATED_DATE and dataset.image_creation_date:
                    dates.append(dataset.image_creation_date.date())
                elif mode == DATASET_LABEL.MEASURE_DATE and dataset.measure_date:
                    dates.append(dataset.measure_date.date())
            except Exception as e:
                logger.debug("Error getting date from dataset: %s", e)
                continue

        return max(dates) if dates else date.today()

    def update_scheme(self, new_scheme: Any) -> None:
        """
        Update the color scheme for border elements.

        Args:
            new_scheme: New color scheme to apply
        """
        try:
            for border in self._borders:
                border.border = (
                    f"1px solid {new_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES}"
                )
        except Exception as e:
            logger.error(
                "Error updating scheme for project card %s: %s",
                self.title,
                e,
                exc_info=True,
            )

    def reset(self) -> "ProjectCard":
        """
        Reset the project card to its initial state.

        Returns:
            New ProjectCard instance
        """
        logger.debug("Resetting project card: %s", self.title)
        return ProjectCard(page=self._page, project=self._project)

    def reset_keep_dataset_selection(
        self, page: "DatasetSelectionPage"
    ) -> "ProjectCard":
        """
        Reset the project card while preserving dataset selections.

        Args:
            page: New parent page instance

        Returns:
            New ProjectCard instance with preserved selections
        """
        logger.debug("Resetting project card %s while keeping selections", self.title)

        try:
            selected_datasets = self._dataset_selector.get_selected_datasets()
            new_card = ProjectCard(page=page, project=self._project)
            new_card._dataset_selector.select_datasets(selected_datasets)

            logger.debug(
                "Preserved %d dataset selections for project %s",
                len(selected_datasets),
                self.title,
            )
            return new_card

        except Exception as e:
            logger.error(
                "Error preserving selections for project card %s: %s",
                self.title,
                e,
                exc_info=True,
            )
            return ProjectCard(page=page, project=self._project)
