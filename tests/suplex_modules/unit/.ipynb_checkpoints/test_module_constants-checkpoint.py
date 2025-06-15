import pytest
import os
import tempfile
from pathlib import Path
from enum import Enum
from unittest.mock import patch, MagicMock

from src.suplex_modules.module_constants import *

class TestModuleConstants:
    def test_default_search_depth(self):
        assert DEFAULT_SEARCH_DEPTH == 4
        assert isinstance(DEFAULT_SEARCH_DEPTH, int)
        assert DEFAULT_SEARCH_DEPTH > 0
    
    def test_standard_readout_file_type(self):
        assert STANDARD_READOUT_FILE_TYPE == ".py"
        assert isinstance(STANDARD_READOUT_FILE_TYPE, str)
        assert STANDARD_READOUT_FILE_TYPE.startswith(".")
    
    def test_tolerance(self):
        assert TOLERANCE == 1e-6
        assert isinstance(TOLERANCE, float)
        assert TOLERANCE > 0
        assert TOLERANCE < 1

    def test_vanilla_module(self):
        assert VANILLA_MODULE == "Vanilla"
        assert isinstance(VANILLA_MODULE, str)
    
    def test_default_module_directory_type(self):
        assert isinstance(DEFAULT_MODULE_DIRECTORY, str)
        assert len(DEFAULT_MODULE_DIRECTORY) > 0
        # Should be an absolute path
        assert os.path.isabs(DEFAULT_MODULE_DIRECTORY)
        
    def test_search_mode_enum(self):
        assert issubclass(SEARCH_MODE, Enum)
        
        assert hasattr(SEARCH_MODE, 'RECURSIVE')
        assert hasattr(SEARCH_MODE, 'ITERATIVE_BOUNDED_BOTTOM')
        assert hasattr(SEARCH_MODE, 'ITERATIVE_BOUNDED_ALL')
        assert hasattr(SEARCH_MODE, 'ITERATIVE_UNBOUND')
        
        assert SEARCH_MODE.RECURSIVE.value == "recursive"
        assert SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM.value == "iterative_bounded_bottom"
        assert SEARCH_MODE.ITERATIVE_BOUNDED_ALL.value == "iterative_bounded_all"
        assert SEARCH_MODE.ITERATIVE_UNBOUND.value == "iterative_unbound"
        
        assert len(SEARCH_MODE) == 4
        
    def test_image_extensions(self):
        assert isinstance(IMAGE_EXTENSIONS, set)
        assert len(IMAGE_EXTENSIONS) == 5
        assert all(isinstance(ext, str) for ext in IMAGE_EXTENSIONS)
        assert IMAGE_EXTENSIONS == {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
     
    def test_ignore_dirs(self):
        assert isinstance(DEFAULT_IGNORE_DIRS, set)
        assert len(DEFAULT_IGNORE_DIRS) == 18
        assert all(isinstance(ext, str) for ext in DEFAULT_IGNORE_DIRS)
        
        expected_dirs = {
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
            ".nox"
        }
        assert all(expected_dir in DEFAULT_IGNORE_DIRS for expected_dir in expected_dirs)
    
    def test_ignore_files(self):
        assert isinstance(DEFAULT_IGNORE_FILES, set)
        assert len(DEFAULT_IGNORE_FILES) == 8
        assert all(isinstance(ext, str) for ext in DEFAULT_IGNORE_FILES)

        expected_files = {
            "__init__.py",
            "setup.py",
            "conftest.py",
            ".gitignore",
            ".gitattributes",
            "requirements.txt",
            "README.md",
            "LICENSE"
        }
        assert all(expected_file in DEFAULT_IGNORE_FILES for expected_file in expected_files)

    def test_ignore_files(self):
        assert isinstance(DEFAULT_IGNORE_EXTENSIONS, set)
        assert len(DEFAULT_IGNORE_EXTENSIONS) == 6
        assert all(isinstance(ext, str) for ext in DEFAULT_IGNORE_EXTENSIONS)

        expected_extensions = {
            ".pyc",
            ".pyo",  
            ".pyd",
            ".so",
            ".egg-info",
            ".dist-info"
        }
        assert all(expected_extension in DEFAULT_IGNORE_EXTENSIONS for expected_extension in expected_extensions)
    
    def test_file_type_consistency(self):
        assert STANDARD_READOUT_FILE_TYPE not in DEFAULT_IGNORE_EXTENSIONS