import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import importlib.util
import sys

from src.ui.styles.scheme_loader import (
    load_all_schemes,
    validate_scheme_files,
    is_system_file,
    try_load_schemes_from_file,
    validate_against_schema,
    get_schemes,
)


class TestSchemeLoader:
    def test_is_system_file(self):
        assert is_system_file(Path("__init__.py"))
        assert is_system_file(Path("__main__.py"))
        assert is_system_file(Path("setup.py"))
        assert is_system_file(Path("conftest.py"))
        assert is_system_file(Path("config.py"))
        assert is_system_file(Path("test_something.py"))
        assert is_system_file(Path("something_test.py"))
        assert is_system_file(Path(".hidden.py"))
        assert is_system_file(Path("file.py.bak"))
        assert is_system_file(Path("file.py.backup"))
        assert is_system_file(Path("file.py.old"))
        assert is_system_file(Path("file.py.tmp"))

        assert not is_system_file(Path("my_scheme.py"))
        assert not is_system_file(Path("dark_theme.py"))

    def test_is_system_file_error_handling(self):
        with patch("src.ui.styles.scheme_loader.logger") as mock_logger:
            result = is_system_file(None)
            assert result == True
            mock_logger.error.assert_called()

    def test_validate_scheme_files(self, temp_scheme_dir):
        valid_file = temp_scheme_dir / "valid_scheme.py"
        valid_file.write_text("# Valid scheme")

        system_file = temp_scheme_dir / "__init__.py"
        system_file.write_text("# System file")

        empty_file = temp_scheme_dir / "empty.py"
        empty_file.write_text("")

        dir_path = temp_scheme_dir / "subdir"
        dir_path.mkdir()

        python_files = [valid_file, system_file, empty_file, dir_path]

        result = validate_scheme_files(python_files)

        assert len(result) == 1
        assert result[0] == valid_file

    def test_validate_against_schema_valid(self, mock_scheme_class):
        schema = {
            "NAME": str,
            "TEXT": {
                "FONT": dict,
                "SIZE": dict,
                "WEIGHT": dict,
                "STYLE": dict,
                "COLOR": dict,
            },
            "LAYOUT_COLOR": {"BACKGROUND": str},
            "ICON": {"DEFAULT": str},
            "OPACITY": {"FULL": float},
        }

        result = validate_against_schema(schema, mock_scheme_class)
        assert result == True

    def test_validate_against_schema_missing_field(self, mock_scheme_class):
        schema = {"NAME": str, "MISSING_FIELD": str}

        result = validate_against_schema(schema, mock_scheme_class)
        assert result == False

    def test_validate_against_schema_wrong_type(self, mock_scheme_class):
        mock_scheme_class.NAME = 123
        schema = {"NAME": str}

        result = validate_against_schema(schema, mock_scheme_class)
        assert result == False

    def test_validate_against_schema_nested(self):
        test_obj = type("TestObj", (), {})()

        level1_class = type("Level1", (), {})
        level2_class = type("Level2", (), {})

        level2_class.value = "test"
        level1_class.level2 = level2_class
        test_obj.level1 = level1_class

        schema = {"level1": {"level2": {"value": str}}}

        result = validate_against_schema(schema, test_obj)
        assert result == True

    @patch("src.ui.styles.scheme_loader.importlib.util.spec_from_file_location")
    @patch("src.ui.styles.scheme_loader.importlib.util.module_from_spec")
    @patch("src.ui.styles.scheme_loader.inspect.isclass")
    def test_try_load_schemes_from_file_success(
        self,
        mock_isclass,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_scheme_class,
    ):
        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module.__name__ = "test"
        mock_module.TestScheme = mock_scheme_class
        mock_scheme_class.__module__ = "test"
        mock_module_from_spec.return_value = mock_module

        mock_isclass.return_value = True

        with patch("src.ui.styles.scheme_loader.inspect.getmembers") as mock_getmembers:
            mock_getmembers.return_value = [("TestScheme", mock_scheme_class)]

            with patch(
                "src.ui.styles.scheme_loader.validate_against_schema"
            ) as mock_validate:
                mock_validate.return_value = True
                result = try_load_schemes_from_file(Path("test.py"))

        assert len(result) == 1
        assert result[0] == mock_scheme_class

    @patch("src.ui.styles.scheme_loader.importlib.util.spec_from_file_location")
    def test_try_load_schemes_from_file_no_spec(self, mock_spec_from_file):
        mock_spec_from_file.return_value = None
        result = try_load_schemes_from_file(Path("test.py"))
        assert result == []

    @patch("src.ui.styles.scheme_loader.importlib.util.spec_from_file_location")
    @patch("src.ui.styles.scheme_loader.importlib.util.module_from_spec")
    def test_try_load_schemes_from_file_import_error(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module.side_effect = ImportError("Test import error")
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module

        result = try_load_schemes_from_file(Path("test.py"))
        assert result == []

    @patch("src.ui.styles.scheme_loader.Path.glob")
    @patch("src.ui.styles.scheme_loader.Path.exists")
    @patch("src.ui.styles.scheme_loader.Path.is_dir")
    def test_load_all_schemes_success(
        self, mock_is_dir, mock_exists, mock_glob, mock_scheme_class, temp_scheme_dir
    ):
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        file1 = Mock(spec=Path)
        file1.name = "scheme1.py"
        file2 = Mock(spec=Path)
        file2.name = "scheme2.py"
        mock_glob.return_value = [file1, file2]

        with patch(
            "src.ui.styles.scheme_loader.validate_scheme_files"
        ) as mock_validate:
            mock_validate.return_value = [file1, file2]

            with patch(
                "src.ui.styles.scheme_loader.try_load_schemes_from_file"
            ) as mock_load:
                scheme1 = Mock()
                scheme1.NAME = "Scheme1"
                scheme2 = Mock()
                scheme2.NAME = "Scheme2"
                mock_load.side_effect = [[scheme1], [scheme2]]

                result = load_all_schemes(temp_scheme_dir)

        assert len(result) == 2
        assert "Scheme1" in result
        assert "Scheme2" in result
        assert result["Scheme1"] == scheme1
        assert result["Scheme2"] == scheme2

    def test_load_all_schemes_no_directory(self):
        non_existent = Path("/non/existent/path")

        result = load_all_schemes(non_existent)
        assert result == {}

    def test_load_all_schemes_not_directory(self, tmp_path):
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("test")

        result = load_all_schemes(file_path)
        assert result == {}

    def test_load_all_schemes_no_python_files(self, temp_scheme_dir):
        (temp_scheme_dir / "readme.txt").write_text("readme")

        result = load_all_schemes(temp_scheme_dir)
        assert result == {}

    def test_load_all_schemes_scheme_without_name(self, temp_scheme_dir):
        file1 = temp_scheme_dir / "bad_scheme.py"
        file1.write_text("# Bad scheme")

        with patch(
            "src.ui.styles.scheme_loader.validate_scheme_files"
        ) as mock_validate:
            mock_validate.return_value = [file1]

            with patch(
                "src.ui.styles.scheme_loader.try_load_schemes_from_file"
            ) as mock_load:
                bad_scheme = Mock()
                del bad_scheme.NAME
                mock_load.return_value = [bad_scheme]

                result = load_all_schemes(temp_scheme_dir)

        assert result == {}

    @patch("src.ui.styles.scheme_loader.Path")
    @patch("src.ui.styles.scheme_loader.load_all_schemes")
    def test_get_schemes_success(self, mock_load_all, mock_path_class):
        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_path)
        mock_path.parent = mock_path
        mock_path.absolute.return_value = Path("/test/path")
        mock_path_class.return_value = mock_path

        schemes = {"Default": Mock(), "Dark": Mock()}
        mock_load_all.return_value = schemes

        result = get_schemes("schemes")

        assert result == schemes
        mock_load_all.assert_called_once()

    @patch("src.ui.styles.scheme_loader.Path")
    @patch("src.ui.styles.scheme_loader.load_all_schemes")
    def test_get_schemes_empty(self, mock_load_all, mock_path_class):
        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=mock_path)
        mock_path.parent = mock_path
        mock_path_class.return_value = mock_path

        mock_load_all.return_value = {}

        with patch("src.ui.styles.scheme_loader.logger") as mock_logger:
            result = get_schemes("schemes")

            assert result == {}
            mock_logger.warning.assert_called()

    def test_validate_against_schema_callable(self):
        test_obj = Mock()
        test_obj.value = 42

        def validator(val):
            return val > 40

        schema = {"value": validator}

        result = validate_against_schema(schema, test_obj)
        assert result == True

        test_obj.value = 30
        result = validate_against_schema(schema, test_obj)
        assert result == False

    def test_validate_against_schema_callable_error(self):
        test_obj = Mock()
        test_obj.value = "not_a_number"

        def validator(val):
            return val > 40

        schema = {"value": validator}

        result = validate_against_schema(schema, test_obj)
        assert result == False

    @patch("src.ui.styles.scheme_loader.importlib.util.spec_from_file_location")
    @patch("src.ui.styles.scheme_loader.importlib.util.module_from_spec")
    def test_module_cleanup_in_try_load_schemes(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        module_name = "test_scheme_module_cleanup"

        mock_spec_obj = Mock()
        mock_spec_obj.loader = Mock()
        mock_spec_from_file.return_value = mock_spec_obj

        test_module = Mock()
        test_module.__name__ = module_name
        mock_module_from_spec.return_value = test_module

        with patch("src.ui.styles.scheme_loader.inspect.getmembers") as mock_members:
            mock_members.return_value = []

            if module_name in sys.modules:
                del sys.modules[module_name]

            try_load_schemes_from_file(Path("test.py"))

            assert module_name not in sys.modules
