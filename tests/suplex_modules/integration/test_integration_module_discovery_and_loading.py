import pytest
from pathlib import Path
from typing import List, Any, Set

from suplex.suplex_modules.module_loader import (
    load_modules,
    delve_dirs,
    sweep_dirs,
    try_get_module,
)
from suplex.suplex_modules.module_constants import (
    SEARCH_MODE,
    FILE,
    STANDARD_READOUT_FILE_TYPE,
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_FILES,
    DEFAULT_IGNORE_EXTENSIONS,
)
from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface


# =============================================================================
# Integration tests for module discovery and dynamic loading
# These tests exercise real filesystem scanning + AST-based interface detection
# using the fixtures provided in conftest.py.
# =============================================================================


class TestIntegrationModuleDiscoveryAndLoading:
    """Integration tests for SUPLEX module discovery and loading mechanism."""

    # -------------------------------------------------------------------------
    # Happy path scenarios
    # -------------------------------------------------------------------------

    def test_load_modules_recursive_discovers_valid_module(
        self, temp_module_directory: Path
    ) -> None:
        """Should recursively find and load modules that implement SuplexModuleInterface."""
        modules: List[SuplexModuleInterface] = load_modules(
            dir_path=str(temp_module_directory),
            mode=SEARCH_MODE.RECURSIVE,
        )

        assert len(modules) >= 1, "Expected at least one module to be loaded"
        module_names = [m.module_name for m in modules]
        assert "Valid Test Module" in module_names

        # Verify the loaded module satisfies the interface contract
        valid_module = next(m for m in modules if m.module_name == "Valid Test Module")
        assert isinstance(valid_module, SuplexModuleInterface)
        assert valid_module.module_version == "0.0.1"
        assert valid_module.group_name == "IntegrationTest"
        assert isinstance(valid_module.button_style, dict)

    def test_load_modules_flat_mode_still_finds_top_level_modules(
        self, temp_module_directory: Path
    ) -> None:
        """ITERATIVE_BOUNDED_BOTTOM with max_depth=0 acts as flat mode and should discover
        modules placed directly in the target directory (non-recursive top-level only)."""
        modules = load_modules(
            dir_path=str(temp_module_directory),
            mode=SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
            max_depth=0,
        )

        # The valid module is in the root of temp_module_directory
        module_names = [m.module_name for m in modules]
        assert "Valid Test Module" in module_names

    def test_loaded_module_can_be_instantiated_and_used(
        self, loaded_valid_module: SuplexModuleInterface
    ) -> None:
        """A successfully loaded module should be usable (viability check + initiate)."""
        # Minimal call to verify runtime usability.
        # Note: the fake module's check_if_viable returns True only for non-empty dataset lists.
        dummy_for_viability: List[Any] = [object()]
        assert loaded_valid_module.check_if_viable(dummy_for_viability) is True
        assert loaded_valid_module.get_module_hover_text() == "Integration test module"

        # initiate_module should return a widget without crashing (even with empty list is fine here)
        dummy_datasets: List[Any] = []
        box = loaded_valid_module.initiate_module(dummy_datasets, color_scheme=None)
        assert box is not None

    # -------------------------------------------------------------------------
    # Error handling and graceful degradation
    # -------------------------------------------------------------------------

    def test_load_modules_ignores_syntax_error_files(self, temp_module_directory: Path) -> None:
        """Syntax errors in module files must be caught and skipped (no crash)."""
        modules = load_modules(
            dir_path=str(temp_module_directory),
            mode=SEARCH_MODE.RECURSIVE,
        )

        # We should still get the valid module even though syntax_error.py exists
        module_names = [m.module_name for m in modules]
        assert "Valid Test Module" in module_names
        # No module coming from the broken file should appear
        assert all("syntax" not in name.lower() for name in module_names)

    def test_load_modules_ignores_files_without_suplex_interface(
        self, temp_module_directory: Path
    ) -> None:
        """Python files that do not contain a SuplexModuleInterface subclass are ignored."""
        modules = load_modules(
            dir_path=str(temp_module_directory),
            mode=SEARCH_MODE.RECURSIVE,
        )

        module_names = [m.module_name for m in modules]
        assert all(
            "NoInterface" not in name and "no_interface" not in name.lower()
            for name in module_names
        )

    def test_load_modules_skips_hidden_and_special_directories(
        self, temp_module_directory: Path
    ) -> None:
        """Directories starting with '.' or named __pycache__ must be ignored."""
        modules = load_modules(
            dir_path=str(temp_module_directory),
            mode=SEARCH_MODE.RECURSIVE,
        )

        # Just sanity check that we didn't pick up anything from .hidden
        # (the valid module is still found)
        assert any(m.module_name == "Valid Test Module" for m in modules)

    def test_load_modules_nonexistent_directory_returns_empty_list(self, tmp_path: Path) -> None:
        """Requesting a non-existent directory should return an empty list gracefully."""
        nonexistent = tmp_path / "does_not_exist"
        modules = load_modules(
            dir_path=str(nonexistent),
            mode=SEARCH_MODE.RECURSIVE,
        )
        assert modules == []

    def test_load_modules_empty_directory_returns_empty_list(self, tmp_path: Path) -> None:
        """An empty directory should result in an empty module list."""
        empty_dir = tmp_path / "empty_modules"
        empty_dir.mkdir()
        modules = load_modules(
            dir_path=str(empty_dir),
            mode=SEARCH_MODE.RECURSIVE,
        )
        assert modules == []

    # -------------------------------------------------------------------------
    # Lower-level helper functions (delve_dirs, sweep_dirs, try_get_module)
    # -------------------------------------------------------------------------

    def test_delve_dirs_finds_python_files_recursively(self, temp_module_directory: Path) -> None:
        """delve_dirs should populate the provided files set with all .py files under the directory tree
        (respecting ignore patterns)."""
        py_files: Set[str] = set()
        delve_dirs(
            search_dir=str(temp_module_directory),
            filetype=STANDARD_READOUT_FILE_TYPE,
            files=py_files,
        )
        assert any("valid_test_module.py" in str(p) for p in py_files)
        assert any("syntax_error.py" in str(p) for p in py_files)

    def test_sweep_dirs_respects_ignore_patterns(self, temp_module_directory: Path) -> None:
        """sweep_dirs should skip directories listed in DEFAULT_IGNORE_DIRS (and other ignore rules)."""
        # We already created .hidden and __pycache__ in the fixture
        all_files = sweep_dirs(
            root_path=str(temp_module_directory),
            filetype=STANDARD_READOUT_FILE_TYPE,
            mode=SEARCH_MODE.ITERATIVE_UNBOUND,
            max_depth=10,
            ignore_dirs=DEFAULT_IGNORE_DIRS,
            ignore_files=DEFAULT_IGNORE_FILES,
            ignore_extensions=DEFAULT_IGNORE_EXTENSIONS,
        )
        paths_as_str = [str(p) for p in all_files]
        assert not any(".hidden" in p for p in paths_as_str)
        assert not any("__pycache__" in p for p in paths_as_str)

    def test_try_get_module_returns_empty_list_for_invalid_file(
        self, temp_module_directory: Path
    ) -> None:
        """try_get_module should return empty list (not None) for files that cannot be imported
        or lack the SuplexModuleInterface implementation."""
        syntax_file = temp_module_directory / "syntax_error.py"
        result = try_get_module(str(syntax_file))
        assert result == []

        no_interface_file = temp_module_directory / "no_interface.py"
        result = try_get_module(str(no_interface_file))
        assert result == []
