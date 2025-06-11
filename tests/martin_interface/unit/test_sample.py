import pytest
from src.martin_interface.sample import Sample, DataStatistics
from src.martin_interface.roi_elements import Spot, SpotValues, RoiParameters, Coordinates
from dataclasses import is_dataclass

class TestSample:
    def test_data_statistics_creation(self, sample_data_statistics_dict):
        stats_data = sample_data_statistics_dict["values"][0]
        
        stats = DataStatistics(
            row=stats_data["row"],
            col=stats_data["col"],
            adjusted_average=stats_data["adjusted_average"],
            adjusted_average_std_deviation=stats_data["adjusted_average_std_deviation"],
            relative_adjusted_average_std_deviation=stats_data["relative_adjusted_average_std_deviation"],
            normalized_average=stats_data["normalized_average"],
            normalized_average_std_deviation=stats_data["normalized_average_std_deviation"],
            relative_normalized_average_std_deviation=stats_data["relative_normalized_average_std_deviation"]
        )
        
        assert is_dataclass(stats)
        assert stats.row == stats_data["row"]
        assert stats.col == stats_data["col"]
        assert stats.adjusted_average == stats_data["adjusted_average"]
        assert stats.adjusted_average_std_deviation == stats_data["adjusted_average_std_deviation"]
        assert stats.relative_adjusted_average_std_deviation == stats_data["relative_adjusted_average_std_deviation"]
        assert stats.normalized_average == stats_data["normalized_average"]
        assert stats.normalized_average_std_deviation == stats_data["normalized_average_std_deviation"]
        assert stats.relative_normalized_average_std_deviation == stats_data["relative_normalized_average_std_deviation"]
        
    def test_sample_creation_basic(self, sample_data_dict):
        spots_data = [sample_data_dict["values"][0]]
        spot_data = spots_data[0]
        
        sample = Sample(spots=spots_data, spot_statistics=None, parameters=None)
        
        assert len(sample.spots) == 1
        assert sample.spots[0].mean_minus_min == spot_data["mean_minus_min"]
        assert sample.spots[0].normalized_mean == spot_data["normalized_mean"]
        assert sample.spots[0].spot == spot_data["spot"]
        assert sample.spots[0].row == spot_data["row"]
        assert sample.spots[0].col == spot_data["col"]
        assert sample.spots[0].min_val == spot_data["min"]
        assert sample.spots[0].max_val == spot_data["max"]
        assert sample.spots[0].mean_val == spot_data["mean"]
        assert sample.spots[0].std_deviation == spot_data["std_deviation"]
        assert sample.data_statistics is None
        assert sample.spots[0].spot_parameters is None

    def test_init_spots_multiple_spots(self, sample_data_dict):
        spots_data = sample_data_dict["values"][:2]
        
        sample = Sample(spots=spots_data, spot_statistics=None, parameters=None)
        
        assert len(sample.spots) == 2

        # Check first spot
        spot_0_data = spots_data[0]
        assert sample.spots[0].mean_minus_min == spot_0_data["mean_minus_min"]
        assert sample.spots[0].normalized_mean == spot_0_data["normalized_mean"]
        assert sample.spots[0].spot == spot_0_data["spot"]
        assert sample.spots[0].row == spot_0_data["row"]
        assert sample.spots[0].col == spot_0_data["col"]
        assert sample.spots[0].min_val == spot_0_data["min"]
        assert sample.spots[0].max_val == spot_0_data["max"]
        assert sample.spots[0].mean_val == spot_0_data["mean"]
        assert sample.spots[0].std_deviation == spot_0_data["std_deviation"]
        assert sample.spots[0].spot_parameters is None
 
        # Check second spot
        spot_1_data = spots_data[1]
        assert sample.spots[1].mean_minus_min == spot_1_data["mean_minus_min"]
        assert sample.spots[1].normalized_mean == spot_1_data["normalized_mean"]
        assert sample.spots[1].spot == spot_1_data["spot"]
        assert sample.spots[1].row == spot_1_data["row"]
        assert sample.spots[1].col == spot_1_data["col"]
        assert sample.spots[1].min_val == spot_1_data["min"]
        assert sample.spots[1].max_val == spot_1_data["max"]
        assert sample.spots[1].mean_val == spot_1_data["mean"]
        assert sample.spots[1].std_deviation == spot_1_data["std_deviation"]
        assert sample.spots[1].spot_parameters is None

        assert sample.data_statistics is None
        
    def test_sample_creation_with_statistics_and_parameters(self, sample_data_dict, 
                                                          sample_data_statistics_dict, 
                                                          sample_parameters_dict_polygon):
        spots_data = sample_data_dict["values"][:2]  # Take first two spots
        stats_data = sample_data_statistics_dict["values"][0]  # Take first statistics entry
        parameters_data = sample_parameters_dict_polygon["spots"][:2]  # Take first two parameters
        
        sample = Sample(spots=spots_data, spot_statistics=stats_data, parameters=parameters_data)

        # Check data statistics
        assert sample.data_statistics is not None
        assert isinstance(sample.data_statistics, DataStatistics)
        assert sample.data_statistics.row == stats_data["row"]
        assert sample.data_statistics.col == stats_data["col"]
        assert sample.data_statistics.adjusted_average == stats_data["adjusted_average"]
        assert sample.data_statistics.adjusted_average_std_deviation == stats_data["adjusted_average_std_deviation"]
        assert sample.data_statistics.relative_adjusted_average_std_deviation == stats_data["relative_adjusted_average_std_deviation"]
        assert sample.data_statistics.normalized_average == stats_data["normalized_average"]
        assert sample.data_statistics.normalized_average_std_deviation == stats_data["normalized_average_std_deviation"]
        assert sample.data_statistics.relative_normalized_average_std_deviation == stats_data["relative_normalized_average_std_deviation"]
        
        # Check spot parameters for both spots
        for i, param_data in enumerate(parameters_data):
            assert sample.spots[i].spot_parameters is not None
            assert isinstance(sample.spots[i].spot_parameters, RoiParameters)
            assert sample.spots[i].shape == param_data["type"]
            assert len(sample.spots[i].coordinates) == len(param_data["coordinates"])
            assert sample.spots[i].diameter is None
    
    def test_init_spots_circle_parameters(self, sample_data_dict, sample_parameters_dict_circle):
        spots_data = [sample_data_dict["values"][0]]  # Take first spot
        parameters_data = [sample_parameters_dict_circle["spots"][0]]  # Take first circular parameter
        param_data = parameters_data[0]
        
        sample = Sample(spots=spots_data, spot_statistics=None, parameters=parameters_data)
        
        assert sample.spots[0].spot_parameters is not None
        assert sample.spots[0].shape == param_data["type"]
        assert len(sample.spots[0].coordinates) == 1
        assert sample.spots[0].diameter == param_data["diameter"]