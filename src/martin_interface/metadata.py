from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Patient:
    """
    Represents general patient or sample information.

    Attributes:
        pat_id (str): Unique identifier for the measurement conducted.
        name (str): Full name of the measurement conducted.
        tags (List[str]): List of tags or labels associated with a measurement.
    """

    pat_id: str  # Changed name due to 'id' beeing a keyword.
    name: str
    tags: List[str]


@dataclass(frozen=True)
class Image:
    """
    Stores metadata about the measured image.

    Attributes:
        created (datetime): Timestamp when the image was captured.
        imager (str): Identifier or name of the imaging device.
        pixel_binning (int): Pixel binning factor used during image capture.
        exposure_time (timedelta): Duration of exposure of image capture.
    """

    created: datetime
    imager: str
    pixel_binning: int
    exposure_time: timedelta


@dataclass(frozen=True)
class Concentration:
    """
    Represents a concentration value with its unit.

    Attributes:
        value (float): Numerical value of the concentration.
        unit (str): Unit of measurement of the concentration.
    """

    value: float
    unit: str


@dataclass(frozen=True)
class Incubation:
    """
    Details of an incubation process, including solution and concentrations.

    Attributes:
        solution (str): Name or type of the solution used in the incubation.
        stock_concentration (Concentration): Initial concentration of the solution.
        final_concentration (Concentration): Final concentration after dilution or process.
        incubation_time (datetime): Duration of the incubation process.
    """

    solution: str
    stock_concentration: Concentration
    final_concentration: Concentration
    incubation_time: timedelta


@dataclass(frozen=True)
class Metadata:
    """
    Collection of a measurements metadata

    Attributes:
        version (str): Version of the metadata schema.
        datetime (str): Timestamp of when the measurement was conducted.
        patient (Patient): Information on the sample or patient of a measurement.
        image (Image): Imaging metadata of the measurement.
        incubations (List[Incubation]): List of incubation processes applied.
    """

    version: str
    datetime: datetime
    patient: Patient
    image: Image
    incubations: List[Incubation]

    @property
    def pat_id(self) -> str:
        return self.patient.pat_id

    @property
    def name(self) -> str:
        return self.patient.name

    @property
    def tags(self) -> List[str]:
        return self.patient.tags

    @property
    def created(self) -> datetime:
        return self.image.created

    @property
    def imager(self) -> str:
        return self.image.imager

    @property
    def pixel_binning(self) -> int:
        return self.image.pixel_binning

    @property
    def exposure_time(self) -> timedelta:
        return self.image.exposure_time
