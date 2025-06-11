import pytest
from src.martin_interface.holder import PathHolder, FileHolder
from dataclasses import is_dataclass

class TestHolders:
    def test_path_holder_creation_complete(self):
        path_holder = PathHolder(
            dataset_path="/test/dataset",
            data_path="/test/dataset/data.json",
            data_statistics_path="/test/dataset/data_statistics.json",
            metadata_path="/test/dataset/metadata.json",
            parameters_path="/test/dataset/parameters.json",
            image_path="/test/dataset/image.png",
            annotated_image_path="/test/dataset/annotated.png",
            suplex_path="/test/dataset/suplex.json"
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
        path_holder = PathHolder(
            dataset_path="/test/dataset",
            data_path="/test/dataset/data.json"
        )
        
        assert path_holder.dataset_path == "/test/dataset"
        assert path_holder.data_path == "/test/dataset/data.json"
        assert path_holder.data_statistics_path is None
        assert path_holder.metadata_path is None
        assert path_holder.parameters_path is None
        assert path_holder.image_path is None
        assert path_holder.annotated_image_path is None
        assert path_holder.suplex_path is None
    
    def test_path_holder_is_frozen(self):
        path_holder = PathHolder(
            dataset_path="/test",
            data_path="/test/data.json"
        )
        assert is_dataclass(path_holder)
        with pytest.raises(AttributeError):
            path_holder.dataset_path = "/new/path"
    
    def test_file_holder_creation_complete(self):
        file_holder = FileHolder(
            data_file=[{"test": "data"}],
            data_statistics_file=[{"test": "stats"}],
            metadata_file={"test": "metadata"},
            parameters_file=[{"test": "params"}],
            suplex_file={"test": "suplex"}
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
        file_holder = FileHolder(
            data_file=[{"test": "data"}]
        )
        
        assert file_holder.data_file == [{"test": "data"}]
        assert isinstance(file_holder.data_file, list)
        assert all(isinstance(item, dict) for item in file_holder.data_file)
        
        assert file_holder.data_statistics_file is None
        assert file_holder.metadata_file is None
        assert file_holder.parameters_file is None
        assert file_holder.suplex_file is None
    
    def test_file_holder_frozen(self):
        file_holder = FileHolder(data_file=[{"test": "data"}])
        
        with pytest.raises(AttributeError):
            file_holder.data_file = [{"new": "data"}]
