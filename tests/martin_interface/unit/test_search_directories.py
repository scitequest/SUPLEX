import pytest
import os
import tempfile
import json
from unittest.mock import patch, Mock
from src.martin_interface.search_directories import delve_dirs, sweep_dirs
from src.martin_interface.constants import SEARCH_MODE

class TestSearchDirectories:    
    def test_delve_dirs_basic(self, temp_dir, sample_data_dict):
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        with open(os.path.join(subdir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        
        detected = set()
        delve_dirs(temp_dir, ["data.json"], detected)
        
        assert len(detected) == 1
        assert subdir in detected
    
    def test_delve_dirs_multiple_targets(self, temp_dir, sample_data_dict):
        sub1 = os.path.join(temp_dir, "sub1")
        sub2 = os.path.join(temp_dir, "sub2")
        os.makedirs(sub1)
        os.makedirs(sub2)
        
        with open(os.path.join(sub1, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(sub2, "data.tsv"), "w") as f:
            f.write("col1\tcol2")
        
        detected = set()
        delve_dirs(temp_dir, ["data.json", "data.tsv"], detected)
        
        assert len(detected) == 2
        assert sub1 in detected
        assert sub2 in detected
    
    def test_delve_dirs_nested(self, temp_dir, sample_data_dict):
        deep_path = os.path.join(temp_dir, "level1", "level2", "level3")
        os.makedirs(deep_path)
        
        with open(os.path.join(deep_path, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        
        detected = set()
        delve_dirs(temp_dir, ["data.json"], detected)
        
        assert len(detected) == 1
        assert deep_path in detected

    def test_delve_dirs_multiple_branches(self, temp_dir, sample_data_dict):
        paths = [
            os.path.join(temp_dir, "branch1", "sub1"),
            os.path.join(temp_dir, "branch1", "sub2", "deep"),
            os.path.join(temp_dir, "branch2", "alpha"),
            os.path.join(temp_dir, "branch2", "beta", "gamma"),
            os.path.join(temp_dir, "branch3", "nested", "very", "deep", "path"),
            os.path.join(temp_dir, "root_level")
        ]
        
        for path in paths:
            os.makedirs(path, exist_ok=True)
        
        for i, path in enumerate(paths):
            test_data = sample_data_dict.copy()
            test_data["path_index"] = i
            with open(os.path.join(path, "data.json"), "w") as f:
                json.dump(test_data, f)
        
        with open(os.path.join(paths[0], "other.txt"), "w") as f:
            f.write("not relevant")
        with open(os.path.join(paths[2], "config.xml"), "w") as f:
            f.write("<config></config>")
        
        detected = delve_dirs(temp_dir, ["data.json"])
        
        assert len(detected) == 6, f"Expected 6 directories, but found {len(detected)}"
        
        for expected_path in paths:
            assert expected_path in detected, f"Path {expected_path} not found in detected paths"
        
        for detected_path in detected:
            data_json_path = os.path.join(detected_path, "data.json")
            assert os.path.exists(data_json_path), f"data.json not found in {detected_path}"
    
    @patch("os.listdir")
    def test_delve_dirs_permission_error(self, mock_listdir):
        mock_listdir.side_effect = PermissionError("Access denied")
        
        detected = set()
        with patch("src.martin_interface.search_directories.logger") as mock_logger:
            delve_dirs("/test/path", ["data.json"], detected)
            mock_logger.warning.assert_called()

    def ttest_sweep_dirs_unbound(self, temp_dir, sample_data_dict):
        paths = [
            os.path.join(temp_dir, "branch1", "sub1"),
            os.path.join(temp_dir, "branch1", "sub2", "deep"),
            os.path.join(temp_dir, "branch2", "alpha"),
            os.path.join(temp_dir, "branch2", "beta", "gamma"),
            os.path.join(temp_dir, "branch3", "nested", "very", "deep", "path"),
            os.path.join(temp_dir, "root_level")
        ]
        
        for path in paths:
            os.makedirs(path, exist_ok=True)
        
        for i, path in enumerate(paths):
            test_data = sample_data_dict.copy()
            test_data["path_index"] = i
            with open(os.path.join(path, "data.json"), "w") as f:
                json.dump(test_data, f)
        
        with open(os.path.join(paths[0], "other.txt"), "w") as f:
            f.write("not relevant")
        with open(os.path.join(paths[2], "config.xml"), "w") as f:
            f.write("<config></config>")
        
        detected = sweep_dirs(temp_dir, ["data.json"], SEARCH_MODE.ITERATIVE_UNBOUND)
        
        assert len(detected) == 6, f"Expected 6 directories, but found {len(detected)}"
        
        for expected_path in paths:
            assert expected_path in detected, f"Path {expected_path} not found in detected paths"
        
        for detected_path in detected:
            data_json_path = os.path.join(detected_path, "data.json")
            assert os.path.exists(data_json_path), f"data.json not found in {detected_path}"
    
    def test_sweep_dirs_bounded_all(self, temp_dir, sample_data_dict):
        sub1 = os.path.join(temp_dir, "sub1")
        sub2 = os.path.join(sub1, "sub2")
        sub3 = os.path.join(sub2, "sub3")
        os.makedirs(sub3)
        
        with open(os.path.join(temp_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(sub1, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(sub2, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(sub3, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        
        detected = sweep_dirs(temp_dir, ["data.json"], SEARCH_MODE.ITERATIVE_BOUNDED_ALL, max_depth=2)
        
        assert len(detected) == 3
        assert temp_dir in detected
        assert sub1 in detected
        assert sub2 in detected
        assert sub3 not in detected
    
    def test_sweep_dirs_bounded_bottom(self, temp_dir, sample_data_dict):
        sub1 = os.path.join(temp_dir, "sub1")
        sub2 = os.path.join(sub1, "sub2")
        os.makedirs(sub2)
        
        with open(os.path.join(temp_dir, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(sub1, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        with open(os.path.join(sub2, "data.json"), "w") as f:
            json.dump(sample_data_dict, f)
        
        detected = sweep_dirs(temp_dir, ["data.json"], SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM, max_depth=2)
        
        assert len(detected) == 1
        assert sub2 in detected
    
    @patch("os.scandir")
    def test_sweep_dirs_permission_error(self, mock_scandir):
        mock_scandir.side_effect = PermissionError("Access denied")
        
        with patch("src.martin_interface.search_directories.logger") as mock_logger:
            detected = sweep_dirs("/test", ["data.json"], SEARCH_MODE.ITERATIVE_UNBOUND)
            mock_logger.warning.assert_called()
            assert len(detected) == 0