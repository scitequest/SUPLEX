"""
This submodule contains both functions for dataset filtering as well as a DatasetFilter class which enables storage and provides filtering widgets.
"""
import logging
import ipywidgets as widgets
import numpy as np
import math
from statistics import variance
from typing import Union, List, Optional, Tuple

from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.attribute_selector import AttributeSelector, get_flat_value_list
from suplex_modules.submodules.submodule_constants import DATASET_ATTRIBUTE, DATA_ATTRIBUTES, DATA_STATISTICS_ATTRIBUTES, FILTER_METHOD
from suplex_modules.submodules.settings.submodule_settings_constants import OPTION_INSET
from suplex_modules.submodules.submodule_utils import calculate_step_size, floor_to_n, ceil_to_n

logger = logging.getLogger(__name__)

def has_flat_distribution(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the value set has a flat distribution based on average to max ratio.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the distribution is considered flat (ratio >= threshold).
    """
    logger.debug(f"Checking if value set has flat distribution with threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return True
    
    avg_intensity = np.nanmean(value_set)
    max_intensity = np.nanmax(value_set)

    # Logic does not work for negative numbers.
    if max_intensity <= 0:
        return True
    
    # If average is too high relative to max, consider it as distributed flatly
    ratio = avg_intensity / max_intensity
    result = ratio >= threshold
    logger.debug(f"Flat distribution check result: {result}, ratio: {ratio}")
    return result

def has_low_variance(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the variance of the value set is below the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the variance is below the threshold (low variance).
    """
    logger.debug(f"Checking if value set has low variance with threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return True
    
    var = np.nanvar(value_set)
    result = var < threshold
    logger.debug(f"Low variance check result: {result}, variance: {var}")
    return result

def contains_value_above(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the value set contains any value above the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if any value in the set is above the threshold.
    """
    logger.debug(f"Checking if value set contains value above threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    result = np.any(np.array(value_set) > threshold)
    logger.debug(f"Contains value above check result: {result}")
    return result


def contains_value_below(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the value set contains any value below the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if any value in the set is below the threshold.
    """
    logger.debug(f"Checking if value set contains value below threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    result = np.any(np.array(value_set) < threshold)
    logger.debug(f"Contains value below check result: {result}")
    return result


def is_avg_value_above(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the average value of the set is above the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the average value is above the threshold.
    """
    logger.debug(f"Checking if average value is above threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    avg_value = np.nanmean(value_set)
    result = avg_value > threshold
    logger.debug(f"Average value above check result: {result}, avg: {avg_value}")
    return result


def is_avg_value_below(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the average value of the set is below the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the average value is below the threshold.
    """
    logger.debug(f"Checking if average value is below threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    avg_value = np.nanmean(value_set)
    result = avg_value < threshold
    logger.debug(f"Average value below check result: {result}, avg: {avg_value}")
    return result


def is_max_value_above(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the maximum value of the set is above the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the maximum value is above the threshold.
    """
    logger.debug(f"Checking if max value is above threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    max_value = np.nanmax(value_set)
    result = max_value > threshold
    logger.debug(f"Max value above check result: {result}, max: {max_value}")
    return result


def is_max_value_below(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the maximum value of the set is below the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the maximum value is below the threshold.
    """
    logger.debug(f"Checking if max value is below threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    max_value = np.nanmax(value_set)
    result = max_value < threshold
    logger.debug(f"Max value below check result: {result}, max: {max_value}")
    return result


def is_min_value_above(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the minimum value of the set is above the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the minimum value is above the threshold.
    """
    logger.debug(f"Checking if min value is above threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    min_value = np.nanmin(value_set)
    result = min_value > threshold
    logger.debug(f"Min value above check result: {result}, min: {min_value}")
    return result


def is_min_value_below(value_set: List[Union[int, float]], threshold: Union[int, float]) -> bool:
    """
    Check if the minimum value of the set is below the threshold.
    
    Args:
        value_set (List[Union[int, float]]): List of numeric values to analyze.
        threshold (Union[int, float]): Reference value to compare against.
        
    Returns:
        True if the minimum value is below the threshold.
    """
    logger.debug(f"Checking if min value is below threshold: {threshold}")
    if not value_set or len(value_set) == 0:
        return False
    
    min_value = np.nanmin(value_set)
    result = min_value < threshold
    logger.debug(f"Min value below check result: {result}, min: {min_value}")
    return result

class DatasetFilter:
    """
    Submodule for configuring dataset filters and applying them to datasets.
    
    Provides a simple interface with dropdowns and slider for selecting filter method, attribute, and threshold.
    Analog to AttributeSelector and DatasetSorter.
    """

    def __init__(
        self,
        default_method: FILTER_METHOD = FILTER_METHOD.MEAN_MAX_RATIO,
        default_attribute: DATASET_ATTRIBUTE = DATASET_ATTRIBUTE.MEAN,
        included_attributes: List[DATASET_ATTRIBUTE] = list(DATASET_ATTRIBUTE),
        default_threshold: float = 0.5
    ):
        """
        Initialize the DatasetFilter with default values and widgets.
        
        Args:
            default_method (FILTER_METHOD): Initial filter method to select.
            default_attribute (DATASET_ATTRIBUTE): Initial dataset attribute to select.
            included_attributes (List[DATASET_ATTRIBUTE]): List of dataset attributes to include in the selector.
            default_threshold (float): Initial threshold value for the slider.
        """
        logger.debug("Initializing DatasetFilter")

        self._threshold_slider = WidgetFactory.float_slider(
            value=default_threshold,
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            description="",
            readout=True,
            readout_format=".2f",
            layout=widgets.Layout(width = "100%", padding = "0px 10px"),
            continuous_update=False
        )
        
        options = [method.value for method in FILTER_METHOD]
        self._method_dropdown =  WidgetFactory.dropdown(
            options=options,
            value=default_method.value,
            description="",
            layout = widgets.Layout(width = "100%", padding = "0px 10px 0px 0px")
        )
        
        self._attribute_selector = AttributeSelector()
        self._attribute_dropdown = self._attribute_selector.get_dropdown_widget(
            included_attributes= included_attributes,
            layout = widgets.Layout(width = "100%", padding = "0px 10px 0px 0px") 
        )
        
        self._attribute_dropdown.value = default_attribute.value

        self._invert_checkbox = WidgetFactory.checkbox(
            description="Invert Filter",
            value=False,
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px")
        )
        
        logger.debug("DatasetFilter initialized")
    
    @property
    def method(self) -> FILTER_METHOD:
        return FILTER_METHOD(self._method_dropdown.value)

    @property
    def attribute(self) -> DATASET_ATTRIBUTE:
        return DATASET_ATTRIBUTE(self._attribute_dropdown.value)

    @property
    def threshold(self) -> float:
        return self._threshold_slider.value

    @property
    def invert(self) -> bool:
        return self._invert_checkbox.value

    def get_method_dropdown(self) -> widgets.Dropdown:
        """
        Get the dropdown widget for selecting the filter method.
        
        Returns:
            Dropdown widget for filter methods.
        """
        return self._method_dropdown

    def get_attribute_dropdown(self) -> widgets.Dropdown:
        """
        Get the dropdown widget for selecting the dataset attribute.
        
        Returns:
            Dropdown widget for dataset attributes.
        """
        return self._attribute_dropdown

    def get_threshold_slider(self) -> widgets.FloatSlider:
        """
        Get the slider widget for setting the threshold value.
        
        Returns:
            FloatSlider widget for threshold.
        """
        return self._threshold_slider

    def get_invert_checkbox(self) -> widgets.Checkbox:
        """
        Get the invert filter checkbox widget.
        
        Returns:
            Checkbox widget for inverting the filter.
        """
        return self._invert_checkbox

    def get_ui(self) -> widgets.Widget:
        """
        Build and return the UI widget for the dataset filter.
        
        Returns:
            VBox widget containing the filter UI components.
        """
        logger.debug("Building DatasetFilter UI")
        
        ui_title = WidgetFactory.html_widget(
            value="<h3>Dataset Filter</h3>"
        )
        
        threshold_label = WidgetFactory.label("Threshold") 
        threshold_box = WidgetFactory.vbox(
            children=[self._threshold_slider], 
            layout=widgets.Layout(padding= OPTION_INSET.PRIMARY)
        )
        threshold_box = WidgetFactory.vbox(
            children=[threshold_label, threshold_box], 
            layout=widgets.Layout(padding= OPTION_INSET.PRIMARY)
        )

        attribute_label = WidgetFactory.label("Filter Attribute")
        attribute_box = WidgetFactory.vbox(
            children=[attribute_label, self._attribute_dropdown], 
            layout=widgets.Layout(padding= OPTION_INSET.PRIMARY, width = "100%")
        )
        
        method_label = WidgetFactory.label("Filter Method")
        method_box = WidgetFactory.vbox(
            children=[method_label, self._method_dropdown], 
            layout=widgets.Layout(padding= OPTION_INSET.PRIMARY, width = "100%")
        )
        
        invert_box = WidgetFactory.vbox(
            children=[self._invert_checkbox], 
            layout=widgets.Layout(padding= OPTION_INSET.SECONDARY, width = "100%")
        )
                                    
        ui = WidgetFactory.vbox(
            children=[ui_title, threshold_box, attribute_box, method_box, invert_box],
            layout=widgets.Layout(padding= OPTION_INSET.BASELINE)
        )
        logger.debug("DatasetFilter UI built")
        return ui

    def on_filter_changed(self, datasets: List[Dataset], method: Optional[FILTER_METHOD] = None, attribute: Optional[DATASET_ATTRIBUTE] = None) -> None:
        """
        Update the threshold slider range based on the selected filter method and attribute across datasets.
        
        Args:
            datasets (List[Dataset]): List of datasets to analyze for range calculation.
            method (Optional[FILTER_METHOD]): Optional filter method (uses current widget value if None).
            attribute (Optional[DATASET_ATTRIBUTE]): Optional dataset attribute (uses current widget value if None).
        """
        logger.debug("Updating filter slider range")
        # Uses current widget values as default
        method = method or self.method

        # Min range is always zero
        min_range = 0

        # Max range is adjustable
        max_range = 1
        
        # MEAN_MAX_RATIO is always between 0 and 1, we do not need to extract any values or attributes
        if method == FILTER_METHOD.MEAN_MAX_RATIO:
            self.update_slider_range(min_range = min_range, max_range = max_range)
            return

        attribute = attribute or self.attribute
        
        all_values = [get_flat_value_list(dataset, attribute) for dataset in datasets]
        
        if method == FILTER_METHOD.AVG_ABOVE:
            # Max average value
            avgs = [np.nanmean(sublist) for sublist in all_values if sublist]
            max_range = np.nanmax(avgs) if avgs else 1.0
        elif method == FILTER_METHOD.LOW_VARIANCE:
            # Calculate the variance for each dataset use the max as the slider limit
            variances = [np.nanvar(sublist) for sublist in all_values if len(sublist) > 1]
            max_range = np.nanmax(variances) if variances else 1
        elif all_values:
            # Max value of all values across datasets
            flat_values = [x for sublist in all_values for x in sublist]
            max_range = np.nanmax(flat_values)
        else:
            max_range = 1.0

        if math.isnan(max_range):
            max_range = 1.0
        
        self.update_slider_range(min_range = min_range, max_range = max_range)
        logger.debug(f"Updated slider range: min={min_range}, max={max_range}")

    def update_slider_range(self, min_range: float, max_range: float, max_step: float = 1) -> None:
        logger.debug(f"Updating slider range: min={min_range}, max={max_range}, max_step={max_step}")
        step_size, decimals = calculate_step_size(min_value = min_range, max_value = max_range, max_step = max_step)
        # Values are automatically clamped when changing min and max
        # If statement prevents trait error when min > max_rang or max < min_range
        if self._threshold_slider.min > max_range:
            self._threshold_slider.min = min_range
            self._threshold_slider.max = max_range
        else:
            self._threshold_slider.max = max_range
            self._threshold_slider.min = min_range
        
        self._threshold_slider.step = step_size
        self._threshold_slider.readout_format = f".{decimals}f"
        logger.debug(f"Slider updated: step={step_size}, format={self._threshold_slider.readout_format}")
        
    def get_filtered_datasets(self, 
                         datasets: List[Dataset], 
                         method: Optional[FILTER_METHOD] = None, 
                         attribute: Optional[DATASET_ATTRIBUTE] = None) -> Tuple[List[Dataset], List[Dataset]]:
        """
        Apply the selected filter to the datasets and return included/excluded lists.
        
        Args:
            datasets (List[Dataset]): List of datasets to filter.
            method (Optional[FILTER_METHOD]): Optional filter method (uses current widget value if None).
            attribute (Optional[DATASET_ATTRIBUTE]): Optional dataset attribute (uses current widget value if None).
        
        Returns:
            Tuple of (included datasets, excluded datasets).
        """
        logger.debug("Getting filtered datasets")
        method = method or self.method
        attribute = attribute or self.attribute
            
        if not datasets:
            logger.warning("No datasets to filter")
            return [], []
        
        included = []
        excluded = []
        
        for dataset in datasets:
            values = get_flat_value_list(dataset, attribute)
            if not values:
                excluded.append(dataset)
                continue
            
            keep = False
            if method == FILTER_METHOD.MEAN_MAX_RATIO:
                keep = not has_flat_distribution(values, self.threshold)
            elif method == FILTER_METHOD.LOW_VARIANCE:
                keep = not has_low_variance(values, self.threshold)
            elif method == FILTER_METHOD.CONTAINS_ABOVE:
                keep = contains_value_above(values, self.threshold)
            elif method == FILTER_METHOD.CONTAINS_BELOW:
                keep = contains_value_below(values, self.threshold)
            elif method == FILTER_METHOD.AVG_ABOVE:
                keep = is_avg_value_above(values, self.threshold)
            elif method == FILTER_METHOD.AVG_BELOW:
                keep = is_avg_value_below(values, self.threshold)
            elif method == FILTER_METHOD.MAX_ABOVE:
                keep = is_max_value_above(values, self.threshold)
            elif method == FILTER_METHOD.MAX_BELOW:
                keep = is_max_value_below(values, self.threshold)
            elif method == FILTER_METHOD.MIN_ABOVE:
                keep = is_min_value_above(values, self.threshold)
            elif method == FILTER_METHOD.MIN_BELOW:
                keep = is_min_value_below(values, self.threshold)
            
            if keep:
                included.append(dataset)
            else:
                excluded.append(dataset)
        
        # If invert is selected swaps sets with one another
        if self._invert_checkbox.value:
            included, excluded = excluded, included
            
        logger.info("State of dataset filter: Included %d datasets, excluded %d", len(included), len(excluded))
        return included, excluded