import logging
from typing import List, Optional, Union, Dict, Any, Callable
import ipywidgets as widgets
import numpy as np
import math
import statistics
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
    NORMALIZATION,
    NORMALIZATION_DEFAULT,
    NORMALIZATION_REFERENCE_POINT,
)
from suplex_modules.submodules.settings.submodule_settings_constants import (
    OPTION_INSET,
)

logger = logging.getLogger(__name__)

ABS_MAX_VALUE = 2**16 - 1


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
        logger.warning(f"Unknown attribute: {attribute}")
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
    - SPOT_COORDINATES_X/Y: Averages are calculated for each coordinate and then flattened
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
        return flat_list

    if attribute in DATA_STATISTICS_ATTRIBUTES:
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
        return avg_coords_list

    if attribute in [
        DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_X,
        DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_Y,
    ]:
        avg_coords_list = [sum(rect) / len(rect) for rect in value_list if rect]
        return avg_coords_list

    # Default case
    logger.warning(f"Unsupported attribute: {attribute}. Returning empty list.")
    return []


def apply_normalization(
    value_lists: Dict[Dataset, List[float]],
    normalization_method: NORMALIZATION,
    custom_factor: Optional[float] = None,
    reference_indices: Optional[List[int]] = None,
) -> Dict[Dataset, List[float]]:
    """
    Apply the selected normalization to the given values.
    This function can be used externally without a ValueExtractor instance.

    Args:
        value_lists: Dict of raw extracted flat values per dataset (1D list per dataset).
        normalization_method: The normalization method as str (e.g., 'RAW', 'CUSTOM').
        custom_factor (Optional): Custom normalization factor (required for 'CUSTOM').
        reference_indices (Optional): List of reference indices (required for reference-based methods).

    Returns:
        Dict of normalized values per dataset.
    """
    logger.debug(f"Applying normalization method: {normalization_method}")
    if normalization_method == NORMALIZATION.RAW:
        return value_lists  # No normalization

    if normalization_method == NORMALIZATION.CUSTOM:
        if custom_factor is None:
            logger.warning("Custom factor not provided for CUSTOM normalization.")
            return value_lists
        if custom_factor == 0:
            logger.warning(
                "Custom factor cannot be zero. Normalization will not be applied."
            )
            return value_lists
        normalized_values = {
            key: normalize_by_factor(value_list, custom_factor)
            for key, value_list in value_lists.items()
        }
        return normalized_values

    if normalization_method == NORMALIZATION.INTERNAL:
        normalized_values = {}
        for key, value_list in value_lists.items():
            if len(value_list) > 0:
                normalized_values[key] = normalize_by_factor(
                    value_list, np.nanmax(value_list)
                )
            else:
                normalized_values[key] = value_list
        return normalized_values

    if normalization_method == NORMALIZATION.GLOBAL:
        all_values = np.concatenate([v for v in value_lists.values()])
        global_max = np.nanmax(all_values) if len(all_values) > 0 else 1
        if global_max == 0:
            logger.warning("Global max is zero. Normalization will not be applied.")
            return value_lists
        normalized_values = {
            key: normalize_by_factor(value_list, global_max)
            for key, value_list in value_lists.items()
        }
        return normalized_values

    if normalization_method in NORMALIZATION_REFERENCE_POINT:
        if not reference_indices:
            logger.info(
                "No reference indices provided for normalization. Value lists will be returned as is."
            )
            return value_lists

        ref_stats = {
            key: get_reference_statistics(v, reference_indices)
            for key, v in value_lists.items()
        }

        normalized_values = {
            key: reference_normalization(
                value_lists[key], ref_stats[key], normalization_method
            )
            for key in value_lists.keys()
        }

        return normalized_values

    else:
        logger.warning(f"Unsupported normalization method: {normalization_method}")
        return value_lists


def normalize_by_factor(
    values: Union[List[float], float], factor: float
) -> Union[List[float], float]:
    """
    Helper to normalize nested lists by dividing by a factor.
    This function can be used externally.

    Args:
        values: Nested list of values or scalar.
        factor (float): Normalization factor.

    Returns:
        Normalized nested list or scalar.
    """
    if isinstance(values, list):
        return [normalize_by_factor(v, factor) for v in values]
    else:
        return values / factor if factor != 0 else values


def get_reference_statistics(
    value_list: List[float], reference_indices: List[int]
) -> Dict[str, float]:
    """
    Calculate statistics for reference points selected by indices.

    Args:
        value_list (List[float]): The list of values from which to select references.
        reference_indices (List[int]): Indices of reference points.

    Returns:
        Dict[str, float]: Dictionary with statistics like avg, stdev, etc.
    """
    if not reference_indices:
        return {
            "n_reference_points": 0,
            "avg": float("nan"),
            "stdev": float("nan"),
            "median": float("nan"),
            "stdev_percent": float("nan"),
        }

    selected_values = [
        value_list[i]
        for i in reference_indices
        if 0 <= i < len(value_list) and not math.isnan(value_list[i])
    ]

    if not selected_values:
        return {
            "n_reference_points": 0,
            "avg": float("nan"),
            "stdev": float("nan"),
            "median": float("nan"),
            "stdev_percent": float("nan"),
        }

    n_refs = len(selected_values)
    avg = statistics.mean(selected_values)
    stdev = statistics.stdev(selected_values) if len(selected_values) > 1 else 0.0
    median = statistics.median(selected_values)
    stdev_percent = (stdev / avg * 100) if avg != 0 else 0.0

    return {
        "n_reference_points": n_refs,
        "avg": avg,
        "stdev": stdev,
        "median": median,
        "stdev_percent": stdev_percent,
    }


def reference_normalization(
    value_list: List[float],
    ref_stat: Dict[str, float],
    normalization_method: NORMALIZATION,
) -> List[float]:
    """
    Apply reference-based normalization to the value list.

    Args:
        value_list (List[float]): The list of values to normalize.
        ref_stat (Dict[str, float]): Reference statistics.
        normalization_method (NORMALIZATION): The specific reference normalization method.

    Returns:
        List[float]: Normalized value list.
    """
    avg = ref_stat.get("avg", float("nan"))
    stdev = ref_stat.get("stdev", float("nan"))

    if math.isnan(stdev) or math.isnan(avg):
        logger.info("All reference values are NaN. Value list will be set to NaN.")
        return [float("nan") for value in value_list]

    if normalization_method not in NORMALIZATION_REFERENCE_POINT:
        logger.error(
            f"Non-reference value normalization method used: {normalization_method}. Values will be set to NaN."
        )
        return [float("nan") for value in value_list]

    if avg == 0:
        logger.info("Reference value avg is zero. Value list will be set to Zero.")
        return [0.0 for value in value_list]

    if normalization_method not in NORMALIZATION_REFERENCE_POINT:
        logger.error(
            f"Non-reference value normalization method used: {normalization_method}. Values will be set to NaN."
        )
        return [float("nan") for value in value_list]

    if avg == 0:
        logger.warning(
            "Reference value avg is zero. Normalization will not be applied."
        )
        return value_list

    if stdev == 0:
        logger.info("No variation between reference values!")
        return [
            (
                value
                if math.isnan(value)
                else (0.0 if value == avg else (-3.0 if value < avg else 3.0))
            )
            for value in value_list
        ]

    normalized_list = []
    for value in value_list:
        if math.isnan(value):
            normalized_list.append(float("nan"))
            continue

        z = (value - avg) / stdev

        if normalization_method == NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE:
            abs_z = abs(z)
            # [-σ ; σ)
            if abs_z < 1:
                normalized = 0.0
            # [σ ; 2σ) or (-2σ ; -σ]
            elif abs_z < 2:
                normalized = 1.0 if z > 0 else -1.0
            # [2σ ; 3σ) or (-3σ ; -2σ]
            elif abs_z < 3:
                normalized = 2.0 if z > 0 else -2.0
            # [3σ ; ∞) or (-∞ ; -3σ]
            else:
                normalized = 3.0 if z > 0 else -3.0
        elif normalization_method == NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL:
            normalized = max(-3.0, min(3.0, z))
        elif normalization_method == NORMALIZATION.BY_POSITION:
            normalized = value / avg
        else:
            # This case should never apply since we catch it earlier in this method
            normalized = float("nan")

        normalized_list.append(normalized)

    return normalized_list


class ValueExtractor:
    """
    Class for handling attribute selection, value extraction, and normalization with a UI similar to JitterplotSettings.
    """

    def __init__(
        self,
        attributes: Optional[List[DATASET_ATTRIBUTE]] = None,
        normalization_methods: Optional[List[NORMALIZATION]] = None,
        custom_factor: Optional[float] = None,
        references: Optional[List[int]] = None,
        max_reference_index: int = 63,
        show_all_options: bool = False,
    ) -> None:
        """
        Initialize ValueExtractor with optional parameters.

        Args:
            attributes (Optional[DATASET_ATTRIBUTE]): List of enabled attributes
            normalization_methods (Optional[str]): List of enabled normalization methods
            custom_factor (Optional[float]): Initial custom factor.
            references (Optional[List[int]]): Initial references.
            max_reference_index (int): Max index for reference selector.
            show_all_options (bool): Show all options with defaults.
        """
        logger.debug(
            "Initializing ValueExtractor with attributes=%s, normalization_methods=%s, custom_factor=%s, references=%s, show_all_options=%s",
            attributes,
            normalization_methods,
            custom_factor,
            references,
            show_all_options,
        )

        self._attribute_enabled = attributes is not None
        attributes = attributes if self._attribute_enabled else list(DATASET_ATTRIBUTE)
        self._attributes = attributes

        self._normalization_enabled = normalization_methods is not None
        normalization_methods = (
            normalization_methods
            if self._normalization_enabled
            else list(NORMALIZATION)
        )
        self._normalization_methods = normalization_methods

        self._custom_factor_enabled = NORMALIZATION.CUSTOM in normalization_methods
        custom_factor = (
            custom_factor
            if self._custom_factor_enabled and custom_factor is not None
            else ABS_MAX_VALUE
        )
        self._custom_factor = custom_factor

        # Gets enabled if any reference point method is in normalization methods
        self._references_enabled = bool(
            set(NORMALIZATION_REFERENCE_POINT) & set(normalization_methods)
        )
        references = references if self._references_enabled and references else []
        self._references = references

        # None or zero not allowed
        self._max_reference_index = max_reference_index or 10

        self._show_all_options = show_all_options

        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Create the interactive widgets for the ValueExtractor UI.
        """
        options = [field.value for field in self._attributes]

        self._attribute_dropdown = WidgetFactory.dropdown(
            options=options,
            value=options[0],
            description="",
            layout=widgets.Layout(
                height="30px", width="auto", margin="0px", padding="0px"
            ),
        )

        norm_options = [option.value for option in self._normalization_methods]

        self._normalization_dropdown = WidgetFactory.dropdown(
            options=norm_options,
            value=norm_options[0],
            description="",
            layout=widgets.Layout(
                height="30px", width="100%", margin="0px", padding="0px"
            ),
        )

        self._custom_factor_input = WidgetFactory.number_input(
            value=self._custom_factor,
            min_value=1,
            max_value=ABS_MAX_VALUE,
            step=1,
            description="",
            layout=widgets.Layout(
                height="30px",
                min_width="100px",
                width="100px",
                margin="0px",
                padding="0px",
            ),
        )

        self._reference_point_selector = ReferencePointSelector(
            max_index=self._max_reference_index, initial_references=self._references
        )

        # Observer to enable/disable custom input and reference selector
        def on_normalization_change(change: Dict[str, Any]) -> None:
            selected = change["new"]
            selected_normalization_method = NORMALIZATION(selected)
            self._custom_factor_input.disabled = (
                selected_normalization_method != NORMALIZATION.CUSTOM
            )
            self._reference_point_selector.set_disabled(
                selected_normalization_method not in NORMALIZATION_REFERENCE_POINT
            )

        on_normalization_change({"new": self._normalization_dropdown.value})
        self._normalization_dropdown.observe(on_normalization_change, names="value")

    def get_active_widgets(self) -> List[widgets.Widget]:
        """
        Get a list of all interactive widgets for value extractor settings.

        Returns:
            List[widgets.Widget]: A list of all interactive widgets for value extractor settings.
        """
        logger.debug("Collecting all interactive widgets for ValueExtractor")
        active_widgets = []

        if self._attribute_enabled or self._show_all_options:
            active_widgets.append(self._attribute_dropdown)
        if self._normalization_enabled or self._show_all_options:
            active_widgets.append(self._normalization_dropdown)
        if self._custom_factor_enabled or self._show_all_options:
            active_widgets.append(self._custom_factor_input)

        return active_widgets

    @property
    def attribute(self) -> DATASET_ATTRIBUTE:
        """
        The selected attribute.

        Returns:
            DATASET_ATTRIBUTE: The value of the attribute dropdown.
        """
        return DATASET_ATTRIBUTE(self._attribute_dropdown.value)

    def get_attribute_widget(self) -> widgets.Dropdown:
        """
        Get the attribute widget.

        Returns:
            widgets.Dropdown: The attribute dropdown widget.
        """
        return self._attribute_dropdown

    @property
    def normalization(self) -> str:
        """
        The normalization method.

        Returns:
            str: The value of the normalization dropdown.
        """
        return NORMALIZATION(self._normalization_dropdown.value)

    def get_normalization_widget(self) -> widgets.Dropdown:
        """
        Get the normalization widget.

        Returns:
            widgets.Dropdown: The normalization dropdown widget.
        """
        return self._normalization_dropdown

    @property
    def custom_factor(self) -> float:
        """
        The custom factor.

        Returns:
            float: The value of the custom_factor widget.
        """
        return self._custom_factor_input.value

    def get_custom_factor_widget(self) -> widgets.FloatText:
        """
        Get the custom_factor widget.

        Returns:
            widgets.FloatText: The custom_factor number input widget.
        """
        return self._custom_factor_input

    @property
    def references(self) -> List[int]:
        """
        The references.

        Returns:
            List[int]: The list of references from the selector.
        """
        return self._reference_point_selector.references

    def get_reference_selector(self) -> "ReferencePointSelector":
        """
        Get the reference selector.

        Returns:
            ReferencePointSelector: The reference point selector.
        """
        return self._reference_point_selector

    def get_ui(self) -> widgets.Widget:
        """
        Get the UI containing all enabled value extractor settings.

        Returns:
            widgets.Widget: The VBox widget containing all value extractor options.
        """
        logger.debug("Getting UI for ValueExtractor")
        value_widgets = []

        if self._attribute_enabled or self._show_all_options:
            attribute_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Attribute:"),
                    WidgetFactory.vbox(
                        children=[self._attribute_dropdown],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
            )
            value_widgets.append(attribute_container)

        if self._normalization_enabled or self._show_all_options:
            norm_box_children = [self._normalization_dropdown]
            if self._custom_factor_enabled or self._show_all_options:
                norm_box_children += [self._custom_factor_input]

            normalization_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Normalization:"),
                    WidgetFactory.hbox(
                        children=norm_box_children,
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
            )
            value_widgets.append(normalization_container)

        if self._references_enabled or self._show_all_options:
            reference_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.vbox(
                        children=[self._reference_point_selector.get_ui()],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
            )
            value_widgets.append(reference_container)

        return WidgetFactory.vbox(
            children=value_widgets, gap="5px", overflow="visible", height="auto"
        )

    def extract_values(
        self,
        datasets: List[Dataset],
        attribute: Optional[DATASET_ATTRIBUTE] = None,
        normalization_method: Optional[NORMALIZATION] = None,
        custom_factor: Optional[float] = None,
        reference_indices: Optional[List[int]] = None,
    ) -> Dict[Dataset, List[float]]:
        """
        Extract and optionally normalize values from the given datasets.

        Args:
            datasets (List[Dataset]): List of datasets to extract from.
            attribute (Optional[DATASET_ATTRIBUTE]): Attribute to extract (defaults to instance attribute).
            normalization_method (Optional[NORMALIZATION]): Normalization method (defaults to instance normalization).
            custom_factor (Optional[float]): Custom factor for normalization.
            reference_indices (Optional[List[int]]): Reference indices for normalization.

        Returns:
            Dict[Dataset, List[float]]: Extracted and normalized values per dataset.
        """
        if not datasets:
            logger.warning("No datasets were selected for extraction.")
            return {}

        attribute = attribute or self.attribute
        normalization_method = normalization_method or self.normalization
        value_lists = {
            dataset: get_flat_value_list(dataset, attribute) for dataset in datasets
        }
        reference_indices = reference_indices or self.references

        return self.normalize_values(
            value_lists=value_lists,
            normalization_method=normalization_method,
            custom_factor=custom_factor,
            reference_indices=reference_indices,
        )

    def normalize_values(
        self,
        value_lists: Dict[Dataset, List[float]],
        normalization_method: Optional[NORMALIZATION] = None,
        custom_factor: Optional[float] = None,
        reference_indices: Optional[List[int]] = None,
    ) -> Dict[Dataset, List[float]]:
        """
        Normalize the given value lists using the specified normalization method.

        Args:
            value_lists (Dict[Dataset, List[float]]): Dictionary of datasets and their extracted values.
            normalization_method (Optional[NORMALIZATION]): Normalization method (defaults to instance normalization).
            custom_factor (Optional[float]): Custom factor for normalization.
            reference_indices (Optional[List[int]]): Reference indices for normalization.

        Returns:
            Dict[Dataset, List[float]]: Normalized values per dataset.
        """
        if not value_lists:
            logger.warning("No value lists provided for normalization.")
            return {}

        normalization_method = normalization_method or self.normalization

        if normalization_method == NORMALIZATION.RAW:
            return value_lists

        custom_factor = 1.0
        if normalization_method == NORMALIZATION.CUSTOM:
            custom_factor = (
                custom_factor if custom_factor is not None else self.custom_factor
            )

        reference_indices = []
        if normalization_method in NORMALIZATION_REFERENCE_POINT:
            reference_indices = reference_indices or self.references

        normalized_value_lists = apply_normalization(
            value_lists=value_lists,
            normalization_method=normalization_method,
            custom_factor=custom_factor,
            reference_indices=reference_indices,
        )

        return normalized_value_lists


class ReferencePointSelector:
    """
    A widget for entering and managing reference point indices.
    Uses a spinner for selection and tags to display selected points.
    """

    def __init__(
        self, max_index: int = 1000, initial_references: Optional[List[int]] = None
    ) -> None:
        """
        Initializes the reference point widget.

        Args:
            max_index: Maximum allowed index
            initial_references: Initial reference points
        """
        self._max_index = max_index
        self._reference_indices = initial_references or []

        self.create_widgets()
        self.update_reference_container()

    def create_widgets(self) -> None:
        """
        Create the interactive widgets for the ReferencePointSelector.
        """
        self._reference_input = WidgetFactory.int_number_input(
            value=0,
            min_value=0,
            max_value=self._max_index,
            step=1,
            description="",
            width="80px",
            height="30px",
        )

        def on_add_clicked() -> None:
            self._reference_indices.append(self._reference_input.value)
            self._reference_indices = sorted(set(self._reference_indices))
            self.update_reference_container()

        self._add_reference_button = WidgetFactory.button_success(
            description="",
            icon="plus",
            width="50px",
            height="25px",
            on_click=lambda b: on_add_clicked(),
        )

        def on_clear_clicked() -> None:
            self._reference_indices = []
            self.update_reference_container()

        self._clear_references_button = WidgetFactory.button_danger(
            description="Clear all",
            width="100px",
            height="25px",
            on_click=lambda b: on_clear_clicked(),
        )

        # Container for tags
        self._ref_container = WidgetFactory.grid_container(
            children=[],
            width="100%",
            height="100%",
            overflow_y="auto",
            overflow_x="hidden",
        )

    def update_reference_container(self) -> None:
        """
        Update the container displaying the selected reference indices as tags.
        """
        children = []

        def remove_idx(ref_btn: widgets.Button, index: int) -> None:
            self._reference_indices.remove(index)
            self._ref_container.children = [
                child for child in self._ref_container.children if child != ref_btn
            ]

        for reference_idx in self._reference_indices:
            idx_button = WidgetFactory.button_emphasis(
                description=str(reference_idx),
                icon="times",
                width="auto",
                height="30px",
                on_click=lambda b, idx=reference_idx: remove_idx(b, idx),
            )
            children.append(idx_button)

        self._ref_container.children = children

    @property
    def references(self) -> List[int]:
        """
        Get the current list of reference indices.

        Returns:
            List[int]: Copy of the reference indices.
        """
        return self._reference_indices.copy()

    def get_reference_input(self) -> widgets.Widget:
        """
        Get the reference input widget.

        Returns:
            widgets.Widget: The reference input widget.
        """
        return self._reference_input

    def get_add_reference_button(self) -> widgets.Widget:
        """
        Get the add reference button widget.

        Returns:
            widgets.Widget: The add reference button.
        """
        return self._add_reference_button

    def get_clear_references_button(self) -> widgets.Widget:
        """
        Get the clear references button widget.

        Returns:
            widgets.Widget: The clear references button.
        """
        return self._clear_references_button

    def get_ref_container(self) -> widgets.Widget:
        """
        Get the ref container widget.

        Returns:
            widgets.Widget: The ref container widget.
        """
        return self._ref_container

    def get_all_interactive_widgets(self) -> List[widgets.Widget]:
        """
        Get all interactive widgets in the selector.

        Returns:
            List[widgets.Widget]: List of interactive widgets.
        """
        widget_list = [
            self._reference_input,
            self._add_reference_button,
            self._clear_references_button,
        ]
        widget_list += list(self._ref_container.children)

        return widget_list

    def set_disabled(self, disabled: bool) -> None:
        """
        Set the disabled state for all widgets in the selector.

        Args:
            disabled (bool): Whether to disable the widgets.
        """
        widget_list = self.get_all_interactive_widgets()
        for widget in widget_list:
            widget.disabled = disabled

    def get_ui(self) -> widgets.Widget:
        """
        Get the UI widget for the reference point selector.

        Returns:
            widgets.Widget: The VBox containing the UI elements.
        """
        title = WidgetFactory.label(value="Select Reference Indices:")

        input_box = WidgetFactory.hbox(
            children=[self._reference_input, self._add_reference_button], gap="5px"
        )

        controls_box = WidgetFactory.hbox(
            children=[input_box, self._clear_references_button],
            width="100%",
            height="40px",
            layout=widgets.Layout(justify_content="space-between", padding="5px"),
            overflow_y="visible",
        )

        ref_box = WidgetFactory.info_field_default(
            children=[self._ref_container],
            layout=widgets.Layout(width="100%", height="100px", padding="5px"),
        )

        ui_box = WidgetFactory.vbox(
            children=[title, controls_box, ref_box],
            gap="1px",
            width="100%",
            height="auto",
        )
        return ui_box
