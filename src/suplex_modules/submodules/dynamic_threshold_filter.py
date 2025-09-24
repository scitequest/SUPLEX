import logging
import math
import statistics
from typing import List
from dataclasses import dataclass
from scipy.stats import shapiro, norm

import numpy as np

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class FilteredValue:
    VALUE: float
    DELTA: float
    GROUP_NR: int
    SIGNIFICANT: bool

def apply_dynamic_filtering(value_list: List[float], use_broad_grouping: bool = True, alpha: float = 0.05) -> List[FilteredValue]:
    """
    Applies dynamic filtering to a list of values by calculating deltas, grouping by contrast,
    and applying adaptive significance cutoffs. This is a convenience wrapper combining the core steps.

    Args:
        value_list (List[float]): List of numeric values to filter.
        use_broad_grouping (bool): If True, uses the lowest value among max-delta candidates for grouping thresholds;
                                   otherwise, uses the highest. Defaults to True.

    Returns:
        List[FilteredValue]: List of filtered values with metadata, where SIGNIFICANT indicates if the value passed the cutoff.
    """
    delta_list = calculate_incremental_deltas(value_list = value_list)
    value_group_map = group_by_delta_contrast(value_list = value_list, delta_list = delta_list, use_broad_grouping = use_broad_grouping)
    filtered_list = apply_adaptive_significance_cutoff(value_list = value_list, value_group_map = value_group_map, alpha = alpha)
    combined_list = []
    for i in range(len(value_list)):
        val = value_list[i]
        delta = delta_list[i]
        group = value_group_map[i]
        sig = not math.isnan(filtered_list[i])
        combined_list.append(FilteredValue(VALUE=val, DELTA=delta, GROUP_NR=group, SIGNIFICANT=sig))
    
    return combined_list
    

def apply_adaptive_significance_cutoff(value_list: List[float], value_group_map: List[int], alpha: float = 0.05, min_elements_shapiro: int = 10) -> List[float]:
    """
    Applies an adaptive statistical cutoff to determine significant values based on group normality and distribution similarity.
    Zero values have to be treated with special consideration since they either result from noise subtraction or stem from low exposure imaging (they are more artifactual than actual noise).
    
    The regular algorithm assumes groups are ordered from highest values (group 0) to lowest (higher group numbers).
    It iteratively checks each group against the distribution of lower-valued groups (higher group numbers).
    - Tests if lower groups follow a normal distribution (Shapiro-Wilk).
    - If normal, tests if the current group follows the same distribution (Kolmogorov-Smirnov).
    - If the current group fits the "noise" distribution of lower groups, it sets a cutoff: preserves values from higher-value groups (lower group numbers)
      and marks lower-value groups (including current) as non-significant (NaN).
    - If no cutoff is found, all values are considered significant.
    - If there are not enough values to calculate a normal distribution combine current group with lower-level groups and don't use Kolmogorov-Smirnov.
    - If there are not enough values in the combined list set the remaining groups to insignificant by default.

    Args:
        value_list (List[float]): Original list of values.
        value_group_map (List[int]): Group numbers from group_by_delta_contrast.
        alpha (float): Significance level for statistical tests.
        min_elements_shapiro (int): Minimum number of elements required for the calculation of a normal distribution.

    Returns:
        List[float]: Filtered list where significant values are preserved; non-significant values are set to NaN.
    """
    
    if len(value_list) != len(value_group_map):
        logger.error(f"Could not apply apply_adaptive_significance_cutoff, value_list ({len(value_list)}) and value_group_map ({len(value_group_map)}) must have the same length. Empty list will be returned.")
        return [math.nan] * len(value_list)

    groups = sorted(set(value_group_map))
    
    if len(groups) <= 1:
        logger.debug(f"Only one group in value set: {value_list}. Will be defaulted to insignificant.")
        return [math.nan] * len(value_list)
    
    for group in groups:
        group_values = [v for v, g in zip(value_list, value_group_map) if g == group]
        if not group_values:
            # This should not occur naturally
            logger.warning(f"Group {group} is empty!")
            continue
        other_values = [v for v, g in zip(value_list, value_group_map) if g > group]
            
        # If other contains less than ten values combine other and group
        if len(other_values) < min_elements_shapiro:
            combined_group_list = other_values + group_values

            # If combined is less than tree set combined to insignificant
            if len(combined_group_list) < 3:
                logger.debug(f"Cutoff at group {group}: Cannot apply shapiro because of combined list length < 3 ({len(combined_group_list)}). Groups will be set to insignificant")
                return [(v if g < group else math.nan) for v, g in zip(value_list, value_group_map)]

            if sum(combined_group_list) <= 0 or shapiro(combined_group_list)[1] > alpha:
                # If normally distributed set group_values + other_values as insignificant
                logger.debug(f"Cutoff at group {group}. No Z test applied because of low group size ({len(combined_group_list)}). Alpha used = {alpha}")
                return [(v if g < group else math.nan) for v, g in zip(value_list, value_group_map)]
            # Combined group is not normally distributed which means that we have to include group and evaluate other_values in the next loop
            continue

        # Check if non group-values are normally distributed sum zero are always considered as normally distributed
        if sum(other_values) <= 0 or shapiro(other_values)[1] > alpha:
            # Estimate if current group is part of the noise normal distribution or an outlier
            other_mean = np.mean(other_values)
            other_std = np.std(other_values, ddof=1)
            
            if other_std == 0:
                logger.debug(f"Cutoff at group {group + 1}. Normally distributed with standard deviation of zero and mean {other_mean}.")
                return [(v if g < (group + 1) else math.nan) for v, g in zip(value_list, value_group_map)]
            
            group_mean = np.mean(group_values)
            group_n = len(group_values)
            z_score = (group_mean - other_mean) / (other_std / np.sqrt(group_n))
            p_value = 1 - norm.cdf(z_score)
            
            if p_value > alpha:
                logger.debug(f"Cutoff at group {group}. Fits to normally distributed group {group + 1} (p-value={p_value:.4f} > {alpha})")
                return [(v if g < group else math.nan) for v, g in zip(value_list, value_group_map)]
    
    # Fallback
    logger.debug("No cutoff found; all values treated as insignificant.")
    return [math.nan] * len(value_list)
    

def group_by_delta_contrast(value_list: List[float], delta_list: List[float], use_broad_grouping: bool = True) -> List[int]:
    """
    Groups values by iteratively finding the largest delta and grouping all values 
    at or above the corresponding threshold value.
    
    The algorithm:
    1. Find the maximum delta in the remaining delta_list
    2. Get the corresponding value from value_list as threshold
    3. Group all values >= threshold into the current group
    4. Remove grouped items and repeat until all values are grouped
    
    Args:
        value_list (List[float]): List of numeric values
        delta_list (List[float]): List of deltas corresponding to value_list (same length)
        use_broad_grouping (bool): If True, grouping is done using the lowest value among those with the highest delta
                                   (for broader groups); else, using the highest value among them (for narrower groups).
                                   Defaults to True.

    Returns:
        List of group numbers (0, 1, 2, ...) with same length as input lists
    """
    if not value_list or not delta_list:
        return []
    
    if len(value_list) != len(delta_list):
        logger.error(f"Could not apply group_by_delta_contrast, value_list ({len(value_list)}) and delta_list ({len(delta_list)}) must have the same length. Empty list will be returned.")
        return []
    
    # Initialize result list with -1 (ungrouped)
    value_group_map = [-1] * len(value_list)
    
    # Keep track of remaining indices
    remaining_indices = set(range(len(value_list)))
    current_group = 0
    
    while remaining_indices:
        # Find indices with maximum delta among remaining items
        max_delta_indices = [i for i in remaining_indices if delta_list[i] == max(delta_list[j] for j in remaining_indices)]
        if use_broad_grouping:
            # Get lowest value with the highest delta - we do this incase the max delta is shared between two or more values.
            threshold_value = min(value_list[max_delta_idx] for max_delta_idx in max_delta_indices)
        else:
            # Get highest value with the highest delta - we do this incase the max delta is shared between two or more values.
            threshold_value = max(value_list[max_delta_idx] for max_delta_idx in max_delta_indices)
        
        
        # Find all remaining indices with values >= threshold
        current_group_indices = [
            i for i in remaining_indices 
            if value_list[i] >= threshold_value
        ]
        
        # Assign group number to all items in current group
        for idx in current_group_indices:
            value_group_map[idx] = current_group
            remaining_indices.remove(idx)
        
        current_group += 1
    
    return value_group_map


def calculate_incremental_deltas(value_list: List[float]) -> List[float]:
    """
    Calculates the difference between each value and its next smaller value in the list.
    
    The smallest value gets its actual value as delta (representing the jump from 0),
    all other values get the difference to the value that directly precedes them in sorted order.
    
    Args:
        value_list (List[float]): List of numeric values
        
    Returns:
        List of deltas in the original order of the input list
    """
    if not value_list:
        return []
    
    # Index mapping to preserve references to original positions
    indexed_values = [(value, i) for i, value in enumerate(value_list)]
    
    # Sort by values for delta calculation
    sorted_indexed = sorted(indexed_values, key=lambda x: x[0])
    
    deltas = {}
    # Smallest value gets its actual value as delta (jump from 0 to this value)
    deltas[sorted_indexed[0][1]] = sorted_indexed[0][0]
    
    # Delta = current value minus previous value in sorted order
    for i in range(1, len(sorted_indexed)):
        current_value, original_index = sorted_indexed[i]
        previous_value = sorted_indexed[i-1][0]
        delta = current_value - previous_value
        deltas[original_index] = delta
    
    # Return in original order
    return [deltas[i] for i in range(len(value_list))]