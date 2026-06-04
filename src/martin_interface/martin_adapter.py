import os
from .validation import *
from .dataset import Dataset
from .project import Project
from .holder import PathHolder, FileHolder
from .martin_interface_constants import (
    SEARCH_MODE,
    STANDARD_READOUT_FILES,
    IMAGE_EXTENSIONS,
)
from .search_directories import delve_dirs, sweep_dirs
import logging
from typing import List

logger = logging.getLogger(__name__)


class Adapter:
    """
    Instances of Adapter extract and store measurements conducted via the MARTin software while maintaining a project-oriented structure.
    During initialization a given path is scanned for appropriate dataset files which are then validated and collected.

    Attributes:
        path (str): Root directory path to scan for MARTin datasets.
        mode (SEARCH_MODE): Search mode from SEARCH_MODE enum.
        search_depth (int): Search depth, not applicable on recursive and unbound search modes.
        readout_files (list): Default file names of files which need to be present to detect a MARTin dataset.

    """

    def __init__(
        self,
        path: str,
        mode: SEARCH_MODE = SEARCH_MODE.RECURSIVE,
        search_depth: int = 5,
        readout_files: List[str] = STANDARD_READOUT_FILES,
    ) -> None:

        self._datasets = []
        self._projects = []
        self._search_depth = search_depth

        if not os.path.isdir(path):
            logger.error(f"{path} is not a directory.")
            return None

        file_dirs = set()
        if mode is SEARCH_MODE.RECURSIVE:
            logger.debug(f"Initiated recursive search of {path} for {readout_files}.")
            delve_dirs(path=path, target_files=readout_files, detected_file_dirs=file_dirs)
        elif isinstance(mode, SEARCH_MODE):  # Ensure proper mode is selected.
            if mode is SEARCH_MODE.ITERATIVE_UNBOUND:
                logger.debug(
                    f"Initiated linear search of {path} for {readout_files} in mode: {mode}."
                )
            else:
                logger.debug(
                    f"Initiated linear search of {path} for {readout_files} in mode: {mode} with depth = {self._search_depth}."
                )
            file_dirs = sweep_dirs(
                root_path=path,
                target_files=readout_files,
                mode=mode,
                max_depth=self._search_depth,
            )

        # If no files could be found terminate early.
        if not file_dirs:
            logger.warning(
                f"The directory {path} does not contain any of the following files: {readout_files}. No datasets detected."
            )
            return None

        # Try to read in files and establish project structure.
        for file_dir in file_dirs:
            path_holder = self.scan_for_files(file_dir)
            if path_holder is None:
                continue
            file_holder = self.validate_files(path_holder)
            if file_holder:
                self.establish_project_structure(path_holder=path_holder, file_holder=file_holder)

    def scan_for_files(self, folder_path: str) -> PathHolder:
        """
        Searches for MARTin related files in a given directory and stores their paths in a `PathHolder` object.
        This method also facilitates data extraction from these paths.
        NOTE: By default, JSON files are prioritized over TSV files.

        Args:
            folder_path (str): Directory path to scan for MARTin datasets.
            mode (SEARCH_MODE): Search mode from SEARCH_MODE enum (assumed to be defined elsewhere).
            readout_files (list): Default file names required to detect a MARTin dataset.

        Returns:
            PathHolder: Object containing paths to detected MARTin dataset files.
        """
        data_path = None
        data_statistics_path = None
        metadata_path = None
        parameters_path = None
        image_path = None
        annotated_image_path = None
        suplex_path = None

        logger.debug(f"Initiate file search in {folder_path}.")
        for item in os.listdir(folder_path):
            if item == "data.json":
                logger.debug(f"File found: {item}.")
                data_path = os.path.join(folder_path, item)
            elif item == "data.tsv" and data_path is None:
                logger.debug(f"File found: {item}.")
                data_path = os.path.join(folder_path, item)
            elif item == "data_statistics.json":
                logger.debug(f"File found: {item}.")
                data_statistics_path = os.path.join(folder_path, item)
            elif item == "data_statistics.tsv" and data_statistics_path is None:
                logger.debug(f"File found: {item}.")
                data_statistics_path = os.path.join(folder_path, item)
            elif item == "metadata.json":
                logger.debug(f"File found: {item}.")
                metadata_path = os.path.join(folder_path, item)
            elif item == "parameters.json":
                logger.debug(f"File found: {item}.")
                parameters_path = os.path.join(folder_path, item)
            elif item == "suplex.json":
                logger.debug(f"File found: {item}.")
                suplex_path = os.path.join(folder_path, item)
            else:
                # Images are only checked for name and format, there is no further validation.
                base_name, extension = os.path.splitext(item)
                base_name = base_name.lower()
                extension = extension.lower()
                if base_name == "image" and extension in IMAGE_EXTENSIONS:
                    image_path = os.path.join(folder_path, item)
                    logger.debug(f"File found: {item}.")
                elif base_name == "annotated_image" and extension in IMAGE_EXTENSIONS:
                    annotated_image_path = os.path.join(folder_path, item)
                    logger.debug(f"File found: {item}.")

        # Minimum requirement
        if not data_path or not folder_path:
            return None

        path_holder = PathHolder(
            dataset_path=folder_path,
            data_path=data_path,
            data_statistics_path=data_statistics_path,
            metadata_path=metadata_path,
            parameters_path=parameters_path,
            image_path=image_path,
            annotated_image_path=annotated_image_path,
            suplex_path=suplex_path,
        )
        return path_holder

    def validate_files(self, path_holder: PathHolder) -> FileHolder:
        """
        Checks the validitiy of dataset-related files and returns them encapsulated in an instance of `FileHolder`.

        Args:
            path_holder (PathHolder): Object holding a set of paths related to a dataset.

        Returns:
            FileHolder: Object containing the contents of dataset-related files.
                Files which failed validation or are not availible are set to None by default.
            None: If there is no valid data file.
        """

        # Minimum requirement is the presence of a data-file.
        data_file = try_get_validated_data(path_holder.data_path)
        if data_file is None:
            return None
        data_statistics_file = try_get_validated_data_statistics(
            path_holder.data_statistics_path, data_file=data_file
        )

        metadata_file = try_get_validated_metadata(
            path_holder.metadata_path
        )  # No comparison to dataFile
        parameters_file = try_get_validated_parameters(
            path_holder.parameters_path, data_file=data_file
        )
        suplex_file = try_get_validated_suplex_file(
            path_holder.suplex_path
        )  # No comparison to dataFile

        file_holder = FileHolder(
            data_file=data_file,
            data_statistics_file=data_statistics_file,
            metadata_file=metadata_file,
            parameters_file=parameters_file,
            suplex_file=suplex_file,
        )

        return file_holder

    def establish_project_structure(self, path_holder: PathHolder, file_holder: FileHolder) -> None:
        """
        Given the presence of a data file, the following code instantiates datasets as objects of `Dataset` and links them bi-directionally to instances of `project`.
        Any new dataset or project is appended to the `datasets` or `projects` attribute of this class, respectively.
        If there is no data file None will be returned.

        Args:
            path_holder (PathHolder): Object holding a set of paths related to a dataset.
            file_holder (FileHilder): Object containing the contents of dataset-related files.

        Returns:
            None: If `file_holder` does not contain a data file.
        """
        if file_holder.data_file is None:
            return None

        # The standard name for no project in MARTin is none.
        project_name = "none"
        project_description = "Measurements which do not belong to any project in particular."

        # If there is no metadata file or no project field a measurement will automatically be listed as none.
        if file_holder.metadata_file is not None:
            if "project" in file_holder.metadata_file.keys():
                project_name = file_holder.metadata_file["project"]["name"]
                # Incase for some reason we have an actual project dict where the name is "none".
                # Under normal circumstances this should not happen.
                if project_name != "none":
                    project_description = file_holder.metadata_file["project"]["description"]

        # Get a list of all project names, and return its reference if the project of the current measurement is already listed.
        existing_projects = [proj.name for proj in self._projects]
        if project_name in existing_projects:
            project = self._projects[existing_projects.index(project_name)]
        # If not create a new project.
        else:
            project = Project(name=project_name, description=project_description)
            logger.debug(
                f"New Project has been generated. Name: {project_name} - Description: {project_description}"
            )
            self._projects.append(project)

        # Establishes bi-directional relationship between datasets and their projects.
        dataset = Dataset(path_holder=path_holder, file_holder=file_holder, project=project)
        project.add_dataset(dataset)
        self.datasets.append(dataset)

    def get_datasets_by_project(self) -> List[dict[str, any]]:
        """
        Returns a list of dictionaries organizing datasets by project for GUI display.
        Additionally it extracts labels and tags for each dataset of all projects.

        Returns:
            list[dict]: A list where each dictionary represents a project and its associated datasets.
        """
        project_dicts = []
        for proj in self.projects:
            dictionary = {
                "name": proj.name,
                "dataset_labels": proj.get_measurement_labels(),
                "datasets": proj.datasets,
                "tags": proj.get_tags(),
                "suplexTags": proj.get_suplex_tags(),
            }
            project_dicts.append(dictionary)

        return project_dicts

    @property
    def datasets(self) -> List[Dataset]:
        return self._datasets

    @property
    def projects(self) -> List[Project]:
        return self._projects
