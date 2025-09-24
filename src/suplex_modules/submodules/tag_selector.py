import logging
from typing import List, Set

import ipywidgets as widgets

from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory

logger = logging.getLogger(__name__)


class TagSelector:
    """
    This class provides a user interface for filtering datasets by their
    associated tags (both MARTin and SUPLEX tags). It supports different
    selection modes and provides methods to retrieve datasets that match
    the selected tag criteria.
    """

    def __init__(self, datasets: List[Dataset]) -> None:
        """
        Initialize the tag selector with a list of datasets.

        Args:
            datasets: List of Dataset objects to extract tags from and filter
        """
        logger.debug("Initializing tag selector for %d datasets", len(datasets))

        self._datasets = datasets
        self._martin_checkboxes: List[widgets.Checkbox] = []
        self._suplex_checkboxes: List[widgets.Checkbox] = []

        logger.debug("Tag selector initialized successfully")

    def get_ui_element(self) -> widgets.VBox:
        """
        Generates checkboxes for all available tags (both MARTin and SUPLEX)
        and arranges them in a scrollable grid layout.

        Returns:
            VBox widget containing the tag selection interface
        """
        logger.debug("Building tag selector UI")

        try:
            # Create checkboxes for different tag types
            self._martin_checkboxes = self.create_tag_checkboxes(
                self.get_all_martin_tags()
            )
            self._suplex_checkboxes = self.create_tag_checkboxes(
                self.get_all_suplex_tags()
            )

            # Combine all checkboxes
            checkboxes = self._martin_checkboxes + self._suplex_checkboxes

            if not checkboxes:
                logger.debug("No tags available for selection")
                no_tags_message = WidgetFactory.html_widget(
                    value="<i>No tags available.</i>", width="100%", height="auto"
                )
                content = [no_tags_message]
            else:
                logger.debug(
                    "Created %d tag checkboxes (%d MARTin, %d SUPLEX)",
                    len(checkboxes),
                    len(self._martin_checkboxes),
                    len(self._suplex_checkboxes),
                )

                header = WidgetFactory.html_widget(
                    value="<b>Tags:</b>", width="100%", height="auto"
                )

                grid = WidgetFactory.grid_container(
                    children=checkboxes, width="100%", height="auto"
                )
                content = [header, grid]

            return WidgetFactory.vbox(
                children=content,
                width="100%",
                height="100%",
                overflow_y="auto",
                layout=widgets.Layout(padding="10px"),
            )

        except Exception as e:
            logger.error("Failed to build tag selector UI: %s", e, exc_info=True)
            return WidgetFactory.html_widget(
                value="<div>Error loading tag selector</div>",
                width="100%",
                height="100%",
            )

    def get_all_martin_tags(self) -> List[str]:
        """
        Extract all unique MARTin tags from the datasets.

        Returns:
            Sorted list of unique MARTin tag strings
        """
        logger.debug("Extracting MARTin tags from datasets")

        try:
            all_tags = set()
            for dataset in self._datasets:
                if hasattr(dataset, "tags") and dataset.tags:
                    all_tags.update(dataset.tags)

            martin_tags = sorted(list(all_tags))
            logger.debug("Found %d unique MARTin tags", len(martin_tags))
            return martin_tags

        except Exception as e:
            logger.error("Error extracting MARTin tags: %s", e, exc_info=True)
            return []

    def get_all_suplex_tags(self) -> List[str]:
        """
        Extract all unique SUPLEX tags from the datasets.

        Returns:
            Sorted list of unique SUPLEX tag strings
        """
        logger.debug("Extracting SUPLEX tags from datasets")

        try:
            all_tags = set()
            for dataset in self._datasets:
                if hasattr(dataset, "suplex_tags") and dataset.suplex_tags:
                    all_tags.update(dataset.suplex_tags)

            suplex_tags = sorted(list(all_tags))
            logger.debug("Found %d unique SUPLEX tags", len(suplex_tags))
            return suplex_tags

        except Exception as e:
            logger.error("Error extracting SUPLEX tags: %s", e, exc_info=True)
            return []

    def create_tag_checkboxes(self, tags: List[str]) -> List[widgets.Checkbox]:
        """
        Create checkbox widgets for a list of tags.

        Args:
            tags: List of tag strings to create checkboxes for

        Returns:
            List of Checkbox widgets configured for grid display
        """
        logger.debug("Creating checkboxes for %d tags", len(tags))

        checkboxes = []

        try:
            for tag in tags:
                checkbox = WidgetFactory.checkbox(
                    value=False, description=str(tag), disabled=False, indent=True
                )
                # Set additional layout properties for grid display
                checkbox.layout.width = "auto"
                checkbox.style.description_width = "initial"

                checkboxes.append(checkbox)

            logger.debug("Successfully created %d tag checkboxes", len(checkboxes))

        except Exception as e:
            logger.error("Error creating tag checkboxes: %s", e, exc_info=True)

        return checkboxes

    def get_selected_martin_tags(self) -> List[str]:
        """
        Get the currently selected MARTin tags.

        Returns:
            List of selected MARTin tag strings
        """
        try:
            selected = [cb.description for cb in self._martin_checkboxes if cb.value]
            logger.debug("Retrieved %d selected MARTin tags", len(selected))
            return selected
        except Exception as e:
            logger.error("Error getting selected MARTin tags: %s", e, exc_info=True)
            return []

    def get_selected_suplex_tags(self) -> List[str]:
        """
        Get the currently selected SUPLEX tags.

        Returns:
            List of selected SUPLEX tag strings
        """
        try:
            selected = [cb.description for cb in self._suplex_checkboxes if cb.value]
            logger.debug("Retrieved %d selected SUPLEX tags", len(selected))
            return selected
        except Exception as e:
            logger.error("Error getting selected SUPLEX tags: %s", e, exc_info=True)
            return []

    def get_all_selected_tags(self) -> List[str]:
        """
        Get all currently selected tags (both MARTin and SUPLEX).

        Returns:
            Combined list of all selected tag strings
        """
        return self.get_selected_martin_tags() + self.get_selected_suplex_tags()

    def get_tagged_datasets_any(self) -> List[Dataset]:
        """
        Returns datasets that contain at least one of the selected tags,
        either in their MARTin tags or SUPLEX tags.

        Returns:
            List of Dataset objects matching the criteria
        """
        logger.debug("Finding datasets with any selected tags")

        try:
            selected_martin_tags = self.get_selected_martin_tags()
            selected_suplex_tags = self.get_selected_suplex_tags()

            if not selected_martin_tags and not selected_suplex_tags:
                logger.debug("No tags selected, returning empty list")
                return []

            matching_datasets = []

            for dataset in self._datasets:
                try:
                    dataset_martin_tags = set(getattr(dataset, "tags", []))
                    dataset_suplex_tags = set(getattr(dataset, "suplex_tags", []))

                    # Check if dataset has any of the selected tags
                    has_martin_tags = bool(
                        dataset_martin_tags.intersection(selected_martin_tags)
                    )
                    has_suplex_tags = bool(
                        dataset_suplex_tags.intersection(selected_suplex_tags)
                    )

                    if has_martin_tags or has_suplex_tags:
                        matching_datasets.append(dataset)

                except Exception as e:
                    logger.warning("Error checking tags for dataset: %s", e)
                    continue

            logger.debug(
                "Found %d datasets with any selected tags", len(matching_datasets)
            )
            return matching_datasets

        except Exception as e:
            logger.error(
                "Error finding datasets with any selected tags: %s", e, exc_info=True
            )
            return []

    def get_tagged_datasets_all(self) -> List[Dataset]:
        """
        Returns datasets that contain all selected tags in their respective
        tag collections (MARTin and SUPLEX tags are checked separately).

        Returns:
            List of Dataset objects matching the criteria
        """
        logger.debug("Finding datasets with all selected tags")

        try:
            selected_martin_tags = self.get_selected_martin_tags()
            selected_suplex_tags = self.get_selected_suplex_tags()

            if not selected_martin_tags and not selected_suplex_tags:
                logger.debug("No tags selected, returning empty list")
                return []

            matching_datasets = []

            for dataset in self._datasets:
                try:
                    dataset_martin_tags = set(getattr(dataset, "tags", []))
                    dataset_suplex_tags = set(getattr(dataset, "suplex_tags", []))

                    # Check if dataset has all selected tags
                    has_all_martin_tags = set(selected_martin_tags).issubset(
                        dataset_martin_tags
                    )
                    has_all_suplex_tags = set(selected_suplex_tags).issubset(
                        dataset_suplex_tags
                    )

                    if has_all_martin_tags and has_all_suplex_tags:
                        matching_datasets.append(dataset)

                except Exception as e:
                    logger.warning("Error checking tags for dataset: %s", e)
                    continue

            logger.debug(
                "Found %d datasets with all selected tags", len(matching_datasets)
            )
            return matching_datasets

        except Exception as e:
            logger.error(
                "Error finding datasets with all selected tags: %s", e, exc_info=True
            )
            return []

    def clear_selection(self) -> None:
        """
        Clear all tag selections by unchecking all checkboxes.
        """
        logger.debug("Clearing all tag selections")

        try:
            for checkbox in self._martin_checkboxes + self._suplex_checkboxes:
                checkbox.value = False
            logger.debug("Successfully cleared all tag selections")

        except Exception as e:
            logger.error("Error clearing tag selections: %s", e, exc_info=True)

    def select_all(self) -> None:
        """
        Select all available tags by checking all checkboxes.
        """
        logger.debug("Selecting all available tags")

        try:
            for checkbox in self._martin_checkboxes + self._suplex_checkboxes:
                checkbox.value = True
            logger.debug("Successfully selected all available tags")

        except Exception as e:
            logger.error("Error selecting all tags: %s", e, exc_info=True)

    def select_tags(
        self, martin_tags: List[str] = None, suplex_tags: List[str] = None
    ) -> None:
        """
        Programmatically select specific tags.

        Args:
            martin_tags: List of MARTin tag strings to select
            suplex_tags: List of SUPLEX tag strings to select
        """
        logger.debug(
            "Programmatically selecting tags: %d MARTin, %d SUPLEX",
            len(martin_tags or []),
            len(suplex_tags or []),
        )

        try:
            if martin_tags:
                for checkbox in self._martin_checkboxes:
                    if checkbox.description in martin_tags:
                        checkbox.value = True
                        logger.debug("Selected MARTin tag: %s", checkbox.description)

            if suplex_tags:
                for checkbox in self._suplex_checkboxes:
                    if checkbox.description in suplex_tags:
                        checkbox.value = True
                        logger.debug("Selected SUPLEX tag: %s", checkbox.description)

        except Exception as e:
            logger.error("Error selecting specified tags: %s", e, exc_info=True)
