import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets
import numpy as np
from suplex_modules.submodules.dataset_filters import *
from suplex_modules.submodules.submodule_constants import FILTER_METHOD, DATASET_ATTRIBUTE

class TestDatasetFiltersFunctions:
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
        """Test contains value above."""
        assert contains_value_above([100, 200], 150)
        assert not contains_value_above([100, 140], 150)

    def test_contains_value_below(self):
        """Test contains value below."""
        assert contains_value_below([100, 200], 150)
        assert not contains_value_below([160, 200], 150)

    def test_is_avg_value_above(self):
        """Test avg value above."""
        assert not is_avg_value_above([100, 200], 150) # Avg=150 ==150, False
        assert is_avg_value_above([160, 200], 150)

    # Similar tests for the other functions: is_avg_below, max_above/below, min_above/below
    def test_is_avg_value_below(self):
        """Test avg value below."""
        assert not is_avg_value_below([100, 200], 150) # Avg=150 ==150, False
        assert is_avg_value_below([100, 140], 150)

    def test_is_max_value_above(self):
        """Test max value above."""
        assert is_max_value_above([100, 200], 150)  # Max=200 >150
        assert not is_max_value_above([100, 140], 150)
        
    def test_is_max_value_below(self):
        """Test max value below."""
        assert not is_max_value_below([100, 200], 150)  # Max=200 >150
        assert is_max_value_below([100, 140], 150)

    def test_is_min_value_above(self):
        """Test min value above."""
        assert not is_min_value_above([100, 200], 150)  # Min=100 <150
        assert is_min_value_above([160, 200], 150)

    def test_is_min_value_below(self):
        """Test min value below."""
        assert is_min_value_below([100, 200], 150) # Min=100 <150
        assert not is_min_value_below([160, 200], 150)

class TestDatasetFilter:
    def test_init(self):
        """Test instantiation."""
        filter_obj = DatasetFilter()
        assert filter_obj.method == FILTER_METHOD.MEAN_MAX_RATIO
        assert filter_obj.attribute == DATASET_ATTRIBUTE.MEAN
        assert filter_obj.threshold == 0.5
        assert not filter_obj._invert_checkbox.value

    def test_get_ui(self):
        """Test UI creation."""
        filter_obj = DatasetFilter()
        ui = filter_obj.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_update_threshold_range(self):
        """Test update of threshold range."""
        filter_obj = DatasetFilter()
        filter_obj._method_dropdown.value = FILTER_METHOD.LOW_VARIANCE.value
        filter_obj.on_filter_changed([], method=FILTER_METHOD.LOW_VARIANCE)
        assert filter_obj._threshold_slider.min == 0
        assert filter_obj._threshold_slider.max == 1

    def test_get_filtered_datasets(self, mock_datasets):
        """Test filtered datasets."""
        filter_obj = DatasetFilter(default_method=FILTER_METHOD.MEAN_MAX_RATIO, default_threshold=0.5, default_attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        with patch("suplex_modules.submodules.dataset_filters.get_flat_value_list", return_value=[100, 200]):
            included, excluded = filter_obj.get_filtered_datasets(mock_datasets)
            assert len(included) == 0
            assert len(excluded) > 0
            # mock datasets uses copies of the same mock dataset which has the same values for all its samples - naturally this leads to a flat distribution of values.