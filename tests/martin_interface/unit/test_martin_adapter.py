import json
import os
from unittest.mock import patch

from suplex.martin_interface.holder import FileHolder
from suplex.martin_interface.martin_adapter import Adapter
from suplex.martin_interface.martin_interface_constants import (
    SEARCH_MODE,
)


class TestAdapter:
    """Tests for the Adapter class that scans, validates, and organizes MARTin datasets into projects."""

    # -------------------------------------------------------------------------
    # Adapter.__init__ tests
    # -------------------------------------------------------------------------

    def test_adapter_init_invalid_path(self):
        """Handles non-existent or invalid directory path gracefully and logs an error."""
        with patch("suplex.martin_interface.martin_adapter.logger") as mock_logger:
            adapter = Adapter("/invalid/path")
            mock_logger.error.assert_called_once()
            assert adapter._datasets == []
            assert adapter._projects == []

    def test_adapter_init_valid_path_no_files(self, temp_dir):
        """When no MARTin files are found, logs a warning and initializes empty collections."""
        with patch("suplex.martin_interface.martin_adapter.logger") as mock_logger:
            adapter = Adapter(temp_dir)
            mock_logger.warning.assert_called()
            assert adapter._datasets == []
            assert adapter._projects == []

    def test_adapter_init_recursive_mode(self, create_sample_files):
        """Uses delve_dirs for SEARCH_MODE.RECURSIVE."""
        with patch("suplex.martin_interface.martin_adapter.delve_dirs") as mock_delve:
            mock_delve.return_value = set()
            adapter = Adapter(create_sample_files, mode=SEARCH_MODE.RECURSIVE)
            mock_delve.assert_called_once()

    def test_adapter_init_iterative_modes(self, create_sample_files):
        """Uses sweep_dirs for all iterative SEARCH_MODE variants."""
        for mode in [
            SEARCH_MODE.ITERATIVE_UNBOUND,
            SEARCH_MODE.ITERATIVE_BOUNDED_ALL,
            SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM,
        ]:
            with patch("suplex.martin_interface.martin_adapter.sweep_dirs") as mock_sweep:
                mock_sweep.return_value = set()
                adapter = Adapter(create_sample_files, mode=mode)
                mock_sweep.assert_called_once()

    # -------------------------------------------------------------------------
    # scan_for_files tests
    # -------------------------------------------------------------------------

    def test_scan_for_files_complete_dataset(self, temp_dir, sample_data_dict):
        """Correctly identifies and populates a PathHolder for a complete MARTin dataset directory (prefers JSON over TSV)."""
        files = {
            "data.json": sample_data_dict,
            "data_statistics.json": {},
            "metadata.json": {},
            "parameters.json": {},
            "suplex.json": {},
            "image.png": "",
            "annotated_image.tiff": "",
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
        """Returns None when no data file (data.json or data.tsv) is present."""
        with open(os.path.join(temp_dir, "metadata.json"), "w") as f:
            json.dump({}, f)

        adapter = Adapter(temp_dir)
        path_holder = adapter.scan_for_files(temp_dir)

        assert path_holder is None

    # -------------------------------------------------------------------------
    # validate_files tests
    # -------------------------------------------------------------------------

    @patch("suplex.martin_interface.martin_adapter.try_get_validated_data")
    @patch("suplex.martin_interface.martin_adapter.try_get_validated_data_statistics")
    @patch("suplex.martin_interface.martin_adapter.try_get_validated_metadata")
    @patch("suplex.martin_interface.martin_adapter.try_get_validated_parameters")
    @patch("suplex.martin_interface.martin_adapter.try_get_validated_suplex_file")
    def test_validate_files(
        self,
        mock_suplex,
        mock_params,
        mock_meta,
        mock_stats,
        mock_data,
        mock_path_holder,
    ):
        """Successfully validates all files and returns a populated FileHolder."""
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

    @patch("suplex.martin_interface.martin_adapter.try_get_validated_data")
    def test_validate_files_no_data(self, mock_data, mock_path_holder):
        """Returns None immediately if the data file validation fails."""
        mock_data.return_value = None

        adapter = Adapter("/test")
        file_holder = adapter.validate_files(mock_path_holder)

        assert file_holder is None

    # -------------------------------------------------------------------------
    # establish_project_structure tests
    # -------------------------------------------------------------------------

    def test_establish_project_structure_no_data_file(self, mock_path_holder):
        """Early return (None) when FileHolder has no valid data_file."""
        from suplex.martin_interface.holder import FileHolder

        file_holder = FileHolder(data_file=None)

        adapter = Adapter("/test")
        result = adapter.establish_project_structure(mock_path_holder, file_holder)

        assert result is None

    def test_establish_project_structure_new_project(self, mock_path_holder, mock_file_holder):
        """Creates a new Project and Dataset when no matching project exists yet."""
        adapter = Adapter("/test")
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)

        assert len(adapter.projects) == 1
        assert adapter.projects[0].name == "TestProject"
        assert len(adapter.datasets) == 1

    def test_establish_project_structure_existing_project(self, mock_path_holder, mock_file_holder):
        """Reuses an existing Project when a second dataset with the same project name is added."""
        adapter = Adapter("/test")

        adapter.establish_project_structure(mock_path_holder, mock_file_holder)
        # Add second dataset to same project
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)

        assert len(adapter.projects) == 1
        assert len(adapter.datasets) == 2
        assert len(adapter.projects[0].datasets) == 2

    def test_establish_project_structure_no_project(
        self, mock_path_holder, mock_file_holder, sample_metadata_dict
    ):
        """Falls back to a default 'none' project when metadata contains no project field."""
        del sample_metadata_dict["project"]

        test_file_holder = FileHolder(
            data_file=mock_file_holder.data_file,
            data_statistics_file=mock_file_holder.data_statistics_file,
            metadata_file=sample_metadata_dict,
            parameters_file=mock_file_holder.parameters_file,
            suplex_file=mock_file_holder.suplex_file,
        )

        adapter = Adapter("/test")
        adapter.establish_project_structure(mock_path_holder, test_file_holder)

        assert adapter.projects[0].name == "none"
        assert (
            adapter.projects[0].description
            == "Measurements which do not belong to any project in particular."
        )

    # -------------------------------------------------------------------------
    # get_datasets_by_project tests
    # -------------------------------------------------------------------------

    def test_get_datasets_by_project(self, mock_path_holder, mock_file_holder):
        """Returns a list of project dictionaries suitable for GUI display (including labels, tags, etc.)."""
        adapter = Adapter("/test")
        adapter.establish_project_structure(mock_path_holder, mock_file_holder)

        project_dicts = adapter.get_datasets_by_project()

        assert len(project_dicts) == 1
        assert project_dicts[0]["name"] == "TestProject"
        assert "dataset_labels" in project_dicts[0]
        assert "datasets" in project_dicts[0]
        assert "tags" in project_dicts[0]
        assert "suplexTags" in project_dicts[0]
