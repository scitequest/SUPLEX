import pytest
from unittest.mock import Mock
from typing import Dict, List, Any
from PIL import Image
import matplotlib.pyplot as plt
import svgutils.transform as sg

from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface
from suplex.martin_interface.dataset import Dataset


@pytest.fixture
def mock_scandir_entry():
    """Helper to create mocked scandir entries."""

    def _create_mock_scandir_entry(name, is_dir=False, is_file=False, base_path="/test"):
        entry = Mock()
        entry.name = name
        entry.path = f"{base_path}/{name}"
        entry.is_dir.return_value = is_dir
        entry.is_file.return_value = is_file
        return entry

    return _create_mock_scandir_entry


@pytest.fixture
def test_suplex_module():
    """Standard TestSuplexModule instance for module interface tests."""

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

        def initiate_module(self, datasets: List[Any], ui: Any) -> None:
            pass

        def update_scheme(self, new_scheme) -> None:
            pass

        def reset_module(self) -> "SuplexModuleInterface":
            pass

    return TestSuplexModule()


@pytest.fixture
def mock_dataset():
    """Basic mock of a Dataset object (used in many tests)."""
    dataset = Mock(spec=Dataset)
    dataset.samples = [Mock() for _ in range(2)]
    for sample in dataset.samples:
        sample.spots = [Mock() for _ in range(3)]
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
    """List containing two identical mock datasets."""
    return [mock_dataset, mock_dataset]


@pytest.fixture
def mock_ui_box():
    """Mock for ipywidgets.Box (used in UI tests)."""
    return Mock()


@pytest.fixture
def mock_color_scheme():
    """Simple color scheme mock."""
    return {"primary": "#000000", "secondary": "#FFFFFF"}


@pytest.fixture
def mock_dataset_for_extractor(mock_dataset):
    """Enhanced mock dataset with all attributes needed by ValueExtractor and SampleSpotFilter."""
    mock_dataset.samples = [Mock() for _ in range(2)]
    for sample in mock_dataset.samples:
        sample.spots = [Mock() for _ in range(3)]
        for spot in sample.spots:
            spot.spot_values = Mock(
                mean_minus_min=100.0,
                normalized_mean=0.5,
                min_val=50.0,
                max_val=150.0,
                mean_val=100.0,
                std_deviation=20.0,
            )
            spot.spot_parameters = Mock(coordinates=[Mock(x=10.0, y=20.0), Mock(x=30.0, y=40.0)])
    mock_dataset.data_statistics = Mock(
        adjusted_average=110.0,
        adjusted_average_std_deviation=15.0,
        relative_adjusted_average_std_deviation=13.6,
        normalized_average=0.55,
        normalized_average_std_deviation=0.07,
        relative_normalized_average_std_deviation=12.7,
    )
    mock_dataset.general_parameters = Mock(
        background_rectangles=[Mock(coordinates=[Mock(x=0.0, y=0.0), Mock(x=5.0, y=5.0)])]
    )
    return mock_dataset


@pytest.fixture
def mock_pil_image():
    """Mock PIL Image with realistic size."""
    img = Mock(spec=Image.Image)
    img.size = (200, 150)
    return img


@pytest.fixture
def mock_matplotlib_figure():
    """Mock matplotlib Figure."""
    fig = Mock(spec=plt.Figure)
    fig.savefig = Mock()
    return fig


@pytest.fixture
def mock_svg_figure():
    """Mock svgutils SVGFigure."""
    svg = Mock(spec=sg.SVGFigure)
    svg.width = "200pt"
    svg.height = "150pt"
    svg.getroot = Mock(return_value=Mock())
    svg.set_size = Mock()
    svg.append = Mock()
    return svg


@pytest.fixture
def mock_collage_svgs(mock_svg_figure):
    """List of 4 identical SVG mock figures for collage tests."""
    return [mock_svg_figure] * 4


@pytest.fixture
def viable_datasets(mock_datasets):
    """Clean datasets that pass all viability rules."""
    return mock_datasets


@pytest.fixture
def datasets_with_issues(mock_datasets):
    """Datasets that deliberately violate multiple viability rules."""
    bad_ds1 = Mock(spec=Dataset)
    bad_ds1.samples = []
    bad_ds1.file_holder = Mock(metadata_file=None, parameters_file=None)

    bad_ds2 = Mock(spec=Dataset)
    bad_ds2.samples = [Mock(spots=[])]
    bad_ds2.file_holder = Mock(metadata_file={}, parameters_file={})

    bad_ds3 = Mock(spec=Dataset)
    bad_ds3.samples = [Mock(spots=[Mock(mean_minus_min=-5.0, normalized_mean=0.0, min_val=-1.0)])]
    bad_ds3.file_holder = Mock(metadata_file={}, parameters_file={})

    return [bad_ds1, bad_ds2, bad_ds3]
