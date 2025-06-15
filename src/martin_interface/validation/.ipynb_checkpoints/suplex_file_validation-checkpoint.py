# TODO: finish this once we have determined an actual suplex file format.

import json
import logging
from typing import List, Optional, Any
from .basic_file_validation import *
from ..constants import SUPLEX_FIELDS

logger = logging.getLogger(__name__)

def try_get_validated_suplex_file(suplex_file_path: str):
    """
    Conducts a set of checks to validate a suplex file.
    Tolerable inconsistencies are logged, while intolerable issues prevent file loading.
    
    Args:
        suplex_file_path (str): Path to the suplex file.
    
    Returns:
        dict: suplex file as a dictionary; returned only if all checks pass.
        None: If the file is invalid or fails critical validation checks.
    """
    
    logging.debug(f"Initiated suplex file validation for {suplex_file_path}")
    
    suplex_file = try_get_valid_json(suplex_file_path)
    
    if suplex_file is None:
        return None

    #is_key_structure_correct cannot be used here, since the suplex files are by nature dynamic in their content.

    

    suplex_file = try_typecast_suplex_file(suplex_file_path = suplex_file_path, suplex_file = suplex_file)
    
    return suplex_file

def try_typecast_suplex_file(suplex_file_path: str, suplex_file: dict[str, Any]):
    """
    Attempts to typecast suplex_file values to their correct format.
    
    Args:
        suplex_file_path: Filepath used for logging error messages
        suplex_file: JSON which is to be typecast

    Returns:
        Typecast dictionary if no error has been fired during the process.
        Returns None if Typecast of even a single value proved to be impossible.
    """
    return suplex_file
