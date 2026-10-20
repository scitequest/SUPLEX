import logging
from datetime import date
from typing import List, Optional, Dict

import ipywidgets as widgets

from .submodule_constants import DATASET_SELECTOR_MODE, DATASET_LABEL
from suplex.martin_interface.dataset import Dataset
from suplex.ui.widget_factory import WidgetFactory

logger = logging.getLogger(__name__)


class DatasetSelector:
    """
    This class provides a user interface for dataset selection with support for
    different selection modes (single, multiple bounded/unbounded), customizable
    labeling, and date-range filtering capabilities.
    """

    def __init__(
        self,
        datasets: List[Dataset],
        mode: DATASET_SELECTOR_MODE = DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
        checkbox_limit: int = 1,
        label_parts: List[DATASET_LABEL] = None,
    ) -> None:
        """
        Initialize the dataset selector.

        Args:
            datasets: List of Dataset objects to make available for selection
            mode: Selection mode determining how many datasets can be selected
            checkbox_limit: Maximum number of selections for bounded modes
            label_parts: List of DATASET_LABEL enums defining what to show in labels
        """
        logger.debug("Initializing dataset selector with %d datasets", len(datasets))

        self._datasets = datasets
        self._mode = mode
        self._label_parts = label_parts or [DATASET_LABEL.NAME]
        self._checkbox_limit = checkbox_limit

        # Override limit for single selection mode
        if mode == DATASET_SELECTOR_MODE.SINGLE:
            self._checkbox_limit = 1

        # Initialize internal state
        self._checkboxes: List[widgets.Checkbox] = []
        self._checkbox_queue: List[widgets.Checkbox] = []
        self._checkbox_dataset_map: Dict[widgets.Checkbox, Dataset] = {}

        try:
            self.setup_checkboxes()
            logger.debug("Dataset selector initialized successfully in %s mode", mode.value)
        except Exception as e:
            logger.error("Failed to initialize dataset selector: %s", e, exc_info=True)
            raise

    def select_all(self) -> None:
        """
        Select all datasets if mode allows it.

        Only works in MULTIPLE_UNBOUND mode to prevent queue overflow.
        """
        logger.debug("Selecting all datasets")

        if self._mode == DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND:
            try:
                for checkbox in self._checkboxes:
                    checkbox.value = True
                logger.debug("Selected all %d datasets", len(self._checkboxes))
            except Exception as e:
                logger.error("Error selecting all datasets: %s", e, exc_info=True)
        else:
            logger.warning("Select all not supported in mode: %s", self._mode.value)

    def get_dataset_label(self, dataset: Dataset) -> str:
        """
        Generate a display label for a dataset based on configured label parts.

        Args:
            dataset: Dataset object to generate label for

        Returns:
            Formatted label string containing requested information
        """
        try:
            label_components = []

            if DATASET_LABEL.NAME in self._label_parts:
                if hasattr(dataset, "metadata") and hasattr(dataset.metadata, "name"):
                    label_components.append(dataset.metadata.name)

            if DATASET_LABEL.ID in self._label_parts:
                if hasattr(dataset, "metadata") and hasattr(dataset.metadata, "pat_id"):
                    label_components.append(dataset.metadata.pat_id)

            if DATASET_LABEL.CREATED_DATE in self._label_parts:
                if hasattr(dataset, "image_creation_date") and dataset.image_creation_date:
                    label_components.append(str(dataset.image_creation_date.date()))

            if DATASET_LABEL.MEASURE_DATE in self._label_parts:
                if hasattr(dataset, "measure_date") and dataset.measure_date:
                    label_components.append(str(dataset.measure_date.date()))

            label = " - ".join(label_components)
            logger.debug("Generated label for dataset: %s", label[:50])  # Truncate for logging
            return label if label else "Unknown Dataset"

        except Exception as e:
            logger.error("Error generating dataset label: %s", e, exc_info=True)
            return "Error Loading Dataset"

    def setup_checkboxes(self) -> None:
        """
        Create and configure checkbox widgets for all datasets.

        Sets up the checkbox-to-dataset mapping and attaches change observers.
        """
        logger.debug("Setting up checkboxes for %d datasets", len(self._datasets))

        try:
            self._checkboxes = []
            self._checkbox_dataset_map = {}

            for i, dataset in enumerate(self._datasets):
                try:
                    checkbox = WidgetFactory.checkbox(
                        value=False,
                        description=self.get_dataset_label(dataset),
                        disabled=False,
                        indent=False,
                    )

                    self._checkboxes.append(checkbox)
                    self._checkbox_dataset_map[checkbox] = dataset

                    # Attach change observer
                    checkbox.observe(
                        lambda change, cb=checkbox: self.checkbox_change(cb),
                        names="value",
                    )

                except Exception as e:
                    logger.error(
                        "Error creating checkbox for dataset %d: %s",
                        i,
                        e,
                        exc_info=True,
                    )
                    continue
            # Sort checkboxes by their labels
            self._checkboxes.sort(key=lambda checkbox: checkbox.description.lower())
            logger.debug("Successfully created %d checkboxes", len(self._checkboxes))

        except Exception as e:
            logger.error("Failed to setup checkboxes: %s", e, exc_info=True)
            raise

    def checkbox_change(self, checkbox: widgets.Checkbox) -> None:
        """
        Handle checkbox state changes and manage selection queue.

        Args:
            checkbox: The checkbox widget that changed state
        """
        try:
            # Checkbox was unchecked
            if not checkbox.value:
                if checkbox in self._checkbox_queue:
                    self._checkbox_queue.remove(checkbox)
                    logger.debug("Removed checkbox from selection queue")
                return

            # Checkbox was checked
            self._checkbox_queue.append(checkbox)
            logger.debug(
                "Added checkbox to selection queue (total: %d)",
                len(self._checkbox_queue),
            )

            # Handle queue limit for bounded modes
            if (
                len(self._checkbox_queue) > self._checkbox_limit
                and self._mode != DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND
            ):

                # Remove oldest selection (triggers this method again)
                oldest_checkbox = self._checkbox_queue[0]
                oldest_checkbox.value = False
                logger.debug("Removed oldest selection due to limit (%d)", self._checkbox_limit)

        except Exception as e:
            logger.error("Error handling checkbox change: %s", e, exc_info=True)

    def get_ui_element(self) -> widgets.VBox:
        """
        Create the user interface for dataset selection.

        Returns:
            VBox widget containing the dataset selection interface
        """
        logger.debug("Building dataset selector UI")

        try:
            header = WidgetFactory.html_widget(value="<b>Datasets</b>", width="100%", height="auto")

            checkbox_elements = [header] + self._checkboxes

            return WidgetFactory.vbox(
                children=checkbox_elements,
                width="100%",
                height="100%",
                overflow_y="auto",
                layout=widgets.Layout(padding="5px"),
            )

        except Exception as e:
            logger.error("Failed to build dataset selector UI: %s", e, exc_info=True)
            return WidgetFactory.html_widget(
                value="<div>Error loading dataset selector</div>",
                width="100%",
                height="100%",
            )

    def get_selected_count(self) -> int:
        """
        Get the number of currently selected datasets.

        Returns:
            Number of selected datasets
        """
        return len(self._checkbox_queue)

    def get_selected_labels(self) -> List[str]:
        """
        Get the display labels of currently selected datasets.

        Returns:
            List of label strings for selected datasets
        """
        try:
            labels = [checkbox.description for checkbox in self._checkbox_queue]
            logger.debug("Retrieved %d selected dataset labels", len(labels))
            return labels
        except Exception as e:
            logger.error("Error getting selected labels: %s", e, exc_info=True)
            return []

    def get_selected_datasets(self) -> List[Dataset]:
        """
        Get the currently selected Dataset objects.

        Returns:
            List of selected Dataset objects in selection order
        """
        try:
            datasets = []
            for checkbox in self._checkbox_queue:
                dataset = self._checkbox_dataset_map.get(checkbox)
                if dataset:
                    datasets.append(dataset)

            logger.debug("Retrieved %d selected datasets", len(datasets))
            return datasets

        except Exception as e:
            logger.error("Error getting selected datasets: %s", e, exc_info=True)
            return []

    def clear_selection(self) -> None:
        """
        Clear all dataset selections.

        Unchecks all selected checkboxes, which automatically updates the queue.
        """
        logger.debug("Clearing all dataset selections")

        try:
            # Process in reverse to avoid queue modification issues
            for checkbox in reversed(self._checkbox_queue.copy()):
                checkbox.value = False
            logger.debug("Successfully cleared all selections")

        except Exception as e:
            logger.error("Error clearing selections: %s", e, exc_info=True)

    def get_checkbox_of_dataset(self, target_dataset: Dataset) -> Optional[widgets.Checkbox]:
        """
        Find the checkbox widget associated with a specific dataset.

        Args:
            target_dataset: Dataset object to find checkbox for

        Returns:
            Checkbox widget for the dataset, or None if not found
        """
        try:
            for checkbox, dataset in self._checkbox_dataset_map.items():
                if dataset is target_dataset:
                    return checkbox

            logger.debug("No checkbox found for target dataset")
            return None

        except Exception as e:
            logger.error("Error finding checkbox for dataset: %s", e, exc_info=True)
            return None

    def select_datasets(self, datasets: List[Dataset]) -> None:
        """
        Programmatically select specific datasets.

        Note: This method may have issues with bounded modes if the selection
        queue hits its limit, as it will remove the oldest elements.

        Args:
            datasets: List of Dataset objects to select
        """
        logger.debug("Programmatically selecting %d datasets", len(datasets))

        try:
            selected_count = 0
            for dataset in datasets:
                checkbox = self.get_checkbox_of_dataset(target_dataset=dataset)
                if checkbox:
                    checkbox.value = True
                    selected_count += 1
                else:
                    logger.warning("Could not find checkbox for dataset to select")

            logger.debug(
                "Successfully selected %d of %d requested datasets",
                selected_count,
                len(datasets),
            )

        except Exception as e:
            logger.error("Error selecting datasets: %s", e, exc_info=True)

    def deselect_datasets(self, datasets: List[Dataset]) -> None:
        """
        Programmatically deselect specific datasets.

        Args:
            datasets: List of Dataset objects to deselect
        """
        logger.debug("Programmatically deselecting %d datasets", len(datasets))

        try:
            deselected_count = 0
            for dataset in datasets:
                checkbox = self.get_checkbox_of_dataset(target_dataset=dataset)
                if checkbox:
                    checkbox.value = False
                    deselected_count += 1
                else:
                    logger.warning("Could not find checkbox for dataset to deselect")

            logger.debug(
                "Successfully deselected %d of %d requested datasets",
                deselected_count,
                len(datasets),
            )

        except Exception as e:
            logger.error("Error deselecting datasets: %s", e, exc_info=True)

    def select_date_range(self, start_date: date, end_date: date, mode: str) -> None:
        """
        Select datasets within a specified date range.

        Args:
            start_date: Start of the date range (inclusive)
            end_date: End of the date range (inclusive)
            mode: Date mode string (from DATASET_LABEL enum values)
        """
        logger.debug(
            "Selecting datasets in date range: %s to %s (%s)",
            start_date,
            end_date,
            mode,
        )

        try:
            selected_count = 0
            for checkbox in self._checkboxes:
                try:
                    dataset = self._checkbox_dataset_map[checkbox]

                    if mode == DATASET_LABEL.CREATED_DATE:
                        check_date = getattr(dataset, "image_creation_date", None)
                    else:
                        check_date = getattr(dataset, "measure_date", None)

                    if check_date and start_date <= check_date.date() <= end_date:
                        checkbox.value = True
                        selected_count += 1

                except Exception as e:
                    logger.warning("Error checking date for dataset: %s", e)
                    continue

            logger.debug("Selected %d datasets in date range", selected_count)

        except Exception as e:
            logger.error("Error selecting date range: %s", e, exc_info=True)

    def deselect_date_range(self, start_date: date, end_date: date, mode: str) -> None:
        """
        Deselect datasets within a specified date range.

        Args:
            start_date: Start of the date range (inclusive)
            end_date: End of the date range (inclusive)
            mode: Date mode string (from DATASET_LABEL enum values)
        """
        logger.debug(
            "Deselecting datasets in date range: %s to %s (%s)",
            start_date,
            end_date,
            mode,
        )

        try:
            deselected_count = 0
            for checkbox in self._checkboxes:
                try:
                    dataset = self._checkbox_dataset_map[checkbox]

                    if mode == DATASET_LABEL.CREATED_DATE:
                        check_date = getattr(dataset, "image_creation_date", None)
                    else:
                        check_date = getattr(dataset, "measure_date", None)

                    if check_date and start_date <= check_date.date() <= end_date:
                        checkbox.value = False
                        deselected_count += 1

                except Exception as e:
                    logger.warning("Error checking date for dataset: %s", e)
                    continue

            logger.debug("Deselected %d datasets in date range", deselected_count)

        except Exception as e:
            logger.error("Error deselecting date range: %s", e, exc_info=True)

    def get_dataset_label_format(self) -> List[DATASET_LABEL]:
        """
        Get the current dataset label format configuration.

        Returns:
            List of DATASET_LABEL enums defining current label format
        """
        return self._label_parts.copy()

    def update_dataset_labels(self, label_parts: Optional[List[DATASET_LABEL]] = None) -> None:
        """
        Update the display labels for all datasets.

        This can be used to change what information is shown in labels
        or to refresh labels if dataset descriptors have changed.

        Args:
            label_parts: New list of DATASET_LABEL enums, or None to refresh with current format
        """
        logger.debug("Updating dataset labels")

        try:
            if label_parts:
                self._label_parts = label_parts
                logger.debug(
                    "Updated label format to include: %s",
                    [part.value for part in label_parts],
                )

            updated_count = 0
            for checkbox, dataset in self._checkbox_dataset_map.items():
                try:
                    old_description = checkbox.description
                    new_description = self.get_dataset_label(dataset)
                    checkbox.description = new_description

                    if old_description != new_description:
                        updated_count += 1

                except Exception as e:
                    logger.warning("Error updating label for dataset: %s", e)
                    continue

            logger.debug("Updated %d dataset labels", updated_count)

        except Exception as e:
            logger.error("Error updating dataset labels: %s", e, exc_info=True)

    def get_checkboxes(self) -> List[widgets.Checkbox]:
        """
        Get a copy of all checkbox widgets.
        This allows external components to add observer methods to checkboxes.

        Returns:
            Copy of the checkbox list to prevent external modification
        """
        return self._checkboxes.copy()
