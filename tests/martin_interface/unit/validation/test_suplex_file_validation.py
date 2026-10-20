from unittest.mock import patch

from suplex.martin_interface.validation.suplex_file_validation import (
    try_get_validated_suplex_file,
    try_typecast_suplex_file,
)


class TestSuplexFileValidation:
    """Tests for the suplex file validation functions (currently minimal/placeholder until the full Suplex file format is finalized)."""

    # -------------------------------------------------------------------------
    # try_get_validated_suplex_file tests
    # -------------------------------------------------------------------------

    @patch("suplex.martin_interface.validation.suplex_file_validation.try_get_valid_json")
    def test_try_get_validated_suplex_file_invalid_json(self, mock_json):
        """Returns None when the underlying JSON parsing fails."""
        mock_json.return_value = None

        result = try_get_validated_suplex_file("/test/path")
        assert result is None

    @patch("suplex.martin_interface.validation.suplex_file_validation.try_get_valid_json")
    def test_try_get_validated_suplex_file_valid(self, mock_json, sample_suplex_dict):
        """Successfully returns the suplex dictionary when JSON validation passes."""
        mock_json.return_value = sample_suplex_dict

        result = try_get_validated_suplex_file("/test/path")
        assert result == sample_suplex_dict

    @patch("suplex.martin_interface.validation.suplex_file_validation.try_get_valid_json")
    def test_try_get_validated_suplex_file_empty_dict(self, mock_json):
        """Accepts an empty dictionary as a valid (minimal) suplex file."""
        mock_json.return_value = {}

        result = try_get_validated_suplex_file("/test/path")
        assert result == {}

    # -------------------------------------------------------------------------
    # try_typecast_suplex_file tests
    # -------------------------------------------------------------------------

    def test_try_typecast_suplex_file(self, sample_suplex_dict):
        """Currently a no-op that simply returns the input dictionary unchanged (typecasting will be implemented later)."""
        # Currently just returns the input
        result = try_typecast_suplex_file("/test/path", sample_suplex_dict)
        assert result == sample_suplex_dict
