import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets
import numpy as np

from suplex_modules.submodules.dataset_filters import (
    has_flat_distribution,
    has_low_variance,
    contains_value_above,
    contains_value_below,
    is_avg_value_above,
    is_avg_value_below,
    is_max_value_above,
    is_max_value_below,
    is_min_value_above,
    is_min_value_below,
    DatasetFilter,
)
from suplex_modules.submodules.submodule_constants import (
    FILTER_METHOD,
    DATASET_ATTRIBUTE,
)


class TestDatasetFiltersFunctions:
    """Unit tests for the pure helper functions used by DatasetFilter."""

    def test_has_flat_distribution(self):
        """Test flat distribution check."""
        assert has_flat_distribution([100, 200, 150], 0.5)  # Avg/Max = 150/200 = 0.75 > 0.5
        assert has_flat_distribution([100, 100, 100], 0.5)
        assert has_flat_distribution([0, 0], 0.5)
        assert not has_flat_distribution([-100, 200], 0.5)  # Avg=50/Max=200=0.25 < 0.5

    def test_has_low_variance(self):
        """Test low variance check."""
        assert has_low_variance([1, 2, 3], 1.0)
        assert not has_low_variance([1, 1, 1], 0)
        assert has_low_variance([], 1)

    def test_contains_value_above(self):
        """Test contains value above threshold."""
        assert contains_value_above([100, 200], 150)
        assert not contains_value_above([100, 140], 150)

    def test_contains_value_below(self):
        """Test contains value below threshold."""
        assert contains_value_below([100, 200], 150)
        assert not contains_value_below([160, 200], 150)

    def test_is_avg_value_above(self):
        """Test average value above threshold."""
        assert not is_avg_value_above([100, 200], 150)  # Avg=150 == 150 → False
        assert is_avg_value_above([160, 200], 150)

    def test_is_avg_value_below(self):
        """Test average value below threshold."""
        assert not is_avg_value_below([100, 200], 150)  # Avg=150 == 150 → False
        assert is_avg_value_below([100, 140], 150)

    def test_is_max_value_above(self):
        """Test max value above threshold."""
        assert is_max_value_above([100, 200], 150)
        assert not is_max_value_above([100, 140], 150)

    def test_is_max_value_below(self):
        """Test max value below threshold."""
        assert not is_max_value_below([100, 200], 150)
        assert is_max_value_below([100, 140], 150)

    def test_is_min_value_above(self):
        """Test min value above threshold."""
        assert not is_min_value_above([100, 200], 150)
        assert is_min_value_above([160, 200], 150)

    def test_is_min_value_below(self):
        """Test min value below threshold."""
        assert is_min_value_below([100, 200], 150)
        assert not is_min_value_below([160, 200], 150)


class TestDatasetFilter:
    """Tests for the DatasetFilter class (UI + filtering logic)."""

    def test_init(self):
        """Test instantiation with default values."""
        filter_obj = DatasetFilter()
        assert filter_obj.attribute == DATASET_ATTRIBUTE.MEAN_MINUS_MIN
        assert filter_obj.method == FILTER_METHOD.MEAN_MAX_RATIO
        assert filter_obj.threshold == 0.5
        assert not filter_obj._invert_checkbox.value

    def test_get_ui(self):
        """Test UI creation."""
        filter_obj = DatasetFilter()
        ui = filter_obj.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_update_threshold_range(self):
        """Test dynamic update of threshold range based on method."""
        filter_obj = DatasetFilter()
        filter_obj._method_dropdown.value = FILTER_METHOD.LOW_VARIANCE.value
        filter_obj.on_filter_changed([], method=FILTER_METHOD.LOW_VARIANCE)
        assert filter_obj._threshold_slider.min == 0
        assert filter_obj._threshold_slider.max == 1

    def test_get_filtered_datasets(self, mock_datasets):
        """Test filtered datasets (basic case)."""
        filter_obj = DatasetFilter(
            default_method=FILTER_METHOD.MEAN_MAX_RATIO,
            default_threshold=0.5,
        )
        with patch(
            "suplex_modules.submodules.dataset_filters.get_flat_value_list",
            return_value=[100, 200],
        ):
            included, excluded = filter_obj.get_filtered_datasets(mock_datasets)
            assert len(included) == 0
            assert len(excluded) > 0

    def test_on_filter_changed_mean_max_ratio(self, mock_datasets):
        """MEAN_MAX_RATIO should always be in a 0–1 range."""
        filter_obj = DatasetFilter()
        filter_obj.on_filter_changed(mock_datasets, method=FILTER_METHOD.MEAN_MAX_RATIO)

        assert filter_obj._threshold_slider.min == 0
        assert filter_obj._threshold_slider.max == 1

    def test_on_filter_changed_low_variance(self, mock_datasets):
        """LOW_VARIANCE should use value as upper limit."""
        filter_obj = DatasetFilter()
        filter_obj.on_filter_changed(mock_datasets, method=FILTER_METHOD.LOW_VARIANCE)

        assert filter_obj._threshold_slider.min == 0
        assert filter_obj._threshold_slider.max >= 0

    def test_on_filter_changed_avg_above(self, mock_datasets):
        """AVG_ABOVE should use value as upper limit."""
        filter_obj = DatasetFilter()
        filter_obj.on_filter_changed(mock_datasets, method=FILTER_METHOD.AVG_ABOVE)

        assert filter_obj._threshold_slider.min == 0
        assert filter_obj._threshold_slider.max > 0

    def test_on_filter_changed_contains_above(self, mock_datasets):
        """CONTAINS_ABOVE should use value as upper limit."""
        filter_obj = DatasetFilter()
        filter_obj.on_filter_changed(mock_datasets, method=FILTER_METHOD.CONTAINS_ABOVE)

        assert filter_obj._threshold_slider.min == 0
        assert filter_obj._threshold_slider.max > 0

    def test_get_filtered_datasets_invert(self, mock_datasets):
        """Test invert logic: swapping included and excluded."""
        filter_obj = DatasetFilter(
            default_method=FILTER_METHOD.MEAN_MAX_RATIO,
            default_threshold=0.5,
        )

        with patch(
            "suplex_modules.submodules.dataset_filters.get_flat_value_list",
            return_value=[100, 200],
        ):
            included, excluded = filter_obj.get_filtered_datasets(mock_datasets)
            # without invert
            assert len(included) == 0
            assert len(excluded) == 2

            # with invert
            filter_obj._invert_checkbox.value = True
            included_inv, excluded_inv = filter_obj.get_filtered_datasets(mock_datasets)
            assert len(included_inv) == 2
            assert len(excluded_inv) == 0

    def test_get_filtered_datasets_empty_list(self):
        """Handling of empty dataset list."""
        filter_obj = DatasetFilter()
        included, excluded = filter_obj.get_filtered_datasets([])
        assert included == []
        assert excluded == []

    def test_get_filtered_datasets_no_values(self, mock_datasets):
        """Excluding datasets without values."""
        filter_obj = DatasetFilter()

        with patch(
            "suplex_modules.submodules.dataset_filters.get_flat_value_list",
            return_value=[],
        ):
            included, excluded = filter_obj.get_filtered_datasets(mock_datasets)
            assert len(included) == 0
            assert len(excluded) == len(mock_datasets)
