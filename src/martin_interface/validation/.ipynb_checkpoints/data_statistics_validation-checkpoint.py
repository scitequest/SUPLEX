import json
import csv
import os
import math
import logging
import copy
from typing import List, Optional, Any
from .basic_file_validation import *
from ..constants import DATA_STATISTICS_FIELDS, TOLERANCE

logger = logging.getLogger(__name__)

def try_get_validated_data_statistics(data_statistics_file_path: str, data_file: dict[str, List[dict[str, Any]]]) -> Optional[dict[str, List[dict[str, Any]]]]:
    """
    Conducts a set of checks to validate a data_statistics file.
    Tolerable inconsistencies are logged, while intolerable issues prevent file loading.
    
    Args:
        data_statistics_file_path (str): Path to the data_statistics file.
        data_file (dict): List of dicts used later on for external validation.
    
    Returns:
        dict: Data_statistics file containing a list of dictionaries, each representing one data_statistics entry; returned only if all checks pass.
        None: If the file is invalid or fails critical validation checks.
    """
    
    logging.debug(f"Initiated data_statistics file validation for {data_statistics_file_path}")
    data_statistics_file = get_data_file(file_path = data_statistics_file_path)
    if data_statistics_file is None:
        return None

    is_key_structure_correct = is_Key_Structure_Identical(file_path = data_statistics_file_path, file = data_statistics_file, keymap = DATA_STATISTICS_FIELDS)
    if not is_key_structure_correct:
        logger.error(f"Data statistics file at {data_statistics_file_path} has not been loaded due to incorrect key structure")
        return None    
    
    # Typecast fields to their expected types per DATA_STATISTICS_FIELDS
    data_statistics_file = try_typecast_data_statistics_file(data_statistics_file_path = data_statistics_file_path, data_statistics_file = data_statistics_file)
    if data_statistics_file is None:
        return None
    
    # Validate logical consistency of data_statistics values
    if not check_internal_value_consistency(data_statistics_file_path = data_statistics_file_path, 
                                            data_statistics_file = data_statistics_file):
        logger.error(f"Data_statistics file at {data_statistics_file_path} was not loaded due to internal inconsistencies")
        return None

    if not check_external_consistency(data_file = data_file,
                                      data_statistics_file_path = data_statistics_file_path,
                                      data_statistics_file = data_statistics_file):
        logger.error(f"Data_statistics file at {data_statistics_file_path} was not loaded due to inconsistencies with its data file")
        return None
        
    return data_statistics_file

def try_typecast_data_statistics_file(data_statistics_file_path: str, data_statistics_file: dict[str, List[dict[str, Any]]]) -> Optional[dict[str, List[dict[str, Any]]]]:
    """
    Attempts to typecast data_statistics_file values to their correct format.
    
    Args:
        data_statistics_file_path (str): data_statistics_file_path used for logging error messages
        data_statistics_file (dict): JSON which is to be typecast

    Returns:
        Typecast list of dictionaries if no error has been fired during the process.
        Returns None if Typecast of even a single value proved to be impossible.
    """
    typecasted_data = []
    type_fields = copy.deepcopy(DATA_STATISTICS_FIELDS["values"][0])

    for dataset in data_statistics_file["values"]:
        try:
            typecasted_data.append({key: type_fields[key](value) for key, value in dataset.items()})
        except Exception as e:
            logger.error(f"Typecasting failed for {data_statistics_file_path}: {str(e)}")
            return None
    
    return {"values": typecasted_data}

def check_internal_value_consistency(data_statistics_file_path: str, data_statistics_file: dict[str, List[dict[str, Any]]]) -> bool:
    """
    Validates logical constraints in data_statistics entries.
    Logs tolerable inconsistencies and prevents usage for critical issues.
    
    Args:
        data_statistics (list): List of dictionaries containing data_statistics entries.
        data_statistics_file_path (str): Path to the data_statistics file, used in log messages.
        data_file (list): List of dictionaries containing data entries.
        
    Returns:
        True if the data_statistics is usable (no critical issues, though warnings may be logged).
        False if the data_statistics is unusable due to critical validation failures.
    """
    # Check float fields for NaN and infinite values
    float_fields = ["adjusted_average", "adjusted_average_std_deviation", 
                   "relative_adjusted_average_std_deviation", "normalized_average",
                   "normalized_average_std_deviation", "relative_normalized_average_std_deviation"]

    # Dictionaries to collect NaN and infinite indices per field, this shortens the log.
    nan_indices = {field: [] for field in float_fields}
    inf_indices = {field: [] for field in float_fields}
        
    for i, datapoint in enumerate(data_statistics_file["values"]):
        # Critical checks that prevent usage of the data_statistics
        if datapoint["row"] < 0:
            logger.error(f"Data_statistics at {data_statistics_file_path} has invalid row index: {datapoint['row']} < 0")
            return False
        if datapoint["col"] < 0:
            logger.error(f"Data_statistics at {data_statistics_file_path} has invalid col index: {datapoint['col']} < 0")
            return False
        
        for key in float_fields:
            if math.isnan(datapoint[key]):
                nan_indices[key].append(i)
            if math.isinf(datapoint[key]):
                inf_indices[key].append(i)

        # Logical consistency checks for data_statistics values
        if datapoint["adjusted_average_std_deviation"] < 0:
            logger.warning(f"{data_statistics_file_path}: Entry {i}: logical inconsistency - adjusted_average_std_deviation < 0 (value: {datapoint['adjusted_average_std_deviation']})")
        if datapoint["relative_adjusted_average_std_deviation"] < 0:
            logger.warning(f"{data_statistics_file_path}: Entry {i}: logical inconsistency - relative_adjusted_average_std_deviation < 0 (value: {datapoint['relative_adjusted_average_std_deviation']})")
        if datapoint["normalized_average"] > 1 or datapoint["normalized_average"] < 0:
            logger.warning(f"{data_statistics_file_path}: Entry {i}: logical inconsistency - normalized_average out of range [0,1] (value: {datapoint['normalized_average']})")
        if datapoint["normalized_average_std_deviation"] < 0:
            logger.warning(f"{data_statistics_file_path}: Entry {i}: logical inconsistency - normalized_average_std_deviation < 0 (value: {datapoint['normalized_average_std_deviation']})")
        if datapoint["relative_normalized_average_std_deviation"] < 0:
            logger.warning(f"{data_statistics_file_path}: Entry {i}: logical inconsistency - relative_normalized_average_std_deviation < 0 (value: {datapoint['relative_normalized_average_std_deviation']})")
    
    for field in float_fields:
        if nan_indices[field]:
            indices_str = ", ".join(map(str, nan_indices[field]))
            logger.warning(f"{data_statistics_file_path}: Field '{field}' has NaN values at entries: {indices_str}")
        
        if inf_indices[field]:
            indices_str = ", ".join(map(str, inf_indices[field]))
            logger.warning(f"{data_statistics_file_path}: Field '{field}' has infinite values at entries: {indices_str}")
        
    return True

def check_external_consistency(data_file: dict[str, List[dict[str, Any]]], data_statistics_file_path: str, data_statistics_file: dict[str, List[dict[str, Any]]]) -> bool:
    """
    Checks for consistency in format and values between the data_file and data_statistics_file.
    This is done because we define datasets by the presence of a data file, therefore every other file should fit to this data file.
    If this is not the case we can assume that files have been wrongly associated with one another and should therefore not be analyzed as one dataset.

    For this validation step it is important to understand what data statistics is. 
    Data represents a set of measurements, as a quality control measure samples may be printed in multiplicate.
    Data_statistics represents the summation of measurement data derived from multiple copies of the same sample.
    A core assumption of data_statistics files produced via MARTin is that all copies are placed at the same grid position.
    As such data_statistics may not be viable for every application of the MARTin software.
    The spot attribute of the data files represents the copy number and affiliated grid of a sample.

    Args:
        data_statistics (list): List of dictionaries containing data_statistics entries.
        data_statistics_file_path (str): Path to the data_statistics file, used in log messages.
        data_file (list): List of dictionaries containing data entries.

    Returns:
        True if it is logical that the data_statistics_file has been derived from the data_file.
        False if it is unlikely that the data_statistics_file has been derived from the data_file.
    """
    data_statistics = data_statistics_file["values"]
    
    # Split measurement data each spot_field beeing one set of copies.
    n_spot_fields = data_file["values"][-1]["spot"] + 1 # Last entry will be part of the highest index spot_field.
    spot_fields = [[] for _ in range(n_spot_fields)]
    for spot in data_file["values"]:
        spot_fields[spot["spot"]].append(spot)

    # Check if dimensions are the same between data and data_statistics.
    n_spots_data = len(spot_fields[0])
    n_spots_data_statistics = len(data_statistics)
    if n_spots_data != n_spots_data_statistics:
        logger.error(f"Data_statistics file at {data_statistics_file_path} has different format than the data file of the same directory. Number of spots data = {n_spots_data}; data_statistics = {n_spots_data_statistics}")
        return False

    # Calculate adjusted averages for validation purposes
    validation_adjusted_averages = []
    for i in range(n_spots_data):
        adjusted_sum = 0
        for spot_field in spot_fields:
            adjusted_sum += spot_field[i]["mean_minus_min"]
        adjusted_average = adjusted_sum / n_spot_fields
        validation_adjusted_averages.append(adjusted_average)

    consistent = True
    for i, spot in enumerate(data_statistics):
        adjusted_average = spot["adjusted_average"]
        if not math.isclose(adjusted_average, validation_adjusted_averages[i], abs_tol = TOLERANCE):
            logging.debug(f"Inconsistency: {data_statistics_file_path} at entry {i} adjusted_average file = {adjusted_average}; calculated = {validation_adjusted_averages[i]}.")
            consistent = False
    return consistent
