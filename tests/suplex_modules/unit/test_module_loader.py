from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from suplex.suplex_modules.module_constants import (
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_EXTENSIONS,
    DEFAULT_IGNORE_FILES,
    SEARCH_MODE,
)
from suplex.suplex_modules.module_loader import (
    delve_dirs,
    has_suplex_interface_classes,
    is_valid_suplex_module_class,
    load_modules,
    should_collect_at_depth,
    should_ignore_directory,
    should_ignore_file,
    sweep_dirs,
    try_get_module,
)
from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface


class TestModuleLoader:
    """Unit tests for module_loader.py – discovers, validates, and loads SUPLEX modules from the filesystem."""

    # -------------------------------------------------------------------------
    # Core Loading Functions
    # -------------------------------------------------------------------------
    def test_load_modules_recursive_mode(self, mock_scandir_entry):
        """load_modules with RECURSIVE mode collects files via delve_dirs and instantiates modules."""
        with (
            patch("suplex.suplex_modules.module_loader.delve_dirs") as mock_delve,
            patch(
                "suplex.suplex_modules.module_loader.try_get_module", return_value=[Mock()]
            ) as mock_try,
        ):
            mock_delve.side_effect = lambda *a, **k: k["files"].update(["/test/module1.py"])

            result = load_modules(dir_path="/test", mode=SEARCH_MODE.RECURSIVE)

            assert len(result) == 1
            mock_delve.assert_called_once()
            mock_try.assert_called()

    def test_load_modules_sweep_modes(self):
        """load_modules dispatches correctly to sweep_dirs for non-RECURSIVE modes."""
        for mode in [
            SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
            SEARCH_MODE.ITERATIVE_BOUNDED_ALL,
            SEARCH_MODE.ITERATIVE_UNBOUND,
        ]:
            with (
                patch("suplex.suplex_modules.module_loader.sweep_dirs") as mock_sweep,
                patch(
                    "suplex.suplex_modules.module_loader.try_get_module", return_value=[]
                ) as mock_try,
            ):
                mock_sweep.return_value = set()
                load_modules(dir_path="/test", mode=mode, max_depth=2)
                mock_sweep.assert_called_once()

    def test_load_modules_with_empty_modules(self, mock_scandir_entry):
        """load_modules returns empty list when try_get_module returns no valid modules."""
        with (
            patch("suplex.suplex_modules.module_loader.delve_dirs") as mock_delve,
            patch("suplex.suplex_modules.module_loader.try_get_module", return_value=[]),
        ):
            mock_delve.side_effect = lambda *a, **k: k["files"].update(["/test/empty.py"])

            result = load_modules(dir_path="/test")
            assert result == []

    # -------------------------------------------------------------------------
    # Directory Traversal
    # -------------------------------------------------------------------------
    def test_delve_dirs_respects_ignore_patterns(self, mock_scandir_entry):
        """delve_dirs skips ignored directories, files, and extensions."""
        files = set()
        mock_entries = [
            mock_scandir_entry("__pycache__", is_dir=True),
            mock_scandir_entry("valid_module.py", is_file=True),
            mock_scandir_entry("ignored.txt", is_file=True),
            mock_scandir_entry(".hidden.py", is_file=True),
        ]

        with patch("os.scandir") as mock_scandir:
            mock_scandir.return_value.__enter__.return_value = mock_entries
            delve_dirs(
                search_dir="/test",
                filetype=".py",
                files=files,
                ignore_dirs={"__pycache__"},
                ignore_files={"ignored.txt"},
                ignore_extensions={".txt"},
            )

        assert len(files) == 1
        assert any("valid_module.py" in f for f in files)

    def test_sweep_dirs_iterative_modes(self, mock_scandir_entry):
        """sweep_dirs correctly handles ITERATIVE_BOUNDED_* and ITERATIVE_UNBOUND modes."""
        for mode in [
            SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
            SEARCH_MODE.ITERATIVE_BOUNDED_ALL,
            SEARCH_MODE.ITERATIVE_UNBOUND,
        ]:
            result = sweep_dirs(
                root_path="/test",
                filetype=".py",
                mode=mode,
                max_depth=2,
                ignore_dirs=set(),
                ignore_files=set(),
                ignore_extensions=set(),
            )
            assert isinstance(result, set)

    def test_permission_error_handling_in_delve_and_sweep(self):
        """Both delve_dirs and sweep_dirs gracefully handle PermissionError."""
        with patch("os.scandir", side_effect=PermissionError):
            files = set()
            delve_dirs(search_dir="/restricted", filetype=".py", files=files)
            assert not files

            result = sweep_dirs(
                root_path="/restricted",
                filetype=".py",
                mode=SEARCH_MODE.ITERATIVE_UNBOUND,
                max_depth=1,
                ignore_dirs=set(),
                ignore_files=set(),
                ignore_extensions=set(),
            )
            assert not result

    # -------------------------------------------------------------------------
    # Ignore Helpers
    # -------------------------------------------------------------------------
    def test_should_ignore_directory(self):
        """should_ignore_directory correctly identifies directories to skip."""
        assert should_ignore_directory("__pycache__", DEFAULT_IGNORE_DIRS) is True
        assert should_ignore_directory(".git", DEFAULT_IGNORE_DIRS) is True
        assert should_ignore_directory("node_modules", DEFAULT_IGNORE_DIRS) is True
        assert should_ignore_directory("cache_dir", set()) is True
        assert should_ignore_directory("normal_dir", set()) is False

    def test_should_ignore_file(self):
        """should_ignore_file correctly identifies files to skip."""
        assert (
            should_ignore_file("__init__.py", DEFAULT_IGNORE_FILES, DEFAULT_IGNORE_EXTENSIONS)
            is True
        )
        assert should_ignore_file("test_module.py", set(), set()) is True
        assert should_ignore_file(".hidden.py", set(), set()) is True
        assert should_ignore_file("module.pyc", set(), DEFAULT_IGNORE_EXTENSIONS) is True
        assert should_ignore_file("backup~", set(), set()) is True
        assert should_ignore_file("normal_module.py", set(), set()) is False

    def test_should_collect_at_depth(self):
        """should_collect_at_depth returns correct result per SEARCH_MODE."""
        assert should_collect_at_depth(SEARCH_MODE.ITERATIVE_UNBOUND, 5, 10) is True
        assert should_collect_at_depth(SEARCH_MODE.ITERATIVE_BOUNDED_ALL, 3, 5) is True
        assert should_collect_at_depth(SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM, 5, 5) is True
        assert should_collect_at_depth(SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM, 4, 5) is False

    # -------------------------------------------------------------------------
    # Module Validation (AST + Dynamic Loading)
    # -------------------------------------------------------------------------
    def test_has_suplex_interface_classes(self):
        """has_suplex_interface_classes correctly detects SuplexModuleInterface usage via AST."""
        # These test files are part of your existing test_data – they are kept for real-world validation
        valid_path = (
            Path(__file__).parent.parent.parent.parent
            / "test_data/test_modules/valid_modules/valid_suplex_module.py"
        )
        if valid_path.exists():
            assert has_suplex_interface_classes(str(valid_path)) is True

        invalid_path = (
            Path(__file__).parent.parent.parent.parent
            / "test_data/test_modules/invalid_modules/no_inheritance_suplex_module.py"
        )
        if invalid_path.exists():
            assert has_suplex_interface_classes(str(invalid_path)) is False

    def test_try_get_module_success(self, test_suplex_module):
        """try_get_module successfully loads and instantiates a valid Suplex module."""
        fake_module = Mock()
        fake_module.TestModule = test_suplex_module.__class__

        with (
            patch(
                "suplex.suplex_modules.module_loader.has_suplex_interface_classes",
                return_value=True,
            ),
            patch(
                "suplex.suplex_modules.module_loader.is_valid_suplex_module_class",
                return_value=True,
            ),
        ):
            mock_spec = MagicMock()
            mock_spec.loader = Mock()

            with (
                patch("importlib.util.spec_from_file_location", return_value=mock_spec),
                patch("importlib.util.module_from_spec", return_value=fake_module),
                patch(
                    "inspect.getmembers",
                    return_value=[("TestModule", test_suplex_module.__class__)],
                ),
            ):
                modules = try_get_module("/fake/test_module.py")
                assert len(modules) == 1
                assert isinstance(modules[0], test_suplex_module.__class__)

    def test_try_get_module_invalid_file(self):
        """try_get_module returns empty list for files without a SuplexModuleInterface."""
        with patch(
            "suplex.suplex_modules.module_loader.has_suplex_interface_classes", return_value=False
        ):
            assert try_get_module("/fake/invalid.py") == []

    def test_is_valid_suplex_module_class(self, test_suplex_module):
        """is_valid_suplex_module_class validates only proper plugin classes."""

        # Create a simple valid class with proper module name for testing
        class ValidSuplexModule(SuplexModuleInterface):
            pass

        ValidSuplexModule.__module__ = "test_module"

        assert (
            is_valid_suplex_module_class(ValidSuplexModule, "test_module", SuplexModuleInterface)
            is True
        )

        class NotASuplex:
            pass

        assert (
            is_valid_suplex_module_class(NotASuplex, "test_module", SuplexModuleInterface) is False
        )

        assert (
            is_valid_suplex_module_class(
                SuplexModuleInterface, "test_module", SuplexModuleInterface
            )
            is False
        )
