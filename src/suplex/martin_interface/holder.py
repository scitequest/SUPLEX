from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass(frozen=True)
class PathHolder:
    """
    An immutable dataclass to store file system paths related to dataset processing.
    Prerequisite paths are `dataset_path` and `data_path`, all other paths are tolerated to not exist.
    If optional paths do not exist they will be set to None by default.

    Attributes:
        dataset_path (str): The path to the directory of the entire dataset.
        data_path (str): The path to the data file.
        data_statistics_path (Optional[str]): The path to the data_statistics file, if available.
        metadata_path (Optional[str]): The path to the metadata file, if available.
        parameters_path (Optional[str]): The path to the parameters file, if available.
        image_path (Optional[str]): The path to the image file, if available.
        annotated_image_path (Optional[str]): The path to the annotated image file, if available.
        suplex_path (Optional[str]): The path to the suplex file, if available.
    """

    dataset_path: str
    data_path: str
    data_statistics_path: Optional[str] = None
    metadata_path: Optional[str] = None
    parameters_path: Optional[str] = None
    image_path: Optional[str] = None
    annotated_image_path: Optional[str] = None
    suplex_path: Optional[str] = None


@dataclass(frozen=True)
class FileHolder:
    """
    An immutable dataclass to store the files specified in an instance of `PathHolder` as lists of dictionaries or dictionaries.
    The only prerequisite file is the `data_file`, all other files are tolerated to not exist.
    If optional files do not exist they will be set to None by default.

    Attributes:
        data_file (list[dict[Any, Any]]): A list of dictionaries containing primary MARTin measurement data. Each entry of this list represents an individual measure field.
        data_statistics_file (list[dict[Any, Any]]): A list of dictionaries containing statistical comparisons between measurements of sample copies from `data_file`.
        metadata_file (list[dict[Any, Any]]): A dictionary containing metadata.
        parameters_file (list[dict[Any, Any]]): A list of dictionaries containing the parameters of a measurement.
        suplex_file (list[dict[Any, Any]]): A dictionary for storage, allowing to carry over information between runtime sessions of this software.
    """

    data_file: dict[str, List[dict[str, Any]]]
    data_statistics_file: Optional[dict[str, List[dict[str, Any]]]] = None
    metadata_file: Optional[dict[Any, Any]] = None
    parameters_file: Optional[dict[str, Any]] = None
    suplex_file: Optional[dict[str, Any]] = None
