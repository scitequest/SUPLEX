from unittest.mock import Mock

import ipywidgets as widgets

from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    NORMALIZATION,
)
from suplex.suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    apply_normalization,
    extract_value_list_from_dataset,
    flatten_list,
    get_flat_value_list,
    get_reference_statistics,
    normalize_by_factor,
)


class TestValueExtractionFunctions:
    """Tests for the pure extraction and helper functions."""

    # -------------------------------------------------------------------------
    # Value extraction
    # -------------------------------------------------------------------------

    def test_extract_value_list_from_dataset_data_attributes(self, mock_dataset_for_extractor):
        """All basic spot data attributes return 2D lists."""
        for attr in [
            DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
            DATASET_ATTRIBUTE.NORMALIZED_MEAN,
            DATASET_ATTRIBUTE.MIN,
            DATASET_ATTRIBUTE.MAX,
            DATASET_ATTRIBUTE.MEAN,
            DATASET_ATTRIBUTE.STD_DEV,
        ]:
            values = extract_value_list_from_dataset(mock_dataset_for_extractor, attr)
            assert isinstance(values, list)
            assert len(values) == len(mock_dataset_for_extractor.samples)
            assert all(isinstance(row, list) for row in values)

    def test_extract_value_list_from_dataset_statistics(self, mock_dataset_for_extractor):
        """Data statistics attributes return 1D lists."""
        for attr in [DATASET_ATTRIBUTE.ADJUSTED_AVERAGE, DATASET_ATTRIBUTE.NORMALIZED_AVERAGE]:
            values = extract_value_list_from_dataset(mock_dataset_for_extractor, attr)
            assert isinstance(values, list)
            assert len(values) == len(mock_dataset_for_extractor.samples)

    def test_extract_value_list_from_dataset_coordinates(self, mock_dataset_for_extractor):
        """Spot and background coordinates return correct nested structure or empty list."""
        values_x = extract_value_list_from_dataset(
            mock_dataset_for_extractor, DATASET_ATTRIBUTE.SPOT_COORDINATES_X
        )
        assert isinstance(values_x, list)
        assert len(values_x) == len(mock_dataset_for_extractor.samples)

        values_bg = extract_value_list_from_dataset(
            mock_dataset_for_extractor, DATASET_ATTRIBUTE.BACKGROUND_RECTANGLES_COORDINATES_X
        )
        assert isinstance(values_bg, list)

    def test_extract_value_list_from_dataset_missing_parameters(self, mock_dataset_for_extractor):
        """Missing parameters → empty list."""
        mock_dataset_for_extractor.samples[0].spots[0].spot_parameters = None
        values = extract_value_list_from_dataset(
            mock_dataset_for_extractor, DATASET_ATTRIBUTE.SPOT_COORDINATES_X
        )
        assert values == []

    def test_flatten_list(self):
        """Recursive flattening of arbitrarily nested lists."""
        nested = [[[1, 2], 3], [4, [5]]]
        assert flatten_list(nested) == [1, 2, 3, 4, 5]
        assert flatten_list(42) == [42]

    def test_get_flat_value_list_data(self, mock_dataset_for_extractor):
        """DATA_ATTRIBUTES are fully flattened."""
        flat = get_flat_value_list(mock_dataset_for_extractor, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert isinstance(flat, list)
        assert all(isinstance(x, (int, float)) for x in flat)

    def test_get_flat_value_list_statistics(self, mock_dataset_for_extractor):
        """DATA_STATISTICS_ATTRIBUTES stay as 1D."""
        flat = get_flat_value_list(mock_dataset_for_extractor, DATASET_ATTRIBUTE.ADJUSTED_AVERAGE)
        assert len(flat) == len(mock_dataset_for_extractor.samples)


class TestNormalizationFunctions:
    """Tests for all normalization helpers."""

    def test_apply_normalization_raw(self):
        """Test RAW normalization (no change)."""
        ds = Mock()
        value_lists = {ds: [10, 20], Mock(): [30, 40]}
        result = apply_normalization(value_lists, NORMALIZATION.RAW)
        assert result == value_lists

    def test_apply_normalization_custom(self):
        """Test CUSTOM normalization."""
        ds = Mock()
        value_lists = {ds: [10, 20]}
        result = apply_normalization(value_lists, NORMALIZATION.CUSTOM, custom_factor=5.0)
        assert result[ds][0] == 2.0

    def test_apply_normalization_internal(self):
        """Test INTERNAL normalization."""
        ds = Mock()
        value_lists = {ds: [10, 20], Mock(): [5, 15]}
        result = apply_normalization(value_lists, NORMALIZATION.INTERNAL)
        assert result[ds][0] == 0.5

    def test_apply_normalization_global(self):
        """Test GLOBAL normalization."""
        ds = Mock()
        value_lists = {ds: [10, 20], Mock(): [5, 30]}
        result = apply_normalization(value_lists, NORMALIZATION.GLOBAL)
        assert max(max(v) for v in result.values()) == 1.0

    def test_apply_normalization_reference_gaussian(self):
        """Test reference-based Gaussian normalization."""
        ds = Mock()
        value_lists = {ds: [10, 20, 30]}
        ref_indices = [0]
        result = apply_normalization(
            value_lists,
            NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE,
            reference_indices=ref_indices,
        )
        assert isinstance(result, dict)

    def test_normalize_by_factor_scalar_and_list(self):
        """normalize_by_factor works with both scalar and list inputs."""
        assert normalize_by_factor(100, 10) == 10.0
        assert normalize_by_factor([10, 20], 10) == [1.0, 2.0]

    def test_get_reference_statistics(self):
        """Test reference point statistics calculation."""
        values = [10, 20, 30, 40]
        stats = get_reference_statistics(values, [0, 2])
        assert stats["n_reference_points"] == 2
        assert stats["avg"] == 20.0


class TestValueExtractor:
    """Tests for the main ValueExtractor class and its UI."""

    def test_value_extractor_init_default(self):
        """Default initialization should set sensible defaults."""
        extractor = ValueExtractor()
        assert extractor.attribute is not None
        assert extractor.normalization is not None

    def test_extract_values(self, value_extractor, mock_dataset_for_extractor):
        """End-to-end extraction + normalization."""
        datasets = [mock_dataset_for_extractor]
        values = value_extractor.extract_values(datasets)
        assert len(values) == 1
        assert isinstance(values[datasets[0]], list)

    def test_normalize_values_custom(self, value_extractor):
        """Custom normalization must actually divide by the provided factor."""
        ds = Mock()
        value_lists = {ds: [100, 200]}
        normalized = value_extractor.normalize_values(
            value_lists, normalization_method=NORMALIZATION.CUSTOM, custom_factor=50.0
        )
        assert normalized[ds][0] == 2.0  # 100 / 50

    def test_get_ui(self, value_extractor):
        """UI should return a valid VBox."""
        ui = value_extractor.get_ui()
        assert isinstance(ui, widgets.VBox)


class TestReferencePointSelector:
    """Tests for the inner ReferencePointSelector widget."""

    def test_reference_point_selector_init(self, reference_point_selector):
        """ReferencePointSelector initializes with the provided references."""
        assert reference_point_selector.references == [0, 3, 5]

    def test_add_and_remove_reference(self, reference_point_selector):
        """Adding and removing references via the widget works."""
        reference_point_selector._reference_input.value = 7
        reference_point_selector._add_reference_button.click()
        assert 7 in reference_point_selector.references

        # Remove via button
        for child in reference_point_selector._ref_container.children:
            if child.description == "7":
                child.click()
                break
        assert 7 not in reference_point_selector.references

    def test_clear_references(self, reference_point_selector):
        """Clear button resets the reference list."""
        reference_point_selector._clear_references_button.click()
        assert reference_point_selector.references == []

    def test_set_disabled(self, reference_point_selector):
        """set_disabled correctly disables the input widget."""
        reference_point_selector.set_disabled(True)
        assert reference_point_selector._reference_input.disabled is True
