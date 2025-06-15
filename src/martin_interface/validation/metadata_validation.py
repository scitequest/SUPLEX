import json
import logging
import copy
from datetime import datetime
import isodate
from typing import List, Optional, Any
from .basic_file_validation import *
from ..martin_interface_constants import METADATA_FIELDS_REQUIRED, PROJECT_FIELDS, INCUBATION_FIELDS

logger = logging.getLogger(__name__)

def try_get_validated_metadata(metadata_file_path: str) -> Optional[dict[str, Any]]:
    """
    Conducts a set of checks to validate a metadata file.
    Tolerable inconsistencies are logged, while intolerable issues prevent file loading.
    
    Args:
        metadata_file_path (str): Path to the Metadata file.
    
    Returns:
        dict: Metadata file as a dictionary; returned only if all checks pass.
        None: If the file is invalid or fails critical validation checks.
    """
    
    logging.debug(f"Initiated metadata file validation for {metadata_file_path}")
    
    metadata_file = try_get_valid_json(file_path = metadata_file_path)
    
    if metadata_file is None:
        return None

    # Metadata has two optional fields incubations and project, this generates a fitting keymap
    keymap = copy.deepcopy(METADATA_FIELDS_REQUIRED)
    if "project" in metadata_file.keys():
        keymap.update(PROJECT_FIELDS)
    if "incubations" not in metadata_file.keys():
        return None
    if metadata_file["incubations"]:
        keymap["incubations"] = [INCUBATION_FIELDS]
    
    is_key_structure_correct = is_Key_Structure_Identical(file_path = metadata_file_path, file = metadata_file, keymap = keymap)
    if not is_key_structure_correct:
        logger.error(f"Metadata file at {metadata_file_path} has not been loaded due to incorrect key structure")
        return None

    metadata_file = try_typecast_metadata_file(metadata_file_path = metadata_file_path, metadata_file = metadata_file)
    
    return metadata_file

def try_typecast_metadata_file(metadata_file_path: str, metadata_file: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Attempts to typecast metadata_file values to their correct format.
    
    Args:
        metadata_file_path (str): metadata_file_path used for logging error messages
        metadata_file (dict): JSON which is to be typecast

    Returns:
        Typecast dictionary if no error has been fired during the process.
        Returns None if Typecast of even a single value proved to be impossible.
    """
    try:
        typecasted_data = {
            "version": str(metadata_file["version"]),
            "datetime": datetime.fromisoformat(metadata_file["datetime"]),
            "patient": {},
            "image": {},
            "incubations": [],
            "project": {
                #Standard parameters, will be overwritten if measurement is part of a project.
                "name": "none",
                "description": ""
            }
        }
    except Exception as e:
        logger.error(f"Typecasting failed for general data of {metadata_file_path}: {str(e)}")
        return None

    try:
        typecasted_patient = {
            "id": str(metadata_file["patient"]["id"]),
            "name": str(metadata_file["patient"]["name"]),
            "tags": []
        }
        typecasted_tags = []
        for tag in metadata_file["patient"]["tags"]:
            typecasted_tags.append(str(tag))

        typecasted_patient["tags"] = typecasted_tags
        typecasted_data["patient"] = typecasted_patient
    except Exception as e:
        logger.error(f"Typecasting failed for patient data of {metadata_file_path}: {str(e)}")
        return None

    try:
        typecasted_image = {
            "created": datetime.fromisoformat(metadata_file["image"]["created"]),
            "imager": str(metadata_file["image"]["imager"]),
            "pixel_binning": int(metadata_file["image"]["pixel_binning"]),
            "exposure_time": isodate.parse_duration(metadata_file["image"]["exposure_time"])
        }
        typecasted_data["image"] = typecasted_image
    except Exception as e:
        logger.error(f"Typecasting failed for image data of {metadata_file_path}: {str(e)}")
        return None

    try:
        typecasted_incubations = []
        for incubation in metadata_file["incubations"]:
            typecasted_incubations.append(
                {
                    "solution": str(incubation["solution"]),
                    "stock_concentration": {
                        "value": float(incubation["stock_concentration"]["value"]),
                        "unit": str(incubation["stock_concentration"]["unit"])
                    },
                    "final_concentration": {
                        "value": float(incubation["final_concentration"]["value"]),
                        "unit": str(incubation["final_concentration"]["unit"])
                    },
                    "incubation_time": isodate.parse_duration(incubation["incubation_time"])
                }
            )
        typecasted_data["incubations"] = typecasted_incubations
    except Exception as e:
        logger.error(f"Typecasting failed for incubation data of {metadata_file_path}: {str(e)}")
        return None     

    if "project" in metadata_file.keys():
        try:
            typecasted_project = {
                "name": str(metadata_file["project"]["name"]),
                "description": str(metadata_file["project"]["description"])
            }
            typecasted_data["project"] = typecasted_project
        except Exception as e:
            logger.error(f"Typecasting failed for project data of {metadata_file_path}: {str(e)}")
            return None
    
    return typecasted_data
