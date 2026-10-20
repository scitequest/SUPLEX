from .roi_elements import *
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class DataStatistics:
    """
    Statistical data of a collection of spots.

    Attributes:
        row (int): Row position index.
        col (int): Column position index.
        adjusted_average (float): Average across all `mean_minus_min` values associated with a sample.
        adjusted_average_std_deviation (float): Standard deviation across all `mean_minus_min` values associated with a sample.
        relative_adjusted_average_std_deviation (float): `adjusted_average_std_deviation` divided by `adjusted_average` in percent.
        normalized_average (float): Average across all `normalized_mean` values associated with a sample.
        normalized_average_std_deviation (float): Standard deviation across all `normalized_mean` values associated with a sample.
        relative_normalized_average_std_deviation (float): `normalized_average_std_deviation` divided by `normalized_average` in percent.
    """

    row: int
    col: int
    adjusted_average: float
    adjusted_average_std_deviation: float
    relative_adjusted_average_std_deviation: float
    normalized_average: float
    normalized_average_std_deviation: float
    relative_normalized_average_std_deviation: float


class Sample:
    """
    A collection of all spots derived from the same sample as well as statistical data across these duplicates.

    Processes raw spot data and ROI parameters from JSON format, converting them into structured Spot objects with proper data types.

    Attributes:
        spots: List of dictionaries containing raw spot measurement data
        spot_statistics: Optional dictionary containing statistical data for the sample
        parameters: Optional list of ROI parameter dictionaries for each spot
    """

    def __init__(
        self,
        spots: List[Dict[str, Any]],
        spot_statistics: Optional[Dict[str, Any]],
        parameters: Optional[List[Dict[str, Any]]],
    ) -> None:
        self._spots = self.init_spots(spots=spots, parameters=parameters)
        self._statistics = None
        if spot_statistics is not None:
            self._statistics = DataStatistics(**spot_statistics)

    def init_spots(
        self, spots: List[Dict[str, Any]], parameters: Optional[List[Dict[str, Any]]]
    ) -> List[Spot]:
        """
        Initialize Spot objects from raw JSON data.

        Converts raw spot dictionaries and ROI parameters into structured Spot objects.
        Handles key name mapping from JSON format to Python-friendly names.

        Args:
            spots: List of dictionaries containing raw spot data from JSON.
            parameters: Optional list of ROI parameter dictionaries for each spot.

        Returns:
            List[Spot]: List of initialized Spot objects with values and ROI parameters.
        """
        samples = []
        for i, spot in enumerate(spots):
            # Change key names of JSON since some of them are python-keywords.
            spot_dict = {
                "mean_minus_min": spot["mean_minus_min"],
                "normalized_mean": spot["normalized_mean"],
                "spot": spot["spot"],
                "row": spot["row"],
                "col": spot["col"],
                "min_val": spot["min"],
                "max_val": spot["max"],
                "mean_val": spot["mean"],
                "std_deviation": spot["std_deviation"],
            }
            spot_values = SpotValues(**spot_dict)
            roi_parameters = None
            # We have to do this explicitly since the terminology is different from the JSON and because we format polygons and circles the same way.
            # We mainly do this because term `type` specified in our JSONs is a keyword in python.
            if parameters is not None:
                shape = parameters[i]["type"]
                if shape == "POLYGON":
                    coordinates = [Coordinates(*coord) for coord in parameters[i]["coordinates"]]
                    diameter = None
                elif shape == "CIRCLE":
                    coordinates = [Coordinates(*parameters[i]["position"])]
                    diameter = parameters[i]["diameter"]
                else:
                    continue
                roi_parameters = RoiParameters(
                    shape=shape, coordinates=coordinates, diameter=diameter
                )

            samples.append(Spot(spot_values, roi_parameters))
        return samples

    @property
    def spots(self) -> List[Spot]:
        return self._spots

    @property
    def data_statistics(self) -> Optional[DataStatistics]:
        return self._statistics
