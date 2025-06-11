import pytest
import os
import json
import copy
from src.martin_interface.martin_adapter import Adapter
from src.martin_interface.constants import SEARCH_MODE

class TestAdapterIntegration:
    @pytest.fixture
    def create_full_dataset_json(self, temp_dir, sample_data_dict, sample_data_statistics_dict,
                           sample_metadata_dict_natural, sample_parameters_dict_polygon, sample_suplex_dict):
        dataset_dir = os.path.join(temp_dir, "project1", "measurement1", "dataset1")
        os.makedirs(dataset_dir)
        
        files = {
            "data.json": sample_data_dict,
            "data_statistics.json": sample_data_statistics_dict,
            "metadata.json": sample_metadata_dict_natural,
            "parameters.json": sample_parameters_dict_polygon,
            "suplex.json": sample_suplex_dict
        }
        
        for filename, content in files.items():
            with open(os.path.join(dataset_dir, filename), 'w') as f:
                json.dump(content, f)
        
        # Create image files
        with open(os.path.join(dataset_dir, "image.png"), 'wb') as f:
            f.write(b"fake image data")
        with open(os.path.join(dataset_dir, "annotated_image.png"), 'wb') as f:
            f.write(b"fake annotated image data")
        
        return temp_dir

    
    @pytest.fixture
    def create_full_dataset_tsv(self, temp_dir, sample_data_tsv, sample_data_statistics_tsv,
                           sample_metadata_dict_natural, sample_parameters_dict_polygon, sample_suplex_dict):
        dataset_dir = os.path.join(temp_dir, "project1", "measurement1", "dataset1")
        os.makedirs(dataset_dir)
        
        # Write TSV files - doing this prevents confusing the csv reader
        with open(os.path.join(dataset_dir, "data.tsv"), 'w', encoding='utf-8', newline='') as f:
            f.write(sample_data_tsv)
        
        with open(os.path.join(dataset_dir, "data_statistics.tsv"), 'w', encoding='utf-8', newline='') as f:
            f.write(sample_data_statistics_tsv)
        
        # Write JSON files normally  
        json_files = {
            "metadata.json": sample_metadata_dict_natural,
            "parameters.json": sample_parameters_dict_polygon,
            "suplex.json": sample_suplex_dict
        }
        
        for filename, content in json_files.items():
            with open(os.path.join(dataset_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(content, f)
        
        # Create image files
        with open(os.path.join(dataset_dir, "image.png"), 'wb') as f:
            f.write(b"fake image data")
        with open(os.path.join(dataset_dir, "annotated_image.png"), 'wb') as f:
            f.write(b"fake annotated image data")
        
        return temp_dir
    
    def test_adapter_full_workflow_json(self, create_full_dataset_json):
        adapter = Adapter(create_full_dataset_json, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        # Verify project structure
        assert len(adapter.projects) == 1
        assert adapter.projects[0].name == "TestProject"
        
        # Verify dataset
        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]
        
        # Verify all components loaded
        assert dataset.metadata is not None
        assert dataset.general_parameters is not None
        assert dataset.suplex_file is not None
        assert len(dataset.samples) > 0

    def test_adapter_full_workflow_tsv(self, create_full_dataset_tsv):
        adapter = Adapter(create_full_dataset_tsv, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        # Verify project structure
        assert len(adapter.projects) == 1
        assert adapter.projects[0].name == "TestProject"
        
        # Verify dataset
        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]
        
        # Verify all components loaded
        assert dataset.metadata is not None
        assert dataset.general_parameters is not None
        assert dataset.suplex_file is not None
        assert len(dataset.samples) > 0
    
    def test_adapter_multiple_datasets(self, temp_dir, sample_data_dict, sample_metadata_dict_natural):
        """Test Adapter with multiple datasets in different projects."""
        # Create datasets for different projects
        projects = ["ProjectA", "ProjectB", "none"]
        
        for i, project_name in enumerate(projects):
            dataset_dir = os.path.join(temp_dir, f"dataset{i}")
            os.makedirs(dataset_dir)
            
            # Modify metadata for different projects
            metadata = copy.deepcopy(sample_metadata_dict_natural)
            if project_name != "none":
                metadata["project"] = {
                    "name": project_name,
                    "description": f"Description for {project_name}"
                }
            else:
                metadata.pop("project", None)
            
            # Write files
            with open(os.path.join(dataset_dir, "data.json"), 'w') as f:
                json.dump(sample_data_dict, f)
            with open(os.path.join(dataset_dir, "metadata.json"), 'w') as f:
                json.dump(metadata, f)
        
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        # Verify projects created
        assert len(adapter.projects) == 3
        project_names = [p.name for p in adapter.projects]
        assert "ProjectA" in project_names
        assert "ProjectB" in project_names
        assert "none" in project_names
        
        # Verify datasets distributed correctly
        assert len(adapter.datasets) == 3
    
    def test_adapter_get_datasets_by_project(self, create_full_dataset_json):
        adapter = Adapter(create_full_dataset_json, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        project_data = adapter.get_datasets_by_project()
        
        assert len(project_data) == 1
        project_dict = project_data[0]
        
        assert project_dict["name"] == "TestProject"
        assert len(project_dict["datasets"]) == 1
        assert project_dict["datasets"][0] == adapter.datasets[0]
        assert len(project_dict["tags"]) > 0
        assert "tag1" in project_dict["tags"]
        assert "analysis1" in project_dict["suplexTags"]

    def test_adapter_mixed_json_tsv_formats(self, temp_dir, sample_data_tsv, sample_data_statistics_dict,
                                       sample_metadata_dict_natural, sample_parameters_dict_polygon, sample_suplex_dict):
        dataset_dir = os.path.join(temp_dir, "project1", "measurement1", "dataset1")
        os.makedirs(dataset_dir)
        
        with open(os.path.join(dataset_dir, "data.tsv"), 'w', encoding='utf-8', newline='') as f:
            f.write(sample_data_tsv)
        
        json_files = {
            "data_statistics.json": sample_data_statistics_dict,
            "metadata.json": sample_metadata_dict_natural,
            "parameters.json": sample_parameters_dict_polygon,
            "suplex.json": sample_suplex_dict
        }
        
        for filename, content in json_files.items():
            with open(os.path.join(dataset_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(content, f)
        
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.projects) == 1
        assert len(adapter.datasets) == 1
        assert len(adapter.datasets[0].samples) > 0

    def test_adapter_data_consistency_json_vs_tsv(self, temp_dir, sample_data_dict, sample_data_tsv,
                                                 sample_metadata_dict_natural, sample_parameters_dict_polygon, sample_suplex_dict):
        json_dir = os.path.join(temp_dir, "json_dataset")
        os.makedirs(json_dir)
        
        json_files = {
            "data.json": sample_data_dict,
            "metadata.json": sample_metadata_dict_natural,
            "parameters.json": sample_parameters_dict_polygon,
            "suplex.json": sample_suplex_dict
        }
        
        for filename, content in json_files.items():
            with open(os.path.join(json_dir, filename), 'w') as f:
                json.dump(content, f)
        
        tsv_dir = os.path.join(temp_dir, "tsv_dataset") 
        os.makedirs(tsv_dir)
        
        with open(os.path.join(tsv_dir, "data.tsv"), 'w', encoding='utf-8', newline='') as f:
            f.write(sample_data_tsv)
        
        for filename, content in json_files.items():
            if filename != "data.json":
                with open(os.path.join(tsv_dir, filename), 'w') as f:
                    json.dump(content, f)
        
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.datasets) == 2
        
        json_samples = len([d for d in adapter.datasets if "json_dataset" in d.path_holder.dataset_path][0].samples)
        tsv_samples = len([d for d in adapter.datasets if "tsv_dataset" in d.path_holder.dataset_path][0].samples)
        
        assert json_samples == tsv_samples
    
    def test_adapter_missing_files_handling(self, temp_dir, sample_data_dict, sample_metadata_dict_natural):
        dataset_dir = os.path.join(temp_dir, "minimal_dataset")
        os.makedirs(dataset_dir)
        
        with open(os.path.join(dataset_dir, "data.json"), 'w') as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(dataset_dir, "metadata.json"), 'w') as f:
            json.dump(sample_metadata_dict_natural, f)
        
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]
        
        assert dataset.metadata is not None
        assert len(dataset.samples) > 0
        assert dataset.general_parameters is None
        assert dataset.suplex_file is None
    
    def test_adapter_empty_directory(self, temp_dir):
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.datasets) == 0
        assert len(adapter.projects) == 0
    
    def test_adapter_invalid_path(self):
        adapter = Adapter("/nonexistent/path", mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.datasets) == 0
        assert len(adapter.projects) == 0
    
    def test_adapter_different_search_modes(self, create_full_dataset_json):
        adapter_recursive = Adapter(create_full_dataset_json, mode=SEARCH_MODE.RECURSIVE)
        assert len(adapter_recursive.datasets) == 1
        
        adapter_unbound = Adapter(create_full_dataset_json, mode=SEARCH_MODE.ITERATIVE_UNBOUND)
        assert len(adapter_unbound.datasets) == 1
        
        assert len(adapter_recursive.datasets) == len(adapter_unbound.datasets)
    
    def test_adapter_priority_json_over_tsv(self, temp_dir, sample_data_dict, sample_data_tsv,
                                           sample_metadata_dict_natural):
        dataset_dir = os.path.join(temp_dir, "priority_test")
        os.makedirs(dataset_dir)
        
        with open(os.path.join(dataset_dir, "data.json"), 'w') as f:
            json.dump(sample_data_dict, f)
        
        with open(os.path.join(dataset_dir, "data.tsv"), 'w', encoding='utf-8', newline='') as f:
            f.write(sample_data_tsv)
        
        with open(os.path.join(dataset_dir, "metadata.json"), 'w') as f:
            json.dump(sample_metadata_dict_natural, f)
        
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]
        
        assert dataset.path_holder.data_path.endswith("data.json")
    
    def test_adapter_image_files_detection(self, temp_dir, sample_data_dict, sample_metadata_dict_natural):
        dataset_dir = os.path.join(temp_dir, "image_test")
        os.makedirs(dataset_dir)
        
        with open(os.path.join(dataset_dir, "data.json"), 'w') as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(dataset_dir, "metadata.json"), 'w') as f:
            json.dump(sample_metadata_dict_natural, f)
        
        with open(os.path.join(dataset_dir, "image.png"), 'wb') as f:
            f.write(b"fake png data")
        with open(os.path.join(dataset_dir, "annotated_image.jpg"), 'wb') as f:
            f.write(b"fake jpg data")
        
        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)
        
        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]
        
        assert dataset.path_holder.image_path is not None
        assert dataset.path_holder.annotated_image_path is not None
        assert dataset.path_holder.image_path.endswith("image.png")
        assert dataset.path_holder.annotated_image_path.endswith("annotated_image.jpg")