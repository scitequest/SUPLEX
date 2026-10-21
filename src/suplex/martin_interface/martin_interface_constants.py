from enum import Enum

# MARTin dictates the folder struction of its exports, by default this has a depth of three - zero beeing root dir.
MARTIN_MEASURE_DIR_DEPTH = 3

# Minimum requirement for a MARTin measurement to be detected as such.
STANDARD_READOUT_FILES = ["data.json", "data.tsv"]

# Defines the maximum allowable difference between float calculations for validation.
TOLERANCE = 1e-6


class SEARCH_MODE(Enum):
    """
    Enumeration of search modes for directory traversal.

    Defines the strategies for searching directories:
    - RECURSIVE: Search an entire directory for files recursively.
    - ITERATIVE_BOUNDED_BOTTOM: Traverse a directory to a defined depth and search for files at the bottom.
    - ITERATIVE_BOUNDED_ALL: Traverse a directory to a defined depth and search for files at every subdirectory.
    - ITERATIVE_UNBOUND: Search an entire directory for files iterativeley.
    """

    RECURSIVE = "recursive"
    ITERATIVE_BOUNDED_BOTTOM = "iterative_bounded_bottom"
    ITERATIVE_BOUNDED_ALL = "iterative_bounded_all"
    ITERATIVE_UNBOUND = "iterative_unbound"


# Possible image extensions of images exported during a MARTin measurement.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

# Fields and types of MARTin data files. Applicable to both JSONs and TSVs.
DATA_FIELDS = {
    "values": [
        {
            "mean_minus_min": float,
            "normalized_mean": float,
            "spot": int,
            "row": int,
            "col": int,
            "min": float,
            "max": float,
            "mean": float,
            "std_deviation": float,
        }
    ]
}

# Fields and types of MARTin data_statistics files. Applicable to both JSONs and TSVs.
DATA_STATISTICS_FIELDS = {
    "values": [
        {
            "row": int,
            "col": int,
            "adjusted_average": float,
            "adjusted_average_std_deviation": float,
            "relative_adjusted_average_std_deviation": float,
            "normalized_average": float,
            "normalized_average_std_deviation": float,
            "relative_normalized_average_std_deviation": float,
        }
    ]
}
# Fields and types of MARTin parameters files if the shape of the measure fields are polygonal.
PARAMETERS_FIELDS_POLYGON = {
    "invert_lut": bool,
    "subtract_background": bool,
    "number_of_spotfields": int,
    "columns_per_spotfield": int,
    "spots_per_spotfield": int,
    "spots": [{"type": str, "coordinates": [[float]]}],
    "background_rectangles": [{"type": str, "coordinates": [[float]]}],
}
# Fields and types of MARTin parameters files if the shape of the measure fields are circles.
PARAMETERS_FIELDS_CIRCLE = {
    "invert_lut": bool,
    "subtract_background": bool,
    "number_of_spotfields": int,
    "columns_per_spotfield": int,
    "spots_per_spotfield": int,
    "spots": [{"type": str, "position": [[float]], "diameter": float}],
    "background_rectangles": [{"type": str, "coordinates": [[float]]}],
}

METADATA_FIELDS_REQUIRED = {
    "version": str,
    "datetime": str,
    "patient": {"id": str, "name": str, "tags": [str]},
    "image": {
        "created": str,
        "imager": str,
        "pixel_binning": int,
        "exposure_time": str,
    },
    "incubations": [],
}

# PROJECT_FIELDS and INCUBATION_FIELDS are both optional parts of metadata.
PROJECT_FIELDS = {"project": {"name": str, "description": str}}

INCUBATION_FIELDS = {
    "solution": str,
    "stock_concentration": {"value": float, "unit": str},
    "final_concentration": {"value": float, "unit": str},
    "incubation_time": str,
}
# Internal storage function for each module. Only Vanilla modules are checked.
SUPLEX_FIELDS = {"tags": [str], "row_labels": [str], "col_labels": [str]}
