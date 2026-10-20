import pytest
from typing import List, Any

from suplex.suplex_modules.submodules.dataset_filters import DatasetFilter
from suplex.suplex_modules.submodules.sample_spot_filter import SampleSpotFilter
from suplex.suplex_modules.submodules.dataset_sorter import DatasetSorter
from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    FILTER_METHOD,
    SORT_METHOD,
)
from suplex.suplex_modules.submodules.value_extractor import get_flat_value_list


class TestIntegrationFilteringAndSortingPipeline:
    """Integration tests for dataset filtering and multi-level sorting."""

    # -------------------------------------------------------------------------
    # DatasetFilter tests
    # -------------------------------------------------------------------------

    def test_dataset_filter_happy_path(self, positive_uniform_datasets: List[Any]):
        dataset_filter = DatasetFilter()
        included, excluded = dataset_filter.get_filtered_datasets(
            positive_uniform_datasets,
            method=FILTER_METHOD.AVG_ABOVE,
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
        )
        assert isinstance(included, list) and isinstance(excluded, list)
        assert len(included) + len(excluded) == len(positive_uniform_datasets)

    def test_dataset_filter_invert_logic(self, positive_uniform_datasets: List[Any]):
        dataset_filter = DatasetFilter()
        dataset_filter._invert_checkbox.value = False
        included_normal, _ = dataset_filter.get_filtered_datasets(
            positive_uniform_datasets,
            method=FILTER_METHOD.AVG_ABOVE,
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
        )
        dataset_filter._invert_checkbox.value = True
        included_inverted, _ = dataset_filter.get_filtered_datasets(
            positive_uniform_datasets,
            method=FILTER_METHOD.AVG_ABOVE,
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
        )
        assert len(included_normal) + len(included_inverted) == len(positive_uniform_datasets)

    # -------------------------------------------------------------------------
    # SampleSpotFilter tests (now work with identity-hashed FakeDataset)
    # -------------------------------------------------------------------------

    def test_sample_spot_filter_produces_threshold_maps(self, positive_uniform_datasets: List[Any]):
        sample_spot_filter = SampleSpotFilter()
        sample_map, spot_map = sample_spot_filter.get_filter_maps(
            positive_uniform_datasets,
            attribute=DATASET_ATTRIBUTE.ADJUSTED_AVERAGE,
            min_threshold=0.0,
            max_threshold=1000.0,
        )
        assert isinstance(sample_map, dict)
        assert len(sample_map) == len(positive_uniform_datasets)

    def test_sample_spot_filter_any_vs_all_propagation(self, positive_uniform_datasets: List[Any]):
        sample_spot_filter = SampleSpotFilter()
        sample_spot_filter._spots_affect_sample_checkbox.value = True
        sample_spot_filter._sample_filter_mode_dropdown.value = "any"

        sample_map, spot_map = sample_spot_filter.get_filter_maps(
            positive_uniform_datasets,
            attribute=DATASET_ATTRIBUTE.ADJUSTED_AVERAGE,
            min_threshold=50.0,
            max_threshold=2000.0,
        )
        assert isinstance(sample_map, dict)

    # -------------------------------------------------------------------------
    # DatasetSorter tests
    # -------------------------------------------------------------------------

    def test_dataset_sorter_single_level_sort(self, positive_uniform_datasets: List[Any]):
        sorter = DatasetSorter(num_levels=1)
        sorter.get_ui()
        step = sorter._sorting_steps[0]
        step._sort_method_dropdown.value = SORT_METHOD.AVG_VALUE_SORT.value
        step._attribute_dropdown.value = DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
        sorted_ds = sorter.get_sorted_datasets(positive_uniform_datasets)
        assert len(sorted_ds) == len(positive_uniform_datasets)

    def test_dataset_sorter_multi_level_sort(self, positive_uniform_datasets: List[Any]):
        sorter = DatasetSorter(num_levels=2)
        sorter.get_ui()
        sorter._sorting_steps[0]._sort_method_dropdown.value = SORT_METHOD.AVG_VALUE_SORT.value
        sorter._sorting_steps[0]._attribute_dropdown.value = DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
        sorter._sorting_steps[1]._sort_method_dropdown.value = SORT_METHOD.MEDIAN_VALUE_SORT.value
        sorter._sorting_steps[1]._attribute_dropdown.value = DATASET_ATTRIBUTE.NORMALIZED_MEAN.value
        sorted_ds = sorter.get_sorted_datasets(positive_uniform_datasets)
        assert len(sorted_ds) == len(positive_uniform_datasets)

    def test_dataset_sorter_with_tag_sort(self, positive_uniform_datasets: List[Any]):
        for i, ds in enumerate(positive_uniform_datasets):
            ds.suplex_tags = [f"tag_{i % 2}"]

        sorter = DatasetSorter(num_levels=1, tags=["tag_0", "tag_1"])
        sorter.get_ui()
        step = sorter._sorting_steps[0]
        step._sort_method_dropdown.value = SORT_METHOD.HAS_TAG_SORT.value
        step._tag_dropdown.value = "tag_0"
        sorted_ds = sorter.get_sorted_datasets(positive_uniform_datasets)
        assert len(sorted_ds) == len(positive_uniform_datasets)

    # -------------------------------------------------------------------------
    # Combined pipeline tests
    # -------------------------------------------------------------------------

    def test_filter_then_sort_pipeline(self, positive_uniform_datasets: List[Any]):
        dataset_filter = DatasetFilter()
        included, _ = dataset_filter.get_filtered_datasets(
            positive_uniform_datasets,
            method=FILTER_METHOD.AVG_ABOVE,
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
        )
        if len(included) > 1:
            sorter = DatasetSorter(num_levels=1)
            sorter.get_ui()
            step = sorter._sorting_steps[0]
            step._sort_method_dropdown.value = SORT_METHOD.AVG_VALUE_SORT.value
            step._attribute_dropdown.value = DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value
            result = sorter.get_sorted_datasets(included)
            assert len(result) == len(included)

    def test_sample_spot_filter_then_value_extraction(self, positive_uniform_datasets: List[Any]):
        sample_spot_filter = SampleSpotFilter()
        sample_map, spot_map = sample_spot_filter.get_filter_maps(
            positive_uniform_datasets,
            attribute=DATASET_ATTRIBUTE.ADJUSTED_AVERAGE,
            min_threshold=0.0,
            max_threshold=10000.0,
        )
        values = get_flat_value_list(positive_uniform_datasets[0], DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert len(values) > 0
