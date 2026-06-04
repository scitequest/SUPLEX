import pytest
import os
from pathlib import Path

from suplex_modules.module_constants import (
    DEFAULT_MODULE_DIRECTORY,
    DEFAULT_SEARCH_DEPTH,
    STANDARD_READOUT_FILE_TYPE,
    TOLERANCE,
    VANILLA_MODULE,
    SEARCH_MODE,
    FILE,
    IMAGE_EXTENSIONS,
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_FILES,
    DEFAULT_IGNORE_EXTENSIONS,
)


class TestModuleConstants:
    # -------------------------------------------------------------------------
    # Core Constants
    # -------------------------------------------------------------------------
    def test_default_module_directory(self):
        """DEFAULT_MODULE_DIRECTORY points to the directory containing module_constants.py."""
        assert DEFAULT_MODULE_DIRECTORY == str(Path(DEFAULT_MODULE_DIRECTORY).resolve())
        # It should be inside the suplex_modules folder
        assert "suplex_modules" in DEFAULT_MODULE_DIRECTORY.lower()

    def test_default_search_depth(self):
        """DEFAULT_SEARCH_DEPTH has the expected value."""
        assert DEFAULT_SEARCH_DEPTH == 4

    def test_standard_readout_file_type(self):
        """STANDARD_READOUT_FILE_TYPE is the expected Python file extension."""
        assert STANDARD_READOUT_FILE_TYPE == ".py"

    def test_tolerance(self):
        """TOLERANCE is the expected floating-point tolerance value."""
        assert TOLERANCE == 1e-6

    def test_vanilla_module_group(self):
        """VANILLA_MODULE constant matches the vanilla group name."""
        assert VANILLA_MODULE == "Vanilla"

    # -------------------------------------------------------------------------
    # SEARCH_MODE Enum
    # -------------------------------------------------------------------------
    def test_search_mode_enum_members(self):
        """SEARCH_MODE enum contains all expected members with correct values."""
        assert SEARCH_MODE.RECURSIVE.value == "recursive"
        assert SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM.value == "iterative_bounded_bottom"
        assert SEARCH_MODE.ITERATIVE_BOUNDED_ALL.value == "iterative_bounded_all"
        assert SEARCH_MODE.ITERATIVE_UNBOUND.value == "iterative_unbound"

        assert len(list(SEARCH_MODE)) == 4

    # -------------------------------------------------------------------------
    # FILE Enum
    # -------------------------------------------------------------------------
    def test_file_enum_members(self):
        """FILE enum contains all expected MARTin file type identifiers."""
        assert FILE.DATA.value == "data"
        assert FILE.DATA_STATISTICS.value == "data_statistics"
        assert FILE.PARAMETERS.value == "parameters"
        assert FILE.METADATA.value == "metadata"
        assert FILE.IMAGE.value == "image"
        assert FILE.ANNOTATED_IMAGE.value == "annotated_image"
        assert FILE.SUPLEX.value == "suplex"

        assert len(list(FILE)) == 7

    # -------------------------------------------------------------------------
    # Image Extensions and Ignore Patterns
    # -------------------------------------------------------------------------
    def test_image_extensions(self):
        """IMAGE_EXTENSIONS contains all supported image file extensions."""
        expected = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
        assert IMAGE_EXTENSIONS == expected

    def test_default_ignore_dirs(self):
        """DEFAULT_IGNORE_DIRS contains the standard set of directories to ignore."""
        assert "__pycache__" in DEFAULT_IGNORE_DIRS
        assert ".git" in DEFAULT_IGNORE_DIRS
        assert ".pytest_cache" in DEFAULT_IGNORE_DIRS
        assert "node_modules" in DEFAULT_IGNORE_DIRS
        assert "venv" in DEFAULT_IGNORE_DIRS
        # Spot-check a few more
        assert len(DEFAULT_IGNORE_DIRS) >= 18

    def test_default_ignore_files(self):
        """DEFAULT_IGNORE_FILES contains common files that should be skipped."""
        assert "__init__.py" in DEFAULT_IGNORE_FILES
        assert "conftest.py" in DEFAULT_IGNORE_FILES
        assert ".gitignore" in DEFAULT_IGNORE_FILES
        assert "README.md" in DEFAULT_IGNORE_FILES
        assert len(DEFAULT_IGNORE_FILES) >= 8

    def test_default_ignore_extensions(self):
        """DEFAULT_IGNORE_EXTENSIONS contains compiled Python and package files to ignore."""
        assert ".pyc" in DEFAULT_IGNORE_EXTENSIONS
        assert ".pyo" in DEFAULT_IGNORE_EXTENSIONS
        assert ".egg-info" in DEFAULT_IGNORE_EXTENSIONS
        assert len(DEFAULT_IGNORE_EXTENSIONS) >= 6
