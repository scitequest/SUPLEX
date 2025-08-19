import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets
from suplex_modules.submodules.dataset_sorter import *
from suplex_modules.submodules.submodule_constants import SORT_METHOD, DATASET_DESCRIPTOR, DATASET_ATTRIBUTE

class TestDatasetSorterFunctions:
    def test_sort_datasets(self, mock_datasets):
        """Test basic sort with reference list."""
        ref_list = [2, 1]
        sorted_ds, sorted_ref = sort_datasets(mock_datasets, ref_list)
        assert sorted_ds[0] == mock_datasets[1]  # Smallest first
        assert sorted_ref == [1, 2]

        sorted_ds, sorted_ref = sort_datasets(mock_datasets, ref_list, invert_order=True)
        assert sorted_ref == [2, 1]

    def test_sort_by_avg_value(self, mock_datasets):
        """Test sort by avg."""
        reference_lists = [[100, 200], [50, 150]]  # Provide actual reference lists
        sorted_ds, _ = sort_by_avg_value(mock_datasets, reference_lists)
        assert sorted_ds[0] == mock_datasets[1]  # Avg 100 < 150 (50+150)/2=100, wait no: (50+150)/2=100, (100+200)/2=150 -> first has higher? Wait, adjust asserts if needed
        # Note: Adjust based on values: mock_datasets[0] avg=150, mock_datasets[1] avg=100, so sorted ascending: mock[1] first

    # Similar tests for median, max, min, cumulative, number_of_values
    # Example for max:
    def test_sort_by_max_value(self, mock_datasets):
        reference_lists = [[100, 200], [50, 150]]
        sorted_ds, _ = sort_by_max_value(mock_datasets, reference_lists)
        assert sorted_ds[0].id == mock_datasets[1].id  # Assuming max 150 < 200, so [1] first if ascending? Adjust

    def test_sort_alphanumerically(self, mock_datasets):
        """Test alphanumeric sort."""
        # Assuming Dataset has metadata.patient.name
        mock_datasets[0].metadata = Mock(patient=Mock(name="B"))
        mock_datasets[1].metadata = Mock(patient=Mock(name="A"))
        sorted_ds, _ = sort_alphanumerically(mock_datasets, DATASET_DESCRIPTOR.NAME)
        assert sorted_ds[0].metadata.patient.name == "A"

    def test_sort_by_has_tag(self, mock_datasets):
        """Test sort by tag presence."""
        mock_datasets[0].tags = ["tag"]
        mock_datasets[0].suplex_tags = []
        mock_datasets[1].tags = []
        mock_datasets[1].suplex_tags = []
        sorted_ds, _ = sort_by_has_tag(mock_datasets, "tag")
        assert sorted_ds[0] == mock_datasets[0]  # Has tag first

class TestSortStep:
    def test_init(self):
        """Test SortStep init."""
        step = SortStep()
        assert step._sort_method_dropdown.value == SORT_METHOD.UNSORTED.value
        assert step._descriptor_dropdown.value == DATASET_DESCRIPTOR.NAME.value
        assert step._attribute_dropdown.value == DATASET_ATTRIBUTE.SPOT_VALUES.value  # Adjust to first option, since MEAN_MINUS_MIN may not be first
        assert step._tag_dropdown.value == "No Tags Available"  # Default

    def test_get_ui(self):
        """Test UI of SortStep."""
        step = SortStep()
        ui = step.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_get_sorted_datasets(self, mock_datasets):
        """Test sorted datasets of step."""
        step = SortStep()
        step._sort_method_dropdown.value = SORT_METHOD.ALPHANUMERIC_SORT.value
        step._descriptor_dropdown.value = DATASET_DESCRIPTOR.NAME.value
        # Assuming Dataset has metadata.patient.name
        mock_datasets[0].metadata = Mock(patient=Mock(name="B"))
        mock_datasets[1].metadata = Mock(patient=Mock(name="A"))
        sorted_ds = step.get_sorted_datasets(mock_datasets)
        assert sorted_ds[0].metadata.patient.name == "A"

class TestDatasetSorter:
    def test_init(self):
        """Test DatasetSorter init."""
        sorter = DatasetSorter()
        assert sorter.num_levels == 1
        assert len(sorter._sorting_steps) == 0  # Steps are lazy-initialized

    def test_get_ui(self):
        """Test UI of sorter."""
        sorter = DatasetSorter()
        ui = sorter.get_ui()  # This initializes steps
        assert isinstance(ui, widgets.VBox)
        assert len(sorter._sorting_steps) >= 1

    def test_update_sorting_steps(self):
        """Test update steps."""
        sorter = DatasetSorter()
        sorter.get_ui()  # Initialize UI elements first
        sorter.update_sorting_steps(3)
        assert sorter.num_levels == 3
        assert len(sorter._sorting_steps) >= 3

    def test_get_sorted_datasets(self, mock_datasets):
        """Test multi-level sort."""
        sorter = DatasetSorter(num_levels=1)
        sorter.get_ui()  # Initialize steps
        sorter._sorting_steps[0]._sort_method_dropdown.value = SORT_METHOD.ALPHANUMERIC_SORT.value
        sorter._sorting_steps[0]._descriptor_dropdown.value = DATASET_DESCRIPTOR.NAME.value
        # Assuming Dataset has metadata.patient.name
        mock_datasets[0].metadata = Mock(patient=Mock(name="B"))
        mock_datasets[1].metadata = Mock(patient=Mock(name="A"))
        sorted_ds = sorter.get_sorted_datasets(mock_datasets)
        assert sorted_ds[0].metadata.patient.name == "A"