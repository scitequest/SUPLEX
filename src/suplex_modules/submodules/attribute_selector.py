import logging
from typing import List, Optional, Union, Dict, Any
import ipywidgets as widgets
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
)

logger = logging.getLogger(__name__)


def extract_value_list_from_dataset(
    dataset: Dataset, attribute: DATASET_ATTRIBUTE
) -> Union[List[float], List[List[float]], List[List[List[float]]]]:
    """
    Extracts the values of the specified attribute from the given dataset and returns them as a nested list.

    The dimensionality of the returned list depends on the type of attribute:
    - Data statistics attributes return a 1D list (one value per sample).
    - Basic spot data attributes return a 2D list (list of values per spot for each sample).
    - Background rectangle coordinates return a 2D list (list of coordinates for each rectangle).
    - Spot coordinates return a 3D list (list of coordinates per spot for each sample).

    For parameter-related attributes, if the required parameters are missing or incomplete,
    an empty list is returned. Data and data statistics are always assumed to be present.
    For unknown attributes, logs a warning and returns an empty list.

    Args:
        dataset (Dataset): The dataset object from which to extract the attribute values.
        attribute (DATASET_ATTRIBUTE): The attribute to extract from the dataset.

    Returns:
        The extracted values in a nested list structure, or an empty list if parameters are missing or attribute is unknown.
    """
    logger.debug(f"Extracting value list for attribute: {attribute}")
    value_list = []

    # Basic Data Values (2D lists: [ [values per spot in sample] per sample ])
    if attribute == DATASET_ATTRIBUTE.MEAN_MINUS_MIN:
        value_list = [
            [spot.spot_values.mean_minus_min for spot in sample.spots]
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.NORMALIZED_MEAN:
        value_list = [
            [spot.spot_values.normalized_mean for spot in sample.spots]
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.MIN:
        value_list = [
            [spot.spot_values.min_val for spot in sample.spots]
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.MAX:
        value_list = [
            [spot.spot_values.max_val for spot in sample.spots]
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.MEAN:
        value_list = [
            [spot.spot_values.mean_val for spot in sample.spots]
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.STD_DEV:
        value_list = [
            [spot.spot_values.std_deviation for spot in sample.spots]
            for sample in dataset.samples
        ]

    # Data Statistics Values (1D lists: [value per sample])
    elif attribute == DATASET_ATTRIBUTE.ADJUSTED_AVERAGE:
        value_list = [
            sample.data_statistics.adjusted_average for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.ADJUSTED_AVERAGE_STD_DEVIATION:
        value_list = [
            sample.data_statistics.adjusted_average_std_deviation
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.RELATIVE_ADJUSTED_AVERAGE_STD_DEVIATION:
        value_list = [
            sample.data_statistics.relative_adjusted_average_std_deviation
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.NORMALIZED_AVERAGE:
        value_list = [
            sample.data_statistics.normalized_average for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.NORMALIZED_AVERAGE_STD_DEVIATION:
        value_list = [
            sample.data_statistics.normalized_average_std_deviation
            for sample in dataset.samples
        ]
    elif attribute == DATASET_ATTRIBUTE.RELATIVE_NORMALIZED_AVERAGE_STD_DEVIATION:
        value_list = [
            sample.data_statistics.relative_normalized_average_std_deviation
            for sample in dataset.samples
        ]

    # Parameters (check for None and return empty list if parameters are missing)
    elif attribute in [
        DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
        DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
    ]:
        # Spot Coordinates (3D lists: [ [ [coords per spot] per spot in sample] per sample ])
        # Since parameters are either all present or all missing, check the first one
        if (
            not dataset.samples
            or not dataset.samples[0].spots
            or dataset.samples[0].spots[0].spot_parameters is None
        ):
            logger.debug(
                f"Missing spot parameters for attribute: {attribute}. Returning empty list."
            )
            return []
        # Extract coordinates
        if attribute == DATASET_ATTRIBUTE.SPOT_COORDINATES_X:
            value_list = [
                [
                    [coord.x for coord in spot.spot_parameters.coordinates]
                    for spot in sample.spots
                ]
                for sample in dataset.samples
            ]
        elif attribute == DATASET_ATTRIBUTE.SPOT_COORDINATES_Y:
            value_list = [
                [
                    [coord.y for coord in spot.spot_parameters.coordinates]
                    for spot in sample.spots
                ]
                for sample in dataset.samples
            ]

    elif attribute in [
        DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_X,
        DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_Y,
    ]:
        # Background Rectangles Coordinates (2D lists: [ [coords per rectangle] ])
        if (
            dataset.general_parameters is None
            or not dataset.general_parameters.background_rectangles
        ):
            logger.debug(
                f"Missing background rectangle parameters for attribute: {attribute}. Returning empty list."
            )
            return []
        if attribute == DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_X:
            value_list = [
                [coord.x for coord in rect.coordinates]
                for rect in dataset.general_parameters.background_rectangles
            ]
        elif attribute == DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_Y:
            value_list = [
                [coord.y for coord in rect.coordinates]
                for rect in dataset.general_parameters.background_rectangles
            ]

    else:
        logger.warning("Unknown attribute: %s", attribute)
        return []

    logger.debug(
        f"Extracted value list for attribute {attribute} with length: {len(value_list)}"
    )
    return value_list


def flatten_list(nested_list: Union[List[Any], Any]) -> List[Any]:
    """
    Convenience method which recursively flattens a nested list structure into a single-level list.

    Takes any arbitrarily nested list and returns a flat list containing all
    non-list elements in their original order. Non-list elements are preserved
    as-is, regardless of their type.

    Args:
        nested_list: A potentially nested list structure, or any non-list value.
                    Can contain lists of lists to any depth.

    Returns:
        A flat list containing all non-list elements from the input structure.
        If the input is not a list, returns it wrapped in a list.

    """
    if not isinstance(nested_list, list):
        return [nested_list]

    flat = []
    for item in nested_list:
        flat.extend(flatten_list(item))

    return flat


def get_flat_value_list(dataset: Dataset, attribute: DATASET_ATTRIBUTE) -> List[float]:
    """
    Extract and flatten values from a dataset based on the specified attribute type.

    Processes different attribute types with specific handling:
    - DATA_ATTRIBUTES: Values are flattened into a 1D list
    - DATA_STATISTICS_ATTRIBUTES: Values are returned as-is
    - SPOT_COORDINATES_X/Y: Averages are calculated for each coordinate and the flattened
    - BACKGROUND_RECTANGLES_COORDINATES_X/Y: Averages are calculated for each rectangle

    Averaging of coordinates is done to simplify analyses,
    essentially we use the center coordinate instead of the individual polygon vertexes.

    Args:
        dataset: Dataset object containing the values to extract
        attribute: DATASET_ATTRIBUTE specifying which values to extract

    Returns:
        List of float values, processed according to the attribute type.
        Returns empty list for unknown attributes.
    """
    logger.debug(f"Getting flat value list for attribute: {attribute}")
    value_list = extract_value_list_from_dataset(dataset, attribute)

    if attribute in DATA_ATTRIBUTES:
        flat_list = flatten_list(value_list)
        logger.debug(f"Flattened DATA_ATTRIBUTES list length: {len(flat_list)}")
        return flat_list

    if attribute in DATA_STATISTICS_ATTRIBUTES:
        logger.debug(
            f"Returning DATA_STATISTICS_ATTRIBUTES list length: {len(value_list)}"
        )
        return value_list

    if attribute in [
        DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
        DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
    ]:
        avg_coords_list = [
            sum(coords) / len(coords)
            for spots in value_list
            for coords in spots
            if coords
        ]
        logger.debug(f"Averaged SPOT_COORDINATES list length: {len(avg_coords_list)}")
        return avg_coords_list

    if attribute in [
        DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_X,
        DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_Y,
    ]:
        avg_coords_list = [sum(rect) / len(rect) for rect in value_list if rect]
        logger.debug(
            f"Averaged BACKGROUND_RECTANGLES_COORDINATES list length: {len(avg_coords_list)}"
        )
        return avg_coords_list

    # Default case
    logger.warning("Unknown attribute: %s", attribute)
    return []


class AttributeSelector:
    """
    Provides UI widgets for selecting predefined dataset attributes and extracting their values.

    This class offers methods to create selection widgets (dropdown, checkboxes, radio buttons)
    for attributes defined in DATASET_ATTRIBUTE enum, and to retrieve selected values from a dataset.
    """

    def __init__(self):
        """
        Initialize the AttributeSelector.
        """
        logger.debug("Initializing AttributeSelector")
        self._widgets = []
        self._selected_fields = set()

    def get_selected_values(self, dataset: Dataset) -> Dict[
        DATASET_ATTRIBUTE,
        Union[List[float], List[List[float]], List[List[List[float]]]],
    ]:
        """
        Collects the selected fields from the widgets and extracts the corresponding values from the given dataset.

        Returns:
            A dictionary with selected attributes as keys and their extracted values as values packed into 1D, 2D or 3D lists.
        """
        logger.debug("Getting selected values from widgets")
        # Reset
        self._selected_fields = set()

        for widget in self._widgets:
            if isinstance(widget, widgets.Dropdown):
                if widget.value:
                    self._selected_fields.add(widget.value)
                continue

            # Radio buttons are also checkboxes and can be handled the same.
            if isinstance(widget, widgets.Checkbox):
                if widget.value:
                    self._selected_fields.add(widget.description)
                continue

            # May add additional widgets in later versions

        selected_values = {}
        for enum_value in self._selected_fields:
            enum = DATASET_ATTRIBUTE(enum_value)
            selected_values[enum] = extract_value_list_from_dataset(dataset, enum)

        logger.debug(f"Selected values for {len(selected_values)} attributes")
        return selected_values

    def get_dropdown_widget(
        self,
        included_attributes: List[DATASET_ATTRIBUTE] = list(DATASET_ATTRIBUTE),
        layout: Optional[widgets.Layout] = None,
    ) -> widgets.Dropdown:
        """
        Get a dropdown widget for single attribute selection.

        Args:
            included_attributes: List of DATASET_ATTRIBUTE members to include as options.
            layout: Optional layout for the widget.

        Returns:
            A Dropdown widget
        """
        logger.debug(
            f"Creating dropdown widget with {len(included_attributes)} options"
        )

        options = [field.value for field in included_attributes]

        dropdown = WidgetFactory.dropdown(
            options=options,
            value=options[0],
            description="",  # Description should be done via external labels
            layout=layout,
        )
        self._widgets.append(dropdown)

        return dropdown

    def get_checkbox_widgets(
        self,
        included_attributes: List[DATASET_ATTRIBUTE] = list(DATASET_ATTRIBUTE),
        layout: Optional[widgets.Layout] = None,
    ) -> List[widgets.Checkbox]:
        """
        Get checkbox widgets for multiple attribute selection.

        Args:
            included_attributes: List of DATASET_ATTRIBUTE members to include as options.
            layout: Optional layout for the widget.

        Returns:
            List of checkbox widgets
        """
        logger.debug(
            f"Creating checkbox widgets with {len(included_attributes)} options"
        )
        options = [field.value for field in included_attributes]

        checkboxes = []
        for option in options:
            checkbox = WidgetFactory.checkbox(
                value=False, description=option, layout=layout
            )
            self._widgets.append(checkbox)
            checkboxes.append(checkbox)

        return checkboxes

    def get_radio_button_widgets(
        self,
        included_attributes: List[DATASET_ATTRIBUTE],
        layout: Optional[widgets.Layout] = None,
    ) -> List[widgets.Checkbox]:
        """
        Get radio button widgets for single attribute selection.

        Args:
            included_attributes: List of DATASET_ATTRIBUTE members to include as options.
            layout: Optional layout for the widget.

        Returns:
            List of checkbox widgets configured as radio buttons
        """
        logger.debug(
            f"Creating radio button widgets with {len(included_attributes)} options"
        )
        # Add all attributes by default
        if not included_attributes:
            included_attributes = list(DATASET_ATTRIBUTE)

        options = [field.value for field in included_attributes]

        radio_buttons = WidgetFactory.radio_buttons(
            options=options, i_selected=0, layout=layout
        )
        self._widgets += radio_buttons

        return radio_buttons
