import math

import pytest

from suplex.suplex_modules.submodules.dynamic_threshold_filter import (
    FilteredValue,
    apply_adaptive_significance_cutoff,
    apply_dynamic_filtering,
    apply_sparsity_cutoff,
    calculate_incremental_deltas,
    group_by_delta_contrast,
)


class TestCalculateIncrementalDeltas:
    """Tests for the calculate_incremental_deltas helper."""

    def test_calculate_incremental_deltas_normal_case(self, sample_value_list):
        """Delta calculation: smallest value = itself, others = difference to previous in sorted order."""
        deltas = calculate_incremental_deltas(sample_value_list)
        assert len(deltas) == len(sample_value_list)
        assert deltas[sample_value_list.index(10.0)] == 10.0  # smallest
        assert deltas[sample_value_list.index(25.0)] == 15.0  # 25-10
        assert deltas[sample_value_list.index(200.0)] == 80.0  # 200-120

    def test_calculate_incremental_deltas_empty(self):
        """Empty list should return empty list."""
        assert calculate_incremental_deltas([]) == []

    def test_calculate_incremental_deltas_single_value(self):
        """Single value should return itself."""
        deltas = calculate_incremental_deltas([42.0])
        assert deltas == [42.0]


class TestGroupByDeltaContrast:
    """Tests for the group_by_delta_contrast helper."""

    def test_group_by_delta_contrast_broad_grouping(self, sample_value_list):
        """Broad grouping (use_broad_grouping=True) uses lowest value at max delta."""
        deltas = calculate_incremental_deltas(sample_value_list)
        groups = group_by_delta_contrast(sample_value_list, deltas, use_broad_grouping=True)
        assert len(groups) == len(sample_value_list)
        assert groups.count(0) > 0  # highest group exists

    def test_group_by_delta_contrast_narrow_grouping(self, sample_value_list):
        """Narrow grouping uses highest value at max delta."""
        deltas = calculate_incremental_deltas(sample_value_list)
        groups = group_by_delta_contrast(sample_value_list, deltas, use_broad_grouping=False)
        assert len(groups) == len(sample_value_list)

    def test_group_by_delta_contrast_empty(self):
        """Empty inputs should return empty list."""
        assert group_by_delta_contrast([], []) == []

    def test_group_by_delta_contrast_mismatched_lengths(self):
        """Mismatched lengths should return empty list (graceful handling)."""
        groups = group_by_delta_contrast([1, 2], [10])
        assert groups == []


class TestApplySparsityCutoff:
    """Tests for the apply_sparsity_cutoff function."""

    def test_apply_sparsity_cutoff_basic(self, sample_value_list, mock_ks_2samp):
        """Sparsity cutoff with KS-merge."""
        mock_ks_2samp.return_value = (0.5, 0.8)  # high p-value → merge
        deltas = calculate_incremental_deltas(sample_value_list)
        groups = group_by_delta_contrast(sample_value_list, deltas)

        filtered = apply_sparsity_cutoff(
            sample_value_list, groups, max_relevant_fraction=0.5, alpha=0.05
        )
        assert len(filtered) == len(sample_value_list)
        # Some values should be NaN (non-significant)
        assert any(math.isnan(v) for v in filtered)

    def test_apply_sparsity_cutoff_small_non_sig_group(self, small_value_list, mock_ks_2samp):
        """Very small non-significant group → early break."""
        deltas = calculate_incremental_deltas(small_value_list)
        groups = group_by_delta_contrast(small_value_list, deltas)
        filtered = apply_sparsity_cutoff(small_value_list, groups, max_relevant_fraction=0.3)
        assert len([v for v in filtered if math.isnan(v)]) > 0

    def test_apply_sparsity_cutoff_mismatched_lengths(self):
        """Mismatched lengths should return all NaN."""
        filtered = apply_sparsity_cutoff([1, 2], [0])
        assert all(math.isnan(v) for v in filtered)


class TestApplyAdaptiveSignificanceCutoff:
    """Tests for the apply_adaptive_significance_cutoff function."""

    def test_apply_adaptive_significance_cutoff_normal_case(self, sample_value_list, mock_shapiro):
        """Adaptive cutoff with Shapiro + Z-test."""
        mock_shapiro.return_value = (0.0, 0.9)  # high p-value = normal
        deltas = calculate_incremental_deltas(sample_value_list)
        groups = group_by_delta_contrast(sample_value_list, deltas)

        filtered = apply_adaptive_significance_cutoff(sample_value_list, groups, alpha=0.05)
        assert len(filtered) == len(sample_value_list)
        assert any(math.isnan(v) for v in filtered)

    def test_apply_adaptive_significance_cutoff_fallback_all_insignificant(self, mock_shapiro):
        """No cutoff found → all NaN."""
        mock_shapiro.return_value = (0.0, 0.01)  # low p-value
        values = [10, 20, 30]
        deltas = calculate_incremental_deltas(values)
        groups = group_by_delta_contrast(values, deltas)
        filtered = apply_adaptive_significance_cutoff(values, groups)
        assert all(math.isnan(v) for v in filtered)

    def test_apply_adaptive_significance_cutoff_small_groups(self, small_value_list, mock_shapiro):
        """Small groups → combined list handling."""
        mock_shapiro.return_value = (0.0, 0.9)  # high p-value = normal

        deltas = calculate_incremental_deltas(small_value_list)
        groups = group_by_delta_contrast(small_value_list, deltas)
        filtered = apply_adaptive_significance_cutoff(small_value_list, groups)
        assert len(filtered) == len(small_value_list)


class TestApplyDynamicFiltering:
    """Tests for the main apply_dynamic_filtering wrapper."""

    def test_apply_dynamic_filtering_end_to_end(self, sample_value_list, mock_ks_2samp):
        """Main wrapper function – full pipeline."""
        mock_ks_2samp.return_value = (0.5, 0.9)  # merge possible
        result = apply_dynamic_filtering(
            sample_value_list, use_broad_grouping=True, alpha=0.05, max_relevant_fraction=0.5
        )

        assert len(result) == len(sample_value_list)
        assert all(isinstance(item, FilteredValue) for item in result)
        # At least some should be significant, some not
        assert any(item.SIGNIFICANT for item in result)
        assert any(not item.SIGNIFICANT for item in result)

    def test_apply_dynamic_filtering_empty_list(self):
        """Empty list should return empty list."""
        result = apply_dynamic_filtering([])
        assert result == []


class TestFilteredValue:
    """Tests for the FilteredValue dataclass."""

    def test_filtered_value_dataclass(self):
        """Dataclass is frozen and contains expected fields."""
        fv = FilteredValue(VALUE=100.5, DELTA=25.0, GROUP_NR=2, SIGNIFICANT=True)
        assert fv.VALUE == 100.5
        assert fv.DELTA == 25.0
        assert fv.GROUP_NR == 2
        assert fv.SIGNIFICANT is True

        # Frozen → immutable
        with pytest.raises(AttributeError):
            fv.VALUE = 999
