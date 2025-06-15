import pytest
from abc import ABC, abstractmethod
from typing import Dict, List
from unittest.mock import Mock, MagicMock
import ipywidgets as widgets

from src.suplex_modules.suplex_module_interface import *

class IncompleteModule(SuplexModuleInterface):
    @property
    def module_name(self) -> str:
        return "Incomplete"

class TestSuplexModuleInterface:
    """
    Only minimal ammount of tests here.
    Test should be written for each module explicitly.
    """
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            SuplexModuleInterface()
    
    def test_incomplete_implementation_raises_error(self):
        with pytest.raises(TypeError):
            IncompleteModule()
    
    def test_complete_implementation_works(self, test_suplex_module):
        module = test_suplex_module
        assert isinstance(module, SuplexModuleInterface)
    
    def test_all_abstract_methods_are_implemented(self, test_suplex_module):
        module = test_suplex_module
        
        assert hasattr(module, "module_name")
        assert hasattr(module, "module_version")
        assert hasattr(module, "group_name")
        assert hasattr(module, "button_style")
        assert hasattr(module, "check_if_viable")
        assert hasattr(module, "get_module_hover_text")
        assert hasattr(module, "initiate_module")
        assert hasattr(module, "reset_module")