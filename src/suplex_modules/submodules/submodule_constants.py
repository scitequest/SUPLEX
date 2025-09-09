"""
Constants and enumerations for SUPLEX submodule components.

This module defines the core enumerations used throughout the SUPLEX submodule
system for dataset selection, labeling, and tag filtering operations.
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DATASET_LABEL(Enum):
    """
    Enumeration for dataset labeling options.

    Defines the different types of information that can be displayed
    in dataset labels within the user interface:
    - Name: Informal name of dataset.
    - ID: Formal identifier of dataset.
    - PROJECT_NAME: Name of associated project.
    - CREATED_DATE: Date the image was generated (typically the same day the assay was conducted).
    - MEASURE_DATE: Date the measurement was taken via MARTin.
    """

    NAME = "Name"
    ID = "ID"
    PROJECT_NAME = "Project"
    CREATED_DATE = "Image Created"
    MEASURE_DATE = "Image Measured"


class DATASET_SELECTOR_MODE(Enum):
    """
    Enumeration for dataset selection modes.

    Defines how many datasets can be selected and the behavior
    when selection limits are reached:
    - SINGLE: Only one dataset can be selected
    - MULTIPLE_UNBOUND: Unlimited multiple selection
    - MULTIPLE_BOUND: Limited multiple selection with queue
    """

    SINGLE = "single"
    MULTIPLE_UNBOUND = "multiple_unbound"
    MULTIPLE_BOUND = "multiple_bound"


class SELECTION_MODE(Enum):
    """
    Defines the logical relationship between selected elements used for filtering datasets

    - ANY: Apply OR logic
    - ALL: Apply AND logic
    """

    ANY = "any"
    ALL = "all"


class DATASET_DESCRIPTOR(Enum):
    NAME = "Dataset Name"
    ID = "Dataset ID"
    PROJECT = "Project Name"


class DATASET_ATTRIBUTE(Enum):
    """
    Enumeration of selectable attributes from datasets.

    Defines the available attributes for extraction from datasets:
    - MEAN_MINUS_MIN: Spot Mean Baseline Adjusted - Difference between the mean value of this spot and the lowest mean value of the entire dataset.
    - NORMALIZED_MEAN: Spot Mean Normalized - The mean_minus_min value of this spot divided by the highest mean_minus_min of the entire dataset.
    - MIN: Spot Min - Signal of the pixel with the lowest intensity within the measurement-ROI.
    - MAX: Spot Max - Signal of the pixel with the highest intensity within the measurement-ROI.
    - MEAN: Spot Mean - Mean signal intensity across all pixels contained within the measurement-ROI.
    - STD_DEV: Spot Standard Deviation - Standard deviation across all pixels contained within the measurement-ROI.
    - ADJUSTED_AVERAGE: Sample Mean Baseline Adjusted - Average across all mean_minus_min values associated with a sample.
    - ADJUSTED_AVERAGE_STD_DEVIATION: Sample Mean Adjusted StdDev - Standard deviation across all mean_minus_min values associated with a sample.
    - RELATIVE_ADJUSTED_AVERAGE_STD_DEVIATION: Sample Mean Adjusted RSD - Adjusted_average_std_deviation divided by adjusted_average in percent.
    - NORMALIZED_AVERAGE: Sample Mean Normalized - Average across all normalized_mean values associated with a sample.
    - NORMALIZED_AVERAGE_STD_DEVIATION: Sample Mean Normalized StdDev - Standard deviation across all normalized_mean values associated with a sample.
    - RELATIVE_NORMALIZED_AVERAGE_STD_DEVIATION: Sample Mean Normalized RSD - Normalized_average_std_deviation divided by normalized_average in percent.
    - SPOT_COORDINATES_X: Spot X-Coordinates - X-coordinates defining the ROI for spot measurements.
    - SPOT_COORDINATES_Y: Spot Y-Coordinates - Y-coordinates defining the ROI for spot measurements.
    - BACKGROUND_RECTANGLES_COORDINATES_X: Background Rectangle X-Coordinates - X-coordinates of background rectangles used for noise subtraction.
    - BACKGROUND_RECTANGLES_COORDINATES_Y: Background Rectangle Y-Coordinates - Y-coordinates of background rectangles used for noise subtraction.
    """

    # Basic Data Values
    MEAN_MINUS_MIN = "Spot Mean Baseline Adjusted"
    NORMALIZED_MEAN = "Spot Mean Normalized"
    MIN = "Spot Min"
    MAX = "Spot Max"
    MEAN = "Spot Mean"
    STD_DEV = "Spot Standard Deviation"

    # Data Statistics Values
    ADJUSTED_AVERAGE = "Sample Mean Baseline Adjusted"
    ADJUSTED_AVERAGE_STD_DEVIATION = "Sample Mean Adjusted StdDev"
    RELATIVE_ADJUSTED_AVERAGE_STD_DEVIATION = "Sample Mean Adjusted RSD"
    NORMALIZED_AVERAGE = "Sample Mean Normalized"
    NORMALIZED_AVERAGE_STD_DEVIATION = "Sample Mean Normalized StdDev"
    RELATIVE_NORMALIZED_AVERAGE_STD_DEVIATION = "Sample Mean Normalized RSD"

    # Parameters
    SPOT_COORDINATES_X = "Spot X-Coordinates"
    SPOT_COORDINATES_Y = "Spot Y-Coordinates"
    BACKGROUND_RECTANGLES_COORDINATES_X = "Background Rectangle X-Coordinates"
    BACKGROUND_RECTANGLES_COORDINATES_Y = "Background Rectangle Y-Coordinates"


# Convenience lists
DATA_ATTRIBUTES = [
    DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
    DATASET_ATTRIBUTE.NORMALIZED_MEAN,
    DATASET_ATTRIBUTE.MIN,
    DATASET_ATTRIBUTE.MAX,
    DATASET_ATTRIBUTE.MEAN,
    DATASET_ATTRIBUTE.STD_DEV,
]
DATA_STATISTICS_ATTRIBUTES = [
    DATASET_ATTRIBUTE.ADJUSTED_AVERAGE,
    DATASET_ATTRIBUTE.ADJUSTED_AVERAGE_STD_DEVIATION,
    DATASET_ATTRIBUTE.RELATIVE_ADJUSTED_AVERAGE_STD_DEVIATION,
    DATASET_ATTRIBUTE.NORMALIZED_AVERAGE,
    DATASET_ATTRIBUTE.NORMALIZED_AVERAGE_STD_DEVIATION,
    DATASET_ATTRIBUTE.RELATIVE_NORMALIZED_AVERAGE_STD_DEVIATION,
]
PARAMETERS_ATTRIBUTES = [
    DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
    DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
    DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_X,
    DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_Y,
]


class SORT_METHOD(Enum):
    """
    Enumeration of available sorting methods for datasets.

    Defines the sorting strategies:
    - UNSORTED: No sorting applied.
    - ALPHANUMERIC_SORT: Sort by dataset string descriptors such as name, id, or project name alphanumerically.
    - AVG_VALUE_SORT: Sort by average values from reference list.
    - MEDIAN_VALUE_SORT: Sort by median values from reference list.
    - MAX_VALUE_SORT: Sort by maximum values from reference list.
    - MIN_VALUE_SORT: Sort by minimum values from reference list.
    - INVERT_ORDER: Option to invert the sorting order.
    """

    UNSORTED = "Unsorted"
    ALPHANUMERIC_SORT = "Alphanumeric"
    HAS_TAG_SORT = "Has Tag"
    AVG_VALUE_SORT = "Average Value"
    MEDIAN_VALUE_SORT = "Median Value"
    MAX_VALUE_SORT = "Maximum Value"
    MIN_VALUE_SORT = "Minimum Value"
    CUMULATIVE_VALUE_SORT = "Cumulative Value"
    NUMBER_OF_VALUES_SORT = "Number of Datapoints"
    INVERT_ORDER = "Invert Order"


class NORMALIZATION(Enum):
    RAW = "RAW"
    INTERNAL = "INTERNAL"
    GLOBAL = "GLOBAL"
    CUSTOM = "CUSTOM"
    BY_POSITION = "BY POSITION"
    BY_POSITION_GAUSSIAN_ABSOLUTE = "GAUSSIAN: ABSOLUTE"
    BY_POSITION_GAUSSIAN_PARTIAL = "GAUSSIAN: PARTIAL"


NORMALIZATION_DEFAULT = [
    NORMALIZATION.RAW,
    NORMALIZATION.INTERNAL,
    NORMALIZATION.GLOBAL,
    NORMALIZATION.CUSTOM,
]

NORMALIZATION_REFERENCE_POINT = [
    NORMALIZATION.BY_POSITION,
    NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE,
    NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL,
]


class FILTER_METHOD(Enum):
    MEAN_MAX_RATIO = "Mean to Max Ratio"
    LOW_VARIANCE = "Variance Below"
    CONTAINS_ABOVE = "Contains Value Above"
    CONTAINS_BELOW = "Contains Value Below"
    AVG_ABOVE = "Average Above"
    AVG_BELOW = "Average Below"
    MAX_ABOVE = "Max Above"
    MAX_BELOW = "Max Below"
    MIN_ABOVE = "Min Above"
    MIN_BELOW = "Min Below"


class THRESHOLD_FILTER_STATE(Enum):
    WITHIN_RANGE = "Within Range"
    BELOW_RANGE = "Below Range"
    ABOVE_RANGE = "Above Range"
    OUTSIDE_RANGE = "Outside Range"

    @classmethod
    def evaluate(cls, comp_val, min_threshold, max_threshold):
        if comp_val < min_threshold:
            return cls.BELOW_RANGE
        elif comp_val > max_threshold:
            return cls.ABOVE_RANGE
        else:
            return cls.WITHIN_RANGE


class COLLAGE_LAYOUT(Enum):
    GRID_EQUAL_ALL = "Grid: cells equally sized"
    GRID_EQUAL_WIDTH = "Grid: equal cell width"
    GRID_EQUAL_HEIGHT = "Grid: equal cell height"
    MOSAIC_EQUAL_ALL = "Mosaic: cells equally sized"
    MOSAIC_EQUAL_WIDTH = "Mosaic: equal cell width"
    MOSAIC_EQUAL_HEIGHT = "Mosaic: equal cell height"


class COLOR(Enum):
    NONE = "none"
    BLACK = "black"
    WHITE = "white"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    GRAY = "gray"


class SCALE_OPTION(Enum):
    NO_SCALE = "Keep original sizes"
    DOWNSCALE_TO_WIDTH = "Downscale to smallest image width"
    UPSCALE_TO_WIDTH = "Upscale to greatest image width"
    DOWNSCALE_TO_HEIGHT = "Downscale to smallest image height"
    UPSCALE_TO_HEIGHT = "Upscale to greatest image height"
    STRETCH_TO_MIN_WIDTH = "Stretch all images to smallest width (ignore ratio)"
    STRETCH_TO_MAX_WIDTH = "Stretch all images to greatest width (ignore ratio)"
    STRETCH_TO_MIN_HEIGHT = "Stretch all images to smallest height (ignore ratio)"
    STRETCH_TO_MAX_HEIGHT = "Stretch all images to greatest height (ignore ratio)"
    STRETCH_TO_MIN_SIZE = "Stretch all images to smallest width & height (ignore ratio)"
    STRETCH_TO_MAX_SIZE = "Stretch all images to greatest width & height (ignore ratio)"


class READING_ORDER(Enum):
    LEFT_RIGHT_TOP_BOTTOM = "left to right -> top to bottom"
    RIGHT_LEFT_TOP_BOTTOM = "right to left -> top to bottom"
    LEFT_RIGHT_BOTTOM_TOP = "left to right -> bottom to top"
    RIGHT_LEFT_BOTTOM_TOP = "right to left -> bottom to top"

    TOP_BOTTOM_LEFT_RIGHT = "top to bottom -> left to right"
    TOP_BOTTOM_RIGHT_LEFT = "top to bottom -> right to left"
    BOTTOM_TOP_LEFT_RIGHT = "bottom to top -> left to right"
    BOTTOM_TOP_RIGHT_LEFT = "bottom to top -> right to left"


class TITLE_POSITION(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    RIGHT = "right"
    LEFT = "left"
    CENTER = "center"
