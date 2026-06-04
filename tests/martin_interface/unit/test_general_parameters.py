import pytest
from dataclasses import is_dataclass
from src.martin_interface.general_parameters import GeneralParameters
from src.martin_interface.roi_elements import RoiParameters, Coordinates


class TestGeneralParameters:
    """Tests for the GeneralParameters dataclass that holds measurement-wide settings and background rectangles."""

    # -------------------------------------------------------------------------
    # GeneralParameters creation and validation
    # -------------------------------------------------------------------------

    def test_general_parameters_creation(self, sample_parameters_dict_polygon):
        """Creates a GeneralParameters instance from polygon sample data (including background rectangles) and verifies all fields."""
        background_data = sample_parameters_dict_polygon["background_rectangles"][0]
        background_rect = RoiParameters(
            shape=background_data["type"],
            coordinates=[
                Coordinates(coord[0], coord[1]) for coord in background_data["coordinates"]
            ],
            diameter=None,
        )
        assert is_dataclass(background_rect)

        params = GeneralParameters(
            invert_lut=sample_parameters_dict_polygon["invert_lut"],
            subtract_background=sample_parameters_dict_polygon["subtract_background"],
            number_of_spotfields=sample_parameters_dict_polygon["number_of_spotfields"],
            columns_per_spotfield=sample_parameters_dict_polygon["columns_per_spotfield"],
            spots_per_spotfield=sample_parameters_dict_polygon["spots_per_spotfield"],
            background_rectangles=[background_rect],
        )

        assert is_dataclass(params)
        assert params.invert_lut == sample_parameters_dict_polygon["invert_lut"]
        assert params.subtract_background == sample_parameters_dict_polygon["subtract_background"]
        assert params.number_of_spotfields == sample_parameters_dict_polygon["number_of_spotfields"]
        assert (
            params.columns_per_spotfield == sample_parameters_dict_polygon["columns_per_spotfield"]
        )
        assert params.spots_per_spotfield == sample_parameters_dict_polygon["spots_per_spotfield"]
        assert len(params.background_rectangles) == 1

    # -------------------------------------------------------------------------
    # Immutability
    # -------------------------------------------------------------------------

    def test_general_parameters_frozen(self, sample_parameters_dict_circle):
        """GeneralParameters dataclass is frozen (immutable) and raises AttributeError on mutation attempts."""
        params = GeneralParameters(
            invert_lut=sample_parameters_dict_circle["invert_lut"],
            subtract_background=sample_parameters_dict_circle["subtract_background"],
            number_of_spotfields=1,
            columns_per_spotfield=1,
            spots_per_spotfield=1,
            background_rectangles=[],
        )

        with pytest.raises(AttributeError):
            params.invert_lut = False
