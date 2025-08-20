import pytest
import tempfile
import os
import shutil
import ipywidgets as widgets
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, List, Set, Any, Callable, Generator, Union, Tuple, Optional
from enum import Enum

from src.suplex_modules.suplex_module_interface import SuplexModuleInterface
from src.martin_interface.dataset import Dataset
from src.martin_interface.holder import FileHolder, PathHolder


@pytest.fixture
def mock_scandir_entry():
    def _create_mock_scandir_entry(
        name, is_dir=False, is_file=False, base_path="/test"
    ):
        entry = Mock()
        entry.name = name
        entry.path = f"{base_path}/{name}"
        entry.is_dir.return_value = is_dir
        entry.is_file.return_value = is_file
        return entry

    return _create_mock_scandir_entry


@pytest.fixture
def test_suplex_module():
    """
    Return a standard TestSuplexModule instance
    """

    class TestSuplexModule(SuplexModuleInterface):
        def __init__(
            self,
            name: str = "TestModule",
            version: str = "1.0.0",
            group_name="test",
            button_colours: Dict[str, str] = {
                "font_color": "#000000",
                "button_color": "#FFFFFF",
            },
        ):
            self._name = name
            self._version = version
            self._group_name = group_name
            self._button_colours = button_colours

        @property
        def module_name(self):
            return self._name

        @property
        def module_version(self):
            return self._version

        @property
        def group_name(self):
            return self._group_name

        @property
        def button_style(self) -> Dict[str, str]:
            return self._button_colours

        def check_if_viable(self, datasets: List[Any]) -> bool:
            return True

        def get_module_hover_text(self) -> str:
            return "Description of module"

        def initiate_module(self, datasets: List[Any], ui: widgets.Box) -> None:
            pass

        def update_scheme(self, new_scheme) -> None:
            pass

        def reset_module(self) -> "SuplexModuleInterface":
            pass

    return TestSuplexModule()


@pytest.fixture
def mock_dataset():
    """Mock of a Dataset object for tests."""
    dataset = Mock(spec=Dataset)
    dataset.samples = [Mock() for _ in range(2)]  # 2 Samples
    for sample in dataset.samples:
        sample.spots = [Mock() for _ in range(3)]  # 3 Spots per Sample
        for spot in sample.spots:
            spot.spot_values = Mock(
                mean_minus_min=100,
                normalized_mean=0.5,
                min_val=50,
                max_val=150,
                mean_val=100,
                std_deviation=20,
            )
    dataset.id = "test_id"
    dataset.name = "Test Dataset"
    dataset.tags = ["tag1"]
    dataset.measure_date = "2023-01-01"
    return dataset


@pytest.fixture
def mock_datasets(mock_dataset):
    """List of mock Datasets."""
    return [mock_dataset, mock_dataset]  # 2 Datasets


@pytest.fixture
def mock_ui_box():
    """Mock of a UI Box (ipywidgets.Box)."""
    return Mock(spec=widgets.Box)


@pytest.fixture
def mock_color_scheme():
    """Mock of a Color Scheme."""
    return {"primary": "#000000", "secondary": "#FFFFFF"}


@pytest.fixture
def mock_attribute_selector():
    """Mock of the AttributeSelector."""
    from src.suplex_modules.submodules.attribute_selector import AttributeSelector

    selector = Mock(spec=AttributeSelector)
    selector.attribute = "MEAN_MINUS_MIN"  # Example
    return selector


@pytest.fixture
def mock_dataset_sorter():
    """Mock of the DatasetSorter."""
    from src.suplex_modules.submodules.dataset_sorter import DatasetSorter

    sorter = Mock(spec=DatasetSorter)
    sorter.get_sorted_datasets = MagicMock(return_value=[])
    return sorter


@pytest.fixture
def mock_dataset_filter():
    """Mock of the DatasetFilter."""
    from src.suplex_modules.submodules.dataset_filters import DatasetFilter

    filter_obj = Mock(spec=DatasetFilter)
    filter_obj.get_filtered_datasets = MagicMock(return_value=([], []))
    return filter_obj


@pytest.fixture
def mock_sample_spot_filter():
    """Mock of the SampleSpotFilter."""
    from src.suplex_modules.submodules.sample_spot_filter import SampleSpotFilter

    filter_obj = Mock(spec=SampleSpotFilter)
    filter_obj.get_filter_maps = MagicMock(return_value=({}, {}))
    return filter_obj


@pytest.fixture
def mock_general_graph_settings():
    """Mock of the GeneralGraphSettings."""
    from src.suplex_modules.submodules.settings.general_graph_settings import (
        GeneralGraphSettings,
    )

    settings = Mock(spec=GeneralGraphSettings)
    return settings


@pytest.fixture
def mock_boxplot_settings():
    """Mock of the BoxplotSettings."""
    from src.suplex_modules.submodules.settings.specific_graph_settings import (
        BoxplotSettings,
    )

    settings = Mock(spec=BoxplotSettings)
    return settings


@pytest.fixture
def mock_jitterplot_settings():
    """Mock of the JitterplotSettings."""
    from src.suplex_modules.submodules.settings.specific_graph_settings import (
        JitterplotSettings,
    )

    settings = Mock(spec=JitterplotSettings)
    return settings


@pytest.fixture
def mock_value_list():
    """Mock of a list of values for attribute extraction."""
    return [100.0, 200.0, 150.0, 50.0]


@pytest.fixture
def mock_nested_value_list():
    """Mock of a nested list for Sample/Spot values."""
    return [[100.0, 200.0], [150.0, 50.0]]


@pytest.fixture
def mock_coordinates_list():
    """Mock for coordinate lists."""
    return [[[1, 2], [3, 4]], [[5, 6]]]
