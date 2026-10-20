from dataclasses import dataclass
from typing import List
from .roi_elements import RoiParameters


@dataclass(frozen=True)
class GeneralParameters:
    """
    General parameters of a measurement conducted with MARTin.
    Spot specific coordinates are stored separately in instances of `RoiParameters` wich are stored in `Spot` objects.

    Attributes:
        invert_lut (bool): Whether the lookup table was inverted for the measurement.
        subtract_background (bool): Whether the cumulative signal of `background_rectangles` was used for noise subtraction
        number_of_spotfields (int): The number of spotfields of a measurement.
        columns_per_spotfield (int): Number of columns in each spotfield.
        spots_per_spotfield (int): Number of spots in each spotfield.
        background_rectangles (List[RoiParameters]): List which contains positional information of all background rectangles.
    """

    invert_lut: bool
    subtract_background: bool
    number_of_spotfields: int
    columns_per_spotfield: int
    spots_per_spotfield: int
    background_rectangles: List[RoiParameters]
