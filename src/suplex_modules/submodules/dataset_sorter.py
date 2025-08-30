import logging
import ipywidgets as widgets
import statistics
import numpy as np
from typing import List, Union, Optional, Callable, Tuple, Any
from enum import Enum

from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.submodule_constants import (
    SORT_METHOD,
    DATASET_ATTRIBUTE,
    DATASET_DESCRIPTOR,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
    PARAMETERS_ATTRIBUTES,
)
from suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    get_flat_value_list,
)
from suplex_modules.submodules.settings.submodule_settings_constants import OPTION_INSET

logger = logging.getLogger(__name__)


def sort_datasets(
    datasets: List[Dataset], reference_list: List[Any], invert_order: bool = False
) -> Tuple[List[Dataset], List[Any]]:
    """
    Sort datasets according to the order of a given reference_list.
    This method requires two 1D lists and can either be called directly or indirectly via other sort methods such as sort_by_avg_value which pre-process the reference list.
    While direct calls can be used to sort for metadata values such as a datasets name, id or its project, indirect calls are used to sort a dataset by its spot values.

    Args:
        datasets: List of Dataset objects to sort
        reference_list: Reference list that determines the sort order
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets copy, sorted reference_list copy)
    """
    logger.debug(
        "Sorting datasets with reference list of length %d, invert_order: %s",
        len(reference_list),
        invert_order,
    )
    if len(datasets) != len(reference_list):
        logger.warning(
            "Sort could not be conducted because datasets and reference list do not have the same number of entries. Datasets: %d, Reference list: %d",
            len(datasets),
            len(reference_list),
        )
        return datasets.copy(), reference_list.copy()

    try:
        paired_data = list(zip(datasets, reference_list))
        sorted_pairs = sorted(
            paired_data, key=lambda pair: pair[1], reverse=invert_order
        )

        sorted_datasets = [pair[0] for pair in sorted_pairs]
        sorted_reference = [pair[1] for pair in sorted_pairs]

        logger.debug("Sorting completed successfully")
        return sorted_datasets, sorted_reference

    except Exception as e:
        logger.error("Error during sorting: %s", e)
        return datasets.copy(), reference_list.copy()


def sort_by_avg_value(
    datasets: List[Dataset],
    reference_lists: List[List[Union[float, int]]],
    invert_order: bool = False,
) -> Tuple[List[Dataset], List[Union[float, int]]]:
    """
    Sort datasets by the average value of their reference lists.

    Args:
        datasets: List of Dataset objects to sort
        reference_lists: List of lists containing numeric values for each dataset
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets, sorted reference values)
    """
    logger.debug("Sorting by average value, invert_order: %s", invert_order)
    reference_list = []
    for ref_list in reference_lists:
        avg = np.nanmean(ref_list) if ref_list else 0
        reference_list.append(avg)

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )
    return sorted_datasets, sorted_reference


def sort_by_cumulative_value(
    datasets: List[Dataset],
    reference_lists: List[List[Union[float, int]]],
    invert_order: bool = False,
) -> Tuple[List[Dataset], List[Union[float, int]]]:
    """
    Sort datasets by the cumulative (sum) value of their reference lists.

    Args:
        datasets: List of Dataset objects to sort
        reference_lists: List of lists containing numeric values for each dataset
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets, sorted reference values)
    """
    logger.debug("Sorting by cumulative value, invert_order: %s", invert_order)
    reference_list = []
    for ref_list in reference_lists:
        cum = np.nansum(ref_list) if ref_list else 0
        reference_list.append(cum)

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )
    return sorted_datasets, sorted_reference


def sort_by_max_value(
    datasets: List[Dataset],
    reference_lists: List[List[Union[float, int]]],
    invert_order: bool = False,
) -> Tuple[List[Dataset], List[Union[float, int]]]:
    """
    Sort datasets by the maximum value in their reference lists.

    Args:
        datasets: List of Dataset objects to sort
        reference_lists: List of lists containing numeric values for each dataset
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets, sorted reference values)
    """
    logger.debug("Sorting by max value, invert_order: %s", invert_order)
    reference_list = []
    for ref_list in reference_lists:
        max_val = np.nanmax(ref_list) if ref_list else 0
        reference_list.append(max_val)

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )
    return sorted_datasets, sorted_reference


def sort_by_min_value(
    datasets: List[Dataset],
    reference_lists: List[List[Union[float, int]]],
    invert_order: bool = False,
) -> Tuple[List[Dataset], List[Union[float, int]]]:
    """
    Sort datasets by the minimum value in their reference lists.

    Args:
        datasets: List of Dataset objects to sort
        reference_lists: List of lists containing numeric values for each dataset
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets, sorted reference values)
    """
    logger.debug("Sorting by min value, invert_order: %s", invert_order)
    reference_list = []
    for ref_list in reference_lists:
        min_val = np.nanmin(ref_list) if ref_list else 0
        reference_list.append(min_val)

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )
    return sorted_datasets, sorted_reference


def sort_by_median_value(
    datasets: List[Dataset],
    reference_lists: List[List[Union[float, int]]],
    invert_order: bool = False,
) -> Tuple[List[Dataset], List[Union[float, int]]]:
    """
    Sort datasets by the median value of their reference lists.

    Args:
        datasets: List of Dataset objects to sort
        reference_lists: List of lists containing numeric values for each dataset
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets, sorted reference values)
    """
    logger.debug("Sorting by median value, invert_order: %s", invert_order)
    reference_list = []
    for ref_list in reference_lists:
        median = np.nanmedian(ref_list) if ref_list else 0
        reference_list.append(median)

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )
    return sorted_datasets, sorted_reference


def sort_by_number_of_values(
    datasets: List[Dataset],
    reference_lists: List[List[Union[float, int]]],
    invert_order: bool = False,
) -> Tuple[List[Dataset], List[Union[float, int]]]:
    """
    Sort datasets by the number of values in their reference lists.

    Args:
        datasets: List of Dataset objects to sort
        reference_lists: List of lists containing numeric values for each dataset
        invert_order: If True, reverse the sort order

    Returns:
        Tuple of (sorted datasets, sorted reference values)
    """
    logger.debug("Sorting by number of values, invert_order: %s", invert_order)
    reference_list = []
    for ref_list in reference_lists:
        num = len(ref_list)
        reference_list.append(num)

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )
    return sorted_datasets, sorted_reference


def sort_alphanumerically(
    datasets: List[Dataset], descriptor: DATASET_DESCRIPTOR, invert_order: bool = False
) -> Tuple[List[Dataset], List[str]]:
    """
    Sort datasets alphanumerically based on the specified descriptor.

    Args:
        datasets: List of Dataset objects to sort
        descriptor: DATASET_DESCRIPTOR to sort by (name, id, project)
        invert_order: If True, reverse the sort order

    Returns:
        Tuple containing Sorted list of datasets as well as sorted reference list with the extracted attribute values
    """
    logger.debug(
        "Sorting alphanumerically by descriptor %s, invert_order: %s",
        descriptor,
        invert_order,
    )
    if descriptor == DATASET_DESCRIPTOR.NAME:
        reference_list = [
            (
                dataset.metadata.patient.name.lower()
                if dataset.metadata and dataset.metadata.patient
                else ""
            )
            for dataset in datasets
        ]
    elif descriptor == DATASET_DESCRIPTOR.ID:
        reference_list = [
            (
                dataset.metadata.patient.pat_id.lower()
                if dataset.metadata and dataset.metadata.patient
                else ""
            )
            for dataset in datasets
        ]
    elif descriptor == DATASET_DESCRIPTOR.PROJECT:
        # None projects are set to "" to collect them at the beginning of the sorted datasets
        reference_list = [
            (
                dataset.project.name.lower()
                if dataset.project and dataset.project.name.lower() != "none"
                else ""
            )
            for dataset in datasets
        ]
    elif descriptor == DATASET_DESCRIPTOR.MEASURE_DATE:
        reference_list = [
            (
                dataset.measure_date.isoformat()
                if dataset.measure_date
                else "0000-00-00T00:00:00"
            )
            for dataset in datasets
        ]
    elif descriptor == DATASET_DESCRIPTOR.IMAGE_CREATION_DATE:
        reference_list = [
            (
                dataset.image_creation_date.isoformat()
                if dataset.image_creation_date
                else "0000-00-00T00:00:00"
            )
            for dataset in datasets
        ]
    else:
        logger.warning(
            "Tried to sort alphanumerically with non existent dataset descriptor: %s",
            descriptor,
        )
        return datasets.copy(), []

    # Have to invert order to sort from A-Z and earliest to latest.
    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order
    )

    return sorted_datasets, sorted_reference


def sort_by_has_tag(
    datasets: List[Dataset], tag: str, invert_order: bool = False
) -> Tuple[List[Dataset], List[bool]]:
    """
    Sort datasets based on whether they have the specified tag.
    Datasets with the tag come before those without it.

    Args:
        datasets: List of Dataset objects to sort
        tag: The tag to check for
        invert_order: If True, reverse the sort order (datasets without tag first)

    Returns:
        Tuple containing sorted list of datasets and sorted reference list of booleans
    """
    logger.debug("Sorting by has_tag '%s', invert_order: %s", tag, invert_order)
    reference_list = [
        tag in (dataset.tags + dataset.suplex_tags) for dataset in datasets
    ]

    sorted_datasets, sorted_reference = sort_datasets(
        datasets, reference_list, invert_order=invert_order
    )

    return sorted_datasets, sorted_reference


# If necessary we may implement another method sort_by_is_true later on.
# This would allow users to sort by boolean general parameters values such as invert_lut.


class SortStep:
    """
    Represents a single sorting step with UI elements and sorting logic.
    Can be used via the DatasetSorter or by itself if just a singular sorting step is needed.
    """

    def __init__(
        self,
        label: str = "",
        allowed_sort_methods: List[SORT_METHOD] = None,
        allowed_set_descriptors: List[DATASET_DESCRIPTOR] = None,
        allowed_attributes: List[DATASET_ATTRIBUTE] = None,
        tags: List[str] = None,
    ):
        """
        Initialize a SortStep instance.

        Args:
            label: Step label
            allowed_sort_methods: List of allowed SORT_METHOD enums
            allowed_set_descriptors: List of allowed DATASET_DESCRIPTOR enums
            allowed_attributes: List of allowed DATASET_ATTRIBUTE enums
            tags: List of tags for has_tag sort option
        """
        logger.debug("Initializing SortStep for: %s", label)
        self._step_label = WidgetFactory.label(value=label)

        self._invert_checkbox = WidgetFactory.checkbox(
            value=False,
            description="Inverted",
            layout=widgets.Layout(margin="0px", padding="0px"),
            indent=False,
        )

        self._allowed_sort_methods = allowed_sort_methods.copy() or list(SORT_METHOD)
        self._allow_inversion = SORT_METHOD.INVERT_ORDER in self._allowed_sort_methods
        if self._allow_inversion:
            self._allowed_sort_methods.remove(SORT_METHOD.INVERT_ORDER)

        sort_method_options = [method.value for method in self._allowed_sort_methods]
        if not sort_method_options:
            logger.warning("No sort method options available")
        self._sort_method_dropdown = WidgetFactory.dropdown(
            options=sort_method_options,
            value=sort_method_options[0] if sort_method_options else None,
            layout=widgets.Layout(margin="0px 5px 0px 0px", padding="0px"),
            on_change=lambda b: self.update_ui(),
        )

        set_descriptors = allowed_set_descriptors or list(DATASET_DESCRIPTOR)
        descriptor_options = (
            [desc.value for desc in set_descriptors]
            if set_descriptors
            else ["No Descriptors Enabled"]
        )
        self._descriptor_dropdown = WidgetFactory.dropdown(
            options=descriptor_options,
            value=descriptor_options[0],
            layout=widgets.Layout(margin="0px 5px 0px 0px", padding="0px"),
        )

        attributes = allowed_attributes or list(DATASET_ATTRIBUTE)
        attribute_options = (
            [attr.value for attr in attributes]
            if attributes
            else ["No Attributes Enabled"]
        )
        self._value_extractor = ValueExtractor(
            attributes = allowed_attributes
        )
        self._attribute_dropdown = self._value_extractor.get_attribute_widget()
        self._attribute_dropdown.layout = widgets.Layout(margin="0px 5px 0px 0px", padding="0px")

        self._tags = tags or []
        tag_options = self._tags if self._tags else ["No Tags Available"]
        self._tag_dropdown = WidgetFactory.dropdown(
            options=tag_options,
            value=tag_options[0],
            layout=widgets.Layout(margin="0px 5px 0px 0px", padding="0px"),
        )

        # Using margins instead of gap works better with dynamic updates
        self._ui_box = WidgetFactory.hbox(
            children=[],
            layout=widgets.Layout(
                margin="0px", padding=OPTION_INSET.PRIMARY, justify_content="flex-start"
            ),
        )
        self.update_ui()

    def update_ui(self):
        """
        Update the UI elements based on current selections.
        """
        logger.debug("Updating UI for SortStep")
        content = []

        content.append(self._sort_method_dropdown)

        sort_method = SORT_METHOD(self._sort_method_dropdown.value)

        if sort_method == SORT_METHOD.ALPHANUMERIC_SORT:
            content.append(self._descriptor_dropdown)
        elif sort_method == SORT_METHOD.HAS_TAG_SORT:
            content.append(self._tag_dropdown)
        elif sort_method != SORT_METHOD.UNSORTED:
            content.append(self._attribute_dropdown)

        if self._allow_inversion:
            content.append(self._invert_checkbox)

        self._ui_box.children = content

    def get_ui(self) -> widgets.Widget:
        """
        Get the complete UI widget for this sort step.

        Returns:
            VBox containing the label and UI box
        """
        logger.debug("Retrieving UI for SortStep")
        return WidgetFactory.vbox(
            children=[self._step_label, self._ui_box],
            layout=widgets.Layout(
                margin="0px", padding=OPTION_INSET.PRIMARY, gap="5px"
            ),
        )

    def get_sorted_datasets(self, datasets: List[Dataset]) -> List[Dataset]:
        """
        Sort the given datasets based on current step settings.

        Args:
            datasets: List of Dataset objects to sort

        Returns:
            Sorted list of datasets
        """
        if not datasets:
            logger.debug("No datasets provided for sorting")
            return []

        sort_method_str = self._sort_method_dropdown.value
        invert = self._invert_checkbox.value

        logger.debug("Sorting with method: %s, invert: %s", sort_method_str, invert)

        try:
            sort_method = SORT_METHOD(sort_method_str)
        except ValueError:
            logger.warning("Invalid sort method: %s", sort_method_str)
            return datasets.copy()

        if sort_method == SORT_METHOD.UNSORTED:
            logger.debug("Unsorted method selected")
            if invert:
                logger.debug("Inverting the dataset list as invert is True")
                return datasets[::-1]
            else:
                return datasets.copy()

        if sort_method == SORT_METHOD.ALPHANUMERIC_SORT:
            descriptor_str = self._descriptor_dropdown.value
            if descriptor_str == "No Descriptors Enabled":
                logger.warning("No descriptors enabled for alphanumeric sort")
                return datasets.copy()
            try:
                descriptor = DATASET_DESCRIPTOR(descriptor_str)
                sorted_datasets, _ = sort_alphanumerically(datasets, descriptor, invert)
                logger.debug("Alphanumeric sorting completed")
                return sorted_datasets
            except ValueError:
                logger.warning("Invalid descriptor: %s", descriptor_str)
                return datasets.copy()

        if sort_method == SORT_METHOD.HAS_TAG_SORT:
            tag = self._tag_dropdown.value
            if tag == "No Tags Available" and len(self._tag_dropdown.children) == 1:
                logger.warning("No tags available for has_tag sort")
                return datasets.copy()
            sorted_datasets, _ = sort_by_has_tag(datasets, tag, invert)
            logger.debug("Has_tag sorting completed")
            return sorted_datasets

        # Value-based sorts
        attribute = self._value_extractor.attribute

        # Extract flat value lists for each dataset
        reference_lists = [get_flat_value_list(ds, attribute) for ds in datasets]
        logger.debug("Extracted reference lists for %d datasets", len(datasets))

        # Apply sort
        if sort_method == SORT_METHOD.AVG_VALUE_SORT:
            sorted_datasets, _ = sort_by_avg_value(datasets, reference_lists, invert)
        elif sort_method == SORT_METHOD.MEDIAN_VALUE_SORT:
            sorted_datasets, _ = sort_by_median_value(datasets, reference_lists, invert)
        elif sort_method == SORT_METHOD.MAX_VALUE_SORT:
            sorted_datasets, _ = sort_by_max_value(datasets, reference_lists, invert)
        elif sort_method == SORT_METHOD.MIN_VALUE_SORT:
            sorted_datasets, _ = sort_by_min_value(datasets, reference_lists, invert)
        elif sort_method == SORT_METHOD.CUMULATIVE_VALUE_SORT:
            sorted_datasets, _ = sort_by_cumulative_value(
                datasets, reference_lists, invert
            )
        elif sort_method == SORT_METHOD.NUMBER_OF_VALUES_SORT:
            sorted_datasets, _ = sort_by_number_of_values(
                datasets, reference_lists, invert
            )
        else:
            logger.warning("Unsupported sort method: %s", sort_method)
            return datasets.copy()

        logger.debug("Value-based sorting completed")
        return sorted_datasets


class DatasetSorter:
    """
    Provides a UI for selecting sorting options to conduct multiple sorting actions iteratively.
    It should be noted that all SortSteps share the same settings.
    """

    def __init__(
        self,
        allowed_sort_methods: List[SORT_METHOD] = list(SORT_METHOD),
        allowed_set_descriptors: List[DATASET_DESCRIPTOR] = list(DATASET_DESCRIPTOR),
        allowed_attributes: List[DATASET_ATTRIBUTE] = list(DATASET_ATTRIBUTE),
        num_levels: int = 1,
        max_num_levels: int = 3,
        tags: List[str] = None,
    ):
        """
        Initialize DatasetSorter.
        The object stores the bounds and current state of the dataset_sorter UI.

        Args:
            allowed_sort_methods: List of allowed SORT_METHOD enums
            allowed_set_descriptors: List of allowed DATASET_DESCRIPTOR enums
            allowed_attributes: List of allowed DATASET_ATTRIBUTE enums
            num_levels: Initial number of sort levels (dropdowns), default 1, minimum 1
            max_num_levels: Maximum number of sort levels allowed, default 3
            tags: List of tags for has_tag sort option
        """
        logger.debug(
            "Initializing DatasetSorter with num_levels: %d, max_num_levels: %d",
            num_levels,
            max_num_levels,
        )

        self._allowed_sort_methods = allowed_sort_methods
        self._allowed_set_descriptors = allowed_set_descriptors
        self._allowed_attributes = allowed_attributes

        self._tags = tags or []

        # No values below 1 allowed
        if num_levels < 1:
            logger.warning(
                "Illegal value: num_levels must be equal or greater than 1. Value given: %d. Attribute num_levels will be defaulted to 1.",
                num_levels,
            )
            num_levels = 1

        # Max num levels must be the same or higher than num levels
        if max_num_levels < num_levels:
            logger.warning(
                "Illegal value: max_num_levels must be equal or greater than num_levels. Value given: %d. Attribute max_num_levels will be set to num_levels.",
                max_num_levels,
            )
            max_num_levels = num_levels

        self._num_levels = num_levels
        self._max_num_levels = max_num_levels

        self._ui_container = None
        self._sorting_steps = []  # List of SortStep instances

    def get_ui(self) -> widgets.Widget:
        """
        Returns a VBox containing UI elements for sorting settings.

        The UI is organized into sections for better organization.

        Returns:
            VBox widget containing the settings interface
        """
        logger.debug("Initiate build of DatasetSorter UI")

        ui_title = WidgetFactory.html_widget(value="<h3>Dataset Sorter</h3>")

        sections = [ui_title]

        sorting_widgets = self.create_sorting_section()
        if sorting_widgets:
            sections.append(sorting_widgets)

        if not sections:
            sections.append(
                WidgetFactory.html_widget(value="No sorting settings configured")
            )

        self._ui_container = WidgetFactory.vbox(
            children=sections,
            width="100%",
            height="auto",
            overflow_y="visible",
            overflow_x="auto",
            gap="5px",
        )

        logger.debug("DatasetSorter UI built with %d sections", len(sections))
        return self._ui_container

    def create_sorting_section(self) -> Optional[widgets.Widget]:
        """
        Create sorting configuration widgets.

        Returns:
            VBox widget for the sorting section or None if not applicable
        """
        logger.debug("Creating sorting section")
        widgets_list = []

        # Section header (no padding)
        widgets_list.append(WidgetFactory.html_widget(value="<h3>Sort Datasets</h3>"))

        n_levels_label = WidgetFactory.label(value="Number of Sorting Operations")
        n_levels_widget = WidgetFactory.number_input(
            value=self._num_levels,
            min_value=1,
            max_value=self._max_num_levels,
            step=1,
            on_change=lambda b: self.update_sorting_steps(
                n_steps=n_levels_widget.value
            ),
            layout=widgets.Layout(margin="0px", padding="0px"),
        )
        n_levels_widget_box = WidgetFactory.vbox(
            children=[n_levels_widget],
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )
        n_sorting_steps_box = WidgetFactory.vbox(
            children=[n_levels_label, n_levels_widget_box],
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )

        self._sort_steps_box = WidgetFactory.vbox(
            children=[],
            overflow_x="auto",
            overflow_y="visible",
            layout=widgets.Layout(margin="0px", padding="0px", gap="5px"),
        )
        self.update_sorting_steps(n_steps=n_levels_widget.value)

        sorting_section = WidgetFactory.vbox(
            children=[n_sorting_steps_box, self._sort_steps_box],
            width="100%",
            height="auto",
            layout=widgets.Layout(
                margin="0px", padding=OPTION_INSET.BASELINE, gap="5px"
            ),
        )
        logger.debug("Sorting section created")
        return sorting_section

    def update_sorting_steps(self, n_steps: int = 1):
        """
        Update the number of sorting steps displayed.

        Args:
            n_steps: Number of steps to display
        """
        logger.debug("Updating sorting steps to %d", n_steps)
        while len(self._sorting_steps) < n_steps:
            step_number = str(len(self._sorting_steps) + 1)
            new_step = SortStep(
                label=f"Step: {step_number}",
                allowed_sort_methods=self._allowed_sort_methods,
                allowed_set_descriptors=self._allowed_set_descriptors,
                allowed_attributes=self._allowed_attributes,
                tags=self._tags,
            )
            self._sorting_steps.append(new_step)
        self._sort_steps_box.children = [
            step.get_ui() for step in self._sorting_steps[:n_steps]
        ]
        self._num_levels = n_steps
        logger.debug("Sorting steps updated to %d", n_steps)

    def get_sorted_datasets(self, datasets) -> List[Dataset]:
        """
        Get sorted datasets based on current settings.
        Applies multi-level sorting in sequence by delegating to each SortStep.

        Returns:
            Sorted list of datasets
        """
        if not datasets:
            logger.debug("No datasets set, returning empty list")
            return []

        sorted_datasets = datasets.copy()
        logger.debug("Starting multi-level sorting with %d levels", self._num_levels)

        for i, step in enumerate(self._sorting_steps[: self._num_levels]):
            logger.debug("Applying sort step %d", i + 1)
            sorted_datasets = step.get_sorted_datasets(sorted_datasets)

        logger.debug("Multi-level sorting completed")
        return sorted_datasets
