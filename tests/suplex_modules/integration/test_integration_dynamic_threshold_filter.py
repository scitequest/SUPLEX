import pytest
from typing import List, Any

from suplex.suplex_modules.submodules.dynamic_threshold_filter import (
    apply_dynamic_filtering,
    FilteredValue,
)
from suplex.suplex_modules.submodules.submodule_constants import DATASET_ATTRIBUTE


# =============================================================================
# Integration tests for dynamic statistical thresholding
# These tests verify the current apply_dynamic_filtering implementation
# (delta grouping + sparsity cutoff) on realistic FakeDataset distributions.
# =============================================================================


class TestIntegrationDynamicThresholdFilter:
    """Integration tests for the dynamic statistical threshold filter."""

    # -------------------------------------------------------------------------
    # Basic functionality
    # -------------------------------------------------------------------------

    def test_apply_dynamic_filtering_on_uniform_data(
        self, positive_uniform_datasets: List[Any]
    ) -> None:
        """Pipeline should run end-to-end on real FakeDataset objects and return correct types."""
        dataset = positive_uniform_datasets[0]
        from suplex.suplex_modules.submodules.value_extractor import get_flat_value_list

        values = get_flat_value_list(dataset, attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN)

        result = apply_dynamic_filtering(
            values,
            use_broad_grouping=True,
            alpha=0.05,
            max_relevant_fraction=0.8,
        )

        assert isinstance(result, list)
        assert all(isinstance(item, FilteredValue) for item in result)
        assert len(result) > 0

    def test_apply_dynamic_filtering_with_narrow_grouping(
        self, positive_uniform_datasets: List[Any]
    ) -> None:
        """Alternative grouping strategy should also run without error."""
        dataset = positive_uniform_datasets[0]
        from suplex.suplex_modules.submodules.value_extractor import get_flat_value_list

        values = get_flat_value_list(dataset, attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN)

        result = apply_dynamic_filtering(
            values,
            use_broad_grouping=False,
            alpha=0.05,
            max_relevant_fraction=0.5,
        )

        assert isinstance(result, list)
        assert len(result) > 0

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------

    def test_dynamic_filtering_on_empty_list(self) -> None:
        """Filter should handle empty input gracefully."""
        result = apply_dynamic_filtering([])
        assert result == []

    def test_dynamic_filtering_on_single_value(self) -> None:
        """Single value input should not crash."""
        result = apply_dynamic_filtering([42.0])
        assert isinstance(result, list)
        assert len(result) == 1

    def test_dynamic_filtering_on_negative_values(self, negative_value_dataset: Any) -> None:
        """Filter should still process datasets containing negatives."""
        from suplex.suplex_modules.submodules.value_extractor import get_flat_value_list

        values = get_flat_value_list(
            negative_value_dataset, attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN
        )

        result = apply_dynamic_filtering(
            values,
            use_broad_grouping=True,
            alpha=0.05,
            max_relevant_fraction=0.5,
        )
        assert isinstance(result, list)

    # -------------------------------------------------------------------------
    # FilteredValue dataclass
    # -------------------------------------------------------------------------

    def test_filtered_value_dataclass(self) -> None:
        """FilteredValue should behave as expected (current fields)."""
        fv = FilteredValue(VALUE=123.4, DELTA=15.0, GROUP_NR=2, SIGNIFICANT=True)
        assert fv.VALUE == 123.4
        assert fv.DELTA == 15.0
        assert fv.GROUP_NR == 2
        assert fv.SIGNIFICANT is True

        # Frozen dataclass → immutable
        with pytest.raises(AttributeError):
            fv.VALUE = 999
