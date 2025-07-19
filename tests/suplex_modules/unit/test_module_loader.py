import pytest
import os
import sys
import ast
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open, MagicMock, call
from pathlib import Path
from collections import deque
from enum import Enum
from contextlib import contextmanager
from src.suplex_modules.module_loader import *
from src.suplex_modules.module_constants import *


class TestLoadModules:
    @patch("src.suplex_modules.module_loader.try_get_module")
    @patch("src.suplex_modules.module_loader.sweep_dirs")
    @patch("src.suplex_modules.module_loader.delve_dirs")
    def test_load_modules(self, mock_delve_dirs, mock_sweep_dirs, mock_try_get_module):
        # Simulates found files
        def delve_dirs_side_effect(search_dir, filetype, files, **kwargs):
            files.update(["/test/module1.py", "/test/module2.py"])
            return files

        mock_delve_dirs.side_effect = delve_dirs_side_effect

        # Simulates successfully loaded modules
        mock_module1 = Mock()
        mock_module2 = Mock()
        mock_try_get_module.side_effect = [[mock_module1], [mock_module2]]

        # Call search methods
        result = load_modules(dir_path="/test", mode=SEARCH_MODE.RECURSIVE)

        assert len(result) == 2
        assert mock_module1 in result
        assert mock_module2 in result
        mock_delve_dirs.assert_called()

        mock_delve_dirs.reset_mock()
        mock_sweep_dirs.reset_mock()
        mock_try_get_module.reset_mock()
        mock_try_get_module.side_effect = [[mock_module1], [mock_module2]]

        mock_sweep_dirs.return_value = {"/test/module1.py", "/test/module2.py"}

        result = load_modules(dir_path="/test", mode=SEARCH_MODE.ITERATIVE_UNBOUND)

        assert len(result) == 2
        assert mock_module1 in result
        assert mock_module2 in result
        mock_delve_dirs.assert_not_called()
        mock_sweep_dirs.assert_called()

    @patch("src.suplex_modules.module_loader.try_get_module")
    @patch("src.suplex_modules.module_loader.sweep_dirs")
    def test_load_modules_iterative_mode(self, mock_sweep_dirs, mock_try_get_module):
        mock_sweep_dirs.return_value = {"/test/module1.py", "/test/module2.py"}

        mock_module1 = Mock()
        mock_module2 = Mock()
        mock_try_get_module.side_effect = [[mock_module1], [mock_module2]]

        result = load_modules(
            dir_path="/test", mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL, max_depth=2
        )

        assert len(result) == 2
        assert mock_module1 in result
        assert mock_module2 in result
        mock_sweep_dirs.assert_called_once()

    @patch("src.suplex_modules.module_loader.try_get_module")
    @patch("src.suplex_modules.module_loader.delve_dirs")
    def test_load_modules_with_empty_modules(
        self, mock_delve_dirs, mock_try_get_module
    ):
        def delve_dirs_side_effect(search_dir, filetype, files, **kwargs):
            files.update(["/test/empty1.py", "/test/empty2.py"])
            return files

        mock_delve_dirs.side_effect = delve_dirs_side_effect
        mock_try_get_module.return_value = []  # Empty list for invalid modules

        result = load_modules(dir_path="/test")

        assert len(result) == 0


class TestDelveDir:
    @patch("src.suplex_modules.module_loader.should_ignore_file")
    @patch("src.suplex_modules.module_loader.should_ignore_directory")
    @patch("src.suplex_modules.module_loader.os.scandir")
    def test_recursive_directory_traversal(
        self, mock_scandir, mock_ignore_dir, mock_ignore_file, mock_scandir_entry
    ):
        root_entries = [
            mock_scandir_entry("subdir", is_dir=True),
            mock_scandir_entry("file1.py", is_file=True),
        ]
        sub_entries = [
            mock_scandir_entry("file2.py", is_file=True, base_path="/test/subdir")
        ]

        @contextmanager
        def mock_scandir_context(path):
            if path == "/test":
                yield iter(root_entries)
            elif path == "/test/subdir":
                yield iter(sub_entries)
            else:
                yield iter([])

        mock_scandir.side_effect = mock_scandir_context
        mock_ignore_dir.return_value = False
        mock_ignore_file.return_value = False

        files = set()
        delve_dirs(
            search_dir="/test",
            filetype=".py",
            files=files,
            ignore_dirs=set(),
            ignore_files=set(),
            ignore_extensions=set(),
        )

        assert "/test/file1.py" in files
        assert "/test/subdir/file2.py" in files

    @patch("src.suplex_modules.module_loader.os.scandir")
    def test_permission_error_in_delve_dirs(self, mock_scandir):
        mock_scandir.side_effect = PermissionError("Access denied")

        files = set()
        delve_dirs(search_dir="/restricted", filetype=".py", files=files)

        assert not files


class TestSweepDirs:
    @patch("src.suplex_modules.module_loader.should_collect_at_depth")
    @patch("src.suplex_modules.module_loader.should_ignore_file")
    @patch("src.suplex_modules.module_loader.should_ignore_directory")
    @patch("src.suplex_modules.module_loader.os.scandir")
    def test_iterative_bounded_bottom_mode(
        self, mock_scandir, mock_ignore_dir, mock_ignore_file, mock_should_collect
    ):
        def create_entry(name, is_dir=False, is_file=False, base_path="/test"):
            entry = Mock()
            entry.name = name
            entry.path = f"{base_path}/{name}"
            entry.is_dir.return_value = is_dir
            entry.is_file.return_value = is_file
            return entry

        root_entries = [
            create_entry("subdir", is_dir=True),
            create_entry("file1.py", is_file=True),
        ]
        sub_entries = [
            create_entry("deepdir", is_dir=True, base_path="/test/subdir"),
            create_entry("file2.py", is_file=True, base_path="/test/subdir"),
        ]
        deep_entries = [
            create_entry("file3.py", is_file=True, base_path="/test/subdir/deepdir")
        ]

        @contextmanager
        def mock_scandir_context(path):
            if path == "/test":
                yield iter(root_entries)
            elif path == "/test/subdir":
                yield iter(sub_entries)
            elif path == "/test/subdir/deepdir":
                yield iter(deep_entries)
            else:
                yield iter([])

        mock_scandir.side_effect = mock_scandir_context
        mock_ignore_dir.return_value = False
        mock_ignore_file.return_value = False

        def should_collect_side_effect(mode, depth, max_depth):
            if mode == SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM:
                return depth == max_depth
            return True

        mock_should_collect.side_effect = should_collect_side_effect

        # Search only in root
        result = sweep_dirs(
            root_path="/test",
            filetype=".py",
            mode=SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
            max_depth=0,
            ignore_dirs=set(),
            ignore_files=set(),
            ignore_extensions=set(),
        )

        assert "/test/file1.py" in result
        assert "/test/subdir/file2.py" not in result
        assert "/test/subdir/deepdir/file3.py" not in result

        # Search only in subdir
        result = sweep_dirs(
            root_path="/test",
            filetype=".py",
            mode=SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
            max_depth=1,
            ignore_dirs=set(),
            ignore_files=set(),
            ignore_extensions=set(),
        )

        assert "/test/file1.py" not in result
        assert "/test/subdir/file2.py" in result
        assert "/test/subdir/deepdir/file3.py" not in result

        # Search only in deepdir
        result = sweep_dirs(
            root_path="/test",
            filetype=".py",
            mode=SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
            max_depth=2,
            ignore_dirs=set(),
            ignore_files=set(),
            ignore_extensions=set(),
        )

        assert "/test/file1.py" not in result
        assert "/test/subdir/file2.py" not in result
        assert "/test/subdir/deepdir/file3.py" in result

    @patch("src.suplex_modules.module_loader.should_collect_at_depth")
    @patch("src.suplex_modules.module_loader.should_ignore_file")
    @patch("src.suplex_modules.module_loader.should_ignore_directory")
    @patch("src.suplex_modules.module_loader.os.scandir")
    def test_iterative_bounded_all_mode(
        self, mock_scandir, mock_ignore_dir, mock_ignore_file, mock_should_collect
    ):
        def create_entry(name, is_dir=False, is_file=False, base_path="/test"):
            entry = Mock()
            entry.name = name
            entry.path = f"{base_path}/{name}"
            entry.is_dir.return_value = is_dir
            entry.is_file.return_value = is_file
            return entry

        root_entries = [
            create_entry("subdir", is_dir=True),
            create_entry("file1.py", is_file=True),
        ]
        sub_entries = [
            create_entry("deepdir", is_dir=True, base_path="/test/subdir"),
            create_entry("file2.py", is_file=True, base_path="/test/subdir"),
        ]
        deep_entries = [
            create_entry("file3.py", is_file=True, base_path="/test/subdir/deepdir")
        ]

        @contextmanager
        def mock_scandir_context(path):
            if path == "/test":
                yield iter(root_entries)
            elif path == "/test/subdir":
                yield iter(sub_entries)
            elif path == "/test/subdir/deepdir":
                yield iter(deep_entries)
            else:
                yield iter([])

        mock_scandir.side_effect = mock_scandir_context
        mock_ignore_dir.return_value = False
        mock_ignore_file.return_value = False

        def should_collect_side_effect(mode, depth, max_depth):
            if mode == SEARCH_MODE.ITERATIVE_BOUNDED_ALL:
                return depth <= max_depth
            return True

        mock_should_collect.side_effect = should_collect_side_effect

        result = sweep_dirs(
            root_path="/test",
            filetype=".py",
            mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL,
            max_depth=1,
            ignore_dirs=set(),
            ignore_files=set(),
            ignore_extensions=set(),
        )

        assert "/test/file1.py" in result
        assert "/test/subdir/file2.py" in result
        assert "/test/subdir/deepdir/file3.py" not in result

    @patch("src.suplex_modules.module_loader.should_collect_at_depth")
    @patch("src.suplex_modules.module_loader.should_ignore_file")
    @patch("src.suplex_modules.module_loader.should_ignore_directory")
    @patch("src.suplex_modules.module_loader.os.scandir")
    def test_iterative_bounded_unbound_mode(
        self, mock_scandir, mock_ignore_dir, mock_ignore_file, mock_should_collect
    ):
        def create_entry(name, is_dir=False, is_file=False, base_path="/test"):
            entry = Mock()
            entry.name = name
            entry.path = f"{base_path}/{name}"
            entry.is_dir.return_value = is_dir
            entry.is_file.return_value = is_file
            return entry

        root_entries = [
            create_entry("subdir", is_dir=True),
            create_entry("file1.py", is_file=True),
        ]
        sub_entries = [create_entry("file2.py", is_file=True, base_path="/test/subdir")]

        @contextmanager
        def mock_scandir_context(path):
            if path == "/test":
                yield iter(root_entries)
            elif path == "/test/subdir":
                yield iter(sub_entries)
            else:
                yield iter([])

        mock_scandir.side_effect = mock_scandir_context
        mock_ignore_dir.return_value = False
        mock_ignore_file.return_value = False
        mock_should_collect.return_value = True

        result = sweep_dirs(
            root_path="/test",
            filetype=".py",
            mode=SEARCH_MODE.ITERATIVE_UNBOUND,
            max_depth=1,
            ignore_dirs=set(),
            ignore_files=set(),
            ignore_extensions=set(),
        )

        assert "/test/file1.py" in result
        assert "/test/subdir/file2.py" in result

    @patch("src.suplex_modules.module_loader.os.scandir")
    def test_permission_error_handling(self, mock_scandir):
        mock_scandir.side_effect = PermissionError("Access denied")

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


class TestShouldIgnoreDirectory:
    def test_ignore_hidden_directories(self):
        assert should_ignore_directory(".git", set())
        assert should_ignore_directory(".hidden", set())
        assert should_ignore_directory(".cache", set())

    def test_ignore_specified_directories(self):
        ignore_dirs = {"build", "dist", "venv"}
        assert should_ignore_directory("build", ignore_dirs)
        assert should_ignore_directory("dist", ignore_dirs)
        assert should_ignore_directory("venv", ignore_dirs)

    def test_ignore_cache_temp_directories(self):
        assert should_ignore_directory("cache_dir", set())
        assert should_ignore_directory("temp_files", set())
        assert should_ignore_directory("tmp_folder", set())
        assert should_ignore_directory("Cache", set())

    def test_allow_normal_directories(self):
        assert not should_ignore_directory("src", set())
        assert not should_ignore_directory("modules", set())
        assert not should_ignore_directory("my_project", set())

    def test_ignore_real_default_directories(self):
        for ignore_dir in ["__pycache__", ".git", ".vscode", "node_modules", "venv"]:
            if ignore_dir in DEFAULT_IGNORE_DIRS:
                assert should_ignore_directory(ignore_dir, DEFAULT_IGNORE_DIRS)


class TestShouldIgnoreFile:
    def test_ignore_hidden_files(self):
        assert should_ignore_file(".gitignore", set(), set())
        assert should_ignore_file(".hidden_file.py", set(), set())

    def test_ignore_specified_files(self):
        ignore_files = {"config.py", "secrets.py"}
        assert should_ignore_file("config.py", ignore_files, set())
        assert should_ignore_file("secrets.py", ignore_files, set())

    def test_ignore_specified_extensions(self):
        ignore_extensions = {".log", ".tmp", ".bak"}
        assert should_ignore_file("debug.log", set(), ignore_extensions)
        assert should_ignore_file("temp.tmp", set(), ignore_extensions)
        assert should_ignore_file("backup.bak", set(), ignore_extensions)

    def test_ignore_temp_backup_files(self):
        assert should_ignore_file("file.tmp", set(), set())
        assert should_ignore_file("backup.bak", set(), set())
        assert should_ignore_file("vim.swp", set(), set())
        assert should_ignore_file("file~", set(), set())

    def test_ignore_test_files(self):
        assert should_ignore_file("test_module.py", set(), set())
        assert should_ignore_file("test_example.py", set(), set())

    def test_allow_normal_files(self):
        assert not should_ignore_file("module.py", set(), set())
        assert not should_ignore_file("main.py", set(), set())
        assert not should_ignore_file("example.py", set(), set())

    def test_ignore_real_default_files_and_extensions(self):
        for ignore_file in ["__init__.py", "setup.py", "README.md"]:
            if ignore_file in DEFAULT_IGNORE_FILES:
                assert should_ignore_file(ignore_file, DEFAULT_IGNORE_FILES, set())

        for ignore_ext in [".pyc", ".pyo", ".pyd"]:
            if ignore_ext in DEFAULT_IGNORE_EXTENSIONS:
                test_file = f"test{ignore_ext}"
                assert should_ignore_file(test_file, set(), DEFAULT_IGNORE_EXTENSIONS)


class TestShouldCollectAtDepth:
    def test_iterative_unbound_mode(self):
        mode = SEARCH_MODE.ITERATIVE_UNBOUND
        assert should_collect_at_depth(mode, 0, 3)
        assert should_collect_at_depth(mode, 5, 3)
        assert should_collect_at_depth(mode, 10, 3)

    def test_iterative_bounded_all_mode(self):
        mode = SEARCH_MODE.ITERATIVE_BOUNDED_ALL
        max_depth = 3
        assert should_collect_at_depth(mode, 0, max_depth)
        assert should_collect_at_depth(mode, 2, max_depth)
        assert should_collect_at_depth(mode, 3, max_depth)
        assert not should_collect_at_depth(mode, 4, max_depth)

    def test_iterative_bounded_bottom_mode(self):
        mode = SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM
        max_depth = 3
        assert not should_collect_at_depth(mode, 0, max_depth)
        assert not should_collect_at_depth(mode, 2, max_depth)
        assert should_collect_at_depth(mode, 3, max_depth)
        assert not should_collect_at_depth(mode, 4, max_depth)


class TestTryGetModule:
    @patch("src.suplex_modules.module_loader.is_valid_suplex_module_class")
    @patch("src.suplex_modules.module_loader.inspect.getmembers")
    @patch("src.suplex_modules.module_loader.importlib.util.module_from_spec")
    @patch("src.suplex_modules.module_loader.importlib.util.spec_from_file_location")
    @patch("src.suplex_modules.module_loader.has_suplex_interface_classes")
    def test_successful_module_loading(
        self,
        mock_has_interface,
        mock_spec_from_file,
        mock_module_from_spec,
        mock_getmembers,
        mock_is_valid,
    ):
        mock_has_interface.return_value = True

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module

        mock_class = Mock()
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        mock_getmembers.return_value = [("TestClass", mock_class)]
        mock_is_valid.return_value = True

        result = try_get_module("test_file.py")

        assert len(result) == 1
        assert result[0] == mock_instance
        mock_spec.loader.exec_module.assert_called_once_with(mock_module)

    @patch("src.suplex_modules.module_loader.has_suplex_interface_classes")
    def test_file_without_suplex_interface(self, mock_has_interface):
        mock_has_interface.return_value = False

        result = try_get_module("test_file.py")

        assert result == []

    @patch("src.suplex_modules.module_loader.importlib.util.spec_from_file_location")
    @patch("src.suplex_modules.module_loader.has_suplex_interface_classes")
    def test_spec_creation_failure(self, mock_has_interface, mock_spec_from_file):
        mock_has_interface.return_value = True
        mock_spec_from_file.return_value = None

        result = try_get_module("test_file.py")

        assert result == []

    @patch("src.suplex_modules.module_loader.importlib.util.spec_from_file_location")
    @patch("src.suplex_modules.module_loader.has_suplex_interface_classes")
    def test_syntax_error_handling(self, mock_has_interface, mock_spec_from_file):
        mock_has_interface.return_value = True
        mock_spec_from_file.side_effect = SyntaxError("Invalid syntax")

        result = try_get_module("test_file.py")

        assert result == []


class TestHasSuplexInterfaceClasses:

    def test_correct_implementation_with_inheritance(self):
        file_dir = (
            Path(__file__).parent.parent.parent
            / "test_data"
            / "test_modules"
            / "valid_modules"
            / "valid_suplex_module.py"
        )
        assert has_suplex_interface_classes(str(file_dir))

    def test_incorrect_implementation_with_inheritance(self):
        file_dir = (
            Path(__file__).parent.parent.parent
            / "test_data"
            / "test_modules"
            / "invalid_modules"
            / "incomplete_suplex_module.py"
        )
        assert has_suplex_interface_classes(str(file_dir))

    def test_correct_implementation_without_inheritance(self):
        file_dir = (
            Path(__file__).parent.parent.parent
            / "test_data"
            / "test_modules"
            / "invalid_modules"
            / "no_inheritance_suplex_module.py"
        )
        assert not has_suplex_interface_classes(str(file_dir))

    def test_correct_implementation_with_multiple_inheritance(self):
        file_dir = (
            Path(__file__).parent.parent.parent
            / "test_data"
            / "test_modules"
            / "valid_modules"
            / "vaild_suplex_module_advanced.py"
        )
        assert has_suplex_interface_classes(str(file_dir))

    def test_no_suplex_related_code(self):
        file_dir = (
            Path(__file__).parent.parent.parent
            / "test_data"
            / "test_modules"
            / "unassociated_code.py"
        )
        assert not has_suplex_interface_classes(str(file_dir))

    def test_different_import_styles(self):
        submodule_import = """from modules.interfaces.SuplexModuleInterface import SuplexModuleInterface
class SubModuleTest(SuplexModuleInterface):
    pass
"""
        with patch("builtins.open", mock_open(read_data=submodule_import)):
            assert has_suplex_interface_classes("submodule_test.py")

        direct_import = """import SuplexModuleInterface
class DirectImportTest(SuplexModuleInterface.SuplexModuleInterface):
    pass
"""
        with patch("builtins.open", mock_open(read_data=direct_import)):
            assert has_suplex_interface_classes("direct_import_test.py")

    def test_alias_import(self):
        alias_import = """from SuplexModuleInterface import SuplexModuleInterface as SMI
class AliasTest(SMI):
    pass
"""
        with patch("builtins.open", mock_open(read_data=alias_import)):
            result = has_suplex_interface_classes("alias_test.py")
            assert result

    def test_file_read_error(self):
        with patch("builtins.open", side_effect=OSError("File not found")):
            assert not has_suplex_interface_classes("nonexistent.py")

    def test_syntax_error(self):
        invalid_python = "invalid python syntax {"
        with patch("builtins.open", mock_open(read_data=invalid_python)):
            assert not has_suplex_interface_classes("invalid.py")

    def test_unicode_decode_error(self):
        with patch(
            "builtins.open",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        ):
            assert not has_suplex_interface_classes("unicode_error.py")

    def test_substring_false_positive(self):
        false_positive_code = """from MySuplexModuleInterfaceHelper import Helper
class TestModule(Helper):
    pass
"""
        with patch("builtins.open", mock_open(read_data=false_positive_code)):
            result = has_suplex_interface_classes("false_positive_test.py")
            assert not result


class TestIsValidSuplexModuleClass:
    def setup_method(self, method):
        # Use a mock interface class for setup
        class MockSuplexModuleInterface:
            pass

        self.interface_class = MockSuplexModuleInterface
        self.module_name = "test_module"

    def test_valid_suplex_module_class(self):
        class ValidModule(self.interface_class):
            pass

        ValidModule.__module__ = self.module_name

        assert is_valid_suplex_module_class(
            ValidModule, self.module_name, self.interface_class
        )

    def test_interface_class_itself(self):
        self.interface_class.__module__ = self.module_name
        assert not is_valid_suplex_module_class(
            self.interface_class, self.module_name, self.interface_class
        )

    def test_class_from_different_module(self):
        class OtherModule(self.interface_class):
            pass

        OtherModule.__module__ = "other_module"

        assert not is_valid_suplex_module_class(
            OtherModule, self.module_name, self.interface_class
        )

    def test_class_without_inheritance(self):
        class RegularClass:
            pass

        RegularClass.__module__ = self.module_name

        assert not is_valid_suplex_module_class(
            RegularClass, self.module_name, self.interface_class
        )

    def test_non_class_object(self):
        def some_function():
            pass

        some_function.__module__ = self.module_name

        assert not is_valid_suplex_module_class(
            some_function, self.module_name, self.interface_class
        )

    def test_object_without_module_attribute(self):
        class NoModuleClass:
            pass

        DynamicClass = type("DynamicClass", (), {})
        if hasattr(DynamicClass, "__module__"):
            with patch("src.suplex_modules.module_loader.hasattr", return_value=False):
                assert not is_valid_suplex_module_class(
                    DynamicClass, self.module_name, self.interface_class
                )
