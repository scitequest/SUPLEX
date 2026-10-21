import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from suplex.martin_interface.martin_adapter import Adapter
from suplex.martin_interface.martin_interface_constants import SEARCH_MODE
from suplex.suplex_modules.module_loader import load_modules
from suplex.ui.elements.navigator import Navigator
from suplex.ui.gui import GUI

# Fixtures shared with the martin_interface tests; imported so pytest can find them here.
from tests.martin_interface.conftest import (  # noqa: F401
    sample_data_dict,
    sample_data_statistics_dict,
    sample_metadata_dict_natural,
    sample_parameters_dict_polygon,
    sample_suplex_dict,
)

# -------------------------------------------------------------------------
# Temporary MARTin Dataset Creation Fixtures
# -------------------------------------------------------------------------


@pytest.fixture
def temp_martin_dataset_dir(
    sample_data_dict,
    sample_data_statistics_dict,
    sample_metadata_dict_natural,
    sample_parameters_dict_polygon,
    sample_suplex_dict,
):
    """Creates a complete, realistic temporary MARTin dataset directory on disk."""
    temp_dir = tempfile.mkdtemp(prefix="e2e_martin_dataset_")

    try:
        with open(os.path.join(temp_dir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(sample_data_dict, f, indent=2)
        with open(os.path.join(temp_dir, "data_statistics.json"), "w", encoding="utf-8") as f:
            json.dump(sample_data_statistics_dict, f, indent=2)
        with open(os.path.join(temp_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(sample_metadata_dict_natural, f, indent=2)
        with open(os.path.join(temp_dir, "parameters.json"), "w", encoding="utf-8") as f:
            json.dump(sample_parameters_dict_polygon, f, indent=2)
        with open(os.path.join(temp_dir, "suplex.json"), "w", encoding="utf-8") as f:
            json.dump(sample_suplex_dict, f, indent=2)

        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_martin_project_with_multiple_datasets(temp_martin_dataset_dir):
    """Creates a temporary directory containing multiple datasets belonging to the same project."""
    base_dir = tempfile.mkdtemp(prefix="e2e_martin_project_")
    project_dir = os.path.join(base_dir, "MyTestProject")
    os.makedirs(project_dir)

    for i in range(3):
        dataset_dir = os.path.join(project_dir, f"measurement_{i:03d}")
        os.makedirs(dataset_dir)
        for filename in [
            "data.json",
            "data_statistics.json",
            "metadata.json",
            "parameters.json",
            "suplex.json",
        ]:
            src = os.path.join(temp_martin_dataset_dir, filename)
            dst = os.path.join(dataset_dir, filename)
            shutil.copy(src, dst)

    yield base_dir
    shutil.rmtree(base_dir, ignore_errors=True)


# -------------------------------------------------------------------------
# NEW: Fixture for "none" project datasets (Better Long-term Fix)
# -------------------------------------------------------------------------


@pytest.fixture
def temp_martin_dataset_dir_none_project(
    sample_data_dict,
    sample_data_statistics_dict,
    sample_parameters_dict_polygon,
    sample_suplex_dict,
):
    """
    Creates a temporary MARTin dataset with project.name = "none".
    Useful for testing default/"none" project handling.
    """
    temp_dir = tempfile.mkdtemp(prefix="e2e_martin_none_project_")

    # Create metadata with project.name = "none"
    metadata_none = {
        "version": "1.0",
        "datetime": "1998-07-13T10:30:00",
        "patient": {"id": "PAT001", "name": "Test Patient", "tags": ["tag1", "tag2"]},
        "image": {
            "created": "1997-07-13T10:00:00",
            "imager": "Test imager",
            "pixel_binning": 1,
            "exposure_time": "PT0.5S",
        },
        "incubations": [],
        "project": {
            "name": "none",
            "description": "Measurements which do not belong to any project in particular.",
        },
    }

    try:
        with open(os.path.join(temp_dir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(sample_data_dict, f, indent=2)
        with open(os.path.join(temp_dir, "data_statistics.json"), "w", encoding="utf-8") as f:
            json.dump(sample_data_statistics_dict, f, indent=2)
        with open(os.path.join(temp_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata_none, f, indent=2)
        with open(os.path.join(temp_dir, "parameters.json"), "w", encoding="utf-8") as f:
            json.dump(sample_parameters_dict_polygon, f, indent=2)
        with open(os.path.join(temp_dir, "suplex.json"), "w", encoding="utf-8") as f:
            json.dump(sample_suplex_dict, f, indent=2)

        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# -------------------------------------------------------------------------
# Adapter Fixtures
# -------------------------------------------------------------------------


@pytest.fixture
def real_adapter(temp_martin_dataset_dir):
    adapter = Adapter(path=temp_martin_dataset_dir, mode=SEARCH_MODE.RECURSIVE, search_depth=5)
    assert len(adapter.datasets) > 0
    return adapter


@pytest.fixture
def real_adapter_with_multiple_datasets(temp_martin_project_with_multiple_datasets):
    adapter = Adapter(path=temp_martin_project_with_multiple_datasets, mode=SEARCH_MODE.RECURSIVE)
    assert len(adapter.datasets) >= 2
    return adapter


# NEW: Adapter that returns datasets from the "none" project
@pytest.fixture
def real_adapter_none_project(temp_martin_dataset_dir_none_project):
    """Returns a real Adapter pointing at a dataset that belongs to the 'none' project."""
    adapter = Adapter(
        path=temp_martin_dataset_dir_none_project, mode=SEARCH_MODE.RECURSIVE, search_depth=5
    )
    assert len(adapter.datasets) > 0
    assert adapter.datasets[0].project.name == "none"
    return adapter


@pytest.fixture
def selected_datasets(real_adapter):
    return real_adapter.datasets


# -------------------------------------------------------------------------
# Color Scheme + Module Fixtures (unchanged)
# -------------------------------------------------------------------------


@pytest.fixture
def mock_color_scheme():
    scheme = MagicMock()
    scheme.NAME = "TestScheme"
    scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT = "#000000"
    scheme.LAYOUT_COLOR.INFO_FIELD.INFO = "#0066cc"
    scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS = "#228b22"
    scheme.LAYOUT_COLOR.INFO_FIELD.WARNING = "#ff8c00"
    scheme.LAYOUT_COLOR.INFO_FIELD.ERROR = "#cc0000"
    scheme.ICON.DEFAULT = "ℹ️"
    scheme.ICON.INFO = "ℹ️"
    scheme.ICON.SUCCESS = "✅"
    scheme.ICON.WARNING = "⚠️"
    scheme.ICON.ERROR = "❌"
    return scheme


@pytest.fixture(scope="session")
def available_modules():
    modules = load_modules()
    assert len(modules) > 0, "No modules were loaded"
    return modules


@pytest.fixture
def viable_module(available_modules, selected_datasets, mock_color_scheme):
    for module in available_modules:
        if module.check_if_viable(selected_datasets):
            return module.reset_module()
    pytest.skip("No module reported as viable for the selected test datasets")


@pytest.fixture
def mock_gui_with_navigator(mock_color_scheme, available_modules):
    content = MagicMock()
    popup_logger = MagicMock()

    gui = GUI(
        modules={m.module_name: m for m in available_modules},
        schemes={"TestScheme": mock_color_scheme},
        content=content,
        popup_logger=popup_logger,
    )

    navigator = Navigator(gui=gui, scheme=mock_color_scheme, modules=available_modules)
    with patch.object(navigator, "initialize_pages"):
        navigator._current_step = "directory_selection"
    return gui, navigator


@pytest.fixture
def full_workflow_setup(real_adapter, selected_datasets, mock_color_scheme, viable_module):
    return {
        "adapter": real_adapter,
        "selected_datasets": selected_datasets,
        "color_scheme": mock_color_scheme,
        "module": viable_module,
    }
