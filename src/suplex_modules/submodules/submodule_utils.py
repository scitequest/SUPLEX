import math
import logging
from typing import Dict, List

from suplex_modules.submodules.submodule_constants import NORMALIZATION
from martin_interface.dataset import Dataset

logger = logging.getLogger(__name__)


def calculate_step_size(
    min_value: float, max_value: float, max_step: float = 1.0
) -> tuple[float, int]:
    """
    Calculates the step size for a slider such that there are at least 100 steps between min_value and max_value.

    The step size is chosen as a power of ten (10^e), selecting the largest possible value that meets the minimum step count.
    For an invalid range (delta <= 0), an error is logged and (1.0, 0) is returned.
    Decimals are clamped to >=0 for valid readout formats.
    The step size is capped at max_step (default 1.0), with exponent/decimals recalculated accordingly.

    Args:
        min_value (float): The minimum value of the range.
        max_value (float): The maximum value of the range.
        max_step (float): Maximum allowed step size (default 1.0).

    Returns:
        tuple[float, int]: The calculated step size and the number of decimals (e.g., (1, 0), (0.1, 1), (0.01, 2), etc.).
    """
    logger.debug(
        "Calculating step size for range: min=%f, max=%f, max_step=%f",
        min_value,
        max_value,
        max_step,
    )
    delta = max_value - min_value
    if delta <= 0:
        logger.error("Illegal range was selected min %f, max %f", min_value, max_value)
        return 1.0, 0

    # Target step for at least 100 steps
    target_step = delta / 100

    # Avoid log of very small numbers
    if target_step <= 0:
        return 1.0, 0
    if target_step < 1e-12:
        return 1e-12, 12

    exponent = math.floor(math.log10(target_step))
    step_size = 10**exponent

    if step_size > max_step:
        step_size = max_step
        # Recalculate exponent based on capped step (handle step_size <=0, but shouldn't happen)
        if step_size > 0:
            exponent = math.floor(math.log10(step_size))
        else:
            exponent = 0

    decimals = max(0, -int(exponent))
    logger.debug("Calculated step_size=%f, decimals=%d", step_size, decimals)
    return step_size, decimals


def floor_to_n(x, n):
    logger.debug("Flooring %f to %d decimals", x, n)
    factor = 10**n
    result = math.floor(x * factor) / factor
    logger.debug("Result: %f", result)
    return result


def ceil_to_n(x, n):
    logger.debug("Ceiling %f to %d decimals", x, n)
    factor = 10**n
    result = math.ceil(x * factor) / factor
    logger.debug("Result: %f", result)
    return result


def apply_normalization(
    value_sets: Dict[Dataset, List[float]],
    normalization_method: NORMALIZATION = NORMALIZATION.RAW,
    normalization_factor: float = 1.0,
) -> Dict[Dataset, List[float]]:
    """
    This method applies normalization to a dictionary of value sets extracted from datasets,
    based on the specified normalization method.
    It supports raw (no normalization), global (normalize by the maximum value across all datasets),
    internal (normalize by the maximum value within each dataset), and custom (normalize by a provided factor) methods.

    Non-finite values are excluded from maximum calculations to ensure valid normalization factors,
    and division by zero is prevented by defaulting to a factor of 1 when necessary.

    Args:
        value_sets (Dict[Dataset, List[float]]): A dictionary mapping each Dataset to a list of float values to be normalized.
        normalization_method (NORMALIZATION): The normalization method to apply, which can be RAW (no normalization), GLOBAL, INTERNAL, or CUSTOM.
        normalization_factor (float): The custom normalization factor to use when the method is CUSTOM; otherwise, it may be computed based on the method.

    Returns:
        Dict[Dataset, List[float]]: A dictionary mapping each Dataset to a list of normalized float values.
    """
    logger.debug(
        "Applying normalization: method=%s, initial_factor=%f, num_datasets=%d",
        normalization_method.value,
        normalization_factor,
        len(value_sets),
    )
    if normalization_method == NORMALIZATION.RAW or not value_sets:
        logger.debug("Skipping normalization (RAW or empty sets)")
        return value_sets

    # If NORMALIZATION.CUSTOM we just use the given normalization_factor

    if normalization_method == NORMALIZATION.GLOBAL:
        all_items = [
            item
            for sublist in value_sets.values()
            for item in sublist
            if math.isfinite(item)
        ]
        normalization_factor = max(all_items) if all_items else 1.0
        logger.debug("Global normalization factor calculated: %f", normalization_factor)
    for key, value_set in value_sets.items():
        if normalization_method == NORMALIZATION.INTERNAL:
            valid_values = [v for v in value_set if math.isfinite(v)]
            normalization_factor = max(valid_values) if valid_values else 1
            logger.debug(
                "Internal normalization for dataset %s: factor=%f",
                key,
                normalization_factor,
            )
        if normalization_factor == 0:
            logger.warning(
                "Prevented division by zero in dataset %s. No normalization has been applied.",
                key,
            )
            normalization_factor = 1
        value_sets[key] = [value / normalization_factor for value in value_set]
    logger.debug("Normalization applied successfully")
    return value_sets
