import pytest
import copy
import math
from unittest.mock import patch, Mock
from src.martin_interface.validation.data_statistics_validation import *


class TestDataStatisticsValidation:
    @patch("src.martin_interface.validation.data_statistics_validation.get_data_file")
    def test_try_get_validated_data_statistics_invalid_file(self, mock_get_data):
        mock_get_data.return_value = None

        result = try_get_validated_data_statistics("/test/path", {})
        assert result is None

    @patch("src.martin_interface.validation.data_statistics_validation.get_data_file")
    def test_try_get_validated_data_statistics_success(
        self,
        mock_get_data,
        sample_data_dict,
        sample_data_statistics_dict,
        sample_data_statistics_dict_raw,
    ):
        mock_get_data.return_value = sample_data_statistics_dict
        result = try_get_validated_data_statistics("/test/path", sample_data_dict)

        assert result is not None
        comp_result = sample_data_statistics_dict["values"][0]
        result = result["values"][0]

        assert result["row"] == comp_result["row"]
        assert result["col"] == comp_result["col"]
        assert result["adjusted_average"] == comp_result["adjusted_average"]
        assert (
            result["adjusted_average_std_deviation"]
            == comp_result["adjusted_average_std_deviation"]
        )
        assert (
            result["relative_adjusted_average_std_deviation"]
            == comp_result["relative_adjusted_average_std_deviation"]
        )
        assert result["normalized_average"] == comp_result["normalized_average"]
        assert (
            result["normalized_average_std_deviation"]
            == comp_result["normalized_average_std_deviation"]
        )
        assert (
            result["relative_normalized_average_std_deviation"]
            == comp_result["relative_normalized_average_std_deviation"]
        )

    def test_try_typecast_data_statistics_file_success(
        self, sample_data_statistics_dict_raw, sample_data_statistics_dict
    ):
        result = try_typecast_data_statistics_file(
            "/test/path", sample_data_statistics_dict_raw
        )
        result = result["values"][0]
        assert result is not None
        assert isinstance(result["row"], int)
        assert isinstance(result["col"], int)
        assert isinstance(result["adjusted_average"], float)
        assert isinstance(result["adjusted_average_std_deviation"], float)
        assert isinstance(result["relative_adjusted_average_std_deviation"], float)
        assert isinstance(result["normalized_average"], float)
        assert isinstance(result["normalized_average_std_deviation"], float)
        assert isinstance(result["relative_normalized_average_std_deviation"], float)

        comp_result = sample_data_statistics_dict["values"][0]

        assert result["row"] == comp_result["row"]
        assert result["col"] == comp_result["col"]
        assert result["adjusted_average"] == comp_result["adjusted_average"]
        assert (
            result["adjusted_average_std_deviation"]
            == comp_result["adjusted_average_std_deviation"]
        )
        assert (
            result["relative_adjusted_average_std_deviation"]
            == comp_result["relative_adjusted_average_std_deviation"]
        )
        assert result["normalized_average"] == comp_result["normalized_average"]
        assert (
            result["normalized_average_std_deviation"]
            == comp_result["normalized_average_std_deviation"]
        )
        assert (
            result["relative_normalized_average_std_deviation"]
            == comp_result["relative_normalized_average_std_deviation"]
        )

    def test_try_typecast_typecasted_data_statistics_file_success(
        self, sample_data_statistics_dict
    ):
        result = try_typecast_data_statistics_file(
            "/test/path", copy.deepcopy(sample_data_statistics_dict)
        )
        result = result["values"][0]
        assert result is not None
        assert isinstance(result["row"], int)
        assert isinstance(result["col"], int)
        assert isinstance(result["adjusted_average"], float)
        assert isinstance(result["adjusted_average_std_deviation"], float)
        assert isinstance(result["relative_adjusted_average_std_deviation"], float)
        assert isinstance(result["normalized_average"], float)
        assert isinstance(result["normalized_average_std_deviation"], float)
        assert isinstance(result["relative_normalized_average_std_deviation"], float)

        comp_result = sample_data_statistics_dict["values"][0]

        assert result["row"] == comp_result["row"]
        assert result["col"] == comp_result["col"]
        assert result["adjusted_average"] == comp_result["adjusted_average"]
        assert (
            result["adjusted_average_std_deviation"]
            == comp_result["adjusted_average_std_deviation"]
        )
        assert (
            result["relative_adjusted_average_std_deviation"]
            == comp_result["relative_adjusted_average_std_deviation"]
        )
        assert result["normalized_average"] == comp_result["normalized_average"]
        assert (
            result["normalized_average_std_deviation"]
            == comp_result["normalized_average_std_deviation"]
        )
        assert (
            result["relative_normalized_average_std_deviation"]
            == comp_result["relative_normalized_average_std_deviation"]
        )

    def test_try_typecast_data_statistics_file_invalid_type(
        self, sample_data_statistics_dict_raw
    ):
        sample_data_statistics_dict_raw["values"][0][
            "adjusted_average"
        ] = "not_a_number"
        result = try_typecast_data_statistics_file(
            "/test/path", sample_data_statistics_dict_raw
        )
        assert result is None

    def test_check_internal_value_consistency_valid(self, sample_data_statistics_dict):
        result = check_internal_value_consistency(
            "/test/path", sample_data_statistics_dict
        )
        assert result is True

    def test_check_value_consistency_negative_row(self, sample_data_statistics_dict):
        sample_data_statistics_dict["values"][0]["row"] = -2
        result = check_internal_value_consistency(
            "/test/path", sample_data_statistics_dict
        )
        assert result is False

    def test_check_value_consistency_negative_col(self, sample_data_statistics_dict):
        sample_data_statistics_dict["values"][0]["col"] = -3
        result = check_internal_value_consistency(
            "/test/path", sample_data_statistics_dict
        )
        assert result is False

    def test_check_value_consistency_nan_values(self, sample_data_statistics_dict):
        sample_data_statistics_dict["values"][0]["adjusted_average"] = float("nan")

        with patch(
            "src.martin_interface.validation.data_statistics_validation.logger"
        ) as mock_logger:
            result = check_internal_value_consistency(
                "/test/path", sample_data_statistics_dict
            )
            assert result is True  # NaN is tolerated but logged
            mock_logger.warning.assert_called()

    def test_check_external_consistency_matching(
        self, sample_data_dict, sample_data_statistics_dict
    ):
        result = check_external_consistency(
            sample_data_dict, "/test/path", sample_data_statistics_dict
        )
        assert result is True

    def test_check_external_consistency_dimension_mismatch(
        self, sample_data_dict, sample_data_statistics_dict
    ):
        double_data_statistics = {
            "values": sample_data_statistics_dict["values"]
            + sample_data_statistics_dict["values"]
        }
        result = check_external_consistency(
            sample_data_dict, "/test/path", double_data_statistics
        )
        assert result is False

        double_data = {
            "values": sample_data_dict["values"] + sample_data_dict["values"]
        }
        result = check_external_consistency(
            double_data, "/test/path", sample_data_statistics_dict
        )
        assert result is False

    def test_check_external_consistency_value_mismatch(
        self, sample_data_dict, sample_data_statistics_dict
    ):
        sample_data_statistics_dict["values"][0]["adjusted_average"] = 0

        result = check_external_consistency(
            sample_data_dict, "/test/path", sample_data_statistics_dict
        )
        assert result is False
