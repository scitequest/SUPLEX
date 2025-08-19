"""
This submodule contains functions for sample and spot-level filtering as well as a SampleSpotFilter 
class which enables storage and provides filtering widgets for hierarchical threshold-based filtering.
"""
import logging
import ipywidgets as widgets
from typing import List, Optional, Dict, Tuple
import numpy as np

from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.attribute_selector import AttributeSelector, extract_value_list_from_dataset, get_flat_value_list
from suplex_modules.submodules.submodule_constants import DATASET_ATTRIBUTE, DATA_ATTRIBUTES, DATA_STATISTICS_ATTRIBUTES, NORMALIZATION, SELECTION_MODE, THRESHOLD_FILTER_STATE
from suplex_modules.submodules.submodule_utils import calculate_step_size
from suplex_modules.submodules.settings.submodule_settings_constants import OPTION_INSET

logger = logging.getLogger(__name__)

def get_sample_threshold_map(
    datasets: List[Dataset], 
    attribute: DATASET_ATTRIBUTE, 
    min_threshold: float, 
    max_threshold: float, 
    normalization_method: NORMALIZATION, 
    normalization_factor: float
) -> Dict[Dataset, List[THRESHOLD_FILTER_STATE]]:
    """
    Generate a threshold map for samples across datasets based on the specified attribute and thresholds.

    This function computes a map indicating whether each sample in the datasets falls within, below, or above
    the given threshold range after normalization.

    Args:
        datasets (List[Dataset]): List of datasets to process.
        attribute (DATASET_ATTRIBUTE): Attribute to use for thresholding.
        min_threshold (float): Minimum threshold value.
        max_threshold (float): Maximum threshold value.
        normalization_method (NORMALIZATION): Method for normalizing the values.
        normalization_factor (float): Factor used for custom normalization.

    Returns:
        Dict[Dataset, List[THRESHOLD_FILTER_STATE]]: Dictionary mapping datasets to lists of filter states for each sample.
    """
    logger.debug(f"Generating sample threshold map for attribute: {attribute}, min_threshold: {min_threshold}, max_threshold: {max_threshold}, normalization: {normalization_method}")

    threshold_map = {} 
    normalization_factors = get_normalization_factors(
        datasets=datasets, 
        attribute=attribute, 
        normalization_method=normalization_method, 
        normalization_factor=normalization_factor
    )
    
    for i, dataset in enumerate(datasets):           
        value_list = extract_value_list_from_dataset(dataset=dataset, attribute=attribute)
        samples_map = []
        
        for stat_value in value_list:
            comp_val = stat_value / normalization_factors[i]
            sample_state = THRESHOLD_FILTER_STATE.evaluate(comp_val, min_threshold, max_threshold)
            samples_map.append(sample_state)
            
        threshold_map[dataset] = samples_map

    logger.debug(f"Generated sample threshold map with {len(threshold_map)} datasets")
    return threshold_map

def get_normalization_factors(
    datasets: List[Dataset], 
    attribute: DATASET_ATTRIBUTE, 
    normalization_method: NORMALIZATION, 
    normalization_factor: float
) -> List[float]:
    """
    Compute normalization factors for datasets based on the specified method.

    This function calculates normalization factors either globally, internally per dataset, custom, or raw (no normalization).

    Args:
        datasets (List[Dataset]): List of datasets to process.
        attribute (DATASET_ATTRIBUTE): Attribute to compute normalization on.
        normalization_method (NORMALIZATION): Method for normalization (RAW, INTERNAL, GLOBAL, CUSTOM).
        normalization_factor (float): Custom factor if normalization_method is CUSTOM.

    Returns:
        List[float]: List of normalization factors, one per dataset.
    """
    logger.debug(f"Computing normalization factors for attribute: {attribute}, method: {normalization_method}, factor: {normalization_factor}")

    normalization_factors = []
    if normalization_method == NORMALIZATION.CUSTOM and normalization_factor == 0:
        logger.warning("Custom normalization factor has been set to zero. No normalization will be conducted.")
        normalization_factor = 1.0
        
    if normalization_method == NORMALIZATION.RAW:
        normalization_factor = 1.0
    
    for dataset in datasets:
        if normalization_method == NORMALIZATION.GLOBAL or normalization_method == NORMALIZATION.INTERNAL:
            value_list = get_flat_value_list(dataset=dataset, attribute=attribute)
            normalization_factor = np.nanmax(value_list) if value_list else 0.0
            if normalization_method == NORMALIZATION.INTERNAL:
                normalization_factor = normalization_factor or 1.0
                
        # else append default value 1.0 for RAW or custom value for CUSTOM
        normalization_factors.append(normalization_factor)

    if normalization_method == NORMALIZATION.GLOBAL:
        normalization_factor = np.nanmax(normalization_factors) or 1.0
        normalization_factors = [normalization_factor] * len(normalization_factors)

    # This does not catch normalization factors of 0 being injected by the CUSTOM option, or RAW if done programmatically.
    logger.debug(f"Computed normalization factors: {normalization_factors}")
    return normalization_factors

def get_spot_threshold_map(
    datasets: List[Dataset],
    attribute: DATASET_ATTRIBUTE,
    min_threshold: float,
    max_threshold: float,
    normalization_method: NORMALIZATION = NORMALIZATION.RAW,
    normalization_factor: float = 1.0
    
) -> Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]:
    """
    Generate a threshold map for spots across datasets based on the specified attribute and thresholds.

    This function computes a nested map indicating whether each spot in each sample falls within, below, or above
    the given threshold range after normalization. Supports data attributes and coordinate attributes.

    Args:
        datasets (List[Dataset]): List of datasets to process.
        attribute (DATASET_ATTRIBUTE): Attribute to use for thresholding (data or coordinates).
        min_threshold (float): Minimum threshold value.
        max_threshold (float): Maximum threshold value.
        normalization_method (NORMALIZATION): Method for normalizing the values (default: NORMALIZATION.RAW).
        normalization_factor (float): Factor used for custom normalization (default: 1.0).

    Returns:
        Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]: Dictionary mapping datasets to lists of lists of filter states for each spot in each sample.
    """
    logger.debug(f"Generating spot threshold map for attribute: {attribute}, min_threshold: {min_threshold}, max_threshold: {max_threshold}, normalization: {normalization_method}")

    normalization_factors = get_normalization_factors(
        datasets=datasets, 
        attribute=attribute, 
        normalization_method=normalization_method, 
        normalization_factor=normalization_factor
    )

    if attribute in DATA_ATTRIBUTES:
        threshold_map = get_spot_data_threshold_map(
            datasets=datasets, 
            attribute=attribute, 
            min_threshold=min_threshold, 
            max_threshold=max_threshold, 
            normalization_factors=normalization_factors
        )
    elif attribute in [DATASET_ATTRIBUTE.SPOT_COORDINATES_X, DATASET_ATTRIBUTE.SPOT_COORDINATES_Y]:
        threshold_map = get_spot_coords_threshold_map(
            datasets=datasets, 
            attribute=attribute, 
            min_threshold=min_threshold, 
            max_threshold=max_threshold, 
            normalization_factors=normalization_factors
        )
    else:
        logger.error(f"Unsupported attribute: {attribute}")
        return {}
    
    logger.debug(f"Generated spot threshold map with {len(threshold_map)} datasets")
    return threshold_map
    
def get_spot_data_threshold_map(
    datasets: List[Dataset], 
    attribute: DATASET_ATTRIBUTE, 
    min_threshold: float, 
    max_threshold: float, 
    normalization_factors: List[float]
) -> Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]:
    """
    Generate a threshold map for spot data attributes across datasets.

    This function computes filter states for spots based on data attributes after normalization.

    Args:
        datasets (List[Dataset]): List of datasets to process.
        attribute (DATASET_ATTRIBUTE): Data attribute to use for thresholding.
        min_threshold (float): Minimum threshold value.
        max_threshold (float): Maximum threshold value.
        normalization_factors (List[float]): Precomputed normalization factors per dataset.

    Returns:
        Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]: Dictionary mapping datasets to lists of lists of filter states for each spot.
    """
    logger.debug(f"Generating spot data threshold map for attribute: {attribute}")

    threshold_map = {}
    
    for i, dataset in enumerate(datasets):           
        value_list = extract_value_list_from_dataset(dataset=dataset, attribute=attribute)
        samples_map = []
        
        for sample in value_list:
            comp_vals = [spot_value / normalization_factors[i] for spot_value in sample]
            spots_map = [THRESHOLD_FILTER_STATE.evaluate(val, min_threshold, max_threshold) for val in comp_vals]
            samples_map.append(spots_map)
                        
        threshold_map[dataset] = samples_map
                
    logger.debug(f"Generated spot data threshold map with {len(threshold_map)} datasets")
    return threshold_map

def get_spot_coords_threshold_map(
    datasets: List[Dataset], 
    attribute: DATASET_ATTRIBUTE, 
    min_threshold: float, 
    max_threshold: float, 
    normalization_factors: List[float]
) -> Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]:
    """
    Generate a threshold map for spot coordinate attributes across datasets.

    This function computes filter states for spots based on average coordinates after normalization.

    Args:
        datasets (List[Dataset]): List of datasets to process.
        attribute (DATASET_ATTRIBUTE): Coordinate attribute (X or Y) to use for thresholding.
        min_threshold (float): Minimum threshold value.
        max_threshold (float): Maximum threshold value.
        normalization_factors (List[float]): Precomputed normalization factors per dataset.

    Returns:
        Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]: Dictionary mapping datasets to lists of lists of filter states for each spot.
    """
    logger.debug(f"Generating spot coords threshold map for attribute: {attribute}")

    threshold_map = {} 
    
    for i, dataset in enumerate(datasets):
        value_list = extract_value_list_from_dataset(dataset=dataset, attribute=attribute)
        samples_map = []
        
        for sample in value_list:
            spot_map = []
            for spot_coords in sample:
                if not spot_coords:
                    # By default within range if we cannot filter by an attribute
                    spot_map.append(THRESHOLD_FILTER_STATE.WITHIN_RANGE)
                    continue
                    
                avg_coord = np.nanmean(spot_coords)
                comp_val = avg_coord / normalization_factors[i]
                threshold_state = THRESHOLD_FILTER_STATE.evaluate(comp_val, min_threshold, max_threshold)
                spot_map.append(threshold_state)
                    
            samples_map.append(spot_map)
                    
        threshold_map[dataset] = samples_map
            
    logger.debug(f"Generated spot coords threshold map with {len(threshold_map)} datasets")
    return threshold_map

def aggregate_filter_states_any(threshold_states: List[THRESHOLD_FILTER_STATE]) -> THRESHOLD_FILTER_STATE:
    """
    Aggregate filter states using 'ANY' logic.

    Returns WITHIN_RANGE if any state is WITHIN_RANGE, otherwise combines BELOW and ABOVE states accordingly.

    Args:
        threshold_states (List[THRESHOLD_FILTER_STATE]): List of filter states to aggregate.

    Returns:
        THRESHOLD_FILTER_STATE: Aggregated filter state.
    """
    if not threshold_states:
        logger.warning(f"ANY: Aggregation list contains no elements. Defaults to WITHIN_RANGE.")
        return THRESHOLD_FILTER_STATE.WITHIN_RANGE
    
    if THRESHOLD_FILTER_STATE.WITHIN_RANGE in threshold_states:
        return THRESHOLD_FILTER_STATE.WITHIN_RANGE

    below = THRESHOLD_FILTER_STATE.BELOW_RANGE in threshold_states
    above = THRESHOLD_FILTER_STATE.ABOVE_RANGE in threshold_states
        
    if below and above:
        return THRESHOLD_FILTER_STATE.OUTSIDE_RANGE
    if below:
        return THRESHOLD_FILTER_STATE.BELOW_RANGE  
    if above:
        return THRESHOLD_FILTER_STATE.ABOVE_RANGE
    if THRESHOLD_FILTER_STATE.OUTSIDE_RANGE in threshold_states:
        return THRESHOLD_FILTER_STATE.OUTSIDE_RANGE

    logger.warning(f"ANY: Aggregation list contains unknown enum: {threshold_states}. Defaults to OUTSIDE_RANGE.")
    return THRESHOLD_FILTER_STATE.OUTSIDE_RANGE

def aggregate_filter_states_all(threshold_states: List[THRESHOLD_FILTER_STATE]) -> THRESHOLD_FILTER_STATE:
    """
    Aggregate filter states using 'ALL' logic.

    Returns WITHIN_RANGE only if all states are WITHIN_RANGE and no outside states, otherwise combines accordingly.

    Args:
        threshold_states (List[THRESHOLD_FILTER_STATE]): List of filter states to aggregate.

    Returns:
        THRESHOLD_FILTER_STATE: Aggregated filter state.
    """
    if not threshold_states:
        logger.warning(f"ANY: Aggregation list contains no elements. Defaults to WITHIN_RANGE.")
        return THRESHOLD_FILTER_STATE.WITHIN_RANGE
    
    below = THRESHOLD_FILTER_STATE.BELOW_RANGE in threshold_states
    above = THRESHOLD_FILTER_STATE.ABOVE_RANGE in threshold_states
    outside = THRESHOLD_FILTER_STATE.OUTSIDE_RANGE in threshold_states

    if THRESHOLD_FILTER_STATE.WITHIN_RANGE in threshold_states and not (below or above or outside):
        return THRESHOLD_FILTER_STATE.WITHIN_RANGE

    if below and above:
        return THRESHOLD_FILTER_STATE.OUTSIDE_RANGE
        
    if below:
        return THRESHOLD_FILTER_STATE.BELOW_RANGE
        
    if above:
        return THRESHOLD_FILTER_STATE.ABOVE_RANGE

    if outside:
        return THRESHOLD_FILTER_STATE.OUTSIDE_RANGE
        
    logger.warning(f"ALL: Aggregation list contains unknown enum: {threshold_states}. Defaults to WITHIN_RANGE.")
    return THRESHOLD_FILTER_STATE.WITHIN_RANGE
    
class SampleSpotFilter:
    """
    This class provides both sample-level and spot-level filtering capabilities with 
    configurable propagation between hierarchical levels. It includes a widget-based UI 
    for interactive parameter adjustment.
    
    The filter supports:
    - Threshold-based filtering on various dataset attributes
    - Multiple normalization methods (RAW, INTERNAL, GLOBAL, CUSTOM)
    - Bidirectional propagation between sample and spot levels
    - Configurable aggregation modes (ANY/ALL) for spot-to-sample propagation
    """
    
    def __init__(
        self,
        included_attributes: List[DATASET_ATTRIBUTE] = None,
        default_attribute: DATASET_ATTRIBUTE = DATASET_ATTRIBUTE.ADJUSTED_AVERAGE,
        included_normalization_methods: List[NORMALIZATION] = None,
        default_normalization_method: NORMALIZATION = NORMALIZATION.RAW,
        default_custom_normalization: float = 1.0,
        default_abs_max: float = 2**16 - 1
    ):
        """
        Initialize the SampleSpotFilter with configurable defaults.
        
        Args:
            included_attributes (List[DATASET_ATTRIBUTE]): List of attributes available for filtering. 
                Defaults to DATA_ATTRIBUTES + DATA_STATISTICS_ATTRIBUTES.
            default_attribute (DATASET_ATTRIBUTE): Default attribute selection.
            included_normalization_methods (List[NORMALIZATION]): List of normalization methods to include. 
                Defaults to all NORMALIZATION enum values.
            default_normalization_method (NORMALIZATION): Default normalization method.
            default_custom_normalization (float): Default value for custom normalization.
            default_abs_max (float): Default maximum value for sliders and inputs.
        """
        logger.debug("Initializing SampleSpotFilter")
        if included_attributes is None:
            included_attributes = DATA_ATTRIBUTES + DATA_STATISTICS_ATTRIBUTES
        if included_normalization_methods is None:
            included_normalization_methods = list(NORMALIZATION)
            
        logger.debug("Initializing SampleSpotFilter")

        self._threshold_range_slider = WidgetFactory.float_range_slider(
            value=[0, default_abs_max],
            min_value=0.0,
            max_value=default_abs_max,
            step=1,
            description="",
            readout=True,
            readout_format=".0f",
            continuous_update=False,
            layout=widgets.Layout(width = "100%", padding = "0px 10px")
        )
        
        self._attribute_selector = AttributeSelector()
        self._attribute_dropdown = self._attribute_selector.get_dropdown_widget(
            included_attributes=included_attributes,
            layout = widgets.Layout(width = "100%", padding = "0px 10px 0px 0px")
        )
        self._attribute_dropdown.value = default_attribute.value

        def on_normalization_method_changed():
            self._normalization_factor_input.disabled = NORMALIZATION(self._normalization_dropdown.value) != NORMALIZATION.CUSTOM
            
        self._normalization_dropdown = WidgetFactory.dropdown(
            options=included_normalization_methods,
            value=default_normalization_method,
            description="",
            on_change=lambda b: on_normalization_method_changed(),
            layout = widgets.Layout(width = "100%")
        )
        
        custom_normalization_is_default = default_normalization_method == NORMALIZATION.CUSTOM
        normalization_factor_input_val = default_custom_normalization if custom_normalization_is_default else 1
        
        self._normalization_factor_input = WidgetFactory.number_input(
            value=normalization_factor_input_val,
            min_value=1,
            max_value=default_abs_max,
            step=1,
            description="",
            disabled=not custom_normalization_is_default,
            layout = widgets.Layout(width = "100%")
        )

        self._invert_checkbox = WidgetFactory.checkbox(
            value=False,
            description="Invert Filter",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px")
        )

        def on_spots_affect_sample_checkbox_changed():
            self._sample_filter_mode_dropdown.disabled = not self._spots_affect_sample_checkbox.value
            
        self._sample_affects_spots_checkbox = WidgetFactory.checkbox(
            value=False,
            description="Sample Filtering Affects Spots",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px")
        )
        self._spots_affect_sample_checkbox = WidgetFactory.checkbox(
            value=False,
            description="Spot Filtering Affects Samples",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            on_change=lambda b: on_spots_affect_sample_checkbox_changed()
        )
        
        self._sample_filter_mode_dropdown = WidgetFactory.dropdown(
            options=[mode.value for mode in SELECTION_MODE],
            value=SELECTION_MODE.ALL.value,
            description="",
            width = "100px"
        )
        
        logger.debug("SampleSpotFilter initialized")

    @property
    def attribute(self) -> DATASET_ATTRIBUTE:
        """Get the currently selected filter attribute."""
        return DATASET_ATTRIBUTE(self._attribute_dropdown.value)

    @property
    def normalization_method(self) -> NORMALIZATION:
        """Get the currently selected normalization method."""
        return NORMALIZATION(self._normalization_dropdown.value)

    @property
    def normalization_factor(self) -> float:
        """Get the current custom normalization factor value."""
        return self._normalization_factor_input.value

    @property
    def min_threshold(self) -> float:
        """Get the current minimum threshold value."""
        return self._threshold_range_slider.value[0]

    @property
    def max_threshold(self) -> float:
        """Get the current maximum threshold value."""
        return self._threshold_range_slider.value[1]

    @property
    def invert(self) -> bool:
        """Get the current invert filter setting."""
        return self._invert_checkbox.value
        
    @property
    def sample_affects_spots(self) -> bool:
        """Get whether sample-level filtering should propagate to spots."""
        return self._sample_affects_spots_checkbox.value

    @property
    def spots_affect_sample(self) -> bool:
        """Get whether spot-level filtering should propagate to samples."""
        return self._spots_affect_sample_checkbox.value

    @property
    def sample_filter_mode(self) -> SELECTION_MODE:
        """Get the current mode for spot-to-sample aggregation (ANY/ALL)."""
        return SELECTION_MODE(self._sample_filter_mode_dropdown.value)

    def get_attribute_dropdown(self) -> widgets.Dropdown:
        """Get the attribute selection dropdown widget."""
        return self._attribute_dropdown

    def get_normalization_dropdown(self) -> widgets.Dropdown:
        """Get the normalization method dropdown widget."""
        return self._normalization_dropdown

    def get_normalization_factor_input(self) -> widgets.BoundedFloatText:
        """Get the custom normalization factor input widget."""
        return self._normalization_factor_input
        
    def get_threshold_range_slider(self) -> widgets.FloatRangeSlider:
        """Get the threshold range slider widget."""
        return self._threshold_range_slider

    def get_invert_checkbox(self) -> widgets.Checkbox:
        """Get the invert filter checkbox widget."""
        return self._invert_checkbox

    def get_sample_affects_spots_checkbox(self) -> widgets.Checkbox:
        """Get the sample affects spots checkbox widget."""
        return self._sample_affects_spots_checkbox

    def get_spots_affect_sample_checkbox(self) -> widgets.Checkbox:
        """Get the spots affect sample checkbox widget."""
        return self._spots_affect_sample_checkbox

    def get_sample_filter_mode_dropdown(self) -> widgets.Dropdown:
        """Get the sample filter mode dropdown widget."""
        return self._sample_filter_mode_dropdown

    def get_default_sample_map(self, datasets: List[Dataset]) -> Dict[Dataset, List[THRESHOLD_FILTER_STATE]]:
        """
        Generates a default sample map for the provided datasets.
    
        This method creates a dictionary where each key is a Dataset object, and the value is a list
        of boolean values (all True) corresponding to each sample in that dataset. This can be used
        as a default inclusion map, indicating that all samples are included.
    
        Args:
            datasets (List[Dataset]): A list of Dataset objects.
    
        Returns:
            Dict[Dataset, List[THRESHOLD_FILTER_STATE]]: A dictionary mapping each Dataset to a list of booleans for its samples.
        """
        logger.debug("Generating default sample map")
        default_map = {dataset: [THRESHOLD_FILTER_STATE.WITHIN_RANGE for _ in dataset.samples] for dataset in datasets}
        logger.debug(f"Generated default sample map with {len(default_map)} datasets")
        return default_map
    
    def get_default_spot_map(self, datasets: List[Dataset]) -> Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]:
        """
        Generates a default spot map for the provided datasets.
    
        This method creates a dictionary where each key is a Dataset object, and the value is a list
        of lists of boolean values (all True). The outer list corresponds to each sample in the dataset,
        and the inner lists correspond to each spot in that sample. This can be used as a default
        inclusion map, indicating that all spots in all samples are included.
    
        Args:
            datasets (List[Dataset]): A list of Dataset objects.
    
        Returns:
            Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]: A dictionary mapping each Dataset to a list of lists of booleans for its samples' spots.
        """
        logger.debug("Generating default spot map")
        default_map = {dataset: [[THRESHOLD_FILTER_STATE.WITHIN_RANGE for _ in sample.spots] for sample in dataset.samples] for dataset in datasets}
        logger.debug(f"Generated default spot map with {len(default_map)} datasets")
        return default_map

    def set_disabled_all_widgets(self, disabled: bool) -> None:
        """
        Convenience method to quickly enable or disable all widgets.

        Args:
            disabled (bool): New state of disabled for all widgets.
        """
        logger.debug(f"Setting all widgets disabled: {disabled}")
        self._threshold_range_slider.disabled = disabled
        self._attribute_selector.disabled = disabled
        self._attribute_dropdown.disabled = disabled
        self._normalization_dropdown.disabled = disabled
        self._normalization_factor_input.disabled = disabled
        self._invert_checkbox.disabled = disabled
        self._sample_affects_spots_checkbox.disabled = disabled
        self._spots_affect_sample_checkbox.disabled = disabled
        self._sample_filter_mode_dropdown.disabled = disabled

    def is_flag_in_selected_range(self, flag: THRESHOLD_FILTER_STATE, invert: Optional[bool] = None) -> bool:
        """
        Determine if a filter state flag is considered selected based on the range and optional inversion.

        Args:
            flag (THRESHOLD_FILTER_STATE): The filter state to check.
            invert (Optional[bool]): Whether to invert the selection logic (uses self.invert if None).

        Returns:
            bool: True if the flag is in the selected range (considering inversion), False otherwise.
        """
        if invert is None:
            invert = self.invert

        if flag == THRESHOLD_FILTER_STATE.WITHIN_RANGE:
            return True ^ invert
        elif flag in [THRESHOLD_FILTER_STATE.BELOW_RANGE, THRESHOLD_FILTER_STATE.ABOVE_RANGE, THRESHOLD_FILTER_STATE.OUTSIDE_RANGE]:
            return False ^ invert
        else:
            logger.warning(f"Invalid flag {flag} was used. Return default value True.")
            return True

    def extract_filtered_values_from_datasets(
        self,
        datasets: List[Dataset],
        attribute: DATASET_ATTRIBUTE,
        sample_threshold_map: Optional[Dict[Dataset, List[THRESHOLD_FILTER_STATE]]] = None,
        spot_threshold_map: Optional[Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]] = None, 
        below_replacement_value: Optional[float] = None,
        above_replacement_value: Optional[float] = None,
        outside_replacement_value: Optional[float] = None,
        invert: Optional[bool] = None
    ) -> Dict[Dataset, List[float]]:
        """
        This method processes a list of datasets to extract values for a given attribute, 
        applying filters based on threshold maps for samples or spots. 
        It optionally replaces values that fall outside specified ranges and normalizes the extracted values according to the chosen method. 
        The filtering can be inverted, and default threshold maps are used if none are provided.
        
        Args:
            datasets (List[Dataset]): A list of Dataset objects to process.
            attribute (DATASET_ATTRIBUTE): The attribute to extract values for, which can be at the sample or spot level.
            sample_threshold_map (Optional[Dict[Dataset, List[THRESHOLD_FILTER_STATE]]], optional): A dictionary mapping datasets to lists of threshold filter states for each sample. Defaults to None, in which case a default map is used.
            spot_threshold_map (Optional[Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]], optional): A dictionary mapping datasets to get_default_sample_maplists of lists of threshold filter states for each spot in each sample. Defaults to None, in which case a default map is used.
            below_replacement_value (Optional[float], optional): Value to replace entries below the threshold range. Defaults to None (skips replacement).
            above_replacement_value (Optional[float], optional): Value to replace entries above the threshold range. Defaults to None (skips replacement).
            outside_replacement_value (Optional[float], optional): Value to replace entries outside the threshold range (within or outside). Defaults to None (skips replacement).
            invert (Optional[bool], optional): If True, inverts the filter selection logic. Defaults to None.
        
        Returns:
            Dict[Dataset, List[float]]: A dictionary mapping each Dataset to a list of extracted and filtered float values.
        """
        
        logger.debug("Extracting values for attribute %s", attribute)
        try:
            sample_threshold_map = sample_threshold_map or self.get_default_sample_map(datasets = datasets)
            spot_threshold_map = spot_threshold_map or self.get_default_spot_map(datasets = datasets)
            if outside_replacement_value is None:
                # By default we use the below value for unspecific replacements if its available else we use above_replacement_value
                outside_replacement_value = below_replacement_value if below_replacement_value is not None else above_replacement_value
            else:
                below_replacement_value = below_replacement_value if below_replacement_value is not None else outside_replacement_value
                above_replacement_value = above_replacement_value if above_replacement_value is not None else outside_replacement_value

                
            value_dict = {}
            for dataset in datasets:
                dataset_value_list = extract_value_list_from_dataset(dataset, attribute)
                dataset_values = []
                for i, sample in enumerate(dataset.samples):
                    if attribute in DATA_STATISTICS_ATTRIBUTES:
                        flag = sample_threshold_map[dataset][i]
                        if self.is_flag_in_selected_range(flag, invert):
                            dataset_values.append(dataset_value_list[i])
                        # Conditional short circuts
                        elif flag in [THRESHOLD_FILTER_STATE.WITHIN_RANGE, THRESHOLD_FILTER_STATE.OUTSIDE_RANGE]:
                            outside_replacement_value is not None and dataset_values.append(outside_replacement_value)     
                        elif flag == THRESHOLD_FILTER_STATE.ABOVE_RANGE:
                            above_replacement_value is not None and dataset_values.append(above_replacement_value)
                        elif flag == THRESHOLD_FILTER_STATE.BELOW_RANGE:
                            below_replacement_value is not None and dataset_values.append(below_replacement_value)

                    else: # Attribute is on spot level
                        for j, spot in enumerate(sample.spots):
                            flag = spot_threshold_map[dataset][i][j]
                            if self.is_flag_in_selected_range(flag, invert):
                                spot_values = dataset_value_list[i][j]
                                if attribute in [DATASET_ATTRIBUTE.SPOT_COORDINATES_X, DATASET_ATTRIBUTE.SPOT_COORDINATES_Y]:
                                    # Use average X/Y Coordinate to flatten list
                                    avg_value = np.nanmean(spot_values) if spot_values else np.nan
                                    dataset_values.append(avg_value)
                                else:
                                    dataset_values.append(spot_values)
                            elif flag in [THRESHOLD_FILTER_STATE.WITHIN_RANGE, THRESHOLD_FILTER_STATE.OUTSIDE_RANGE]:
                                outside_replacement_value is not None and dataset_values.append(outside_replacement_value)     
                            elif flag == THRESHOLD_FILTER_STATE.ABOVE_RANGE:
                                above_replacement_value is not None and dataset_values.append(above_replacement_value)
                            elif flag == THRESHOLD_FILTER_STATE.BELOW_RANGE:
                                below_replacement_value is not None and dataset_values.append(below_replacement_value)
                                
                    value_dict[dataset] = dataset_values
                
            logger.debug(f"Extracted filtered values for {len(value_dict)} datasets")
            return value_dict
        except Exception as e:
            logger.error("Failed to extract values: %s", e, exc_info=True)
            return {}
        
    def get_ui(self) -> widgets.Widget:
        """
        Build and return a formatted VBox containing all filter widgets.
        
        Returns:
            widgets.Widget: Widget containing the complete filter UI with threshold controls,
            attribute selection, normalization options, and propagation settings.
        """
        logger.debug("Building SampleSpotFilter UI")
        
        ui_title = WidgetFactory.html_widget(
            value="<h3>Sample & Spot Filter</h3>"
        )
        
        threshold_label = WidgetFactory.label("Threshold")
        threshold_box = WidgetFactory.vbox(
            children=[self._threshold_range_slider],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        threshold_box = WidgetFactory.vbox(
            children=[threshold_label, threshold_box],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        
        attribute_label = WidgetFactory.label("Attribute")
        attribute_dropdown_box = WidgetFactory.vbox(
            children=[self._attribute_dropdown],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        attribute_box = WidgetFactory.vbox(
            children=[attribute_label, attribute_dropdown_box],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        
        normalization_label = WidgetFactory.label("Normalization Method")
        factor_input_box = WidgetFactory.vbox(
            children = [self._normalization_factor_input],
            layout=widgets.Layout(width = "100%", padding = "0px 10px 0px 0px")
            )                              
        normalization_dropdown_box = WidgetFactory.hbox(
            children=[self._normalization_dropdown, factor_input_box],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        normalization_box = WidgetFactory.vbox(
            children=[normalization_label, normalization_dropdown_box],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )

        invert_checkbox_box = WidgetFactory.vbox(
            children=[self._invert_checkbox],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.SECONDARY)
        )

        propagation_label = WidgetFactory.label("Filter Propagation")
        
        propagation_checkbox_box = WidgetFactory.vbox(
            children=[self._sample_affects_spots_checkbox, self._spots_affect_sample_checkbox],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        propagation_mode_label_prefix = WidgetFactory.html_widget(value = "Keep Sample if", width = "100px")
        propagation_mode_label_suffix = WidgetFactory.html_widget(value = " Spots are viable", width = "100px")
        
        propagation_dropdown_box = WidgetFactory.hbox(
            children=[propagation_mode_label_prefix, self._sample_filter_mode_dropdown, propagation_mode_label_suffix],
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY, justify_content="flex-start"),
            gap="5px"
        )
        
        propagation_box = WidgetFactory.vbox(
            children=[propagation_label, propagation_checkbox_box, propagation_dropdown_box],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.PRIMARY)
        )
        
        ui = WidgetFactory.vbox(
            children=[ui_title, threshold_box, attribute_box, normalization_box, invert_checkbox_box, propagation_box],
            layout=widgets.Layout(gap="5px", padding=OPTION_INSET.BASELINE)
        )
        logger.debug("SampleSpotFilter UI built")
        return ui

    def on_filter_params_changed(
        self, 
        datasets: List[Dataset], 
        attribute: Optional[DATASET_ATTRIBUTE] = None, 
        normalization_method: Optional[NORMALIZATION] = None, 
        normalization_factor: Optional[float] = None
    ) -> None:
        """
        Update the threshold slider based on changed filter parameters.

        Recalculates the min, max, and step of the threshold slider based on the normalized value range across datasets.

        Args:
            datasets (List[Dataset]): List of datasets to compute ranges from.
            attribute (Optional[DATASET_ATTRIBUTE]): Attribute to use (uses widget value if None).
            normalization_method (Optional[NORMALIZATION]): Normalization method (uses widget value if None).
            normalization_factor (Optional[float]): Normalization factor (uses widget value if None).
        """
        logger.debug("Updating filter params")
        if not datasets:
            logger.debug("No datasets to be filtered")
            return
            
        attribute = attribute or self.attribute
        
        normalization_method = normalization_method or self.normalization_method
        normalization_factor = normalization_factor
        if normalization_factor is None:
            normalization_factor = self._normalization_factor_input.value
        normalization_factors = get_normalization_factors(
            datasets=datasets, 
            attribute=attribute, 
            normalization_method=normalization_method, 
            normalization_factor=normalization_factor
        )

        all_values_flat_normalized = []
        for i, dataset in enumerate(datasets):
            values = get_flat_value_list(dataset=dataset, attribute=attribute)
            if attribute in [DATASET_ATTRIBUTE.SPOT_COORDINATES_X, DATASET_ATTRIBUTE.SPOT_COORDINATES_Y]:
                value_list = extract_value_list_from_dataset(dataset, attribute)
                avgs = [np.nanmean(spot) for sample in value_list for spot in sample if spot]
                all_values_flat_normalized += [avg / normalization_factors[i] for avg in avgs]
            else:
                all_values_flat_normalized += [value / normalization_factors[i] for value in values]
            
        max_range = np.nanmax(all_values_flat_normalized)
        min_range = np.nanmin(all_values_flat_normalized)
        step_size, decimals = calculate_step_size(min_value=min_range, max_value=max_range)

        # Values are automatically clamped when changing min and max
        # If statement prevents trait error when min > max_range or max < min_range
        
        if self._threshold_range_slider.min > max_range:
            self._threshold_range_slider.min = min_range
            self._threshold_range_slider.max = max_range
        else:
            self._threshold_range_slider.max = max_range
            self._threshold_range_slider.min = min_range
            
        self._threshold_range_slider.step = step_size
        self._threshold_range_slider.readout_format = f".{decimals}f"
        
        self._threshold_range_slider.value = [min_range, max_range]
        logger.debug(f"Updated threshold slider: min={min_range}, max={max_range}, step={step_size}")
    
    def get_filter_maps(self, 
                       datasets: List[Dataset], 
                       attribute: Optional[DATASET_ATTRIBUTE] = None, 
                       min_threshold: Optional[float] = None, 
                       max_threshold: Optional[float] = None, 
                       normalization_method: Optional[NORMALIZATION] = None, 
                       normalization_factor: Optional[float] = None, 
                       spots_affect_sample: Optional[bool] = None, 
                       sample_affects_spots: Optional[bool] = None, 
                       sample_filter_mode: Optional[SELECTION_MODE] = None
                      ) -> Tuple[Dict[Dataset, List[THRESHOLD_FILTER_STATE]], Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]]:
        """
        Generate threshold-based filter maps for datasets at both sample and spot levels.
        
        This method creates boolean filter maps that can be used to include/exclude samples 
        and spots based on specified attribute thresholds. The filtering can operate at 
        different hierarchical levels with configurable interaction between sample-level 
        and spot-level filters.
        
        Args:
            datasets (List[Dataset]): List of datasets to process.
            attribute (Optional[DATASET_ATTRIBUTE]): Attribute to filter on (uses widget value if None).
            min_threshold (Optional[float]): Minimum threshold value for filtering (uses widget value if None).
            max_threshold (Optional[float]): Maximum threshold value for filtering (uses widget value if None).
            normalization_method (Optional[NORMALIZATION]): Method for data normalization (uses widget value if None).
            normalization_factor (Optional[float]): Factor for normalization (uses widget value if None).
            spots_affect_sample (Optional[bool]): Whether spot-level filtering should influence 
                sample-level decisions (uses widget value if None).
            sample_affects_spots (Optional[bool]): Whether sample-level filtering should propagate 
                to spot-level decisions (uses widget value if None).
            sample_filter_mode (Optional[SELECTION_MODE]): Mode for aggregating spot decisions to sample level 
                (ANY/ALL) (uses widget value if None).
        
        Returns:
            Tuple[Dict[Dataset, List[THRESHOLD_FILTER_STATE]], Dict[Dataset, List[List[THRESHOLD_FILTER_STATE]]]]: A tuple containing:
            - sample_threshold_map: Dictionary mapping datasets to lists of boolean 
              flags for each sample (True = include sample)
            - spot_threshold_map: Dictionary mapping datasets to lists of lists of 
              boolean flags for each spot in each sample (True = include spot)
            By default these dictionaries are filled with True values for each sample and spot.
            If filtering occurs they may be set to False.
            
        Note:
            When both spots_affect_sample and sample_affects_spots are True, the 
            filtering process applies spot -> sample aggregation first, then sample -> spot 
            propagation. This allows spots to affect other spots of the same sample.
        """
        logger.debug("Generating filter maps")
        attribute = attribute or self.attribute
        normalization_method = normalization_method or self.normalization_method
        sample_filter_mode = sample_filter_mode or self.sample_filter_mode
        
        min_threshold = min_threshold if min_threshold is not None else self.min_threshold
        max_threshold = max_threshold if max_threshold is not None else self.max_threshold
        normalization_factor = normalization_factor if normalization_factor is not None else self.normalization_factor
        sample_affects_spots = sample_affects_spots if sample_affects_spots is not None else self.sample_affects_spots
        spots_affect_sample = spots_affect_sample if spots_affect_sample is not None else self.spots_affect_sample

        if attribute in DATA_STATISTICS_ATTRIBUTES:
            sample_threshold_map = get_sample_threshold_map(
                datasets=datasets,
                attribute=attribute,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
                normalization_method=normalization_method,
                normalization_factor=normalization_factor
            )
        else:
            sample_threshold_map = self.get_default_sample_map(datasets)
        
        spot_attributes = DATA_ATTRIBUTES + [DATASET_ATTRIBUTE.SPOT_COORDINATES_X, DATASET_ATTRIBUTE.SPOT_COORDINATES_Y]
        if attribute in spot_attributes:
            spot_threshold_map = get_spot_threshold_map(
                datasets=datasets,
                attribute=attribute,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
                normalization_method=normalization_method,
                normalization_factor=normalization_factor
            )         
        else:
            # Default spot map filled with true statements
            spot_threshold_map = self.get_default_spot_map(datasets = datasets)

        # Spot attributes first so spots can affect other spots of the same sample if both spots_affect_sample and sample_affects_spots is true
        if attribute in spot_attributes and spots_affect_sample:
            if sample_filter_mode == SELECTION_MODE.ANY:
                sample_threshold_map = {dataset: [aggregate_filter_states_any(sample_spots) for sample_spots in samples] for dataset, samples in spot_threshold_map.items()}
            elif sample_filter_mode == SELECTION_MODE.ALL:
                sample_threshold_map = {dataset: [aggregate_filter_states_all(sample_spots) for sample_spots in samples] for dataset, samples in spot_threshold_map.items()}

        if (attribute in DATA_STATISTICS_ATTRIBUTES and sample_affects_spots) or (spots_affect_sample and sample_affects_spots):
            spot_threshold_map = {
                dataset: [[sample_flag for _ in sample.spots] for sample_flag, sample in zip(sample_flags, dataset.samples)] for dataset, sample_flags in sample_threshold_map.items()
            }

        logger.debug(f"Generated filter maps with {len(sample_threshold_map)} datasets")
        return sample_threshold_map, spot_threshold_map