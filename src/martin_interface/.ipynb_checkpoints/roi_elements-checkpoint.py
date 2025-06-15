from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class Coordinates:
    """
    Represents a 2D coordinate point.
    
    Attributes:
        x (float): The x-coordinate
        y (float): The y-coordinate
    """
    x: float
    y: float

@dataclass(frozen=True)
class SpotValues:
    """
    Contains measured values for an individual spot as well as their grid-position.
    A spot measurement is a statistical evaluation of all pixels contained within the measurement-ROI.
    
    Attributes:
        mean_minus_min (float): Difference between the `mean_val` of this spot and the lowest `mean_val` of the entire dataset.
        normalized_mean (float): The `mean_minus_min` value of this spot divided by the highest `mean_minus_min` of the entire dataset.
        spot (int): Index of the spotfield in which the spot is contained.
        row (int): Row position of this spot.
        col (int): Column position of this spot.
        min_val (float): Signal of the pixel with the lowest intensity within the measurement-ROI.
        max_val (float): Signal of the pixel with the highest intensity within the measurement-ROI.
        mean_val (float): Mean signal intensity across all pixels contained within the measurement-ROI.
        std_deviation (float): Standard deviation across all pixels contained within the measurement-ROI.
    """
    mean_minus_min: float
    normalized_mean: float
    spot: int
    row: int
    col: int
    min_val: float # Changed name due to `min` beeing a keyword.
    max_val: float # Changed name due to `max` beeing a keyword.
    mean_val: float # Changed to fit in with min and max.
    std_deviation: float

@dataclass(frozen=True)
class RoiParameters:
    """
    Parameters defining positional information of the region of interest (ROI) used for measurement.
    
    Attributes:
        shape (str): Shape type of the ROI. Either CIRCLE or POLYGON.
        coordinates (List[Coordinates]): List of coordinate points defining the ROI.
        diameter (float): Diameter of the ROI. Only relevant for circular shapes, will be None for polygons.
    """
    shape: str # Changed name due to `type` beeing a keyword.
    coordinates: List[Coordinates]
    diameter: float
    
@dataclass(frozen=True)
class Spot:
    """
    Summarizes measured values and positional information of a spot.
    
    Attributes:
        spot_values (SpotValues): Measured values for this spot.
        spot_parameters (RoiParameters): ROI parameters used for measurement.
    """
    spot_values: SpotValues
    spot_parameters: RoiParameters
    
    @property
    def mean_minus_min(self) -> float:
        return self.spot_values.mean_minus_min
    
    @property
    def normalized_mean(self) -> float:
        return self.spot_values.normalized_mean
    
    @property
    def spot(self) -> int:
        return self.spot_values.spot
    
    @property
    def row(self) -> int:
        return self.spot_values.row
    
    @property
    def col(self) -> int:
        return self.spot_values.col
    
    @property
    def min_val(self) -> float:
        return self.spot_values.min_val
    
    @property
    def max_val(self) -> float:
        return self.spot_values.max_val
    
    @property
    def mean_val(self) -> float:
        return self.spot_values.mean_val
    
    @property
    def std_deviation(self) -> float:
        return self.spot_values.std_deviation
    
    @property
    def shape(self) -> Optional[str]:
        """
        Returns the shape of the ROI used for this spot measurement.
        
        Returns:
            Optional[str]: The shape type or None if spot_parameters is None.
        """
        if self.spot_parameters is None:
            return None
        return self.spot_parameters.shape
    
    @property
    def diameter(self) -> Optional[float]:
        """
        Returns the diameter of the ROI if available.
        
        Returns:
            Optional[float]: The diameter value if spot_parameters exists otherwise None.
        """
        if self.spot_parameters is None:
            return None
    
        return self.spot_parameters.diameter
    
    @property
    def coordinates(self) -> Optional[List[Coordinates]]:
        """
        Returns the coordinates defining the ROI.
        
        Attempts to retrieve coordinates from the 'coordinates' attribute of spot_parameters.
        
        Returns:
            Optional[List[Coordinates]]: List of coordinate points defining the ROI,
                                       or None if not available
        """
        if self.spot_parameters is None:
            return None

        return self.spot_parameters.coordinates