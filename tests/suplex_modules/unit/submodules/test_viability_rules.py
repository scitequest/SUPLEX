import pytest
from unittest.mock import Mock

from suplex_modules.submodules.viability_rules import (
    no_datasets_selected,
    has_insufficient_number_of_datasets,
    has_insufficient_number_of_samples,
    has_insufficient_number_of_spots,
    missing_metadata,
    missing_parameters,
    sample_count_not_uniform,
    spot_count_is_not_uniform,
    spot_shapes_inconsistent,
    has_inconsistent_imaging_parameters,
    has_inconsistent_incubation_parameters,
    has_negative_data_values,
    has_negative_data_statistics_values,
    has_negative_spot_coordinates,
    has_negative_values,
)


class TestViabilityRules:
    """Tests for all viability check functions (return True = rule violated)."""

    # -------------------------------------------------------------------------
    # Basic viability checks
    # -------------------------------------------------------------------------

    def test_no_datasets_selected(self):
        """No datasets selected should return True (violated)."""
        assert no_datasets_selected([]) is True
        assert no_datasets_selected([Mock()]) is False

    def test_has_insufficient_number_of_datasets(self, viable_datasets):
        """Check minimum number of datasets."""
        assert has_insufficient_number_of_datasets(viable_datasets, min_count=2) is False
        assert has_insufficient_number_of_datasets(viable_datasets[:1], min_count=2) is True

    def test_has_insufficient_number_of_samples(self, viable_datasets, datasets_with_issues):
        """Check minimum number of samples per dataset."""
        assert has_insufficient_number_of_samples(viable_datasets, min_count=1) is False
        assert has_insufficient_number_of_samples(datasets_with_issues, min_count=2) is True

    def test_has_insufficient_number_of_spots(self, viable_datasets, datasets_with_issues):
        """Check minimum number of spots per sample."""
        assert has_insufficient_number_of_spots(viable_datasets, min_count=2) is False
        assert has_insufficient_number_of_spots(datasets_with_issues, min_count=2) is True

    def test_missing_metadata(self, viable_datasets, datasets_with_issues):
        """Missing metadata should be detected."""
        assert missing_metadata(viable_datasets) is False
        assert missing_metadata(datasets_with_issues) is True

    def test_missing_parameters(self, viable_datasets, datasets_with_issues):
        """Missing parameters file should be detected."""
        assert missing_parameters(viable_datasets) is False
        assert missing_parameters(datasets_with_issues) is True

    def test_sample_count_not_uniform(self, viable_datasets):
        """Sample count must be the same across all datasets."""
        assert sample_count_not_uniform(viable_datasets) is False

        ds1 = Mock(samples=[Mock()] * 3)
        ds2 = Mock(samples=[Mock()] * 5)
        assert sample_count_not_uniform([ds1, ds2]) is True

    def test_spot_count_is_not_uniform(self, viable_datasets):
        """Spot count must be uniform within each dataset."""
        assert spot_count_is_not_uniform(viable_datasets) is False

        ds = Mock(samples=[Mock(spots=[Mock()] * 4), Mock(spots=[Mock()] * 2)])
        assert spot_count_is_not_uniform([ds]) is True

    def test_spot_shapes_inconsistent(self):
        """All spots in a dataset must have the same shape."""
        # Consistent case - all CIRCLE
        spot_consistent = Mock()
        spot_consistent.shape = "CIRCLE"
        sample_consistent = Mock()
        sample_consistent.spots = [spot_consistent] * 3
        ds_consistent = Mock()
        ds_consistent.samples = [sample_consistent]

        assert spot_shapes_inconsistent([ds_consistent]) is False

        # Inconsistent case - mixed CIRCLE and POLYGON
        spot_circle = Mock()
        spot_circle.shape = "CIRCLE"
        spot_polygon = Mock()
        spot_polygon.shape = "POLYGON"
        sample_inconsistent = Mock()
        sample_inconsistent.spots = [spot_circle, spot_polygon]
        ds_inconsistent = Mock()
        ds_inconsistent.samples = [sample_inconsistent]

        assert spot_shapes_inconsistent([ds_inconsistent]) is True

    # -------------------------------------------------------------------------
    # Inconsistent parameters
    # -------------------------------------------------------------------------

    def test_has_inconsistent_incubation_parameters(self, viable_datasets, datasets_with_issues):
        """Incubation parameters must be identical across datasets."""
        # Configure mocks for incubation parameters
        common_incub = Mock()
        common_incub.solution = "Buffer"
        common_incub.stock_concentration = Mock(value=100.0, unit="nM")
        common_incub.final_concentration = Mock(value=10.0, unit="nM")
        common_incub.incubation_time = 60

        diff_incub = Mock()
        diff_incub.solution = "DiffBuffer"
        diff_incub.stock_concentration = Mock(value=50.0, unit="nM")
        diff_incub.final_concentration = Mock(value=5.0, unit="nM")
        diff_incub.incubation_time = 30

        # Viable: all same
        for dataset in viable_datasets:
            dataset.metadata = Mock()
            dataset.metadata.incubations = [common_incub]

        # Issues: inconsistent across datasets
        for i, dataset in enumerate(datasets_with_issues):
            dataset.metadata = Mock()
            if i == 0:
                dataset.metadata.incubations = [common_incub]
            else:
                dataset.metadata.incubations = [diff_incub]

        assert has_inconsistent_incubation_parameters(viable_datasets) is False
        assert has_inconsistent_incubation_parameters(datasets_with_issues) is True

    # -------------------------------------------------------------------------
    # Negative value checks
    # -------------------------------------------------------------------------

    def test_has_negative_data_values(self, viable_datasets, datasets_with_issues):
        """Negative values in spot data should be detected."""
        # Configure positive values for viable
        for dataset in viable_datasets:
            for sample in dataset.samples:
                for spot in sample.spots:
                    spot.mean_minus_min = 5.0
                    spot.normalized_mean = 0.8
                    spot.min_val = 1.0
                    spot.max_val = 10.0
                    spot.mean_val = 5.0
                    spot.std_deviation = 1.0

        # Negative in issues
        for dataset in datasets_with_issues:
            for sample in dataset.samples:
                for spot in sample.spots:
                    spot.mean_minus_min = -0.1
                    break

        assert has_negative_data_values(viable_datasets) is False
        assert has_negative_data_values(datasets_with_issues) is True

    def test_has_negative_data_statistics_values(self, viable_datasets, datasets_with_issues):
        """Negative values in data_statistics should be detected."""
        # Configure for viable
        for dataset in viable_datasets:
            for sample in dataset.samples:
                sample.data_statistics = Mock()
                stats = sample.data_statistics
                stats.row = 1
                stats.col = 1
                stats.adjusted_average = 5.0
                stats.adjusted_average_std_deviation = 1.0
                stats.relative_adjusted_average_std_deviation = 20.0
                stats.normalized_average = 0.8
                stats.normalized_average_std_deviation = 0.1
                stats.relative_normalized_average_std_deviation = 12.5

        # Issues with negative
        for dataset in datasets_with_issues:
            for sample in dataset.samples:
                sample.data_statistics = Mock()
                stats = sample.data_statistics
                stats.row = 1
                stats.col = 1
                stats.adjusted_average = 5.0
                stats.adjusted_average_std_deviation = 1.0
                stats.relative_adjusted_average_std_deviation = 20.0
                stats.normalized_average = 0.8
                stats.normalized_average_std_deviation = 0.1
                stats.relative_normalized_average_std_deviation = 12.5
                stats.adjusted_average = -1.0  # trigger
                break

        assert has_negative_data_statistics_values(viable_datasets) is False
        assert has_negative_data_statistics_values(datasets_with_issues) is True

    def test_has_negative_spot_coordinates(self, viable_datasets, datasets_with_issues):
        """Negative coordinates should be detected."""
        # Viable: positive coords
        for dataset in viable_datasets:
            for sample in dataset.samples:
                for spot in sample.spots:
                    coord = Mock()
                    coord.x = 10.0
                    coord.y = 20.0
                    spot.coordinates = [coord]

        # Issues: negative
        for dataset in datasets_with_issues:
            for sample in dataset.samples:
                for spot in sample.spots:
                    coord = Mock()
                    coord.x = -5.0
                    coord.y = 10.0
                    spot.coordinates = [coord]
                    break

        assert has_negative_spot_coordinates(viable_datasets) is False
        assert has_negative_spot_coordinates(datasets_with_issues) is True

    def test_has_negative_values_combined(self, viable_datasets, datasets_with_issues):
        """Combined negative value check (data + statistics + coordinates)."""
        # positive viable
        for dataset in viable_datasets:
            for sample in dataset.samples:
                for spot in sample.spots:
                    spot.mean_minus_min = 5.0
                    spot.normalized_mean = 0.8
                    spot.min_val = 1.0
                    spot.max_val = 10.0
                    spot.mean_val = 5.0
                    spot.std_deviation = 1.0
                    coord = Mock()
                    coord.x = 10.0
                    coord.y = 20.0
                    spot.coordinates = [coord]
                sample.data_statistics = Mock()
                stats = sample.data_statistics
                stats.row = 1
                stats.col = 1
                stats.adjusted_average = 5.0
                stats.adjusted_average_std_deviation = 1.0
                stats.relative_adjusted_average_std_deviation = 20.0
                stats.normalized_average = 0.8
                stats.normalized_average_std_deviation = 0.1
                stats.relative_normalized_average_std_deviation = 12.5

        # negative in issues (one type sufficient)
        for dataset in datasets_with_issues:
            for sample in dataset.samples:
                for spot in sample.spots:
                    spot.mean_minus_min = -0.1
                    break

        assert has_negative_values(viable_datasets) is False
        assert has_negative_values(datasets_with_issues) is True

    # -------------------------------------------------------------------------
    # Empty list safety
    # -------------------------------------------------------------------------

    def test_all_rules_with_empty_list(self):
        """All rules should safely handle empty dataset list."""
        empty = []
        assert no_datasets_selected(empty) is True
        assert has_insufficient_number_of_datasets(empty) is True
        assert has_insufficient_number_of_samples(empty) is False
        assert has_insufficient_number_of_spots(empty) is False
        assert missing_metadata(empty) is False
        assert missing_parameters(empty) is False
        assert sample_count_not_uniform(empty) is True
        assert spot_count_is_not_uniform(empty) is False
        assert spot_shapes_inconsistent(empty) is False
        assert has_inconsistent_imaging_parameters(empty) is False
        assert has_inconsistent_incubation_parameters(empty) is True
        assert has_negative_values(empty) is False
