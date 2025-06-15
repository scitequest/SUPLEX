from .holder import *
from .sample import Sample, DataStatistics
from .roi_elements import Spot, RoiParameters, Coordinates
from .general_parameters import GeneralParameters
from .metadata import *
from .project import Project

import copy
from datetime import datetime
import statistics
import math

class Dataset:
    """
    This class is the overarching structure which orders all data related to a measurement.
    In other words: a dataset stores the information of an individual measurement.

    Attributes:
        _path_holder (PathHolder): Object containing the paths to all available files of a measurement.
        _file_holder (FileHolder): Object containing all available files of a measurement as JSONs.
        _project (Project): The project associated with the dataset.
        _samples (List[Sample]): List of Sample objects, each containing all spots for an individual sample, along with their positional information and statistical data computed between them.
        _general_parameters (GeneralParameters): General parameters of the measurement.
        _metadata (Metadata): Metadata associated with the dataset.
        _suplex_file (Any): File used to store analyses and additional information added via `SUPLEX` modules.
    """
    def __init__(self, path_holder: PathHolder, file_holder: FileHolder, project: Project) -> None:
        self._path_holder = path_holder
        self._file_holder = file_holder
        self._project = project
        
        self._samples = self.init_samples()
        self._general_parameters = self.init_general_parameters()
        self._metadata = self.init_metadata()
        self._suplex_file = copy.deepcopy(file_holder.suplex_file)

    def init_samples(self) -> List[Sample]:
        """
        This re-organizes the original structure of our measurement files into a spot focused approach.
        Spots of the same row and column are assumed to be sample duplicates and are collected with their corresponding parameters and data_statistics entry into an instance of `Sample`.

        Returns:
            A list containing all samples of a measurement.
        """
        data = self._file_holder.data_file["values"]
        
        data_statistics = None 
        if self._file_holder.data_statistics_file is not None:
            data_statistics = self._file_holder.data_statistics_file["values"]

        # Incase there has been no file or the file could not be read in.
        if data_statistics is None:
            data_statistics = self.generate_data_statistics()
        
        spot_parameters = None
        if self._file_holder.parameters_file is not None:
            spot_parameters = self._file_holder.parameters_file["spots"]
        
        samples = []
        # Calculate number of spots using the highest index spot.
        n_spots = (1 + data[-1]["row"]) * (1 + data[-1]["col"])
        n_cols = data[-1]["col"] + 1
        spots = [[] for _ in range(n_spots)]
        parameters = None
        if spot_parameters is not None:
            parameters = [[] for _ in range(n_spots)]

        # Collects spots of the same row and column in a sublist.
        # The same is done for the corresponding parameters.
        for i, spot in enumerate(data):
            internal_index = spot["col"] + spot["row"] * n_cols
            spots[internal_index].append(spot)
            if spot_parameters is not None:
                parameters[internal_index].append(spot_parameters[i])

        for i, spot_set in enumerate(spots):
            params = None
            if spot_parameters is not None:
                params = parameters[i]
                
            samples.append(Sample(spots = spot_set, spot_statistics = data_statistics[i], parameters = params))
            
        return samples

    def generate_data_statistics(self) -> List[DataStatistics]:
        """
        Values of DataStatistics are calculated in cases where either there is no data_statistics file or where it could not be read in.
        The calculations are analogous to the ones conducted in MARTin.

        Returns:
            List of DataStatistics objects based on a data-file.
        """
        data = self._file_holder.data_file["values"]
        n_spotfield_spots = int(len(data) / (1 + data[-1]["spot"]))
        data_statistics = [{
            "row": 0,
            "col": 0,
            "mean_minus_min_values": [],
            "normalized_mean_values": []
        } for _ in range(n_spotfield_spots)]

        # Set up format and collect mean_minus_min and normalized_mean values for each sample.
        for i, spot in enumerate(data):
            spotfield_index = i % n_spotfield_spots
            if spot["spot"] == 0:
                data_statistics[spotfield_index]["row"] = spot["row"]
                data_statistics[spotfield_index]["col"] = spot["col"]
            data_statistics[spotfield_index]["mean_minus_min_values"].append(spot["mean_minus_min"])
            data_statistics[spotfield_index]["normalized_mean_values"].append(spot["normalized_mean"])

        for d_stat in data_statistics:
            mean_minus_min_values = d_stat.pop("mean_minus_min_values")
            normalized_mean_values = d_stat.pop("normalized_mean_values")
            
            # Calculating mean_minus_min_values
            adjusted_average = statistics.mean(mean_minus_min_values)
            adjusted_average_std_deviation = statistics.stdev(mean_minus_min_values) if len(mean_minus_min_values) > 1 else 0
            relative_adjusted_average_std_deviation = (adjusted_average_std_deviation*100 / adjusted_average) if adjusted_average != 0 else 0
            if math.isnan(relative_adjusted_average_std_deviation):
                relative_adjusted_average_std_deviation = 0.0
            
            # Calculating normalized_mean_values
            normalized_average = statistics.mean(normalized_mean_values)
            normalized_average_std_deviation = statistics.stdev(normalized_mean_values) if len(normalized_mean_values) > 1 else 0
            relative_normalized_average_std_deviation = (normalized_average_std_deviation*100 / normalized_average) if normalized_average != 0 else 0
            if math.isnan(relative_normalized_average_std_deviation):
                relative_normalized_average_std_deviation = 0.0
            
            # Adding new values to dictionary
            d_stat["adjusted_average"] = adjusted_average
            d_stat["adjusted_average_std_deviation"] = adjusted_average_std_deviation
            d_stat["relative_adjusted_average_std_deviation"] = relative_adjusted_average_std_deviation
            d_stat["normalized_average"] = normalized_average
            d_stat["normalized_average_std_deviation"] = normalized_average_std_deviation
            d_stat["relative_normalized_average_std_deviation"] = relative_normalized_average_std_deviation                   
            
        return data_statistics

    def init_general_parameters(self) -> GeneralParameters:
        """
        Initializes non-spot-specific parameters of a measurement as an instance of `GeneralParameters`.
        Spot-specific parameters are stored in the individual entries of `_samples`.

        Returns:
            GeneralParameters storing non-spot-specific parameters of a measurement.
        """
        parameters_file = self._file_holder.parameters_file
        if parameters_file is None:
            return None

        background_rectangles = []
        for b_rect in parameters_file["background_rectangles"]:
            shape = b_rect["type"]
            coordinates = [Coordinates(*coord) for coord in b_rect["coordinates"]]
            diameter = None
            background_rectangles.append(RoiParameters(shape=shape,coordinates=coordinates,diameter=diameter))
            
        parameters = {
            "invert_lut": parameters_file["invert_lut"],
            "subtract_background": parameters_file["subtract_background"],
            "number_of_spotfields": parameters_file["number_of_spotfields"],
            "columns_per_spotfield": parameters_file["columns_per_spotfield"],
            "spots_per_spotfield": parameters_file["spots_per_spotfield"],
            "background_rectangles": background_rectangles
        }
        
        return GeneralParameters(**parameters)
        
    def init_metadata(self) -> Metadata:
        """
        Initializes the metadata of a measurement as an instance of `Metadata`.

        Returns:
            Metadata object related to a measurement.
        """
        metadata_file = self._file_holder.metadata_file
        if metadata_file is None:
            return None

        # Explicit since we have to rename id to pat_id
        patient = {
            "pat_id": metadata_file["patient"]["id"],
            "name": metadata_file["patient"]["name"],
            "tags": metadata_file["patient"]["tags"]
        }

        incubations = []
        for incub in metadata_file["incubations"]:
            incubation_step = {
                "solution": incub["solution"],
                "stock_concentration": Concentration(**incub["stock_concentration"]),
                "final_concentration": Concentration(**incub["final_concentration"]),
                "incubation_time": incub["incubation_time"]
            }
            incubations.append(Incubation(**incubation_step))
        
        metadata = {
            "version": metadata_file["version"],
            "datetime": metadata_file["datetime"],
            "patient": Patient(**patient),
            "image": Image(**metadata_file["image"]),
            "incubations": incubations
        }
        
        return Metadata(**metadata)

    def get_name_label(self) -> str:
            """
            Returns a formatted string combining patient ID and name for dataset depiction on the GUI.
            
            Returns:
                str: A string in the format 'pat_id - name'.
            """
            return f"{self._metadata.pat_id} - {self._metadata.name}"
    
    def get_image_creation_label(self) -> str:
        """
        Returns a formatted string combining the creation date and name label for dataset depiction on the GUI.
        
        Returns:
            str: A string combining the creation date and the name label.
        """
        ret = str(self._metadata.created.date())
        return ret + self.get_name_label
    
    def get_measure_date_label(self) -> str:
        """
        Returns a formatted string combining the measurement date and name label for dataset depiction on the GUI.
        
        Returns:
            str: A string combining the measurement date and the name label.
        """
        ret = str(self._metadata.datetime.date())
        return ret + self.get_name_label
    
    def has_some_tags(self, comp_tags: List[str]) -> bool:
        """
        Checks if any of the provided tags are present in the dataset's tags or suplex_tags.
        
        Args:
            comp_tags (List[str]): List of tags to check against.
            
        Returns:
            bool: True if at least one tag from comp_tags is found, False otherwise.
        """
        tag_list = self.tags + self.suplex_tags
        return any(tag in tag_list for tag in comp_tags)
    
    def has_all_tags(self, comp_tags: List[str]) -> bool:
        """
        Checks if all provided tags are present in the dataset's tags or suplex_tags.
        
        Args:
            comp_tags (List[str]): List of tags to check against.
            
        Returns:
            bool: True if all tags from comp_tags are found, False if comp_tags is empty or not all tags are found.
        """
        tag_list = self.tags + self.suplex_tags
        if not comp_tags:
            return False
        return set(comp_tags).issubset(set(tag_list))
    
    def is_in_timeframe(self, check_date: datetime, start_date: datetime, end_date: datetime) -> bool:
        """
        Checks if the dataset's creation date falls within the specified timeframe.
        The parameter `check_date` is either `metadata.datetime` or `metadata.created`
        
        Args:
            check_date (datetime): Date to be checked if it is in the given timeframe.
            start_date (datetime): Start date of the timeframe.
            end_date (datetime): End date of the timeframe.
            
        Returns:
            bool: True if the creation date is within the timeframe, False otherwise.
        """
        if self._metadata is None:
            return False
        
        return start_date <= check_date <= end_date

    # Allowing direct access to attributes of relevant objects of `Dataset`.
    @property    
    def measure_date(self) -> datetime | None:
        if self._metadata is not None:
            return self._metadata.datetime
        return None
        
    @property
    def image_creation_date(self) -> datetime | None:
        if self._metadata is not None:
            return self._metadata.created
        return None

    @property
    def tags(self) -> List[any]:
        if self._metadata is not None:
            return self._metadata.tags
        return []

    @property
    def suplex_tags(self) -> List[str]:
        if self._suplex_file is not None:
            if "tags" in self._suplex_file.keys():
                if isinstance(self._suplex_file["tags"], list):
                    return self._suplex_file["tags"]
        return []
        
    # Returns lists of specific attributes of `samples`.
    @property
    def spots(self) -> List[List[Spot]]:
        return [sample_list.spots for sample_list in self._samples]

    @property
    def data_statistics(self) -> List[DataStatistics]:
        return [sample_list.data_statistics for sample_list in self._samples]

    # Allow direct access for all parameters incase future devs need it.
    @property
    def path_holder(self) -> PathHolder:
        return self._path_holder
    
    @property
    def file_holder(self) -> FileHolder:
        return self._file_holder
    
    @property
    def project(self) -> Project:
        return self._project
    
    @property
    def samples(self) -> List[Sample]:
        return self._samples
    
    @property
    def general_parameters(self) -> List[RoiParameters]:
        return self._general_parameters
    
    @property
    def metadata(self) -> GeneralParameters:
        return self._metadata
    
    @property
    def suplex_file(self) -> dict[str,any]:
        return self._suplex_file
