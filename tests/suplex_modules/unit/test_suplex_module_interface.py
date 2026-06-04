import pytest
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import ipywidgets as widgets
import inspect

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset


class TestSuplexModuleInterface:
    # -------------------------------------------------------------------------
    # Abstract Contract
    # -------------------------------------------------------------------------
    def test_is_abstract_base_class(self):
        """SuplexModuleInterface cannot be instantiated directly (it is abstract)."""
        with pytest.raises(TypeError) as exc_info:
            SuplexModuleInterface()
        assert (
            "abstract" in str(exc_info.value).lower()
            or "instantiate" in str(exc_info.value).lower()
        )

    def test_has_all_required_abstract_members(self):
        """All required abstract properties and methods are declared in the interface."""
        abstract_members = {
            "module_name",
            "module_version",
            "group_name",
            "button_style",
            "check_if_viable",
            "get_module_hover_text",
            "initiate_module",
            "update_scheme",
            "reset_module",
        }

        # Get all abstract methods/properties from the ABC
        for name in abstract_members:
            assert hasattr(SuplexModuleInterface, name), f"Missing required member: {name}"
            attr = getattr(SuplexModuleInterface, name)
            assert getattr(attr, "__isabstractmethod__", False), f"{name} is not marked as abstract"

    # -------------------------------------------------------------------------
    # Test Fixture Validation
    # -------------------------------------------------------------------------
    def test_suplex_module_fixture_implements_interface(self, test_suplex_module):
        """The test_suplex_module fixture from conftest.py is a valid concrete implementation."""
        # Handle src-layout import differences between test and conftest
        assert any(
            base.__name__ == "SuplexModuleInterface" for base in type(test_suplex_module).__mro__
        )

        # Verify all required methods/properties are implemented (no abstract left)
        for name in dir(SuplexModuleInterface):
            if name.startswith("_") or name in ("__abstractmethods__", "__module__"):
                continue
            attr = getattr(SuplexModuleInterface, name, None)
            if getattr(attr, "__isabstractmethod__", False):
                concrete_attr = getattr(type(test_suplex_module), name)
                assert not getattr(concrete_attr, "__isabstractmethod__", False)

        # Basic smoke test of the fixture's implementation
        assert test_suplex_module.module_name == "TestModule"
        assert test_suplex_module.module_version == "1.0.0"
        assert test_suplex_module.group_name == "test"
        assert test_suplex_module.check_if_viable([]) is True
        assert test_suplex_module.get_module_hover_text() == "Description of module"

    # -------------------------------------------------------------------------
    # Type / Signature Sanity Checks
    # -------------------------------------------------------------------------
    def test_initiate_module_signature(self):
        """initiate_module has the expected signature."""
        sig = inspect.signature(SuplexModuleInterface.initiate_module)
        params = list(sig.parameters.keys())
        assert params == ["self", "datasets", "color_scheme"]
        assert sig.return_annotation == widgets.Box

    def test_check_if_viable_signature(self):
        """check_if_viable has the expected signature."""
        sig = inspect.signature(SuplexModuleInterface.check_if_viable)
        params = list(sig.parameters.keys())
        assert params == ["self", "datasets"]
        assert sig.return_annotation == bool
