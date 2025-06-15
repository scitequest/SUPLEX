import json
import csv
import os
import math
import logging
import copy
from typing import List, Optional, Any
from .basic_file_validation import *
from ..martin_interface_constants import DATA_FIELDS

logger = logging.getLogger(__name__)

def try_get_validated_data(data_file_path: str) -> dict[str, List[dict[str, Any]]]:
    """
    Conducts a set of checks if a data file is valid.
    Tolerable inconsistencies are logged, if not tolerable entire dataset is not loaded.
    
    Args:
        data_file_path (str): Path to the data file.
    
    Returns:
        dict: Data file containing a list of dictionaries each representing one spot; only returned if all checks pass.
        None: If the file is invalid.
    """
    
    logging.debug(f"Initiated data file validation for {data_file_path}")
    data_file = get_data_file(file_path = data_file_path)
    if data_file is None:
        return None

    is_key_structure_correct = is_Key_Structure_Identical(file_path=data_file_path, file=data_file, keymap=DATA_FIELDS)
    if not is_key_structure_correct:
        logger.error(f"Data file at {data_file_path} has not been loaded due to incorrect key structure")
        return None

    data_file = try_typecast_data_file(data_file_path, data_file)
    
    if data_file is None:
        logger.error(f"Data file at {data_file_path} was not loaded since values could not be typecasted")
        return None
    
    if not check_value_consistency(data_file_path=data_file_path, data_file=data_file):
        logger.error(f"Data file at {data_file_path} was not loaded due to value inconsistencies")
        return None
        
    return data_file

def try_typecast_data_file(data_file_path: str, data_file: dict[str, List[dict[str, Any]]]) -> dict[str, List[dict[str, Any]]]:
    """
    Attempts to typecast data_file values to their correct format.
    
    Args:
        data_file_path (str): data_file_path used for logging error messages
        data_file (dict): JSON which is to be typecast

    Returns:
        Typecast list of dictionaries if no error has been fired during the process.
        Returns None if Typecast of even a single value proved to be impossible.
    """
    typecasted_data = []
    type_fields = copy.deepcopy(DATA_FIELDS["values"][0])
                    
    for dataset in data_file["values"]:
        try:
            typecasted_data.append({key: type_fields[key](value) for key, value in dataset.items()})
        except Exception as e:
            logger.error(f"Typecasting failed for {data_file_path}: {str(e)}")
            return None
    
    return {"values": typecasted_data}
    
def check_value_consistency(data_file_path: str, data_file: dict[str, List[dict[str, Any]]]) -> bool:
    """
    Check for logical constraints.
    This method mostly logs logical inconsistencies but may also bar the usage of a dataset entirely.
    Handling of any issues, such as the occurrence of NaN, has to be handled by the modules themselves.

    Data represents a set of measurements, as a quality control measure samples may be printed in multiplicate.
    These copies are placed in the same position of different grids dubbed spot_fields.
    The spot attribute of the data files represents the copy number and affiliated grid of a sample.
    We therefore also need to check for uniformity between the size of different spot_fields.
    
    Args:
        data_file (list): List of dictionaries containing dataset spots.
        data_file_path (str): Path to the dataset file, used in log messages.
    
    Returns:
        True if the dataset is usable (no critical issues found, though inconsistencies may be logged).
        False if the dataset is unusable due to critical issues.
    """
    data = data_file["values"]
    
    for i, datapoint in enumerate(data):
        # If conditions don't apply, do not read in dataset
        if datapoint["spot"] < 0:
            logger.error(f"Dataset at {data_file_path} has invalid spot index: {datapoint['spot']} < 0 at entry {i}")
            return False
        if datapoint["row"] < 0:
            logger.error(f"Dataset at {data_file_path} has invalid row index: {datapoint['row']} < 0 at entry {i}")
            return False
        if datapoint["col"] < 0:
            logger.error(f"Dataset at {data_file_path} has invalid col index: {datapoint['col']} < 0 at entry {i}")
            return False

    # Check if all spot fields have the same number of entries.
    
    # Split measurement data each spot_field beeing one set of copies.
    n_spot_fields = data[-1]["spot"] + 1 # last entry will be part of the highest index spot_field
    spot_fields = [[] for _ in range(n_spot_fields)]
    # Confusing terminology, spot in measurement files is a shorthand for spot-field
    for spot in data:
        spot_fields[spot["spot"]].append(spot)

    
    spot_field_length = len(spot_fields[0])
    for sField in spot_fields:
        if len(sField) != spot_field_length:
            logger.error(f"{data_file_path}: Spotfields have a varying number of entries.")
            return False
            
    # Dictionaries to collect NaN and infinite indices per field, this shortens the log.
    keymap = DATA_FIELDS["values"][0].keys()
    nan_indices = {field: [] for field in keymap}
    inf_indices = {field: [] for field in keymap}  
    
    for i, datapoint in enumerate(data):
        # If conditions don't apply, log warnings via logger with data_file_path, logical inconsistency label, and values
        for key in keymap:
            if math.isnan(datapoint[key]):
                nan_indices[key].append(i)
            if math.isinf(datapoint[key]):
                inf_indices[key].append(i)
        
        if datapoint["min"] > datapoint["max"]:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - min > max (min: {datapoint['min']}, max: {datapoint['max']})")
        if datapoint["std_deviation"] < 0:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - std_deviation < 0 (value: {datapoint['std_deviation']})")
        if datapoint["mean"] < datapoint["min"]:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - mean < min (mean: {datapoint['mean']}, min: {datapoint['min']})")
        if datapoint["mean"] > datapoint["max"]:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - mean > max (mean: {datapoint['mean']}, max: {datapoint['max']})")
        if datapoint["normalized_mean"] > 1:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - normalized_mean > 1 (value: {datapoint['normalized_mean']})")
        if datapoint["normalized_mean"] < 0:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - normalized_mean < 0 (value: {datapoint['normalized_mean']})")
        if datapoint["mean_minus_min"] > datapoint["mean"]:
            logger.warning(f"{data_file_path}: Spot {i}: logical inconsistency - mean_minus_min > mean (mean_minus_min: {datapoint['mean_minus_min']}, mean: {datapoint['mean']})")
            
    for key in keymap:
        if nan_indices[key]:
            indices_str = ", ".join(map(str, nan_indices[key]))
            logger.warning(f"{data_file_path}: {key} has NaN values at entries: {indices_str}")
        
        if inf_indices[key]:
            indices_str = ", ".join(map(str, inf_indices[key]))
            logger.warning(f"{data_file_path}: {key} has infinite values at entries: {indices_str}")
            
    return True
