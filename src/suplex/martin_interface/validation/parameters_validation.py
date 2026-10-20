import json
import logging
from typing import List, Optional, Any
from .basic_file_validation import *
from ..martin_interface_constants import (
    PARAMETERS_FIELDS_POLYGON,
    PARAMETERS_FIELDS_CIRCLE,
)

logger = logging.getLogger(__name__)


def try_get_validated_parameters(
    parameters_file_path: str, data_file: dict[str, List[dict[str, Any]]]
) -> Optional[dict[str, Any]]:
    """
    Conducts a set of checks to validate a parameters file.
    Tolerable inconsistencies are logged, while intolerable issues prevent file loading.

    Args:
        parameters_file_path (str): Path to the parameters file.
        data_file (dict): Currently unused parameter reserved for future functionality.

    Returns:
        dict: Parameters file as a dictionary; returned only if all checks pass.
        None: If the file is invalid or fails critical validation checks.
    """

    logging.debug(f"Initiated parameters file validation for {parameters_file_path}")

    parameters_file = try_get_valid_json(parameters_file_path)

    if parameters_file is None:
        return None

    if isinstance(parameters_file, dict):
        # Allows for compatibility with older versions of MARTin which had a typo, namely 'subract'.
        if "subract_background" in parameters_file.keys():
            parameters_file["subtract_background"] = parameters_file.pop("subract_background")
        # A Parameters-file can have two distinct formats, here we check which one we have to use.
        keymap = PARAMETERS_FIELDS_POLYGON
        spots_are_circular = False
        if "spots" in parameters_file.keys():
            if isinstance(parameters_file["spots"], list):
                if "type" in parameters_file["spots"][0].keys():
                    if parameters_file["spots"][0]["type"] == "CIRCLE":
                        keymap = PARAMETERS_FIELDS_CIRCLE
                        spots_are_circular = True

    is_key_structure_correct = is_Key_Structure_Identical(
        file_path=parameters_file_path, file=parameters_file, keymap=keymap
    )

    if not is_key_structure_correct:
        logger.error(
            f"Parameters file at {parameters_file_path} has not been loaded due to incorrect key structure"
        )
        return None

    parameters_file = try_typecast_parameters_file(
        parameters_file_path=parameters_file_path,
        parameters_file=parameters_file,
        spots_are_circular=spots_are_circular,
    )
    if parameters_file is None:
        return None

    # Validate logical consistency of parameters values.
    if not check_internal_value_consistency(
        parameters_file_path=parameters_file_path, parameters_file=parameters_file
    ):
        logger.error(
            f"Parameters file at {parameters_file_path} was not loaded due to internal inconsistencies"
        )
        return None

    if not check_external_consistency(
        data_file=data_file,
        parameters_file_path=parameters_file_path,
        parameters_file=parameters_file,
    ):
        logger.error(
            f"Parameters file at {parameters_file_path} was not loaded due to inconsistencies with its data file"
        )
        return None

    return parameters_file


def try_typecast_parameters_file(
    parameters_file_path: str, parameters_file: dict[str, Any], spots_are_circular: bool
) -> Optional[dict[str, Any]]:
    """
    Attempts to typecast parameters_file values to their correct format.

    Args:
        parameters_file_path (str): parameters_file_path used for logging error messages
        parameters_file (dict): JSON which is to be typecast
        spots_are_circular (bool): Boolean, dennotes the shape of spots

    Returns:
        Typecast dictionary if no error has been fired during the process.
        Returns None if Typecast of even a single value proved to be impossible.
    """
    try:
        typecasted_data = {
            "invert_lut": typecast_to_bool(parameters_file["invert_lut"]),
            "subtract_background": typecast_to_bool(parameters_file["subtract_background"]),
            "number_of_spotfields": int(parameters_file["number_of_spotfields"]),
            "columns_per_spotfield": int(parameters_file["columns_per_spotfield"]),
            "spots_per_spotfield": int(parameters_file["spots_per_spotfield"]),
            "spots": [],
            "background_rectangles": [],
        }
    except Exception as e:
        logger.error(f"Typecasting failed for {parameters_file_path}: {str(e)}")
        return None

    for i, spot in enumerate(parameters_file["spots"]):
        try:
            if spots_are_circular:
                typecasted_spot = {
                    "type": str(spot["type"]),
                    "position": [float(coord) for coord in spot["position"]],
                    "diameter": float(spot["diameter"]),
                }
            else:
                typecasted_spot = {
                    "type": str(spot["type"]),
                    "coordinates": [
                        [float(coord) for coord in sublist] for sublist in spot["coordinates"]
                    ],
                }
            typecasted_data["spots"].append(typecasted_spot)
        except Exception as e:
            logger.error(f"Typecasting failed for {parameters_file_path} on spot {i}: {str(e)}")
            return None

    for i, rectangle in enumerate(parameters_file["background_rectangles"]):
        try:
            typecasted_rectangle = {
                "type": str(rectangle["type"]),
                "coordinates": [
                    [float(coord) for coord in coord_list]
                    for coord_list in rectangle["coordinates"]
                ],
            }
            typecasted_data["background_rectangles"].append(typecasted_rectangle)
        except Exception as e:
            logger.error(
                f"Typecasting failed for {parameters_file_path} on background rectangle {i}: {str(e)}"
            )
            return None

    return typecasted_data


def check_internal_value_consistency(
    parameters_file_path: str, parameters_file: dict[str, Any]
) -> bool:
    """
    Validates logical constraints in parameters entries.
    Logs tolerable inconsistencies and prevents usage for critical issues.

    Args:
        parameters_file (list): List of dictionaries containing parameters entries.
        parameters_file_path (str): Path to the parameters file, used in log messages.

    Returns:
        True if the parameters file is usable (no critical issues, though warnings may be logged).
        False if the parameters file is unusable due to critical validation failures.
    """
    if parameters_file["number_of_spotfields"] < 1:
        logger.error(
            f"Internal inconsistency in {parameters_file_path}: number_of_spotfields cannot be below 1"
        )
        return False
    if parameters_file["columns_per_spotfield"] < 1:
        logger.error(
            f"Internal inconsistency in {parameters_file_path}: columns_per_spotfield cannot be below 1"
        )
        return False
    if parameters_file["spots_per_spotfield"] < 1:
        logger.error(
            f"Internal inconsistency in {parameters_file_path}: spots_per_spotfield cannot be below 1"
        )
        return False

    return True


def check_external_consistency(
    data_file: dict[str, List[dict[str, Any]]],
    parameters_file_path: str,
    parameters_file: dict[str, Any],
) -> bool:
    """
    Checks for consistency in format and values between the data_file and parameters_file.
    This is done because we define datasets by the presence of a data file, therefore every other file should fit to this data file.
    If this is not the case we can assume that files have been wrongly associated with one another and should therefore not be analyzed as one dataset.

    For this validation step it is important to understand what parameters is.
    Data represents a set of measurements, as a quality control measure samples may be printed in multiplicate.
    Parameters represents the summation of measurement data derived from multiple copies of the same sample.
    A core assumption of parameters files produced via MARTin is that all copies are placed at the same grid position.
    As such parameters may not be viable for every application of the MARTin software.
    The spot attribute of the data files represents the copy number and affiliated grid of a sample.

    Args:
        parameters_file (list): List of dictionaries containing parameters entries.
        parameters_file_path (str): Path to the parameters file, used in log messages.
        data_file (list): List of dictionaries containing data entries.

    Returns:
        bool
            - True if it is logical that the parameters_file has been derived from the data_file.
            - False if it is unlikely that the parameters_file has been derived from the data_file.
    """
    n_spot_fields = data_file["values"][-1]["spot"] + 1
    if n_spot_fields != parameters_file["number_of_spotfields"]:
        logging.error(
            f"Parameters file at {parameters_file_path} has different format than the data file of the same directory. Number of spot fields data: {n_spot_fields}, number of spot fields parameters: {parameters_file['number_of_spotfields']}"
        )
        return False

    n_spots = len(data_file["values"])
    n_spots_parameters = len(parameters_file["spots"])

    if n_spot_fields != parameters_file["number_of_spotfields"]:
        logging.error(
            f"Parameters file at {parameters_file_path} has different format than the data file of the same directory. Number of spot fields data: {n_spots}, number of spot fields parameters: {n_spots_parameters}"
        )
        return False

    return True


def typecast_to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return json.loads(value.lower())
    return bool(value)
