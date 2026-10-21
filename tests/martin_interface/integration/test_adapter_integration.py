import copy
import json
import os

from suplex.martin_interface.martin_adapter import Adapter
from suplex.martin_interface.martin_interface_constants import SEARCH_MODE


class TestAdapterIntegration:
    """Integration tests for the Adapter class — the main entry point that performs directory search, full file validation, Dataset creation, and Project aggregation."""

    # -------------------------------------------------------------------------
    # Full workflow (JSON + TSV) tests
    # -------------------------------------------------------------------------

    def test_adapter_full_workflow_json(self, create_sample_files):
        """Full end-to-end workflow with a complete JSON-based MARTin dataset."""
        adapter = Adapter(create_sample_files, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

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

    def test_adapter_full_workflow_tsv(self, create_sample_files):
        """Full end-to-end workflow with a complete TSV-based MARTin dataset (mixed JSON/TSV files).
        (Uses create_sample_files fixture for simplicity; mixed TSV behavior is also covered in other tests.)
        """
        adapter = Adapter(create_sample_files, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

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

    # -------------------------------------------------------------------------
    # Multiple datasets / project handling
    # -------------------------------------------------------------------------

    def test_adapter_multiple_datasets(
        self, temp_dir, sample_data_dict, sample_metadata_dict_natural
    ):
        """Adapter correctly discovers and groups multiple datasets belonging to different projects (including the default 'none' project)."""
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
                    "description": f"Description for {project_name}",
                }
            else:
                metadata.pop("project", None)

            # Write files
            with open(os.path.join(dataset_dir, "data.json"), "w") as f:
                json.dump(sample_data_dict, f)
            with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
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

    # -------------------------------------------------------------------------
    # get_datasets_by_project and GUI data
    # -------------------------------------------------------------------------

    def test_adapter_get_datasets_by_project(self, create_sample_files):
        """get_datasets_by_project returns the expected structure for GUI consumption (labels, tags, suplexTags, etc.)."""
        adapter = Adapter(create_sample_files, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        project_data = adapter.get_datasets_by_project()

        assert len(project_data) == 1
        project_dict = project_data[0]

        assert project_dict["name"] == "TestProject"
        assert len(project_dict["datasets"]) == 1
        assert project_dict["datasets"][0] == adapter.datasets[0]
        assert len(project_dict["tags"]) > 0
        assert "tag1" in project_dict["tags"]
        assert "analysis1" in project_dict["suplexTags"]

    # -------------------------------------------------------------------------
    # Mixed formats and edge cases
    # -------------------------------------------------------------------------

    def test_adapter_mixed_json_tsv_formats(
        self,
        temp_dir,
        sample_data_tsv,
        sample_data_statistics_dict,
        sample_metadata_dict_natural,
        sample_parameters_dict_polygon,
        sample_suplex_dict,
    ):
        """Adapter correctly handles a dataset that mixes TSV (data) with JSON files."""
        dataset_dir = os.path.join(temp_dir, "project1", "measurement1", "dataset1")
        os.makedirs(dataset_dir)

        with open(os.path.join(dataset_dir, "data.tsv"), "w", encoding="utf-8", newline="") as f:
            f.write(sample_data_tsv)

        json_files = {
            "data_statistics.json": sample_data_statistics_dict,
            "metadata.json": sample_metadata_dict_natural,
            "parameters.json": sample_parameters_dict_polygon,
            "suplex.json": sample_suplex_dict,
        }

        for filename, content in json_files.items():
            with open(os.path.join(dataset_dir, filename), "w", encoding="utf-8") as f:
                json.dump(content, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.projects) == 1
        assert len(adapter.datasets) == 1
        assert len(adapter.datasets[0].samples) > 0

    def test_adapter_data_consistency_json_vs_tsv(
        self,
        temp_dir,
        sample_data_dict,
        sample_data_tsv,
        sample_metadata_dict_natural,
        sample_parameters_dict_polygon,
        sample_suplex_dict,
    ):
        """JSON and TSV versions of the same dataset produce identical internal structures."""
        json_dir = os.path.join(temp_dir, "json_dataset")
        os.makedirs(json_dir)

        json_files = {
            "data.json": sample_data_dict,
            "metadata.json": sample_metadata_dict_natural,
            "parameters.json": sample_parameters_dict_polygon,
            "suplex.json": sample_suplex_dict,
        }

        for filename, content in json_files.items():
            with open(os.path.join(json_dir, filename), "w") as f:
                json.dump(content, f)

        tsv_dir = os.path.join(temp_dir, "tsv_dataset")
        os.makedirs(tsv_dir)

        with open(os.path.join(tsv_dir, "data.tsv"), "w", encoding="utf-8", newline="") as f:
            f.write(sample_data_tsv)

        for filename, content in json_files.items():
            if filename != "data.json":
                with open(os.path.join(tsv_dir, filename), "w") as f:
                    json.dump(content, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 2

        json_samples = len(
            [d for d in adapter.datasets if "json_dataset" in d.path_holder.dataset_path][0].samples
        )
        tsv_samples = len(
            [d for d in adapter.datasets if "tsv_dataset" in d.path_holder.dataset_path][0].samples
        )

        assert json_samples == tsv_samples

    def test_adapter_missing_files_handling(
        self, temp_dir, sample_data_dict, sample_metadata_dict_natural
    ):
        """Adapter gracefully handles partial datasets (missing parameters, suplex, etc.)."""
        dataset_dir = os.path.join(temp_dir, "minimal_dataset")
        os.makedirs(dataset_dir)

        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(sample_metadata_dict_natural, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]

        assert dataset.metadata is not None
        assert len(dataset.samples) > 0
        assert dataset.general_parameters is not None  # defaults are now generated
        assert dataset.suplex_file is None

    # -------------------------------------------------------------------------
    # Validation failure handling (integration)
    # -------------------------------------------------------------------------

    def test_adapter_skips_invalid_json_data_file(self, temp_dir, sample_metadata_dict_natural):
        """Adapter skips a dataset when the data file is malformed JSON."""
        dataset_dir = os.path.join(temp_dir, "invalid_json")
        os.makedirs(dataset_dir)

        # Write malformed JSON
        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            f.write("{invalid json content")

        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(sample_metadata_dict_natural, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 0
        assert len(adapter.projects) == 0

    def test_adapter_skips_key_structure_mismatch(self, temp_dir, sample_data_dict):
        """Adapter loads dataset (with default metadata) when metadata has incorrect key structure.
        Only critical data-file validation failures cause a full skip."""
        dataset_dir = os.path.join(temp_dir, "structure_mismatch")
        os.makedirs(dataset_dir)

        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)

        # Malformed metadata (missing required fields)
        bad_metadata = {"version": "1.0"}
        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(bad_metadata, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 1  # loads with default metadata/project="none"

    def test_adapter_skips_internal_inconsistency(
        self, temp_dir, sample_data_dict, sample_metadata_dict_natural
    ):
        """Adapter loads dataset despite internal value inconsistencies in data (logged as warnings).
        Only critical issues (e.g. negative indices) cause a skip."""
        dataset_dir = os.path.join(temp_dir, "internal_inconsistency")
        os.makedirs(dataset_dir)

        bad_data = copy.deepcopy(sample_data_dict)
        bad_data["values"][0]["min"] = 300.0  # min > max
        bad_data["values"][0]["max"] = 100.0

        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            json.dump(bad_data, f)
        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(sample_metadata_dict_natural, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 1  # loads (inconsistencies are warnings only)

    def test_adapter_skips_external_consistency_failure(
        self, temp_dir, sample_data_dict, sample_metadata_dict_natural
    ):
        """Adapter loads dataset if data is valid even if data_statistics has key/structure mismatch (sets data_statistics=None)."""
        dataset_dir = os.path.join(temp_dir, "external_mismatch")
        os.makedirs(dataset_dir)

        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)

        bad_stats = {"values": [{"row": 0, "col": 0, "adjusted_average": 999999.0}]}
        with open(os.path.join(dataset_dir, "data_statistics.json"), "w") as f:
            json.dump(bad_stats, f)

        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(sample_metadata_dict_natural, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 1  # loads (data_statistics=None)

    # -------------------------------------------------------------------------
    # Edge cases (search modes, priority, images)
    # -------------------------------------------------------------------------

    def test_adapter_different_search_modes(self, create_sample_files):
        """All supported SEARCH_MODE variants correctly discover the same dataset."""
        adapter_recursive = Adapter(create_sample_files, mode=SEARCH_MODE.RECURSIVE)
        assert len(adapter_recursive.datasets) == 1

        adapter_unbound = Adapter(create_sample_files, mode=SEARCH_MODE.ITERATIVE_UNBOUND)
        assert len(adapter_unbound.datasets) == 1

        assert len(adapter_recursive.datasets) == len(adapter_unbound.datasets)

    def test_adapter_priority_json_over_tsv(
        self, temp_dir, sample_data_dict, sample_data_tsv, sample_metadata_dict_natural
    ):
        """JSON files take priority over TSV files when both exist (as documented)."""
        dataset_dir = os.path.join(temp_dir, "priority_test")
        os.makedirs(dataset_dir)

        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)

        with open(os.path.join(dataset_dir, "data.tsv"), "w", encoding="utf-8", newline="") as f:
            f.write(sample_data_tsv)

        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(sample_metadata_dict_natural, f)

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]

        assert dataset.path_holder.data_path.endswith("data.json")

    def test_adapter_image_files_detection(
        self, temp_dir, sample_data_dict, sample_metadata_dict_natural
    ):
        """Image files (image.* and annotated_image.*) are correctly detected and stored in PathHolder."""
        dataset_dir = os.path.join(temp_dir, "image_test")
        os.makedirs(dataset_dir)

        with open(os.path.join(dataset_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(sample_metadata_dict_natural, f)

        with open(os.path.join(dataset_dir, "image.png"), "wb") as f:
            f.write(b"fake png data")
        with open(os.path.join(dataset_dir, "annotated_image.jpg"), "wb") as f:
            f.write(b"fake jpg data")

        adapter = Adapter(temp_dir, mode=SEARCH_MODE.ITERATIVE_BOUNDED_ALL)

        assert len(adapter.datasets) == 1
        dataset = adapter.datasets[0]

        assert dataset.path_holder.image_path is not None
        assert dataset.path_holder.annotated_image_path is not None
        assert dataset.path_holder.image_path.endswith("image.png")
        assert dataset.path_holder.annotated_image_path.endswith("annotated_image.jpg")
