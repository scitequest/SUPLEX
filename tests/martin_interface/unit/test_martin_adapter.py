import json
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.martin_interface.martin_adapter import Adapter
from src.martin_interface.martin_interface_constants import SEARCH_MODE, STANDARD_READOUT_FILES
from src.martin_interface.holder import FileHolder

class TestAdapter:
    def test_adapter_init_invalid_path(self):
        with patch("src.martin_interface.martin_adapter.logger") as mock_logger:
            adapter = Adapter("/invalid/path")
            mock_logger.error.assert_called_once()
            assert adapter._datasets == []
            assert adapter._projects == []
    
    def test_adapter_init_valid_path_no_files(self, temp_dir):
        with patch("src.martin_interface.martin_adapter.logger") as mock_logger:
            adapter = Adapter(temp_dir)
            mock_logger.warning.assert_called()
            assert adapter._datasets == []
            assert adapter._projects == []
    
    def test_adapter_init_recursive_mode(self, create_sample_files):
        with patch("src.martin_interface.martin_adapter.delve_dirs") as mock_delve:
            mock_delve.return_value = set()
            adapter = Adapter(create_sample_files, mode=SEARCH_MODE.RECURSIVE)
            mock_delve.assert_called_once()
    
    def test_adapter_init_iterative_modes(self, create_sample_files):
        for mode in [SEARCH_MODE.ITERATIVE_UNBOUND, 
                     SEARCH_MODE.ITERATIVE_BOUNDED_ALL,
                     SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM]:
            with patch("src.martin_interface.martin_adapter.sweep_dirs") as mock_sweep:
                mock_sweep.return_value = set()
                adapter = Adapter(create_sample_files, mode=mode)
                mock_sweep.assert_called_once()
    
    def test_scan_for_files_complete_dataset(self, temp_dir, sample_data_dict):
        files = {
            "data.json": sample_data_dict,
            "data_statistics.json": {},
            "metadata.json": {},
            "parameters.json": {},
            "suplex.json": {},
            "image.png": "",
            "annotated_image.tiff": ""
        }
        
        for filename, content in files.items():
            filepath = os.path.join(temp_dir, filename)
            if filename.endswith(".json"):
                with open(filepath, "w") as f:
                    json.dump(content, f)
            else:
                with open(filepath, "w") as f:
                    f.write(content)
        
        adapter = Adapter(temp_dir)
        path_holder = adapter.scan_for_files(temp_dir)
        
        assert path_holder is not None
        assert path_holder.data_path.endswith("data.json")
        assert path_holder.data_statistics_path.endswith("data_statistics.json")
        assert path_holder.metadata_path.endswith("metadata.json")
        assert path_holder.parameters_path.endswith("parameters.json")
        assert path_holder.suplex_path.endswith("suplex.json")
        assert path_holder.image_path.endswith("image.png")
        assert path_holder.annotated_image_path.endswith("annotated_image.tiff")
    
    def test_scan_for_files_no_data_file(self, temp_dir):
        with open(os.path.join(temp_dir, "metadata.json"), "w") as f:
            json.dump({}, f)
        
        adapter = Adapter(temp_dir)
        path_holder = adapter.scan_for_files(temp_dir)
        
        assert path_holder is None
    
    @patch("src.martin_interface.martin_adapter.try_get_validated_data")
    @patch("src.martin_interface.martin_adapter.try_get_validated_data_statistics")
    @patch("src.martin_interface.martin_adapter.try_get_validated_metadata")
    @patch("src.martin_interface.martin_adapter.try_get_validated_parameters")
    @patch("src.martin_interface.martin_adapter.try_get_validated_suplex_file")
    def test_validate_files(self, mock_suplex, mock_params, mock_meta, 
                           mock_stats, mock_data, mock_path_holder):
        # Mock successful validation
        mock_data.return_value = {"values": []}
        mock_stats.return_value = {"values": []}
        mock_meta.return_value = {}
        mock_params.return_value = {}
        mock_suplex.return_value = {}
        
        adapter = Adapter("/test")
        file_holder = adapter.validate_files(mock_path_holder)
        
        assert file_holder is not None
        assert file_holder.data_file == {"values": []}
    
    @patch("src.martin_interface.martin_adapter.try_get_validated_data")
    def test_validate_files_no_data(self, mock_data, mock_path_holder):
        mock_data.return_value = None
        
        adapter = Adapter("/test")
        file_holder = adapter.validate_files(mock_path_holder)
        
        assert file_holder is None
    
    def test_establish_project_structure_no_data_file(self, mock_path_holder):
        from src.martin_interface.holder import FileHolder
        file_holder = FileHolder(data_file=None)
        
        adapter = Adapter("/test")
        result = adapter.establish_project_structure(mock_path_holder, file_holder)
        
        assert result is None
    
    def test_establish_project_structure_new_project(self, mock_path_holder, mock_file_holder):
        adapter = Adapter("/test")
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)
        
        assert len(adapter.projects) == 1
        assert adapter.projects[0].name == "TestProject"
        assert len(adapter.datasets) == 1
    
    def test_establish_project_structure_existing_project(self, mock_path_holder, mock_file_holder):
        adapter = Adapter("/test")
        
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)
        # Add second dataset to same project
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)
        
        assert len(adapter.projects) == 1
        assert len(adapter.datasets) == 2
        assert len(adapter.projects[0].datasets) == 2
    
    def test_establish_project_structure_no_project(self, mock_path_holder, mock_file_holder, sample_metadata_dict):
        del sample_metadata_dict["project"]
        
        test_file_holder = FileHolder(
            data_file = mock_file_holder.data_file,
            data_statistics_file = mock_file_holder.data_statistics_file,
            metadata_file = sample_metadata_dict,
            parameters_file = mock_file_holder.parameters_file,
            suplex_file = mock_file_holder.suplex_file
        )
        
        adapter = Adapter("/test")
        adapter.establish_project_structure(mock_path_holder, test_file_holder)
        
        assert adapter.projects[0].name == "none"
        assert adapter.projects[0].description == "Measurements which do not belong to any project in particular."
    
    def test_get_datasets_by_project(self, mock_path_holder, mock_file_holder):
        adapter = Adapter("/test")
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)
        
        project_dicts = adapter.get_datasets_by_project()
        
        assert len(project_dicts) == 1
        assert project_dicts[0]["name"] == "TestProject"
        assert "dataset_labels" in project_dicts[0]
        assert "datasets" in project_dicts[0]
        assert "tags" in project_dicts[0]
        assert "suplexTags" in project_dicts[0]
