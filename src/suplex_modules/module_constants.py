import os
from enum import Enum

# Root directory of SUPLEX modules. Based on the location of the module_constants file
DEFAULT_MODULE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# MARTin dictates the folder struction of its exports, by default this has a depth of three - zero beeing root dir.
DEFAULT_SEARCH_DEPTH = 4

# By default modules are python files
STANDARD_READOUT_FILE_TYPE = ".py"

# Defines the maximum allowable difference between float calculations for validation. Currently not used, maybe useful in future modules
TOLERANCE = 1e-6

# Default module group name for vanilla modules
VANILLA_MODULE = "Vanilla"


class SEARCH_MODE(Enum):
    """
    Enumeration of search modes for directory traversal.
    Identical to enum in martin_interface_constants.

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


class FILE(Enum):
    """
    Identificators for MARTin related files.

    Defines the strategies for searching directories:
    - DATA: Measurement of individual spots.
    - DATA_STATISTICS: Statistical analyses across spots of the same sample.
    - PARAMETERS: Information about the measurement such as positional data of every spot.
    - METADATA: More general information about the assay.
    - IMAGE: Whole image on which the measurement was conducted.
    - ANNOTATED_IMAGE: An annotated cutout of IMAGE depicting where exactly the measurement was conducted.
    - SUPLEX: A file allowing for storage of information between runs of the SUPLEX software.
    """

    DATA = "data"
    DATA_STATISTICS = "data_statistics"
    PARAMETERS = "parameters"
    METADATA = "metadata"
    IMAGE = "image"
    ANNOTATED_IMAGE = "annotated_image"
    SUPLEX = "suplex"


# Possible image extensions of images exported during a MARTin measurement.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

# Default ignore patterns for directories and files
DEFAULT_IGNORE_DIRS = {
    "__pycache__",
    ".ipynb_checkpoints",
    ".git",
    ".vscode",
    ".idea",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "node_modules",
    "venv",
    "env",
    ".venv",
    ".env",
    "build",
    "dist",
    ".coverage",
    "htmlcov",
    ".nox",
}
# Default ignore patterns for files
DEFAULT_IGNORE_FILES = {
    "__init__.py",
    "setup.py",
    "conftest.py",
    ".gitignore",
    ".gitattributes",
    "requirements.txt",
    "README.md",
    "LICENSE",
}
# Default ignore patterns for file extensions
DEFAULT_IGNORE_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".so", ".egg-info", ".dist-info"}
