from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.martin_interface.dataset import Dataset
from suplex.suplex_modules.submodules.sample_spot_filter import (
    SampleSpotFilter,
    aggregate_filter_states_all,
    aggregate_filter_states_any,
    get_normalization_factors,
    get_sample_threshold_map,
    get_spot_threshold_map,
)
from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    NORMALIZATION,
    SELECTION_MODE,
    THRESHOLD_FILTER_STATE,
)


class TestSampleSpotFilterFunctions:
    """Unit tests for the pure helper functions in sample_spot_filter."""

    # -------------------------------------------------------------------------
    # Threshold map helpers
    # -------------------------------------------------------------------------

    def test_get_sample_threshold_map(self, mock_datasets):
        """Test sample threshold map with distinct mocks."""
        ds1 = Mock(spec=Dataset)
        ds2 = Mock(spec=Dataset)
        mock_datasets_local = [ds1, ds2]

        with (
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.get_normalization_factors",
                return_value=[1.0, 1.0],
            ),
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset",
                side_effect=[[100, 200], [50, 150]],
            ),
        ):
            threshold_map = get_sample_threshold_map(
                mock_datasets_local,
                DATASET_ATTRIBUTE.ADJUSTED_AVERAGE,
                min_threshold=75,
                max_threshold=175,
                normalization_method=NORMALIZATION.RAW,
                normalization_factor=1.0,
            )
            assert len(threshold_map) == len(mock_datasets_local)
            assert threshold_map[ds1] == [
                THRESHOLD_FILTER_STATE.WITHIN_RANGE,
                THRESHOLD_FILTER_STATE.ABOVE_RANGE,
            ]

    def test_get_spot_threshold_map(self, mock_datasets):
        """Test spot threshold map for regular numeric attributes."""
        ds1 = Mock(spec=Dataset)
        ds2 = Mock(spec=Dataset)
        mock_datasets_local = [ds1, ds2]

        with (
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.get_normalization_factors",
                return_value=[1.0, 1.0],
            ),
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset",
                side_effect=[[[10, 20, 30], [40, 50, 60]], [[70, 80, 90], [100, 110, 120]]],
            ),
        ):
            threshold_map = get_spot_threshold_map(
                mock_datasets_local,
                DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
                min_threshold=50,
                max_threshold=150,
                normalization_method=NORMALIZATION.RAW,
                normalization_factor=1.0,
            )
            assert len(threshold_map) == len(mock_datasets_local)

    def test_get_spot_threshold_map_coordinates(self, mock_datasets):
        """Test spot threshold map for coordinate attributes."""
        ds1 = Mock(spec=Dataset)
        ds2 = Mock(spec=Dataset)
        mock_datasets_local = [ds1, ds2]

        with (
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.get_normalization_factors",
                return_value=[1.0, 1.0],
            ),
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset",
                side_effect=[[[10, 20], [30, 40]], [[50, 60], [70, 80]]],
            ),
        ):
            threshold_map = get_spot_threshold_map(
                mock_datasets_local,
                DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
                min_threshold=25,
                max_threshold=55,
                normalization_method=NORMALIZATION.RAW,
                normalization_factor=1.0,
            )
            assert len(threshold_map) == len(mock_datasets_local)

    # -------------------------------------------------------------------------
    # Filter state aggregation
    # -------------------------------------------------------------------------

    def test_aggregate_filter_states_any(self):
        """ANY mode should return WITHIN_RANGE if at least one state matches."""
        states = [THRESHOLD_FILTER_STATE.BELOW_RANGE, THRESHOLD_FILTER_STATE.WITHIN_RANGE]
        assert aggregate_filter_states_any(states) == THRESHOLD_FILTER_STATE.WITHIN_RANGE

    def test_aggregate_filter_states_all(self):
        """ALL mode should return WITHIN_RANGE only if all states match."""
        states = [THRESHOLD_FILTER_STATE.WITHIN_RANGE] * 3
        assert aggregate_filter_states_all(states) == THRESHOLD_FILTER_STATE.WITHIN_RANGE

    def test_aggregate_filter_states_any_all_combinations(self):
        """Test all combinations of aggregate_filter_states_any / all."""
        states = [
            THRESHOLD_FILTER_STATE.WITHIN_RANGE,
            THRESHOLD_FILTER_STATE.BELOW_RANGE,
            THRESHOLD_FILTER_STATE.ABOVE_RANGE,
        ]
        assert aggregate_filter_states_any(states) == THRESHOLD_FILTER_STATE.WITHIN_RANGE
        assert (
            aggregate_filter_states_all([THRESHOLD_FILTER_STATE.WITHIN_RANGE] * 3)
            == THRESHOLD_FILTER_STATE.WITHIN_RANGE
        )
        assert (
            aggregate_filter_states_all(
                [THRESHOLD_FILTER_STATE.BELOW_RANGE, THRESHOLD_FILTER_STATE.ABOVE_RANGE]
            )
            == THRESHOLD_FILTER_STATE.OUTSIDE_RANGE
        )

    # -------------------------------------------------------------------------
    # Normalization factors
    # -------------------------------------------------------------------------

    def test_get_normalization_factors_raw(self, mock_datasets):
        """RAW normalization should return factor 1.0 for every dataset."""
        factors = get_normalization_factors(
            mock_datasets, DATASET_ATTRIBUTE.MEAN_MINUS_MIN, NORMALIZATION.RAW, 42.0
        )
        assert factors == [1.0] * len(mock_datasets)

    def test_get_normalization_factors_internal(self, mock_datasets):
        """INTERNAL normalization uses max value per dataset."""
        with patch(
            "suplex.suplex_modules.submodules.sample_spot_filter.get_flat_value_list",
            side_effect=[[100, 200], [50, 150]],
        ):
            factors = get_normalization_factors(
                mock_datasets, DATASET_ATTRIBUTE.MEAN_MINUS_MIN, NORMALIZATION.INTERNAL, 1.0
            )
            assert factors == [200.0, 150.0]

    def test_get_normalization_factors_global(self, mock_datasets):
        """GLOBAL normalization uses the overall maximum across all datasets."""
        with patch(
            "suplex.suplex_modules.submodules.sample_spot_filter.get_flat_value_list",
            side_effect=[[100, 200], [50, 150]],
        ):
            factors = get_normalization_factors(
                mock_datasets, DATASET_ATTRIBUTE.MEAN_MINUS_MIN, NORMALIZATION.GLOBAL, 1.0
            )
            assert factors == [200.0, 200.0]

    def test_get_normalization_factors_custom_zero(self, mock_datasets):
        """CUSTOM normalization with factor=0 should safely return 1.0."""
        factors = get_normalization_factors(
            mock_datasets, DATASET_ATTRIBUTE.MEAN_MINUS_MIN, NORMALIZATION.CUSTOM, 0.0
        )
        assert factors == [1.0] * len(mock_datasets)


class TestSampleSpotFilter:
    """Tests for the SampleSpotFilter class (UI + filter map logic)."""

    def test_init(self):
        """Test default initialization values."""
        filter_obj = SampleSpotFilter()
        assert filter_obj.attribute == DATASET_ATTRIBUTE.MEAN_MINUS_MIN
        assert filter_obj.normalization_method == NORMALIZATION.RAW
        assert filter_obj.min_threshold == 0
        assert filter_obj.max_threshold == 65535

    def test_get_ui(self):
        """Test UI creation."""
        filter_obj = SampleSpotFilter()
        ui = filter_obj.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_get_filter_maps(self, mock_dataset_for_extractor):
        """Basic test of get_filter_maps."""
        mock_datasets_local = [mock_dataset_for_extractor]
        filter_obj = SampleSpotFilter()
        sample_map, spot_map = filter_obj.get_filter_maps(mock_datasets_local)
        assert len(sample_map) == 1
        assert len(spot_map) == 1

    def test_get_filter_maps_propagation_both_directions_any(self, mock_dataset_for_extractor):
        """Test propagation logic when both sample ↔ spot checkboxes are enabled (ANY mode)."""
        mock_datasets_local = [mock_dataset_for_extractor]
        filter_obj = SampleSpotFilter()
        filter_obj._spots_affect_sample_checkbox.value = True
        filter_obj._sample_affects_spots_checkbox.value = True
        filter_obj._sample_filter_mode_dropdown.value = SELECTION_MODE.ANY.value

        with patch(
            "suplex.suplex_modules.submodules.sample_spot_filter.get_spot_threshold_map",
            return_value={
                mock_datasets_local[0]: [
                    [THRESHOLD_FILTER_STATE.WITHIN_RANGE, THRESHOLD_FILTER_STATE.BELOW_RANGE]
                ]
            },
        ):
            sample_map, _ = filter_obj.get_filter_maps(mock_datasets_local)
            assert sample_map[mock_datasets_local[0]] == [THRESHOLD_FILTER_STATE.WITHIN_RANGE]

    def test_extract_filtered_values_replacement_and_invert(self, mock_dataset_for_extractor):
        """Test replacement + invert logic on a spot-level attribute."""
        mock_datasets_local = [mock_dataset_for_extractor]

        filter_obj = SampleSpotFilter()
        filter_obj._invert_checkbox.value = True

        # Build a spot_threshold_map that matches the fixture:
        # 1 dataset → 2 samples → each sample has 3 spots
        spot_map = {
            mock_datasets_local[0]: [
                [THRESHOLD_FILTER_STATE.BELOW_RANGE] * 3,  # sample 0
                [THRESHOLD_FILTER_STATE.BELOW_RANGE] * 3,  # sample 1
            ]
        }

        with patch(
            "suplex.suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset",
            return_value=[[100, 200, 300], [400, 500, 600]],
        ):
            values = filter_obj.extract_filtered_values_from_datasets(
                mock_datasets_local,
                DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
                spot_threshold_map=spot_map,
                below_replacement_value=-999,
                above_replacement_value=999,
                invert=True,
            )
            # invert=True makes BELOW_RANGE "selected" → keep original values
            assert values[mock_datasets_local[0]] == [100, 200, 300, 400, 500, 600]

    def test_on_filter_params_changed_slider_update(self, mock_dataset_for_extractor):
        """on_filter_params_changed should update slider range based on current data."""
        filter_obj = SampleSpotFilter()
        with (
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.get_flat_value_list",
                return_value=[10, 20, 30, 100],
            ),
            patch(
                "suplex.suplex_modules.submodules.sample_spot_filter.extract_value_list_from_dataset",
                return_value=[[10, 20], [30, 100]],
            ),
        ):
            filter_obj.on_filter_params_changed([mock_dataset_for_extractor])
            assert filter_obj._threshold_range_slider.min == 10
            assert filter_obj._threshold_range_slider.max == 100

    def test_is_flag_in_selected_range_invert(self):
        """Test is_flag_in_selected_range with and without invert flag."""
        filter_obj = SampleSpotFilter()
        assert (
            filter_obj.is_flag_in_selected_range(THRESHOLD_FILTER_STATE.WITHIN_RANGE, invert=False)
            is True
        )
        assert (
            filter_obj.is_flag_in_selected_range(THRESHOLD_FILTER_STATE.WITHIN_RANGE, invert=True)
            is False
        )
        assert (
            filter_obj.is_flag_in_selected_range(THRESHOLD_FILTER_STATE.BELOW_RANGE, invert=False)
            is False
        )
        assert (
            filter_obj.is_flag_in_selected_range(THRESHOLD_FILTER_STATE.BELOW_RANGE, invert=True)
            is True
        )
