import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets
from suplex_modules.submodules.sample_spot_filter import *
from suplex_modules.submodules.submodule_constants import THRESHOLD_FILTER_STATE, NORMALIZATION, DATASET_ATTRIBUTE, SELECTION_MODE

class TestSampleSpotFilterFunctions:
    def test_get_sample_threshold_map(self):
        """Test sample threshold map."""
        mock1 = Mock(spec=Dataset)
        mock2 = Mock(spec=Dataset)
        mock_datasets = [mock1, mock2]
        with patch('suplex_modules.submodules.sample_spot_filter.get_normalization_factors', return_value=[1.0, 1.0]):
            with patch('suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset', side_effect=[[100, 200], [50, 150]]):
                map_ = get_sample_threshold_map(mock_datasets, DATASET_ATTRIBUTE.ADJUSTED_AVERAGE, 50, 150, NORMALIZATION.RAW, 1.0)
                assert len(map_) == len(mock_datasets)
                assert map_[mock_datasets[0]][0] == THRESHOLD_FILTER_STATE.WITHIN_RANGE  # Example

    def test_get_spot_threshold_map(self):
        """Test spot threshold map."""
        mock1 = Mock(spec=Dataset)
        mock2 = Mock(spec=Dataset)
        mock_datasets = [mock1, mock2]
        with patch('suplex_modules.submodules.sample_spot_filter.get_normalization_factors', return_value=[1.0, 1.0]):
            with patch('suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset', side_effect=[[[10,20,30],[40,50,60]], [[70,80,90],[100,110,120]]]):
                map_ = get_spot_threshold_map(mock_datasets, DATASET_ATTRIBUTE.MEAN_MINUS_MIN, 50, 150, NORMALIZATION.RAW, 1.0)
                assert len(map_) == len(mock_datasets)

    def test_aggregate_filter_states_any(self):
        """Test aggregate any."""
        states = [[THRESHOLD_FILTER_STATE.BELOW_RANGE, THRESHOLD_FILTER_STATE.WITHIN_RANGE]]
        agg = aggregate_filter_states_any(states[0])
        assert agg == THRESHOLD_FILTER_STATE.WITHIN_RANGE

    def test_aggregate_filter_states_all(self):
        """Test aggregate all."""
        states = [[THRESHOLD_FILTER_STATE.WITHIN_RANGE, THRESHOLD_FILTER_STATE.WITHIN_RANGE]]
        agg = aggregate_filter_states_all(states[0])
        assert agg == THRESHOLD_FILTER_STATE.WITHIN_RANGE

class TestSampleSpotFilter:
    def test_init(self):
        """Test init."""
        filter_obj = SampleSpotFilter()
        assert filter_obj.attribute == DATASET_ATTRIBUTE.ADJUSTED_AVERAGE
        assert filter_obj.normalization_method == NORMALIZATION.RAW
        assert filter_obj.min_threshold == 0
        assert filter_obj.max_threshold == 65535

    def test_get_ui(self):
        """Test UI."""
        filter_obj = SampleSpotFilter()
        ui = filter_obj.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_get_filter_maps(self):
        """Test filter maps."""
        mock1 = Mock(spec=Dataset)
        mock2 = Mock(spec=Dataset)
        mock_datasets = [mock1, mock2]
        with patch('suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset', side_effect=[[100, 200], [50, 150]]):
            with patch('suplex_modules.submodules.sample_spot_filter.get_normalization_factors', return_value=[1.0, 1.0]):
                filter_obj = SampleSpotFilter()
                sample_map, spot_map = filter_obj.get_filter_maps(mock_datasets)
                assert len(sample_map) == len(mock_datasets)
                assert len(spot_map) == len(mock_datasets)