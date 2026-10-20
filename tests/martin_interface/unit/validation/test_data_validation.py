import copy
from unittest.mock import patch

from suplex.martin_interface.validation.data_validation import (
    check_value_consistency,
    try_get_validated_data,
    try_typecast_data_file,
)


class TestDataValidation:
    """Tests for the data file validation functions (JSON/TSV parsing, key structure, typecasting, and value consistency checks)."""

    # -------------------------------------------------------------------------
    # try_get_validated_data tests
    # -------------------------------------------------------------------------

    @patch("suplex.martin_interface.validation.data_validation.get_data_file")
    def test_try_get_validated_data_invalid_file(self, mock_get_data):
        """Returns None when get_data_file fails to load the file (invalid JSON/TSV or missing file)."""
        mock_get_data.return_value = None

        result = try_get_validated_data("/test/path")
        assert result is None

    @patch("suplex.martin_interface.validation.data_validation.get_data_file")
    def test_try_get_validated_data_invalid_structure(self, mock_get_data):
        """Returns None when the key structure does not match DATA_FIELDS (is_Key_Structure_Identical fails)."""
        mock_get_data.return_value = {"wrong_key": []}

        result = try_get_validated_data("/test/path")
        assert result is None

    @patch("suplex.martin_interface.validation.data_validation.get_data_file")
    def test_try_get_validated_data_success(self, mock_get_data, sample_data_dict):
        """Successfully validates and returns a properly structured data file after all checks pass."""
        mock_get_data.return_value = sample_data_dict

        result = try_get_validated_data("/test/path")
        assert result is not None

        comp_result = sample_data_dict["values"][0]
        result = result["values"][0]

        assert result["mean_minus_min"] == comp_result["mean_minus_min"]
        assert result["normalized_mean"] == comp_result["normalized_mean"]
        assert result["spot"] == comp_result["spot"]
        assert result["row"] == comp_result["row"]
        assert result["col"] == comp_result["col"]
        assert result["min"] == comp_result["min"]
        assert result["max"] == comp_result["max"]
        assert result["mean"] == comp_result["mean"]
        assert result["std_deviation"] == comp_result["std_deviation"]

    # -------------------------------------------------------------------------
    # try_typecast_data_file tests
    # -------------------------------------------------------------------------

    def test_try_typecast_data_file_success(self, sample_data_dict_raw, sample_data_dict):
        """Correctly typecasts raw string values from a data file into proper Python types (float/int)."""
        result = try_typecast_data_file("/test/path", sample_data_dict_raw)
        result = result["values"][0]
        assert result is not None
        assert isinstance(result["mean_minus_min"], float)
        assert isinstance(result["normalized_mean"], float)
        assert isinstance(result["spot"], int)
        assert isinstance(result["row"], int)
        assert isinstance(result["col"], int)
        assert isinstance(result["min"], float)
        assert isinstance(result["max"], float)
        assert isinstance(result["mean"], float)
        assert isinstance(result["std_deviation"], float)

        comp_result = sample_data_dict["values"][0]

        assert result["mean_minus_min"] == comp_result["mean_minus_min"]
        assert result["normalized_mean"] == comp_result["normalized_mean"]
        assert result["spot"] == comp_result["spot"]
        assert result["row"] == comp_result["row"]
        assert result["col"] == comp_result["col"]
        assert result["min"] == comp_result["min"]
        assert result["max"] == comp_result["max"]
        assert result["mean"] == comp_result["mean"]
        assert result["std_deviation"] == comp_result["std_deviation"]

    def test_try_typecast_typecasted_data_file_success(self, sample_data_dict):
        """Idempotent: already-typecasted data file is returned unchanged."""
        result = try_typecast_data_file("/test/path", copy.deepcopy(sample_data_dict))
        result = result["values"][0]
        assert result is not None
        assert isinstance(result["mean_minus_min"], float)
        assert isinstance(result["normalized_mean"], float)
        assert isinstance(result["spot"], int)
        assert isinstance(result["row"], int)
        assert isinstance(result["col"], int)
        assert isinstance(result["min"], float)
        assert isinstance(result["max"], float)
        assert isinstance(result["mean"], float)
        assert isinstance(result["std_deviation"], float)

        comp_result = sample_data_dict["values"][0]

        assert result["mean_minus_min"] == comp_result["mean_minus_min"]
        assert result["normalized_mean"] == comp_result["normalized_mean"]
        assert result["spot"] == comp_result["spot"]
        assert result["row"] == comp_result["row"]
        assert result["col"] == comp_result["col"]
        assert result["min"] == comp_result["min"]
        assert result["max"] == comp_result["max"]
        assert result["mean"] == comp_result["mean"]
        assert result["std_deviation"] == comp_result["std_deviation"]

    def test_try_typecast_data_file_invalid_type(self, sample_data_dict_raw):
        """Returns None when any value cannot be typecasted to the expected Python type."""
        sample_data_dict_raw["values"][0]["mean_minus_min"] = "not_a_number"
        result = try_typecast_data_file("/test/path", sample_data_dict_raw)
        assert result is None

    # -------------------------------------------------------------------------
    # check_value_consistency tests
    # -------------------------------------------------------------------------

    def test_check_value_consistency_valid(self, sample_data_dict):
        """Valid data file passes all consistency checks (returns True)."""
        result = check_value_consistency("/test/path", sample_data_dict)
        assert result is True

    def test_check_value_consistency_negative_spot(self, sample_data_dict):
        """Rejects data with negative spot index (critical error)."""
        sample_data_dict["values"][0]["spot"] = -1
        result = check_value_consistency("/test/path", sample_data_dict)
        assert result is False

    def test_check_value_consistency_negative_row(self, sample_data_dict):
        """Rejects data with negative row index (critical error)."""
        sample_data_dict["values"][0]["row"] = -2
        result = check_value_consistency("/test/path", sample_data_dict)
        assert result is False

    def test_check_value_consistency_negative_col(self, sample_data_dict):
        """Rejects data with negative col index (critical error)."""
        sample_data_dict["values"][0]["col"] = -3
        result = check_value_consistency("/test/path", sample_data_dict)
        assert result is False

    def test_check_value_consistency_spotfield_mismatch(self):
        """Rejects data where spotfields have unequal number of entries."""
        data = {
            "values": [
                {
                    "spot": 0,
                    "row": 0,
                    "col": 0,
                    "min": 50.0,
                    "max": 200.0,
                    "mean": 150.0,
                    "std_deviation": 25.0,
                    "mean_minus_min": 100.0,
                    "normalized_mean": 0.5,
                },
                {
                    "spot": 0,
                    "row": 0,
                    "col": 1,
                    "min": 50.0,
                    "max": 200.0,
                    "mean": 150.0,
                    "std_deviation": 25.0,
                    "mean_minus_min": 100.0,
                    "normalized_mean": 0.5,
                },
                {
                    "spot": 1,
                    "row": 0,
                    "col": 0,
                    "min": 50.0,
                    "max": 200.0,
                    "mean": 150.0,
                    "std_deviation": 25.0,
                    "mean_minus_min": 100.0,
                    "normalized_mean": 0.5,
                },
            ]
        }

        result = check_value_consistency("/test/path", data)
        assert result is False

    def test_check_value_consistency_nan_values(self, sample_data_dict):
        """NaN values are tolerated (logged as warning) but do not cause failure."""
        sample_data_dict["values"][0]["min"] = float("nan")

        with patch("suplex.martin_interface.validation.data_validation.logger") as mock_logger:
            result = check_value_consistency("/test/path", sample_data_dict)
            assert result is True  # NaN is tolerated but logged
            mock_logger.warning.assert_called()

    def test_check_value_consistency_logical_errors(self, sample_data_dict):
        """Logical inconsistencies (min > max, negative std, etc.) are logged as warnings but do not cause failure."""
        sample_data_dict["values"][0]["min"] = 250
        sample_data_dict["values"][0]["std_deviation"] = -25.0
        sample_data_dict["values"][0]["normalized_mean"] = 1.5

        with patch("suplex.martin_interface.validation.data_validation.logger") as mock_logger:
            result = check_value_consistency("/test/path", sample_data_dict)
            assert result is True  # Logical errors are tolerated but logged
            assert mock_logger.warning.call_count >= 3
