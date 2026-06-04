"""
A suite of methods for analyzing the composition of multiple datasets.
These methods enable the development of a rules-based system to ensure modules are loaded only with compatible data.
For simplicity, all methods return False when data is usable and True when data is not usable.
"""

from typing import List, Set, Optional
from datetime import datetime, timedelta
from martin_interface.dataset import Dataset


def no_datasets_selected(datasets: List[Dataset]) -> bool:
    """
    Checks if no dataset has been selected.
    Args:
        datasets (List[Dataset]): A list of Dataset objects to check.
    Returns:
        bool: True if no datasets are provided (empty list), False otherwise.
    """
    return not datasets


def has_insufficient_number_of_datasets(datasets: List[Dataset], min_count: int = 2) -> bool:
    """
    Checks if there are fewer datasets than the minimum required.
    Args:
        datasets: List of datasets to check
        min_count: Minimum number of datasets required (default: 2)
    Returns:
        bool: True if insufficient number of datasets, False otherwise.
    """
    return len(datasets) < min_count


def has_insufficient_number_of_samples(datasets: List[Dataset], min_count: int = 2) -> bool:
    """
    Checks if any of the datasets selected has fewer samples than required.
    Args:
        datasets: List of datasets to check
        min_count: Minimum number of datasets required (default: 2)
    Returns:
        bool: True if insufficient number of samples, False otherwise.
    """
    for dataset in datasets:
        if len(dataset.samples) < min_count:
            return True
    return False


def has_insufficient_number_of_spots(datasets: List[Dataset], min_count: int = 2) -> bool:
    """
    Checks if any of the datasets selected has fewer spots per sample than required.
    Args:
        datasets: List of datasets to check
        min_count: Minimum number of datasets required (default: 2)
    Returns:
        bool: True if insufficient number of samples, False otherwise.
    """
    for dataset in datasets:
        for sample in dataset.samples:
            if len(sample.spots) < min_count:
                return True
    return False


def missing_metadata(datasets: List[Dataset]) -> bool:
    """
    Checks if any dataset is missing metadata.
    Args:
        datasets: List of datasets to check
    Returns:
        bool: True if any dataset lacks metadata, False otherwise.
    """
    return any(dataset.file_holder.metadata_file is None for dataset in datasets)


def missing_parameters(datasets: List[Dataset]) -> bool:
    """
    Checks if any dataset is missing general parameters.
    Args:
        datasets: List of datasets to check
    Returns:
        bool: True if any dataset lacks general parameters, False otherwise.
    """
    return any(dataset.file_holder.parameters_file is None for dataset in datasets)


def sample_count_not_uniform(datasets: List[Dataset]) -> bool:
    """
    Checks if datasets have different numbers of samples.
    Args:
        datasets: List of datasets to check
    Returns:
        bool: True if sample counts are inconsistent, False otherwise.
    """
    if not datasets:
        return True

    sample_counts = [len(dataset.samples) for dataset in datasets]
    return len(set(sample_counts)) > 1


def spot_count_is_not_uniform(datasets: List[Dataset]) -> bool:
    """
    Checks if the number of spots per sample varies within or across datasets.
    Args:
        datasets: List of datasets to check
    Returns:
        bool: True if spot counts per sample are inconsistent, False otherwise.
    """
    spot_counts: Set[int] = set()

    for dataset in datasets:
        for sample in dataset.samples:
            spot_counts.add(len(sample.spots))

    return len(spot_counts) > 1


def spot_shapes_inconsistent(datasets: List[Dataset]) -> bool:
    """
    Checks if spot shapes are inconsistent across datasets.
    Args:
        datasets: List of datasets to check
    Returns:
        bool: True if spot shapes are inconsistent, False otherwise.
    """
    shapes: Set[Optional[str]] = set()

    for dataset in datasets:
        for sample in dataset.samples:
            for spot in sample.spots:
                shapes.add(spot.shape)

    valid_shapes = {shape for shape in shapes if shape is not None}
    return len(valid_shapes) > 1


def has_inconsistent_imaging_parameters(datasets: List[Dataset]) -> bool:
    """
    Checks if imaging parameters differ across datasets.
    Args:
        datasets: List of datasets to check
    Returns:
        bool: True if imaging parameters are inconsistent, False otherwise.
    """
    binning_values: Set[Optional[int]] = set()
    exposure_times: Set[Optional[str]] = set()

    for dataset in datasets:
        if dataset.metadata:
            binning_values.add(dataset.metadata.pixel_binning)
            exposure_str = (
                str(dataset.metadata.exposure_time) if dataset.metadata.exposure_time else None
            )
            exposure_times.add(exposure_str)

    valid_binning = {b for b in binning_values if b is not None}
    valid_exposures = {e for e in exposure_times if e is not None}

    return len(valid_binning) > 1 or len(valid_exposures) > 1


def has_inconsistent_incubation_parameters(datasets: List[Dataset]) -> bool:
    """
    Checks if incubation parameters differ across datasets.

    This function examines all incubation steps across datasets and checks for
    inconsistencies in:
    - Number of incubation steps
    - Solution names and their order
    - Stock concentrations (value and unit)
    - Final concentrations (value and unit)
    - Incubation times

    Args:
        datasets: List of datasets to check

    Returns:
        bool: True if incubation parameters are inconsistent, False otherwise.
    """
    if not datasets:
        return True

    # Skip datasets without metadata
    datasets_with_metadata = [d for d in datasets if d.metadata is not None]
    if not datasets_with_metadata:
        return False

    # Get reference incubations from first dataset with metadata
    reference_incubations = datasets_with_metadata[0].metadata.incubations
    reference_count = len(reference_incubations)

    # Check each dataset's incubations against the reference
    for dataset in datasets_with_metadata[1:]:
        current_incubations = dataset.metadata.incubations

        # Check if number of incubation steps matches
        if len(current_incubations) != reference_count:
            return True

        # Check each incubation step
        for i, (ref_incub, curr_incub) in enumerate(
            zip(reference_incubations, current_incubations)
        ):
            # Check solution name
            if ref_incub.solution != curr_incub.solution:
                return True

            # Check stock concentration value and unit
            if (
                ref_incub.stock_concentration.value != curr_incub.stock_concentration.value
                or ref_incub.stock_concentration.unit != curr_incub.stock_concentration.unit
            ):
                return True

            # Check final concentration value and unit
            if (
                ref_incub.final_concentration.value != curr_incub.final_concentration.value
                or ref_incub.final_concentration.unit != curr_incub.final_concentration.unit
            ):
                return True

            # Check incubation time
            if ref_incub.incubation_time != curr_incub.incubation_time:
                return True

    return False


def has_negative_data_values(datasets: List[Dataset]) -> bool:
    """
    Checks if any of the numerical values contained within spot data of a list of datasets is below zero.

    Args:
        datasets: List of datasets to check

    Returns:
        bool: True if any of the data values contains a negative number. False if otherwise.
    """
    for dataset in datasets:
        for sample in dataset.samples:
            for spot in sample.spots:
                if (
                    spot.mean_minus_min < 0
                    or spot.normalized_mean < 0
                    or spot.min_val < 0
                    or spot.max_val < 0
                    or spot.mean_val < 0
                    or spot.std_deviation < 0
                ):
                    return True
    return False


def has_negative_data_statistics_values(datasets: List[Dataset]) -> bool:
    """
    Checks if any of the numerical values contained within spot statistics of a list of datasets is below zero.

    Args:
        datasets: List of datasets to check

    Returns:
        bool: True if any of the data statistics values contains a negative number. False if otherwise.
    """
    for dataset in datasets:
        for sample in dataset.samples:
            data_statistics = sample.data_statistics
            if (
                data_statistics.row < 0
                or data_statistics.col < 0
                or data_statistics.adjusted_average < 0
                or data_statistics.adjusted_average_std_deviation < 0
                or data_statistics.relative_adjusted_average_std_deviation < 0
                or data_statistics.normalized_average < 0
                or data_statistics.normalized_average_std_deviation < 0
                or data_statistics.relative_normalized_average_std_deviation < 0
            ):
                return True
    return False


def has_negative_spot_coordinates(datasets: List[Dataset]) -> bool:
    """
    Checks if any of the numerical values contained within spot coordinates of a list of datasets is below zero.

    Args:
        datasets: List of datasets to check

    Returns:
        bool: True if any of the spot coordinates contains a negative number. False if otherwise.
    """
    for dataset in datasets:
        for sample in dataset.samples:
            for spot in sample.spots:
                for coordinate in spot.coordinates:
                    if coordinate.x < 0 or coordinate.y < 0:
                        return True
    return False


def has_negative_values(datasets: List[Dataset]) -> bool:
    """
    Checks if any of the numerical values contained within a list of datasets is below zero.
    This method uses has_negative_data_values, has_negative_data_statistics_values and has_negative_spot_coordinates.

    Args:
        datasets: List of datasets to check

    Returns:
        bool: True if any of the datasets checked contains a negative number. False if otherwise.
    """
    return (
        has_negative_data_values(datasets=datasets)
        or has_negative_data_statistics_values(datasets=datasets)
        or has_negative_spot_coordinates(datasets=datasets)
    )
