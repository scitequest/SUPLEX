import pytest
from dataclasses import is_dataclass
from src.martin_interface.holder import PathHolder, FileHolder


class TestHolders:
    """Tests for the immutable dataclasses PathHolder and FileHolder used throughout the MARTin interface."""

    # -------------------------------------------------------------------------
    # PathHolder tests
    # -------------------------------------------------------------------------

    def test_path_holder_creation_complete(self):
        """Creates a fully populated PathHolder with all optional paths and verifies every field."""
        path_holder = PathHolder(
            dataset_path="/test/dataset",
            data_path="/test/dataset/data.json",
            data_statistics_path="/test/dataset/data_statistics.json",
            metadata_path="/test/dataset/metadata.json",
            parameters_path="/test/dataset/parameters.json",
            image_path="/test/dataset/image.png",
            annotated_image_path="/test/dataset/annotated.png",
            suplex_path="/test/dataset/suplex.json",
        )
        assert is_dataclass(path_holder)

        assert path_holder.dataset_path == "/test/dataset"
        assert path_holder.data_path == "/test/dataset/data.json"
        assert path_holder.data_statistics_path == "/test/dataset/data_statistics.json"
        assert path_holder.metadata_path == "/test/dataset/metadata.json"
        assert path_holder.parameters_path == "/test/dataset/parameters.json"
        assert path_holder.image_path == "/test/dataset/image.png"
        assert path_holder.annotated_image_path == "/test/dataset/annotated.png"
        assert path_holder.suplex_path == "/test/dataset/suplex.json"

    def test_path_holder_creation_minimal(self):
        """Creates a minimal PathHolder (only required fields) and confirms all optional fields default to None."""
        path_holder = PathHolder(dataset_path="/test/dataset", data_path="/test/dataset/data.json")

        assert path_holder.dataset_path == "/test/dataset"
        assert path_holder.data_path == "/test/dataset/data.json"
        assert path_holder.data_statistics_path is None
        assert path_holder.metadata_path is None
        assert path_holder.parameters_path is None
        assert path_holder.image_path is None
        assert path_holder.annotated_image_path is None
        assert path_holder.suplex_path is None

    def test_path_holder_is_frozen(self):
        """PathHolder is frozen (immutable) and raises AttributeError on mutation attempts."""
        path_holder = PathHolder(dataset_path="/test", data_path="/test/data.json")
        assert is_dataclass(path_holder)
        with pytest.raises(AttributeError):
            path_holder.dataset_path = "/new/path"

    # -------------------------------------------------------------------------
    # FileHolder tests
    # -------------------------------------------------------------------------

    def test_file_holder_creation_complete(self):
        """Creates a fully populated FileHolder and verifies all fields plus their expected Python types."""
        file_holder = FileHolder(
            data_file=[{"test": "data"}],
            data_statistics_file=[{"test": "stats"}],
            metadata_file={"test": "metadata"},
            parameters_file=[{"test": "params"}],
            suplex_file={"test": "suplex"},
        )
        assert is_dataclass(file_holder)

        assert file_holder.data_file == [{"test": "data"}]
        assert isinstance(file_holder.data_file, list)
        assert all(isinstance(item, dict) for item in file_holder.data_file)

        assert file_holder.data_statistics_file == [{"test": "stats"}]
        assert isinstance(file_holder.data_statistics_file, list)
        assert all(isinstance(item, dict) for item in file_holder.data_statistics_file)

        assert file_holder.metadata_file == {"test": "metadata"}
        assert isinstance(file_holder.metadata_file, dict)

        assert file_holder.parameters_file == [{"test": "params"}]
        assert isinstance(file_holder.parameters_file, list)
        assert all(isinstance(item, dict) for item in file_holder.parameters_file)

        assert file_holder.suplex_file == {"test": "suplex"}
        assert isinstance(file_holder.suplex_file, dict)

    def test_file_holder_creation_minimal(self):
        """Creates a minimal FileHolder (only the required data_file) and confirms all optional fields default to None."""
        file_holder = FileHolder(data_file=[{"test": "data"}])

        assert file_holder.data_file == [{"test": "data"}]
        assert isinstance(file_holder.data_file, list)
        assert all(isinstance(item, dict) for item in file_holder.data_file)

        assert file_holder.data_statistics_file is None
        assert file_holder.metadata_file is None
        assert file_holder.parameters_file is None
        assert file_holder.suplex_file is None

    def test_file_holder_frozen(self):
        """FileHolder is frozen (immutable) and raises AttributeError on mutation attempts."""
        file_holder = FileHolder(data_file=[{"test": "data"}])

        with pytest.raises(AttributeError):
            file_holder.data_file = [{"new": "data"}]
