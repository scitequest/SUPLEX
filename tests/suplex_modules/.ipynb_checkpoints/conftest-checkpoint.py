import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, List, Set, Any, Callable, Generator, Union, Tuple
from enum import Enum

from src.suplex_modules.suplex_module_interface import SuplexModuleInterface
import ipywidgets as widgets

@pytest.fixture
def mock_scandir_entry():
    def _create_mock_scandir_entry(name, is_dir=False, is_file=False, base_path="/test"):
        entry = Mock()
        entry.name = name
        entry.path = f"{base_path}/{name}"
        entry.is_dir.return_value = is_dir
        entry.is_file.return_value = is_file
        return entry
    return _create_mock_scandir_entry

@pytest.fixture
def test_suplex_module():
    """
    Return a standard TestSuplexModule instance
    """
    class TestSuplexModule(SuplexModuleInterface):
        def __init__(self, name: str = "TestModule", version: str = "1.0.0", group_name = "test",
                     button_colours: Dict[str, str] = {"font_color": "#000000", "button_color": "#FFFFFF"}):
            self._name = name
            self._version = version
            self._group_name = group_name
            self._button_colours = button_colours
    
        @property
        def module_name(self):
            return self._name
            
        @property
        def module_version(self):
            return self._version
    
        @property
        def group_name(self):
            return self._group_name
            
        @property
        def button_style(self) -> Dict[str, str]:
            return self._button_colours
            
        def check_if_viable(self, datasets: List[Any]) -> bool:
            return True
        
        def get_module_hover_text(self) -> str:
            return "Description of module"
        
        def initiate_module(self, datasets: [], ui: widgets.Box) -> None:
            pass
    
        def reset_module(self) -> "SuplexModuleInterface":
            pass
        
    return TestSuplexModule()