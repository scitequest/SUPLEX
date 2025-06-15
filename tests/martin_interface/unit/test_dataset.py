import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.martin_interface.dataset import Dataset
from src.martin_interface.sample import Sample, DataStatistics
from src.martin_interface.holder import PathHolder, FileHolder


class TestDataset:
    @pytest.fixture
    def basic_file_holder(self, sample_data_dict):
        return FileHolder(
            data_file=sample_data_dict,
            data_statistics_file=None,
            metadata_file=None,
            parameters_file=None,
            suplex_file=None,
        )

    @pytest.fixture
    def mock_project(self):
        project = Mock()
        project.name = "TestProject"
        project.description = "Test Description"
        return project

    def test_dataset_initialization(
        self, mock_path_holder, basic_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, basic_file_holder, mock_project)

        assert dataset.path_holder == mock_path_holder
        assert dataset.file_holder == basic_file_holder
        assert dataset.project == mock_project
        assert len(dataset.samples) > 0

    def test_init_samples_basic(
        self, mock_path_holder, basic_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, basic_file_holder, mock_project)
        assert len(dataset.samples) == 2

    def test_init_samples_with_statistics(
        self, mock_path_holder, mock_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)
        assert dataset.samples[0].data_statistics is not None

    def test_generate_data_statistics(
        self, mock_path_holder, mock_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)
        stats = dataset.generate_data_statistics()

        # Check if all fields are generated
        assert len(stats) == 2
        assert all("row" in stat for stat in stats)
        assert all("col" in stat for stat in stats)
        assert all("adjusted_average" in stat for stat in stats)
        assert all("normalized_average" in stat for stat in stats)
        assert all("relative_adjusted_average_std_deviation" in stat for stat in stats)
        assert all("normalized_average" in stat for stat in stats)
        assert all("normalized_average_std_deviation" in stat for stat in stats)
        assert all(
            "relative_normalized_average_std_deviation" in stat for stat in stats
        )

        stats = [DataStatistics(**stats[0]), DataStatistics(**stats[1])]
        # Check if values are correct with tolerance
        # row 0 col 0
        assert dataset.data_statistics[0].row == stats[0].row
        assert dataset.data_statistics[0].col == stats[0].col
        assert dataset.data_statistics[0].adjusted_average == pytest.approx(
            stats[0].adjusted_average
        )
        assert dataset.data_statistics[0].normalized_average == pytest.approx(
            stats[0].normalized_average
        )
        assert dataset.data_statistics[
            0
        ].relative_adjusted_average_std_deviation == pytest.approx(
            stats[0].relative_adjusted_average_std_deviation
        )
        assert dataset.data_statistics[
            0
        ].normalized_average_std_deviation == pytest.approx(
            stats[0].normalized_average_std_deviation
        )
        assert dataset.data_statistics[
            0
        ].relative_normalized_average_std_deviation == pytest.approx(
            stats[0].relative_normalized_average_std_deviation
        )

        # row 0 col 1
        assert dataset.data_statistics[1].row == stats[1].row
        assert dataset.data_statistics[1].col == stats[1].col
        assert dataset.data_statistics[1].adjusted_average == pytest.approx(
            stats[1].adjusted_average
        )
        assert dataset.data_statistics[1].normalized_average == pytest.approx(
            stats[1].normalized_average
        )
        assert dataset.data_statistics[
            1
        ].relative_adjusted_average_std_deviation == pytest.approx(
            stats[1].relative_adjusted_average_std_deviation
        )
        assert dataset.data_statistics[
            1
        ].normalized_average_std_deviation == pytest.approx(
            stats[1].normalized_average_std_deviation
        )
        assert dataset.data_statistics[
            1
        ].relative_normalized_average_std_deviation == pytest.approx(
            stats[1].relative_normalized_average_std_deviation
        )

    def test_init_general_parameters_none(
        self, mock_path_holder, basic_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, basic_file_holder, mock_project)
        assert dataset.general_parameters is None

    def test_init_general_parameters_with_data(
        self, mock_path_holder, mock_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)

        params = dataset.general_parameters
        assert params is not None
        # Same as sample_parameters_dict_circle in polygon
        assert params.invert_lut == False
        assert params.subtract_background == True
        assert params.number_of_spotfields == 2
        assert params.columns_per_spotfield == 2
        assert params.spots_per_spotfield == 2
        assert len(params.background_rectangles) == 1

    def test_init_metadata_none(
        self, mock_path_holder, basic_file_holder, mock_project
    ):
        dataset = Dataset(mock_path_holder, basic_file_holder, mock_project)
        assert dataset.metadata is None

    def test_init_metadata_with_data(
        self, mock_path_holder, mock_file_holder, mock_project, sample_metadata_dict
    ):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)

        metadata = dataset.metadata
        assert metadata is not None
        assert metadata.version == sample_metadata_dict["version"]
        assert metadata.datetime == sample_metadata_dict["datetime"]
        assert metadata.pat_id == sample_metadata_dict["patient"]["id"]
        assert metadata.name == sample_metadata_dict["patient"]["name"]
        assert len(metadata.tags) == len(sample_metadata_dict["patient"]["tags"])
        assert dataset.tags == sample_metadata_dict["patient"]["tags"]
        assert metadata.created == sample_metadata_dict["image"]["created"]
        assert metadata.imager == sample_metadata_dict["image"]["imager"]
        assert metadata.pixel_binning == sample_metadata_dict["image"]["pixel_binning"]
        assert metadata.exposure_time == sample_metadata_dict["image"]["exposure_time"]
        assert len(metadata.incubations) == len(sample_metadata_dict["incubations"])

        assert isinstance(dataset.spots, list)
        assert isinstance(dataset.data_statistics, list)

    def test_get_name_label(self, mock_path_holder, mock_file_holder, mock_project):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)

        label = dataset.get_name_label()
        assert "PAT001" in label
        assert "Test Patient" in label

    def test_has_some_tags(self, mock_path_holder, mock_file_holder, mock_project):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)

        assert dataset.has_some_tags(["tag1", "nonexistent"]) is True
        assert dataset.has_some_tags(["nonexistent"]) is False

        assert dataset.has_some_tags(["analysis1"]) is True

    def test_has_all_tags(self, mock_path_holder, mock_file_holder, mock_project):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)

        assert dataset.has_all_tags(["tag1"]) is True
        assert dataset.has_all_tags(["tag1", "tag2"]) is True
        assert dataset.has_all_tags(["tag1", "tag2", "tag3"]) is False
        assert dataset.has_all_tags(["tag1", "nonexistent"]) is False
        assert dataset.has_all_tags([]) is False

    def test_is_in_timeframe(self, mock_path_holder, mock_file_holder, mock_project):
        dataset = Dataset(mock_path_holder, mock_file_holder, mock_project)

        # Metadata "datetime" = "1998-07-13T10:30:00"
        measured = dataset.measure_date
        # Test within timeframe
        start = datetime(1997, 1, 1)
        end = datetime(1999, 2, 1)
        assert dataset.is_in_timeframe(measured, start, end) is True

        # Test outside timeframe
        start = datetime(2025, 2, 1)
        end = datetime(2025, 3, 1)
        assert dataset.is_in_timeframe(measured, start, end) is False

        # Metadata "created" = "1997-07-13T10:00:00"
        created = dataset.image_creation_date
        # Test within timeframe
        start = datetime(1996, 1, 1)
        end = datetime(2000, 2, 1)
        assert dataset.is_in_timeframe(created, start, end) is True

        # Test outside timeframe
        start = datetime(2027, 2, 1)
        end = datetime(2030, 3, 1)
        assert dataset.is_in_timeframe(created, start, end) is False
