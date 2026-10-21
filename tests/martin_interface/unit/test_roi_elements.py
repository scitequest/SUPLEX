from dataclasses import is_dataclass

import pytest

from suplex.martin_interface.roi_elements import (
    Coordinates,
    RoiParameters,
    Spot,
    SpotValues,
)


class TestRoiElements:
    """Tests for the core ROI dataclasses (Coordinates, SpotValues, RoiParameters) and the Spot wrapper."""

    # -------------------------------------------------------------------------
    # Coordinates tests
    # -------------------------------------------------------------------------

    def test_coordinates_creation(self, sample_parameters_dict_polygon):
        """Creates a Coordinates dataclass instance from raw polygon data and verifies fields."""
        coord_data = sample_parameters_dict_polygon["spots"][0]["coordinates"][0]
        coord = Coordinates(x=coord_data[0], y=coord_data[1])
        assert is_dataclass(coord)

        assert coord.x == coord_data[0]
        assert coord.y == coord_data[1]

    def test_coordinates_frozen(self, sample_parameters_dict_polygon):
        """Coordinates dataclass is frozen (immutable) and raises AttributeError on mutation."""
        coord_data = sample_parameters_dict_polygon["spots"][0]["coordinates"][0]
        coord = Coordinates(coord_data[0], coord_data[1])

        with pytest.raises(AttributeError):
            coord.x = 15

    # -------------------------------------------------------------------------
    # SpotValues tests
    # -------------------------------------------------------------------------

    def test_spot_values_creation(self, sample_data_dict):
        """Creates a SpotValues dataclass from raw data dictionary and verifies all fields."""
        spot_data = sample_data_dict["values"][0]
        spot_values = SpotValues(
            mean_minus_min=spot_data["mean_minus_min"],
            normalized_mean=spot_data["normalized_mean"],
            spot=spot_data["spot"],
            row=spot_data["row"],
            col=spot_data["col"],
            min_val=spot_data["min"],
            max_val=spot_data["max"],
            mean_val=spot_data["mean"],
            std_deviation=spot_data["std_deviation"],
        )
        assert is_dataclass(spot_values)

        assert spot_values.mean_minus_min == spot_data["mean_minus_min"]
        assert spot_values.normalized_mean == spot_data["normalized_mean"]
        assert spot_values.spot == spot_data["spot"]
        assert spot_values.row == spot_data["row"]
        assert spot_values.col == spot_data["col"]
        assert spot_values.min_val == spot_data["min"]
        assert spot_values.max_val == spot_data["max"]
        assert spot_values.mean_val == spot_data["mean"]
        assert spot_values.std_deviation == spot_data["std_deviation"]

    # -------------------------------------------------------------------------
    # RoiParameters tests
    # -------------------------------------------------------------------------

    def test_roi_parameters_polygon(self, sample_parameters_dict_polygon):
        """Creates RoiParameters for a POLYGON shape and verifies fields."""
        polygon_data = sample_parameters_dict_polygon["spots"][0]
        coords = [Coordinates(coord[0], coord[1]) for coord in polygon_data["coordinates"]]

        roi = RoiParameters(shape=polygon_data["type"], coordinates=coords, diameter=None)
        assert is_dataclass(roi)

        assert roi.shape == polygon_data["type"]
        assert len(roi.coordinates) == len(polygon_data["coordinates"])
        assert roi.diameter is None

    def test_roi_parameters_circle(self, sample_parameters_dict_circle):
        """Creates RoiParameters for a CIRCLE shape (different coordinate key + diameter)."""
        circle_data = sample_parameters_dict_circle["spots"][0]
        center = [Coordinates(circle_data["position"][0], circle_data["position"][1])]

        roi = RoiParameters(
            shape=circle_data["type"],
            coordinates=center,
            diameter=circle_data["diameter"],
        )

        assert roi.shape == circle_data["type"]
        assert len(roi.coordinates) == 1
        assert roi.diameter == circle_data["diameter"]

    # -------------------------------------------------------------------------
    # Spot tests
    # -------------------------------------------------------------------------

    def test_spot_creation_and_properties(self, sample_data_dict, sample_parameters_dict_circle):
        """Creates a fully populated Spot with values and circle parameters; verifies property delegation."""
        spot_data = sample_data_dict["values"][0]
        circle_data = sample_parameters_dict_circle["spots"][0]

        spot_values = SpotValues(
            mean_minus_min=spot_data["mean_minus_min"],
            normalized_mean=spot_data["normalized_mean"],
            spot=spot_data["spot"],
            row=spot_data["row"],
            col=spot_data["col"],
            min_val=spot_data["min"],
            max_val=spot_data["max"],
            mean_val=spot_data["mean"],
            std_deviation=spot_data["std_deviation"],
        )

        roi_params = RoiParameters(
            shape=circle_data["type"],
            coordinates=[Coordinates(circle_data["position"][0], circle_data["position"][1])],
            diameter=circle_data["diameter"],
        )

        spot = Spot(spot_values=spot_values, spot_parameters=roi_params)
        assert is_dataclass(spot)

        assert spot.mean_minus_min == spot_data["mean_minus_min"]
        assert spot.normalized_mean == spot_data["normalized_mean"]
        assert spot.spot == spot_data["spot"]
        assert spot.row == spot_data["row"]
        assert spot.col == spot_data["col"]
        assert spot.min_val == spot_data["min"]
        assert spot.max_val == spot_data["max"]
        assert spot.mean_val == spot_data["mean"]
        assert spot.std_deviation == spot_data["std_deviation"]
        assert spot.shape == circle_data["type"]
        assert spot.diameter == circle_data["diameter"]
        assert len(spot.coordinates) == 1

    def test_spot_none_parameters(self, sample_data_dict):
        """Handles Spot with no ROI parameters (all optional properties return None)."""
        spot_data = sample_data_dict["values"][0]
        spot_values = SpotValues(
            spot_data["mean_minus_min"],
            spot_data["normalized_mean"],
            spot_data["spot"],
            spot_data["row"],
            spot_data["col"],
            spot_data["min"],
            spot_data["max"],
            spot_data["mean"],
            spot_data["std_deviation"],
        )
        spot = Spot(spot_values=spot_values, spot_parameters=None)

        assert spot.spot_parameters is None
        assert spot.shape is None
        assert spot.diameter is None
        assert spot.coordinates is None
