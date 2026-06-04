import pytest
import copy
import json  # added to fix NameError in test_empty_string_raises_error
from unittest.mock import patch
from src.martin_interface.validation.parameters_validation import (
    try_get_validated_parameters,
    try_typecast_parameters_file,
    check_internal_value_consistency,
    check_external_consistency,
    typecast_to_bool,
)


class TestParametersValidation:
    """Tests for the parameters file validation functions (handles both POLYGON and CIRCLE formats, typecasting, internal/external consistency checks)."""

    # -------------------------------------------------------------------------
    # try_get_validated_parameters tests
    # -------------------------------------------------------------------------

    @patch("src.martin_interface.validation.parameters_validation.try_get_valid_json")
    def test_try_get_validated_parameters_invalid_json(self, mock_json):
        """Returns None immediately when the JSON file cannot be parsed."""
        mock_json.return_value = None

        result = try_get_validated_parameters("/test/path", {})
        assert result is None

    @patch("src.martin_interface.validation.parameters_validation.try_get_valid_json")
    def test_try_get_validated_parameters_typo_compatibility(
        self, mock_json, sample_parameters_dict_polygon
    ):
        """Handles legacy MARTin v1.0 typo 'subract_background' → 'subtract_background' for compatibility."""
        params = sample_parameters_dict_polygon.copy()
        params["subract_background"] = params.pop("subtract_background")
        mock_json.return_value = params

        with patch(
            "src.martin_interface.validation.parameters_validation.is_Key_Structure_Identical",
            return_value=True,
        ):
            with patch(
                "src.martin_interface.validation.parameters_validation.try_typecast_parameters_file"
            ) as mock_typecast:
                mock_typecast.return_value = sample_parameters_dict_polygon
                with patch(
                    "src.martin_interface.validation.parameters_validation.check_internal_value_consistency",
                    return_value=True,
                ):
                    with patch(
                        "src.martin_interface.validation.parameters_validation.check_external_consistency",
                        return_value=True,
                    ):
                        result = try_get_validated_parameters("/test/path", {})
                        assert (
                            "subtract_background" in mock_typecast.call_args[1]["parameters_file"]
                        )

    @patch("src.martin_interface.validation.parameters_validation.check_external_consistency")
    @patch("src.martin_interface.validation.parameters_validation.check_internal_value_consistency")
    @patch("src.martin_interface.validation.parameters_validation.try_typecast_parameters_file")
    @patch("src.martin_interface.validation.parameters_validation.is_Key_Structure_Identical")
    @patch("src.martin_interface.validation.parameters_validation.try_get_valid_json")
    def test_try_get_validated_parameters_success_polygon(
        self,
        mock_json,
        mock_key_structure,
        mock_typecast,
        mock_internal,
        mock_external,
        sample_parameters_dict_polygon,
        sample_parameters_dict_polygon_raw,
        sample_data_dict,
    ):
        """Successfully validates and returns a POLYGON-style parameters file after all checks pass."""
        mock_json.return_value = sample_parameters_dict_polygon_raw
        mock_key_structure.return_value = True
        mock_typecast.return_value = sample_parameters_dict_polygon
        mock_internal.return_value = True
        mock_external.return_value = True

        result = try_get_validated_parameters("/test/path", sample_data_dict)

        assert result is not None

        # Explicit value comparisons with sample_parameters_dict_polygon
        assert result["invert_lut"] == sample_parameters_dict_polygon["invert_lut"]
        assert (
            result["subtract_background"] == sample_parameters_dict_polygon["subtract_background"]
        )
        assert (
            result["number_of_spotfields"] == sample_parameters_dict_polygon["number_of_spotfields"]
        )
        assert (
            result["columns_per_spotfield"]
            == sample_parameters_dict_polygon["columns_per_spotfield"]
        )
        assert (
            result["spots_per_spotfield"] == sample_parameters_dict_polygon["spots_per_spotfield"]
        )
        assert result["spots"][0]["type"] == sample_parameters_dict_polygon["spots"][0]["type"]
        assert (
            result["spots"][0]["coordinates"]
            == sample_parameters_dict_polygon["spots"][0]["coordinates"]
        )
        assert result["spots"][1]["type"] == sample_parameters_dict_polygon["spots"][1]["type"]
        assert (
            result["spots"][1]["coordinates"]
            == sample_parameters_dict_polygon["spots"][1]["coordinates"]
        )
        assert (
            result["background_rectangles"][0]["type"]
            == sample_parameters_dict_polygon["background_rectangles"][0]["type"]
        )
        assert (
            result["background_rectangles"][0]["coordinates"]
            == sample_parameters_dict_polygon["background_rectangles"][0]["coordinates"]
        )

    @patch("src.martin_interface.validation.parameters_validation.check_external_consistency")
    @patch("src.martin_interface.validation.parameters_validation.check_internal_value_consistency")
    @patch("src.martin_interface.validation.parameters_validation.try_typecast_parameters_file")
    @patch("src.martin_interface.validation.parameters_validation.is_Key_Structure_Identical")
    @patch("src.martin_interface.validation.parameters_validation.try_get_valid_json")
    def test_try_get_validated_parameters_success_circle(
        self,
        mock_json,
        mock_key_structure,
        mock_typecast,
        mock_internal,
        mock_external,
        sample_parameters_dict_circle,
        sample_parameters_dict_circle_raw,
        sample_data_dict,
    ):
        """Successfully validates and returns a CIRCLE-style parameters file after all checks pass."""
        mock_json.return_value = sample_parameters_dict_circle_raw
        mock_key_structure.return_value = True
        mock_typecast.return_value = sample_parameters_dict_circle
        mock_internal.return_value = True
        mock_external.return_value = True

        result = try_get_validated_parameters("/test/path", sample_data_dict)

        assert result is not None

        # Explicit value comparisons with sample_parameters_dict_circle
        assert result["invert_lut"] == sample_parameters_dict_circle["invert_lut"]
        assert result["subtract_background"] == sample_parameters_dict_circle["subtract_background"]
        assert (
            result["number_of_spotfields"] == sample_parameters_dict_circle["number_of_spotfields"]
        )
        assert (
            result["columns_per_spotfield"]
            == sample_parameters_dict_circle["columns_per_spotfield"]
        )
        assert result["spots_per_spotfield"] == sample_parameters_dict_circle["spots_per_spotfield"]
        assert result["spots"][0]["type"] == sample_parameters_dict_circle["spots"][0]["type"]
        assert (
            result["spots"][0]["position"] == sample_parameters_dict_circle["spots"][0]["position"]
        )
        assert (
            result["spots"][0]["diameter"] == sample_parameters_dict_circle["spots"][0]["diameter"]
        )
        assert result["spots"][1]["type"] == sample_parameters_dict_circle["spots"][1]["type"]
        assert (
            result["spots"][1]["position"] == sample_parameters_dict_circle["spots"][1]["position"]
        )
        assert (
            result["spots"][1]["diameter"] == sample_parameters_dict_circle["spots"][1]["diameter"]
        )
        assert (
            result["background_rectangles"][0]["type"]
            == sample_parameters_dict_circle["background_rectangles"][0]["type"]
        )
        assert (
            result["background_rectangles"][0]["coordinates"]
            == sample_parameters_dict_circle["background_rectangles"][0]["coordinates"]
        )

    # -------------------------------------------------------------------------
    # try_typecast_parameters_file tests
    # -------------------------------------------------------------------------

    def test_try_typecast_parameters_file_polygon(
        self, sample_parameters_dict_polygon, sample_parameters_dict_polygon_raw
    ):
        """Correctly typecasts a raw POLYGON parameters file (strings → proper Python types)."""
        result = try_typecast_parameters_file(
            "/test/path", sample_parameters_dict_polygon_raw, spots_are_circular=False
        )

        assert result is not None

        assert isinstance(result["invert_lut"], bool)
        assert isinstance(result["subtract_background"], bool)
        assert isinstance(result["number_of_spotfields"], int)
        assert isinstance(result["columns_per_spotfield"], int)
        assert isinstance(result["spots_per_spotfield"], int)
        assert isinstance(result["spots"], list)
        assert isinstance(result["spots"][0]["type"], str)
        assert isinstance(result["spots"][0]["coordinates"], list)
        assert isinstance(result["spots"][0]["coordinates"][0], list)
        assert isinstance(result["spots"][0]["coordinates"][0][0], float)
        assert isinstance(result["background_rectangles"], list)
        assert isinstance(result["background_rectangles"][0]["type"], str)
        assert isinstance(result["background_rectangles"][0]["coordinates"], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0][0], float)

        assert result["invert_lut"] == sample_parameters_dict_polygon["invert_lut"]
        assert (
            result["subtract_background"] == sample_parameters_dict_polygon["subtract_background"]
        )
        assert (
            result["number_of_spotfields"] == sample_parameters_dict_polygon["number_of_spotfields"]
        )
        assert (
            result["columns_per_spotfield"]
            == sample_parameters_dict_polygon["columns_per_spotfield"]
        )
        assert (
            result["spots_per_spotfield"] == sample_parameters_dict_polygon["spots_per_spotfield"]
        )
        assert result["spots"] == sample_parameters_dict_polygon["spots"]
        assert (
            result["background_rectangles"]
            == sample_parameters_dict_polygon["background_rectangles"]
        )

    def test_try_typecast_parameters_file_circle(
        self, sample_parameters_dict_circle, sample_parameters_dict_circle_raw
    ):
        """Correctly typecasts a raw CIRCLE parameters file (different coordinate key + diameter)."""
        result = try_typecast_parameters_file(
            "/test/path", sample_parameters_dict_circle_raw, spots_are_circular=True
        )

        assert result is not None

        assert isinstance(result["invert_lut"], bool)
        assert isinstance(result["subtract_background"], bool)
        assert isinstance(result["number_of_spotfields"], int)
        assert isinstance(result["columns_per_spotfield"], int)
        assert isinstance(result["spots_per_spotfield"], int)
        assert isinstance(result["spots"], list)
        assert isinstance(result["spots"][0]["type"], str)
        assert isinstance(result["spots"][0]["position"], list)
        assert isinstance(result["spots"][0]["position"][0], float)
        assert isinstance(result["spots"][0]["diameter"], float)
        assert isinstance(result["background_rectangles"], list)
        assert isinstance(result["background_rectangles"][0]["type"], str)
        assert isinstance(result["background_rectangles"][0]["coordinates"], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0][0], float)

        assert result["invert_lut"] == sample_parameters_dict_circle["invert_lut"]
        assert result["subtract_background"] == sample_parameters_dict_circle["subtract_background"]
        assert (
            result["number_of_spotfields"] == sample_parameters_dict_circle["number_of_spotfields"]
        )
        assert (
            result["columns_per_spotfield"]
            == sample_parameters_dict_circle["columns_per_spotfield"]
        )
        assert result["spots_per_spotfield"] == sample_parameters_dict_circle["spots_per_spotfield"]
        assert result["spots"] == sample_parameters_dict_circle["spots"]
        assert (
            result["background_rectangles"]
            == sample_parameters_dict_circle["background_rectangles"]
        )

    def test_try_typecast_typecasted_parameters_file_polygon(self, sample_parameters_dict_polygon):
        """Idempotent: already-typecasted POLYGON parameters are returned unchanged."""
        result = try_typecast_parameters_file(
            "/test/path",
            copy.deepcopy(sample_parameters_dict_polygon),
            spots_are_circular=False,
        )

        assert result is not None

        assert isinstance(result["invert_lut"], bool)
        assert isinstance(result["subtract_background"], bool)
        assert isinstance(result["number_of_spotfields"], int)
        assert isinstance(result["columns_per_spotfield"], int)
        assert isinstance(result["spots_per_spotfield"], int)
        assert isinstance(result["spots"], list)
        assert isinstance(result["spots"][0]["type"], str)
        assert isinstance(result["spots"][0]["coordinates"], list)
        assert isinstance(result["spots"][0]["coordinates"][0], list)
        assert isinstance(result["spots"][0]["coordinates"][0][0], float)
        assert isinstance(result["background_rectangles"], list)
        assert isinstance(result["background_rectangles"][0]["type"], str)
        assert isinstance(result["background_rectangles"][0]["coordinates"], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0][0], float)

        assert result["invert_lut"] == sample_parameters_dict_polygon["invert_lut"]
        assert (
            result["subtract_background"] == sample_parameters_dict_polygon["subtract_background"]
        )
        assert (
            result["number_of_spotfields"] == sample_parameters_dict_polygon["number_of_spotfields"]
        )
        assert (
            result["columns_per_spotfield"]
            == sample_parameters_dict_polygon["columns_per_spotfield"]
        )
        assert (
            result["spots_per_spotfield"] == sample_parameters_dict_polygon["spots_per_spotfield"]
        )
        assert result["spots"] == sample_parameters_dict_polygon["spots"]
        assert (
            result["background_rectangles"]
            == sample_parameters_dict_polygon["background_rectangles"]
        )

    def test_try_typecast_typecasted_parameters_file_circle(self, sample_parameters_dict_circle):
        """Idempotent: already-typecasted CIRCLE parameters are returned unchanged."""
        result = try_typecast_parameters_file(
            "/test/path",
            copy.deepcopy(sample_parameters_dict_circle),
            spots_are_circular=True,
        )

        assert result is not None

        assert isinstance(result["invert_lut"], bool)
        assert isinstance(result["subtract_background"], bool)
        assert isinstance(result["number_of_spotfields"], int)
        assert isinstance(result["columns_per_spotfield"], int)
        assert isinstance(result["spots_per_spotfield"], int)
        assert isinstance(result["spots"], list)
        assert isinstance(result["spots"][0]["type"], str)
        assert isinstance(result["spots"][0]["position"], list)
        assert isinstance(result["spots"][0]["position"][0], float)
        assert isinstance(result["spots"][0]["diameter"], float)
        assert isinstance(result["background_rectangles"], list)
        assert isinstance(result["background_rectangles"][0]["type"], str)
        assert isinstance(result["background_rectangles"][0]["coordinates"], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0], list)
        assert isinstance(result["background_rectangles"][0]["coordinates"][0][0], float)

        assert result["invert_lut"] == sample_parameters_dict_circle["invert_lut"]
        assert result["subtract_background"] == sample_parameters_dict_circle["subtract_background"]
        assert (
            result["number_of_spotfields"] == sample_parameters_dict_circle["number_of_spotfields"]
        )
        assert (
            result["columns_per_spotfield"]
            == sample_parameters_dict_circle["columns_per_spotfield"]
        )
        assert result["spots_per_spotfield"] == sample_parameters_dict_circle["spots_per_spotfield"]
        assert result["spots"] == sample_parameters_dict_circle["spots"]
        assert (
            result["background_rectangles"]
            == sample_parameters_dict_circle["background_rectangles"]
        )

    def test_try_typecast_parameters_file_invalid_data_polygon(
        self, sample_parameters_dict_polygon_raw
    ):
        """Returns None when typecasting fails for any field (POLYGON case)."""
        sample_parameters_dict_polygon_raw["number_of_spotfields"] = "not_a_number"
        result = try_typecast_parameters_file(
            "/test/path", sample_parameters_dict_polygon_raw, spots_are_circular=False
        )
        assert result is None

    def test_try_typecast_parameters_file_invalid_data_circle(
        self, sample_parameters_dict_circle_raw
    ):
        """Returns None when typecasting fails for any field (CIRCLE case)."""
        sample_parameters_dict_circle_raw["number_of_spotfields"] = "not_a_number"
        result = try_typecast_parameters_file(
            "/test/path", sample_parameters_dict_circle_raw, spots_are_circular=False
        )
        assert result is None

    # -------------------------------------------------------------------------
    # check_internal_value_consistency tests
    # -------------------------------------------------------------------------

    def test_check_internal_value_consistency_valid_polygon(self, sample_parameters_dict_polygon):
        """Valid POLYGON parameters pass internal consistency checks."""
        result = check_internal_value_consistency("/test/path", sample_parameters_dict_polygon)
        assert result is True

    def test_check_internal_value_consistency_valid_circle(self, sample_parameters_dict_circle):
        """Valid CIRCLE parameters pass internal consistency checks."""
        result = check_internal_value_consistency("/test/path", sample_parameters_dict_circle)
        assert result is True

    def test_check_internal_value_consistency_invalid_spotfields(
        self, sample_parameters_dict_polygon
    ):
        """Rejects parameters with number_of_spotfields < 1."""
        sample_parameters_dict_polygon["number_of_spotfields"] = 0
        result = check_internal_value_consistency("/test/path", sample_parameters_dict_polygon)
        assert result is False

    def test_check_internal_value_consistency_spot_count_mismatch(
        self, sample_parameters_dict_polygon
    ):
        sample_parameters_dict_polygon["spots"] = [sample_parameters_dict_polygon["spots"][0]]
        result = check_internal_value_consistency("/test/path", sample_parameters_dict_polygon)
        assert result is True

    # -------------------------------------------------------------------------
    # check_external_consistency tests
    # -------------------------------------------------------------------------

    def test_check_external_consistency_matching(
        self, sample_parameters_dict_polygon, sample_data_dict
    ):
        """Parameters file is consistent with its corresponding data file (happy path)."""
        result = check_external_consistency(
            sample_data_dict, "/test/path", sample_parameters_dict_polygon
        )
        assert result is True

    def test_check_external_consistency_spotfield_mismatch(
        self, sample_parameters_dict_polygon, sample_data_dict
    ):
        """Rejects parameters file if the number of spotfields or total spots does not match the data file."""
        double_data = {"values": [sample_data_dict["values"][0], sample_data_dict["values"][0]]}

        result = check_external_consistency(
            double_data, "/test/path", sample_parameters_dict_polygon
        )
        assert result is False

        sample_parameters_dict_polygon["number_of_spotfields"] = 3

        result = check_external_consistency(
            sample_data_dict, "/test/path", sample_parameters_dict_polygon
        )
        assert result is False

    # -------------------------------------------------------------------------
    # typecast_to_bool helper tests
    # -------------------------------------------------------------------------

    def test_bool_input_true(self):
        assert typecast_to_bool(True) is True

    def test_bool_input_false(self):
        """typecast_to_bool returns False when input is already a boolean False."""
        assert typecast_to_bool(False) is False

    def test_string_true_variants(self):
        """typecast_to_bool correctly converts all common string representations of True."""
        true_variants = ["true", "TRUE", "True", "TrUe", "tRuE"]
        for variant in true_variants:
            assert typecast_to_bool(variant) is True, f"Failed for: {variant}"

    def test_string_false_variants(self):
        """typecast_to_bool correctly converts all common string representations of False."""
        false_variants = ["false", "FALSE", "False", "FaLsE", "fAlSe"]
        for variant in false_variants:
            assert typecast_to_bool(variant) is False, f"Failed for: {variant}"

    def test_empty_string_raises_error(self):
        """typecast_to_bool raises JSONDecodeError for an empty string (invalid boolean representation)."""
        with pytest.raises(json.JSONDecodeError):
            typecast_to_bool("")
