"""
Pytest configuration and shared fixtures for SUPLEX integration tests.

This conftest provides realistic fake Dataset objects (duck-typed to match
martin_interface.dataset.Dataset expectations) and helper factories so that
integration tests can exercise full pipelines (value extraction, filtering,
sorting, module initiation, collage generation, exports, etc.) without
requiring the real martin_interface package or hardware.

Fixtures are designed to be reusable across:
- module_loader integration
- data processing pipelines (ValueExtractor + filters + sorters)
- end-to-end flows for Heatmap Collage, Hitmap, Intensity Overview,
  Overview Heatmap, and Excel Adapter modules.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Any, Dict
from unittest.mock import Mock
import numpy as np
import pytest
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# Minimal Fake Data Classes (duck-typed to martin_interface structures)
# These implement only the attributes actually accessed by the SUPLEX modules
# and submodules. They are intentionally lightweight for fast test execution.
# =============================================================================


@dataclass
class FakeCoordinate:
    x: float
    y: float


@dataclass
class FakeSpotValues:
    mean_minus_min: float = 100.0
    normalized_mean: float = 0.5
    min_val: float = 50.0
    max_val: float = 200.0
    mean_val: float = 120.0
    std_deviation: float = 25.0


@dataclass
class FakeSpotParameters:
    coordinates: List[FakeCoordinate] = field(default_factory=list)


@dataclass
class FakeSpot:
    spot_values: FakeSpotValues = field(default_factory=FakeSpotValues)
    spot_parameters: Optional[FakeSpotParameters] = None
    shape: Optional[str] = "circle"

    # Compatibility properties for viability_rules (which expects direct attributes)
    @property
    def mean_minus_min(self):
        return self.spot_values.mean_minus_min

    @property
    def normalized_mean(self):
        return self.spot_values.normalized_mean

    @property
    def min_val(self):
        return self.spot_values.min_val

    @property
    def max_val(self):
        return self.spot_values.max_val

    @property
    def mean_val(self):
        return self.spot_values.mean_val

    @property
    def std_deviation(self):
        return self.spot_values.std_deviation

    @property
    def coordinates(self):
        return self.spot_parameters.coordinates if self.spot_parameters else []


@dataclass
class FakeDataStatistics:
    row: int = 0
    col: int = 0
    adjusted_average: float = 125.0
    adjusted_average_std_deviation: float = 22.0
    relative_adjusted_average_std_deviation: float = 17.6
    normalized_average: float = 0.62
    normalized_average_std_deviation: float = 0.11
    relative_normalized_average_std_deviation: float = 17.7


@dataclass
class FakeSample:
    data_statistics: FakeDataStatistics = field(default_factory=FakeDataStatistics)
    spots: List[FakeSpot] = field(default_factory=list)


@dataclass
class FakeBackgroundRectangle:
    coordinates: List[FakeCoordinate] = field(default_factory=list)


@dataclass
class FakeGeneralParameters:
    columns_per_spotfield: int = 8
    number_of_spotfields: int = 1
    spots_per_spotfield: int = 64
    invert_lut: bool = False
    subtract_background: bool = True
    background_rectangles: List[FakeBackgroundRectangle] = field(default_factory=list)


@dataclass
class FakeImage:
    imager: str = "TestImager v1.0"
    pixel_binning: int = 1
    exposure_time: Any = "120ms"


@dataclass
class FakeIncubation:
    solution: str = "Blocking Buffer"
    stock_concentration: Any = field(default_factory=lambda: Mock(value=5.0, unit="percent"))
    final_concentration: Any = field(default_factory=lambda: Mock(value=1.0, unit="percent"))
    incubation_time: timedelta = field(default_factory=lambda: timedelta(minutes=30))


@dataclass
class FakeMetadata:
    incubations: List[FakeIncubation] = field(default_factory=list)
    image: FakeImage = field(default_factory=FakeImage)


@dataclass
class FakeProject:
    name: str = "IntegrationTestProject"


@dataclass
class FakeFileHolder:
    metadata_file: Any = field(default_factory=Mock)
    parameters_file: Any = field(default_factory=Mock)


@dataclass
class FakeDataset:
    """
    Lightweight stand-in for martin_interface.dataset.Dataset.
    Uses identity-based hashing so it can be used as dict keys in filters/sorters.
    """

    id: str = "DS_INT_001"
    name: str = "Integration Test Dataset"
    tags: List[str] = field(default_factory=lambda: ["test", "integration"])
    suplex_tags: List[str] = field(default_factory=list)
    project: FakeProject = field(default_factory=FakeProject)
    measure_date: datetime = field(default_factory=lambda: datetime(2025, 6, 1, 10, 30))
    image_creation_date: datetime = field(default_factory=lambda: datetime(2025, 6, 1, 9, 15))
    samples: List[FakeSample] = field(default_factory=list)
    general_parameters: Optional[FakeGeneralParameters] = field(
        default_factory=FakeGeneralParameters
    )
    metadata: Optional[FakeMetadata] = field(default_factory=FakeMetadata)
    file_holder: Any = field(default_factory=FakeFileHolder)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


# =============================================================================
# Dataset Factory Helpers
# =============================================================================


def create_fake_dataset(
    *,
    dataset_id: str = "DS_INT_001",
    n_samples: int = 3,
    n_spots_per_sample: int = 8,
    base_value: float = 120.0,
    noise_std: float = 18.0,
    with_negatives: bool = False,
    uniform_spots: bool = True,
    seed: int = 42,
) -> FakeDataset:
    """
    Create a controlled FakeDataset for integration testing.

    Args:
        dataset_id: Identifier for the dataset.
        n_samples: Number of samples.
        n_spots_per_sample: Spots per sample (can vary if uniform_spots=False).
        base_value: Mean intensity level.
        noise_std: Standard deviation of added noise.
        with_negatives: Inject one negative value (useful for viability tests).
        uniform_spots: Keep spot count identical across samples.
        seed: Random seed for reproducibility.

    Returns:
        Fully populated FakeDataset ready for value extraction, filtering, etc.
    """
    np.random.seed(seed)
    samples: List[FakeSample] = []

    for s_idx in range(n_samples):
        spots: List[FakeSpot] = []
        n_spots = n_spots_per_sample if uniform_spots else max(3, n_spots_per_sample - s_idx)

        for sp_idx in range(n_spots):
            val = base_value + np.random.normal(0, noise_std)
            if with_negatives and s_idx == 0 and sp_idx == 0:
                val = -15.0

            coord_count = 4
            coords = [
                FakeCoordinate(x=10.0 + sp_idx * 5.0 + s_idx, y=20.0 + np.random.uniform(-2, 2))
                for _ in range(coord_count)
            ]

            spots.append(
                FakeSpot(
                    spot_values=FakeSpotValues(
                        mean_minus_min=round(val, 2),
                        normalized_mean=round(max(0.0, val / 250.0), 4),
                        min_val=round(val - 12, 2),
                        max_val=round(val + 35, 2),
                        mean_val=round(val, 2),
                        std_deviation=round(noise_std * 0.8, 2),
                    ),
                    spot_parameters=FakeSpotParameters(coordinates=coords),
                )
            )

        samples.append(
            FakeSample(
                data_statistics=FakeDataStatistics(
                    adjusted_average=round(base_value + s_idx * 4.5, 2),
                    adjusted_average_std_deviation=round(noise_std * 0.9, 2),
                ),
                spots=spots,
            )
        )

    return FakeDataset(
        id=dataset_id,
        name=f"Integration Dataset {dataset_id}",
        samples=samples,
    )


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def positive_uniform_datasets() -> List[FakeDataset]:
    """Two clean, uniform, positive-value datasets (typical happy-path case)."""
    return [
        create_fake_dataset(
            dataset_id="DS_POS_01", n_samples=4, n_spots_per_sample=10, base_value=145.0, seed=42
        ),
        create_fake_dataset(
            dataset_id="DS_POS_02", n_samples=4, n_spots_per_sample=10, base_value=168.0, seed=43
        ),
    ]


@pytest.fixture(scope="function")
def negative_value_dataset() -> FakeDataset:
    """Dataset containing at least one negative value (triggers viability rule)."""
    return create_fake_dataset(
        dataset_id="DS_NEG_01",
        n_samples=2,
        n_spots_per_sample=6,
        base_value=80.0,
        with_negatives=True,
        seed=99,
    )


@pytest.fixture(scope="function")
def non_uniform_sample_count_datasets() -> List[FakeDataset]:
    """Datasets with different numbers of samples (violates uniformity rule)."""
    ds1 = create_fake_dataset(dataset_id="DS_UNI_01", n_samples=3, n_spots_per_sample=8, seed=10)
    ds2 = create_fake_dataset(dataset_id="DS_UNI_02", n_samples=5, n_spots_per_sample=8, seed=11)
    return [ds1, ds2]


@pytest.fixture(scope="function")
def insufficient_samples_dataset() -> FakeDataset:
    """Dataset with fewer than 3 samples (Hitmap requires at least 3)."""
    return create_fake_dataset(dataset_id="DS_FEW_01", n_samples=2, n_spots_per_sample=8, seed=55)


@pytest.fixture(scope="function")
def empty_dataset_list() -> List[FakeDataset]:
    """Empty list of datasets (edge case for many modules)."""
    return []


@pytest.fixture
def mock_color_scheme() -> Mock:
    """
    Minimal color scheme mock expected by SuplexModuleInterface.initiate_module
    and update_scheme.
    """
    scheme = Mock()
    # Table colors used in dataset statistics HTML
    scheme.LAYOUT_COLOR.TABLE.HEAD = "#2E75B6"
    scheme.LAYOUT_COLOR.TABLE.LINES = "#BDD7EE"
    scheme.TEXT.COLOR.TABLE.HEAD = "#FFFFFF"
    scheme.TEXT.COLOR.TABLE.BODY = "#1F4E79"
    return scheme


@pytest.fixture
def temp_module_directory(tmp_path: Path) -> Path:
    """
    Temporary directory pre-populated with example valid and invalid modules.
    Used by module_loader integration tests.
    """
    mod_dir = tmp_path / "suplex_modules"
    mod_dir.mkdir()

    # Valid minimal module
    valid_module = mod_dir / "valid_test_module.py"
    valid_module.write_text(
        """
from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface
from typing import List, Dict, Any, Optional
from typing_extensions import Self
import ipywidgets as widgets
from suplex.martin_interface.dataset import Dataset

class ValidTestModule(SuplexModuleInterface):
    @property
    def module_name(self) -> str:
        return "Valid Test Module"

    @property
    def module_version(self) -> str:
        return "0.0.1"

    @property
    def group_name(self) -> str:
        return "IntegrationTest"

    @property
    def button_style(self) -> Dict[str, str]:
        return {"font_color": "#000000", "button_color": "#00FF00", "button_icon": "🧪"}

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        return "Integration test module"

    def initiate_module(self, datasets: List[Dataset], color_scheme: Any) -> widgets.Box:
        return widgets.VBox()

    def update_scheme(self, new_scheme: Any) -> Optional[Self]:
        return self

    def reset_module(self) -> Optional[Self]:
        return ValidTestModule()
""",
        encoding="utf-8",  # ← THIS IS THE FIX
    )

    # Invalid: syntax error
    syntax_error_module = mod_dir / "syntax_error.py"
    syntax_error_module.write_text("this is not valid python : syntax error here", encoding="utf-8")

    # Invalid: no SuplexModuleInterface
    no_interface_module = mod_dir / "no_interface.py"
    no_interface_module.write_text(
        """
class NotASuplexModule:
    pass
""",
        encoding="utf-8",
    )

    # Hidden / ignored directory
    (mod_dir / ".hidden").mkdir()
    (mod_dir / "__pycache__").mkdir(exist_ok=True)

    return mod_dir


@pytest.fixture
def loaded_valid_module(temp_module_directory: Path):
    """Convenience fixture that returns the loaded ValidTestModule instance."""
    from suplex.suplex_modules.module_loader import load_modules
    from suplex.suplex_modules.module_constants import SEARCH_MODE

    modules = load_modules(
        dir_path=str(temp_module_directory),
        mode=SEARCH_MODE.RECURSIVE,
    )
    valid_ones = [m for m in modules if m.module_name == "Valid Test Module"]
    assert len(valid_ones) == 1, "Expected exactly one valid test module"
    return valid_ones[0]
