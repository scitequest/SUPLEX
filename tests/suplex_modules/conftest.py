import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

from suplex.martin_interface.dataset import Dataset
from suplex.suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE


# =============================================================================
# Fixtures used only within the submodules tests
# =============================================================================


@pytest.fixture
def mock_attribute_selector():
    """Mock of the AttributeSelector class."""
    from suplex.suplex_modules.submodules.attribute_selector import AttributeSelector

    selector = Mock(spec=AttributeSelector)
    selector.attribute = "MEAN_MINUS_MIN"
    return selector


@pytest.fixture
def mock_dataset_sorter():
    """Mock of the DatasetSorter class."""
    from suplex.suplex_modules.submodules.dataset_sorter import DatasetSorter

    sorter = Mock(spec=DatasetSorter)
    sorter.get_sorted_datasets = MagicMock(return_value=[])
    return sorter


@pytest.fixture
def mock_dataset_filter():
    """Mock of the DatasetFilter class."""
    from suplex.suplex_modules.submodules.dataset_filters import DatasetFilter

    filter_obj = Mock(spec=DatasetFilter)
    filter_obj.get_filtered_datasets = MagicMock(return_value=([], []))
    return filter_obj


@pytest.fixture
def mock_sample_spot_filter():
    """Mock of the SampleSpotFilter class."""
    from suplex.suplex_modules.submodules.sample_spot_filter import SampleSpotFilter

    filter_obj = Mock(spec=SampleSpotFilter)
    filter_obj.get_filter_maps = MagicMock(return_value=({}, {}))
    return filter_obj


@pytest.fixture
def mock_value_list():
    """Mock list of values for attribute extraction."""
    return [100.0, 200.0, 150.0, 50.0]


@pytest.fixture
def mock_nested_value_list():
    """Mock nested list for Sample/Spot values."""
    return [[100.0, 200.0], [150.0, 50.0]]


@pytest.fixture
def mock_coordinates_list():
    """Mock for coordinate lists."""
    return [[[1, 2], [3, 4]], [[5, 6]]]


@pytest.fixture
def attribute_selector():
    """Fresh AttributeSelector instance for widget testing."""
    from suplex.suplex_modules.submodules.attribute_selector import AttributeSelector

    return AttributeSelector()


@pytest.fixture
def attribute_selector_with_checkboxes(attribute_selector):
    """AttributeSelector with checkbox widgets already created."""
    attribute_selector.get_checkbox_widgets(DATA_ATTRIBUTES)
    return attribute_selector


@pytest.fixture
def mock_datasets_with_labels():
    """Multiple mock datasets with realistic metadata for label and date testing."""
    ds1 = Mock(spec=Dataset)
    ds1.metadata = Mock(name="Patient A", pat_id="PAT001")
    ds1.image_creation_date = datetime(2024, 1, 15)
    ds1.measure_date = datetime(2024, 1, 20)

    ds2 = Mock(spec=Dataset)
    ds2.metadata = Mock(name="Patient B", pat_id="PAT002")
    ds2.image_creation_date = datetime(2024, 2, 5)
    ds2.measure_date = datetime(2024, 2, 10)

    ds3 = Mock(spec=Dataset)
    ds3.metadata = Mock(name="Patient C", pat_id="PAT003")
    ds3.image_creation_date = datetime(2024, 1, 10)
    ds3.measure_date = datetime(2024, 3, 1)

    return [ds1, ds2, ds3]


@pytest.fixture
def dataset_selector(mock_datasets_with_labels):
    """Fresh DatasetSelector in MULTIPLE_UNBOUND mode (default)."""
    from suplex.suplex_modules.submodules.dataset_selector import DatasetSelector

    return DatasetSelector(
        datasets=mock_datasets_with_labels,
        mode=DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
    )


@pytest.fixture
def bounded_dataset_selector(mock_datasets_with_labels):
    """DatasetSelector in MULTIPLE_BOUND mode with limit=2."""
    from suplex.suplex_modules.submodules.dataset_selector import DatasetSelector

    return DatasetSelector(
        datasets=mock_datasets_with_labels,
        mode=DATASET_SELECTOR_MODE.MULTIPLE_BOUND,
        checkbox_limit=2,
    )


@pytest.fixture
def single_dataset_selector(mock_datasets_with_labels):
    """DatasetSelector in SINGLE mode."""
    from suplex.suplex_modules.submodules.dataset_selector import DatasetSelector

    return DatasetSelector(
        datasets=mock_datasets_with_labels,
        mode=DATASET_SELECTOR_MODE.SINGLE,
    )


@pytest.fixture
def mock_datasets_with_tags():
    """Mock datasets with a mix of MARTin tags and SUPLEX tags."""
    ds1 = Mock(spec=Dataset)
    ds1.tags = ["tag1", "tag2"]
    ds1.suplex_tags = ["analysis1"]

    ds2 = Mock(spec=Dataset)
    ds2.tags = ["tag2", "tag3"]
    ds2.suplex_tags = []

    ds3 = Mock(spec=Dataset)
    ds3.tags = []
    ds3.suplex_tags = ["validated", "analysis1"]

    ds4 = Mock(spec=Dataset)
    ds4.tags = ["tag1"]
    ds4.suplex_tags = ["validated"]

    return [ds1, ds2, ds3, ds4]


@pytest.fixture
def tag_selector(mock_datasets_with_tags):
    """Fresh TagSelector instance."""
    from suplex.suplex_modules.submodules.tag_selector import TagSelector

    return TagSelector(datasets=mock_datasets_with_tags)


@pytest.fixture
def sample_value_list():
    """Realistic intensity values with clear gaps for delta/group testing."""
    return [10.0, 25.0, 30.0, 45.0, 50.0, 80.0, 100.0, 120.0, 200.0]


@pytest.fixture
def small_value_list():
    """Small list for edge-case testing (normality, grouping)."""
    return [5.0, 10.0, 50.0]


@pytest.fixture
def mock_shapiro():
    """Mock for shapiro test (used in apply_adaptive_significance_cutoff)."""
    with patch("suplex.suplex_modules.submodules.dynamic_threshold_filter.shapiro") as mock:
        yield mock


@pytest.fixture
def mock_ks_2samp():
    """Mock for ks_2samp test (used in apply_sparsity_cutoff)."""
    with patch("suplex.suplex_modules.submodules.dynamic_threshold_filter.ks_2samp") as mock:
        yield mock


@pytest.fixture
def value_extractor():
    """Fresh ValueExtractor with all options enabled (default)."""
    from suplex.suplex_modules.submodules.value_extractor import ValueExtractor

    return ValueExtractor(show_all_options=True)


@pytest.fixture
def reference_point_selector():
    """Fresh ReferencePointSelector for testing reference logic."""
    from suplex.suplex_modules.submodules.value_extractor import ReferencePointSelector

    return ReferencePointSelector(max_index=10, initial_references=[0, 3, 5])


# =============================================================================
# Settings fixtures
# =============================================================================


@pytest.fixture
def general_graph_settings():
    """Fresh GeneralGraphSettings with all options enabled (default behaviour)."""
    from suplex.suplex_modules.submodules.settings.general_graph_settings import GeneralGraphSettings

    return GeneralGraphSettings(show_all_options=True)


@pytest.fixture
def minimal_general_graph_settings():
    """Minimal GeneralGraphSettings – only a few options explicitly enabled."""
    from suplex.suplex_modules.submodules.settings.general_graph_settings import GeneralGraphSettings

    return GeneralGraphSettings(
        show_all_options=False,
        col_descriptor="Column",
        row_descriptor="Row",
        show_grid=True,
        x_scale=None,
    )


@pytest.fixture
def boxplot_settings():
    """Fresh BoxplotSettings instance with all options enabled (default behaviour)."""
    from suplex.suplex_modules.submodules.settings.boxplot_settings import BoxplotSettings

    return BoxplotSettings(show_all_options=True)


@pytest.fixture
def minimal_boxplot_settings():
    """BoxplotSettings with only the most important options enabled."""
    from suplex.suplex_modules.submodules.settings.boxplot_settings import BoxplotSettings

    return BoxplotSettings(
        show_boxplot=True,
        show_outliers=True,
        whisker_mode=None,
        show_all_options=False,
    )


@pytest.fixture
def heatmap_settings():
    """Fresh HeatmapSettings instance with all options enabled (default behaviour)."""
    from suplex.suplex_modules.submodules.settings.heatmap_settings import HeatmapSettings

    return HeatmapSettings(show_all_options=True)


@pytest.fixture
def minimal_heatmap_settings():
    """Minimal HeatmapSettings – only core options explicitly enabled."""
    from suplex.suplex_modules.submodules.settings.heatmap_settings import HeatmapSettings

    return HeatmapSettings(
        square=True,
        annot=True,
        show_all_options=False,
    )


@pytest.fixture
def jitterplot_settings():
    """Fresh JitterplotSettings instance with all options enabled (default behaviour)."""
    from suplex.suplex_modules.submodules.settings.jitterplot_settings import JitterplotSettings

    return JitterplotSettings(show_all_options=True)


@pytest.fixture
def minimal_jitterplot_settings():
    """Minimal JitterplotSettings – only core options explicitly enabled."""
    from suplex.suplex_modules.submodules.settings.jitterplot_settings import JitterplotSettings

    return JitterplotSettings(
        show_jitterplot=True,
        apply_jitter=True,
        show_all_options=False,
    )
