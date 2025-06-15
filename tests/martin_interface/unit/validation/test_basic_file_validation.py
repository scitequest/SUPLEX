import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from src.martin_interface.validation.basic_file_validation import *


class TestBasicFileValidation:
    def test_get_data_file_not_a_file(self):
        with patch("os.path.isfile", return_value=False):
            result = get_data_file("/fake/path")
            assert result is None

    def test_get_data_file_valid_json(self, temp_dir):
        data = {"values": [{"test": 1}]}
        json_path = os.path.join(temp_dir, "test.json")

        with open(json_path, "w") as f:
            json.dump(data, f)

        result = get_data_file(json_path)
        assert result == data

    def test_get_data_file_valid_tsv(self, temp_dir):
        tsv_content = "col1\tcol2\nval1\tval2"
        tsv_path = os.path.join(temp_dir, "test.tsv")

        with open(tsv_path, "w") as f:
            f.write(tsv_content)

        result = get_data_file(tsv_path)
        assert result == {"values": [{"col1": "val1", "col2": "val2"}]}

    def test_get_data_file_invalid_format(self, temp_dir):
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write("invalid content")

        result = get_data_file(txt_path)
        assert result is None

    def test_try_get_valid_json_success(self, temp_dir):
        data = {"key": "value"}
        json_path = os.path.join(temp_dir, "test.json")

        with open(json_path, "w") as f:
            json.dump(data, f)

        result = try_get_valid_json(json_path)
        assert result == data

    def test_try_get_valid_json_not_json_file(self):
        result = try_get_valid_json("/path/to/file.txt")
        assert result is None

    def test_try_get_valid_json_empty_path(self):
        result = try_get_valid_json("")
        assert result is None

    def test_try_get_valid_json_not_dict(self, temp_dir):
        json_path = os.path.join(temp_dir, "test.json")

        with open(json_path, "w") as f:
            json.dump([1, 2, 3], f)

        result = try_get_valid_json(json_path)
        assert result is None

    def test_try_get_valid_json_invalid_json(self, temp_dir):
        json_path = os.path.join(temp_dir, "test.json")

        with open(json_path, "w") as f:
            f.write("{invalid json}")

        result = try_get_valid_json(json_path)
        assert result is None

    def test_try_get_valid_tsv_as_dicts_success(self, temp_dir):
        tsv_content = "id\tname\nS001\tSample 1\nS002\tSample 2"
        tsv_path = os.path.join(temp_dir, "test.tsv")

        with open(tsv_path, "w") as f:
            f.write(tsv_content)

        result = try_get_valid_tsv_as_dicts(tsv_path)
        assert result == [
            {"id": "S001", "name": "Sample 1"},
            {"id": "S002", "name": "Sample 2"},
        ]

    def test_try_get_valid_tsv_as_dicts_not_tsv(self):
        result = try_get_valid_tsv_as_dicts("/path/to/file.csv")
        assert result is None

    def test_try_get_valid_tsv_as_dicts_no_headers(self, temp_dir):
        tsv_path = os.path.join(temp_dir, "test.tsv")

        with open(tsv_path, "w") as f:
            f.write("")

        result = try_get_valid_tsv_as_dicts(tsv_path)
        assert result is None

    def test_is_Key_Structure_Identical_matching(self):
        file_data = {
            "key1": "value1",
            "key2": [{"nested": "value"}],
            "key2-2": [{"nested": "value"}, {"nested": "value2"}, {"nested": "value3"}],
            "key2-3": [],
            "key3": {"nested": "dict"},
            "key4": {"nested": ["value1"]},
            "key4-2": {"nested": ["value1", "value2", "value3"]},  # tags
            "key5": [
                {
                    "nested_direct": "value",
                    "nested_dict": {"sub_nested1": 0.1, "sub_nested2": "value"},
                }
            ],
            "key5-2": [
                {
                    "nested_direct": "value",
                    "nested_dict": {"sub_nested1": 0.1, "sub_nested2": "value"},
                },
                {
                    "nested_direct": "value2",
                    "nested_dict": {"sub_nested1": 0.2, "sub_nested2": "value2"},
                },
            ],  # incubations
        }

        keymap = {
            "key1": str,
            "key2": [{"nested": str}],
            "key2-2": [{"nested": str}],
            "key2-3": [{"nested": str}],
            "key3": {"nested": str},
            "key4": {"nested": [str]},
            "key4-2": {"nested": [str]},
            "key5": [
                {
                    "nested_direct": str,
                    "nested_dict": {"sub_nested1": float, "sub_nested2": str},
                }
            ],
            "key5-2": [
                {
                    "nested_direct": str,
                    "nested_dict": {"sub_nested1": float, "sub_nested2": str},
                }
            ],
        }

        result = is_Key_Structure_Identical("/test/path", file_data, keymap)
        assert result is True

    def test_is_Key_Structure_Identical_missing_key(self):
        file_data = {"key1": "value1"}
        keymap = {"key1": str, "key2": str}

        result = is_Key_Structure_Identical("/test/path", file_data, keymap)
        assert result is False

    def test_is_Key_Structure_Identical_extra_key(self):
        file_data = {"key1": "value1", "key2": "value2"}
        keymap = {"key1": str}

        result = is_Key_Structure_Identical("/test/path", file_data, keymap)
        assert result is False

    def test_is_Key_Structure_Identical_wrong_type(self):
        file_data = {"key1": [1, 2, 3]}
        keymap = {"key1": str}

        result = is_Key_Structure_Identical("/test/path", file_data, keymap)
        assert result is False

    def test_is_dict_list_uniform_uniform(self):
        dict_list = [{"key1": 1, "key2": 2}, {"key1": 3, "key2": 4}]

        result = is_dict_list_uniform("/test/path", dict_list)
        assert result is True

    def test_is_dict_list_uniform_non_uniform(self):
        dict_list = [{"key1": 1, "key2": 2}, {"key1": 3, "key3": 4}]

        with patch(
            "src.martin_interface.validation.basic_file_validation.logger"
        ) as mock_logger:
            result = is_dict_list_uniform("/test/path", dict_list)
            assert result is False
            mock_logger.error.assert_called()

    def test_tsv_vs_json_identical_data_structures(self, temp_dir):
        test_data = [
            {"spot": "0", "row": "0", "col": "0", "mean": "150.5"},
            {"spot": "1", "row": "0", "col": "1", "mean": "75.25"},
        ]

        json_data = {"values": test_data}
        tsv_content = "spot\trow\tcol\tmean\n0\t0\t0\t150.5\n1\t0\t1\t75.25"

        json_path = os.path.join(temp_dir, "comparison.json")
        tsv_path = os.path.join(temp_dir, "comparison.tsv")

        with open(json_path, "w") as f:
            json.dump(json_data, f)

        with open(tsv_path, "w", newline="") as f:
            f.write(tsv_content)

        json_result = get_data_file(json_path)
        tsv_result = get_data_file(tsv_path)

        assert json_result == tsv_result
        assert json_result["values"] == test_data
        assert tsv_result["values"] == test_data
