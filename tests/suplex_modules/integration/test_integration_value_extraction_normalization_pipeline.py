from typing import Any

from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    NORMALIZATION,
)
from suplex.suplex_modules.submodules.value_extractor import (
    ReferencePointSelector,
    ValueExtractor,
    extract_value_list_from_dataset,
    flatten_list,
    get_flat_value_list,
)

# =============================================================================
# Integration tests for value extraction and normalization pipeline
# Fully aligned with the current ValueExtractor API (extract_values + get_flat_value_list)
# =============================================================================


class TestIntegrationValueExtractionAndNormalizationPipeline:
    """Integration tests for the value extraction and normalization pipeline."""

    # -------------------------------------------------------------------------
    # Happy path - basic extraction
    # -------------------------------------------------------------------------

    def test_extract_value_list_from_dataset_mean_minus_min(
        self, positive_uniform_datasets: list[Any]
    ) -> None:
        """Should correctly extract MEAN_MINUS_MIN values."""
        dataset = positive_uniform_datasets[0]

        nested_values = extract_value_list_from_dataset(dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert isinstance(nested_values, list)
        assert len(nested_values) > 0
        assert all(isinstance(sample_vals, list) for sample_vals in nested_values)

        flat_values = get_flat_value_list(dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert isinstance(flat_values, list)
        assert len(flat_values) > 0
        assert all(isinstance(v, (int, float)) for v in flat_values)
        assert all(v > 0 for v in flat_values)

    def test_extract_value_list_from_dataset_normalized_mean(
        self, positive_uniform_datasets: list[Any]
    ) -> None:
        """Should extract NORMALIZED_MEAN values (0-1 range)."""
        dataset = positive_uniform_datasets[0]
        flat_values = get_flat_value_list(dataset, DATASET_ATTRIBUTE.NORMALIZED_MEAN)

        assert len(flat_values) > 0
        assert all(isinstance(v, (int, float)) for v in flat_values)
        assert all(0.0 <= v <= 1.0 for v in flat_values)

    def test_get_flat_value_list_returns_flat_list(
        self, positive_uniform_datasets: list[Any]
    ) -> None:
        """get_flat_value_list should return a single flat list of numeric values."""
        dataset = positive_uniform_datasets[0]
        flat_values = get_flat_value_list(dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)

        assert isinstance(flat_values, list)
        assert all(isinstance(v, (int, float)) for v in flat_values)
        assert len(flat_values) >= len(dataset.samples)

    # -------------------------------------------------------------------------
    # Normalization strategies - use the public extract_values() API
    # -------------------------------------------------------------------------

    def test_value_extractor_raw_normalization(self, positive_uniform_datasets: list[Any]) -> None:
        """RAW normalization should return the original extracted values."""
        extractor = ValueExtractor()
        dataset = positive_uniform_datasets[0]

        result = extractor.extract_values(
            datasets=[dataset],
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
            normalization_method=NORMALIZATION.RAW,
        )

        assert isinstance(result, dict)
        assert len(result) > 0
        # result is Dict[Dataset, List[float]]
        values = list(result.values())[0]
        assert len(values) > 0

    def test_value_extractor_internal_normalization(
        self, positive_uniform_datasets: list[Any]
    ) -> None:
        """INTERNAL normalization should scale values relative to each dataset's own min/max."""
        extractor = ValueExtractor()
        dataset = positive_uniform_datasets[0]

        result = extractor.extract_values(
            datasets=[dataset],
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
            normalization_method=NORMALIZATION.INTERNAL,
        )

        values = list(result.values())[0]
        if values:
            assert min(values) >= 0.0
            assert max(values) <= 1.0

    def test_value_extractor_global_normalization_across_multiple_datasets(
        self, positive_uniform_datasets: list[Any]
    ) -> None:
        """GLOBAL normalization should use statistics from all provided datasets."""
        extractor = ValueExtractor()
        result = extractor.extract_values(
            datasets=positive_uniform_datasets,
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
            normalization_method=NORMALIZATION.GLOBAL,
        )

        assert len(result) > 0
        # At least one dataset should have values
        assert any(len(v) > 0 for v in result.values())

    # -------------------------------------------------------------------------
    # Reference point handling
    # -------------------------------------------------------------------------

    def test_reference_point_selector_initialization(self) -> None:
        """ReferencePointSelector should initialize without error."""
        selector = ReferencePointSelector()
        assert selector is not None
        assert hasattr(selector, "references")
        assert hasattr(selector, "get_ref_container")

    def test_value_extractor_supports_reference_points_via_selector(
        self, positive_uniform_datasets: list[Any]
    ) -> None:
        """ValueExtractor should support reference-based normalization via the selector."""
        extractor = ValueExtractor()
        dataset = positive_uniform_datasets[0]

        # Use a reference-based normalization method
        result = extractor.extract_values(
            datasets=[dataset],
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
            normalization_method=NORMALIZATION.BY_POSITION,  # one of the reference point methods
        )

        assert isinstance(result, dict)

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------

    def test_extract_from_negative_value_dataset(self, negative_value_dataset: Any) -> None:
        """Extraction should still work on datasets containing negative values."""
        flat_values = get_flat_value_list(negative_value_dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert isinstance(flat_values, list)
        assert len(flat_values) > 0
        assert any(v < 0 for v in flat_values)

    def test_extract_from_empty_dataset_list(self, empty_dataset_list: list[Any]) -> None:
        """Extractor should handle empty dataset list gracefully."""
        extractor = ValueExtractor()
        result = extractor.extract_values(
            datasets=empty_dataset_list,
            attribute=DATASET_ATTRIBUTE.MEAN_MINUS_MIN,
            normalization_method=NORMALIZATION.RAW,
        )

        assert result == {}  # or empty dict when no datasets

    def test_flatten_list_handles_nested_and_flat_input(self) -> None:
        """flatten_list utility should correctly flatten nested lists of values."""
        nested = [[10.0, 20.0], [30.0], [40.0, 50.0, 60.0]]
        flat = flatten_list(nested)
        assert flat == [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]

        already_flat = [1.0, 2.0, 3.0]
        assert flatten_list(already_flat) == already_flat

    def test_get_flat_value_list_on_dataset_with_varying_spot_counts(
        self, non_uniform_sample_count_datasets: list[Any]
    ) -> None:
        """Should correctly flatten even when samples have different numbers of spots."""
        for dataset in non_uniform_sample_count_datasets:
            flat = get_flat_value_list(dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
            assert isinstance(flat, list)
            total_spots = sum(len(s.spots) for s in dataset.samples)
            assert len(flat) == total_spots
