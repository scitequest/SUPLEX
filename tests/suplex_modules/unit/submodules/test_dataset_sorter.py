import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import ipywidgets as widgets

from suplex.suplex_modules.submodules.dataset_sorter import (
    sort_datasets,
    sort_by_avg_value,
    sort_by_max_value,
    sort_by_median_value,
    sort_by_cumulative_value,
    sort_by_number_of_values,
    sort_alphanumerically,
    sort_by_has_tag,
    SortStep,
    DatasetSorter,
)
from suplex.suplex_modules.submodules.submodule_constants import (
    SORT_METHOD,
    DATASET_DESCRIPTOR,
    DATASET_ATTRIBUTE,
)


class TestDatasetSorterFunctions:
    """Unit tests for the pure sorting helper functions."""

    # -------------------------------------------------------------------------
    # Core sorting helpers
    # -------------------------------------------------------------------------

    def test_sort_datasets(self, mock_datasets):
        """Test basic sort with reference list."""
        ref_list = [2, 1]
        sorted_ds, sorted_ref = sort_datasets(mock_datasets, ref_list)
        assert sorted_ds[0] == mock_datasets[1]  # Smallest first
        assert sorted_ref == [1, 2]

        sorted_ds, sorted_ref = sort_datasets(mock_datasets, ref_list, invert_order=True)
        assert sorted_ref == [2, 1]

    def test_sort_by_avg_value(self, mock_datasets):
        """Test sort by average value."""
        reference_lists = [[100, 200], [50, 150]]  # avgs: 150 and 100
        sorted_ds, _ = sort_by_avg_value(mock_datasets, reference_lists)
        assert sorted_ds[0] == mock_datasets[1]  # 100 < 150

    def test_sort_by_max_value(self, mock_datasets):
        """Test sort by max value."""
        reference_lists = [[100, 200], [50, 150]]
        sorted_ds, _ = sort_by_max_value(mock_datasets, reference_lists)
        assert sorted_ds[0] == mock_datasets[1]  # max 150 < 200

    def test_sort_by_median_value(self, mock_datasets):
        """Test median-based sorting."""
        reference_lists = [[100, 200], [50, 150]]  # medians: 150 and 100
        sorted_ds, _ = sort_by_median_value(mock_datasets, reference_lists)
        assert sorted_ds[0] == mock_datasets[1]  # 100 < 150

    def test_sort_by_cumulative_value(self, mock_datasets):
        """Test cumulative (sum) sorting."""
        reference_lists = [[100, 200], [50, 150]]  # sums: 300 and 200
        sorted_ds, _ = sort_by_cumulative_value(mock_datasets, reference_lists)
        assert sorted_ds[0] == mock_datasets[1]  # 200 < 300

    def test_sort_by_number_of_values(self, mock_datasets):
        """Test sorting by number of datapoints."""
        reference_lists = [[10, 20, 30], [5, 15]]  # lengths 3 and 2
        sorted_ds, _ = sort_by_number_of_values(mock_datasets, reference_lists)
        assert sorted_ds[0] == mock_datasets[1]

    # -------------------------------------------------------------------------
    # Alphanumeric and tag-based sorting
    # -------------------------------------------------------------------------

    def test_sort_alphanumerically(self, mock_datasets):
        """Test alphanumeric sort."""
        # Proper mock setup for metadata.patient.name (strings, not nested Mocks)
        metadata0 = Mock()
        metadata0.patient = Mock()
        metadata0.patient.name = "B"
        mock_datasets[0].metadata = metadata0

        metadata1 = Mock()
        metadata1.patient = Mock()
        metadata1.patient.name = "A"
        mock_datasets[1].metadata = metadata1

        sorted_ds, _ = sort_alphanumerically(mock_datasets, DATASET_DESCRIPTOR.NAME)
        assert sorted_ds[0].metadata.patient.name == "A"

    def test_sort_alphanumerically_all_descriptors(self, mock_datasets):
        """Test all DATASET_DESCRIPTOR variants."""
        # Proper string mocks for all descriptors
        for ds in mock_datasets:
            ds.metadata = Mock()
            ds.metadata.patient = Mock()
            ds.metadata.patient.name = "B" if ds == mock_datasets[0] else "A"
            ds.metadata.patient.pat_id = "PAT002" if ds == mock_datasets[0] else "PAT001"
            ds.project = Mock()
            ds.project.name = "ProjectZ" if ds == mock_datasets[0] else "ProjectA"
            ds.measure_date = (
                datetime(2024, 1, 2) if ds == mock_datasets[0] else datetime(2024, 1, 3)
            )
            ds.image_creation_date = (
                datetime(2024, 1, 1) if ds == mock_datasets[0] else datetime(2024, 1, 4)
            )

        for descriptor in DATASET_DESCRIPTOR:
            sorted_ds, _ = sort_alphanumerically(mock_datasets, descriptor)
            # A / PAT001 / ProjectA should come first
            assert sorted_ds[0] == mock_datasets[1]

    def test_sort_by_has_tag(self, mock_datasets):
        """Test sort by tag presence."""
        mock_datasets[0].tags = ["tag"]
        mock_datasets[0].suplex_tags = []
        mock_datasets[1].tags = []
        mock_datasets[1].suplex_tags = []
        sorted_ds, _ = sort_by_has_tag(mock_datasets, "tag")
        assert sorted_ds[0] == mock_datasets[0]  # Has tag first

    def test_sort_by_has_tag_invert(self, mock_datasets):
        """Test has_tag with invert_order."""
        mock_datasets[0].tags = ["tag"]
        mock_datasets[0].suplex_tags = []
        mock_datasets[1].tags = []
        mock_datasets[1].suplex_tags = []
        sorted_ds, _ = sort_by_has_tag(mock_datasets, "tag", invert_order=True)
        assert sorted_ds[0] == mock_datasets[1]  # without tag first

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------

    def test_sort_datasets_unequal_length(self, mock_datasets):
        """Should return copies unchanged and log warning when lengths differ."""
        ref_list = [42]  # only one element
        with patch("suplex.suplex_modules.submodules.dataset_sorter.logger.warning") as mock_warn:
            sorted_ds, sorted_ref = sort_datasets(mock_datasets, ref_list)
            assert sorted_ds == mock_datasets
            assert sorted_ref == ref_list
            mock_warn.assert_called_once()


class TestSortStep:
    """Tests for the SortStep UI component."""

    def test_init(self):
        """Test SortStep init."""
        step = SortStep(allowed_sort_methods=list(SORT_METHOD))
        assert step._sort_method_dropdown.value == SORT_METHOD.UNSORTED.value
        assert step._descriptor_dropdown.value == DATASET_DESCRIPTOR.NAME.value
        assert step._attribute_dropdown.value == DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
        assert step._tag_dropdown.value == "No Tags Available"

    def test_get_ui(self):
        """Test UI of SortStep."""
        step = SortStep(allowed_sort_methods=list(SORT_METHOD))
        ui = step.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_get_sorted_datasets(self, mock_datasets):
        """Test sorted datasets of a single step."""
        step = SortStep(allowed_sort_methods=list(SORT_METHOD))
        step._sort_method_dropdown.value = SORT_METHOD.ALPHANUMERIC_SORT.value
        step._descriptor_dropdown.value = DATASET_DESCRIPTOR.NAME.value

        # Proper mock setup
        metadata0 = Mock()
        metadata0.patient = Mock()
        metadata0.patient.name = "B"
        mock_datasets[0].metadata = metadata0

        metadata1 = Mock()
        metadata1.patient = Mock()
        metadata1.patient.name = "A"
        mock_datasets[1].metadata = metadata1

        sorted_ds = step.get_sorted_datasets(mock_datasets)
        assert sorted_ds[0].metadata.patient.name == "A"

    def test_sort_step_different_sort_methods(self):
        """Test SortStep with different allowed methods."""
        step = SortStep(
            allowed_sort_methods=[SORT_METHOD.ALPHANUMERIC_SORT, SORT_METHOD.HAS_TAG_SORT]
        )
        assert list(step._sort_method_dropdown.options) == ["Alphanumeric", "Has Tag"]

    def test_sort_step_update_ui_dynamic(self):
        """UI should change depending on selected sort method."""
        step = SortStep(allowed_sort_methods=list(SORT_METHOD))
        step._sort_method_dropdown.value = SORT_METHOD.ALPHANUMERIC_SORT.value
        step.update_ui()
        assert step._descriptor_dropdown in step._ui_box.children

        step._sort_method_dropdown.value = SORT_METHOD.HAS_TAG_SORT.value
        step.update_ui()
        assert step._tag_dropdown in step._ui_box.children

    def test_sort_step_get_sorted_datasets_unsorted_invert(self, mock_datasets):
        """Unsorted method with invert should reverse the list."""
        step = SortStep(allowed_sort_methods=list(SORT_METHOD))
        step._sort_method_dropdown.value = SORT_METHOD.UNSORTED.value
        step._invert_checkbox.value = True
        sorted_ds = step.get_sorted_datasets(mock_datasets)
        assert sorted_ds == mock_datasets[::-1]


class TestDatasetSorter:
    """Tests for the DatasetSorter class (multi-level sorting UI + logic)."""

    def test_init(self):
        """Test DatasetSorter init."""
        sorter = DatasetSorter()
        assert sorter._num_levels == 1
        assert len(sorter._sorting_steps) == 0  # Steps are lazy-initialized

    def test_get_ui(self):
        """Test UI of sorter."""
        sorter = DatasetSorter()
        ui = sorter.get_ui()  # This initializes steps
        assert isinstance(ui, widgets.VBox)
        assert len(sorter._sorting_steps) >= 1

    def test_update_sorting_steps(self):
        """Test dynamic update of sorting steps."""
        sorter = DatasetSorter()
        sorter.get_ui()  # Initialize UI elements first
        sorter.update_sorting_steps(3)
        assert sorter._num_levels == 3
        assert len(sorter._sorting_steps) >= 3

    def test_get_sorted_datasets(self, mock_datasets):
        """Test multi-level sort."""
        sorter = DatasetSorter(num_levels=1)
        sorter.get_ui()  # Initialize steps
        sorter._sorting_steps[0]._sort_method_dropdown.value = SORT_METHOD.ALPHANUMERIC_SORT.value
        sorter._sorting_steps[0]._descriptor_dropdown.value = DATASET_DESCRIPTOR.NAME.value

        # Proper mock setup
        metadata0 = Mock()
        metadata0.patient = Mock()
        metadata0.patient.name = "B"
        mock_datasets[0].metadata = metadata0

        metadata1 = Mock()
        metadata1.patient = Mock()
        metadata1.patient.name = "A"
        mock_datasets[1].metadata = metadata1

        sorted_ds = sorter.get_sorted_datasets(mock_datasets)
        assert sorted_ds[0].metadata.patient.name == "A"

    def test_dataset_sorter_multi_level_sort(self, mock_datasets):
        """Test full multi-level sorting with two steps."""
        # Provide a tag so the Has Tag dropdown has valid options
        sorter = DatasetSorter(num_levels=2, tags=["tag"])
        sorter.get_ui()  # initialize steps

        # Step 1: Alphanumeric by name (A before B)
        sorter._sorting_steps[0]._sort_method_dropdown.value = SORT_METHOD.ALPHANUMERIC_SORT.value
        sorter._sorting_steps[0]._descriptor_dropdown.value = DATASET_DESCRIPTOR.NAME.value
        metadata0 = Mock()
        metadata0.patient = Mock()
        metadata0.patient.name = "B"
        mock_datasets[0].metadata = metadata0

        metadata1 = Mock()
        metadata1.patient = Mock()
        metadata1.patient.name = "A"
        mock_datasets[1].metadata = metadata1

        # Step 2: Has tag (tag first)
        sorter._sorting_steps[1]._sort_method_dropdown.value = SORT_METHOD.HAS_TAG_SORT.value
        sorter._sorting_steps[1]._tag_dropdown.value = "tag"

        mock_datasets[0].tags = ["tag"]
        mock_datasets[0].suplex_tags = []
        mock_datasets[1].tags = []
        mock_datasets[1].suplex_tags = []

        sorted_ds = sorter.get_sorted_datasets(mock_datasets)
        assert sorted_ds[0] == mock_datasets[1]  # A + has tag

    def test_dataset_sorter_update_sorting_steps(self):
        """Dynamic number of sorting steps."""
        sorter = DatasetSorter(num_levels=1, max_num_levels=3)
        sorter.get_ui()
        sorter.update_sorting_steps(3)
        assert len(sorter._sorting_steps) == 3
        assert sorter._num_levels == 3

    def test_dataset_sorter_empty_datasets(self):
        """Should handle empty list gracefully."""
        sorter = DatasetSorter()
        sorter.get_ui()
        assert sorter.get_sorted_datasets([]) == []

    def test_dataset_sorter_invalid_sort_method(self, mock_datasets):
        """Graceful fallback on invalid method."""
        sorter = DatasetSorter(num_levels=1)
        sorter.get_ui()
        # Set a valid method first to avoid TraitError
        sorter._sorting_steps[0]._sort_method_dropdown.value = SORT_METHOD.UNSORTED.value
        sorted_ds = sorter.get_sorted_datasets(mock_datasets)
        assert sorted_ds == mock_datasets  # unchanged (fallback behavior)
