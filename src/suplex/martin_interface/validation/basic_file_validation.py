import json
import csv
import os
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)


def get_data_file(file_path: str) -> Optional[dict[str, List]]:
    """
    Validates if a file is a JSON or TSV in the format of data or data_statistics and converts it to a list of dictionaries.

    Args:
        file_path (str): Path to the data file or data_statistics file.

    Returns:
        list: File as a dictionary; returned if all checks pass.
        None: If the file is invalid (e.g., wrong format, missing required structure, or not found).
    """
    if file_path is None:
        return None

    if not os.path.isfile(file_path):
        logging.error(f"Selected path {file_path} is not a file")
        return None

    data_file = try_get_valid_json(file_path=file_path)
    if data_file is not None:
        return data_file

    data_file = try_get_valid_tsv_as_dicts(file_path=file_path)
    if data_file is not None:
        # This makes tsv data the same format as json data.
        return {"values": data_file}

    logging.error(f"Selected file {file_path} cannot be read as JSON or TSV")
    return None


def try_get_valid_json(file_path: str) -> Optional[dict[str, Any]]:
    """
    Attempts to load a JSON file and verify it has a dictionary as its top-level structure.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: The loaded JSON data if valid and a dictionary at the top level.
        None: If the file isn’t a JSON, can’t be loaded, or isn’t a dictionary.
    """
    if not file_path:
        return None

    if not file_path.lower().endswith(".json"):
        return None

    logger.debug(f"Attempting to load JSON from {file_path}")
    try:
        with open(file_path, "r") as file:
            file_data = json.load(file)
        if not isinstance(file_data, dict):
            logger.error(f"JSON at {file_path} is not a dictionary at the top level")
            return None
        logger.debug(f"Successfully loaded JSON from {file_path}")
        return file_data
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {str(e)}")
        return None


def try_get_valid_tsv_as_dicts(file_path: str) -> Optional[List[dict[str, Any]]]:
    """
    Attempts to load a TSV file and convert it to a list of dictionaries.

    Args:
        file_path (str): Path to the TSV file.

    Returns:
        list: List of dictionaries if the TSV is valid.
        None: If the file isn’t a TSV, can’t be loaded, or lacks headers.
    """
    if not file_path.lower().endswith(".tsv"):
        return None

    logger.debug(f"Attempting to load TSV from {file_path}")
    try:
        with open(file_path, "r", newline="") as file:
            reader = csv.DictReader(file, delimiter="\t")
            if not reader.fieldnames:
                logger.error(f"TSV at {file_path} has no headers")
                return None
            data = list(reader)
            logger.debug(f"Successfully loaded TSV from {file_path}")
            return data
    except Exception as e:
        logger.error(f"Failed to load TSV from {file_path}: {str(e)}")
        return None


def is_Key_Structure_Identical(
    file_path: str, file: dict[str, Any], keymap: dict[str, Any]
) -> bool:
    """
    Checks if the key structure of a dictionary matches a reference keymap.
    The order of keys is not regarded during this check.
    Args:
        file_path (str): Path to the file (for logging purposes).
        file (dict): The dictionary to check.
        keymap (dict): The reference keymap to compare against. Assumed to be a constant with valid structure
                       (non-empty lists contain at least one element, contains only dicts, lists, or primitives).
    Returns:
        bool: True if the key structure matches, False otherwise.
    """
    if not isinstance(file, dict):
        logger.error(f"Top level of {file_path} is not a dictionary")
        return False

    # Check keys while disregarding their order.
    if not set(file.keys()) == set(keymap.keys()):
        logger.error(
            f"Key mismatch in: {file_path}. Expected: {keymap.keys()}. Received: {file.keys()}"
        )
        return False

    for key, content in keymap.items():
        if isinstance(content, list):
            # Structure has to be the same as keymap
            if not isinstance(file[key], list):
                return False
            # If list is empty in file skip further checks
            if not file[key]:
                continue
            if isinstance(content[0], dict):
                # Structure has to be the same as keymap
                if not isinstance(file[key][0], dict):
                    return False
                sub_is_identical = is_Key_Structure_Identical(file_path, file[key][0], content[0])
                if not sub_is_identical:
                    return False
                list_is_uniform = is_dict_list_uniform(file_path, file[key])
                if not list_is_uniform:
                    return False
        elif isinstance(content, dict):
            if not isinstance(file[key], dict):
                return False
            sub_is_identical = is_Key_Structure_Identical(file_path, file[key], keymap[key])
            if not sub_is_identical:
                return False
        else:
            if key not in file:
                return False
            # content of keymap is not list or dict so file has to adhere as well
            if isinstance(file[key], list) or isinstance(file[key], dict):
                return False

    return True


def is_dict_list_uniform(file_path: str, file: List[dict[str, Any]]) -> bool:
    """
    Checks if all dictionaries in a list have the same keys.

    Args:
        file_path (str): Path to the file (for logging purposes).
        file (list): List of dictionaries to check.

    Returns:
        bool: True if all dictionaries have identical keys, False otherwise.
    """
    keys = file[0].keys()
    for i, entry in enumerate(file):
        if keys != entry.keys():
            logger.error(
                f"{file_path} data is not uniform. Entry {i} has keys {entry.keys()} differing from first entry {keys}"
            )
            return False
    return True
