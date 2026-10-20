import pytest
from enum import Enum

from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_LABEL,
    DATASET_SELECTOR_MODE,
    SELECTION_MODE,
    DATASET_DESCRIPTOR,
    DATASET_ATTRIBUTE,
    SORT_METHOD,
    NORMALIZATION,
    FILTER_METHOD,
    THRESHOLD_FILTER_STATE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
    PARAMETERS_ATTRIBUTES,
)


class TestSubmoduleConstants:
    """Tests for all enums, constants, and helper methods defined in submodule_constants."""

    # -------------------------------------------------------------------------
    # Enum tests
    # -------------------------------------------------------------------------

    def test_dataset_label_enum(self):
        """Test of the DATASET_LABEL enum."""
        assert issubclass(DATASET_LABEL, Enum)
        assert len(DATASET_LABEL) == 5
        assert DATASET_LABEL.NAME.value == "Name"
        assert DATASET_LABEL.ID.value == "ID"

    def test_dataset_selector_mode_enum(self):
        """Test of the DATASET_SELECTOR_MODE enum."""
        assert issubclass(DATASET_SELECTOR_MODE, Enum)
        assert len(DATASET_SELECTOR_MODE) == 3
        assert DATASET_SELECTOR_MODE.SINGLE.value == "single"

    def test_selection_mode_enum(self):
        """Test of the SELECTION_MODE enum."""
        assert issubclass(SELECTION_MODE, Enum)
        assert len(SELECTION_MODE) == 2
        assert SELECTION_MODE.ANY.value == "any"

    def test_dataset_descriptor_enum(self):
        """Test of the DATASET_DESCRIPTOR enum."""
        assert issubclass(DATASET_DESCRIPTOR, Enum)
        assert len(DATASET_DESCRIPTOR) == 3
        assert DATASET_DESCRIPTOR.NAME.value == "Dataset Name"

    def test_dataset_attribute_enum(self):
        """Test of the DATASET_ATTRIBUTE enum."""
        assert issubclass(DATASET_ATTRIBUTE, Enum)
        assert len(DATASET_ATTRIBUTE) > 10
        assert DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value == "Spot Mean Baseline Adjusted"

    def test_sort_method_enum(self):
        """Test of the SORT_METHOD enum."""
        assert issubclass(SORT_METHOD, Enum)
        assert len(SORT_METHOD) == 10
        assert SORT_METHOD.UNSORTED.value == "Unsorted"

    def test_normalization_enum(self):
        """Test of the NORMALIZATION enum."""
        assert issubclass(NORMALIZATION, Enum)
        assert len(NORMALIZATION) == 7
        assert NORMALIZATION.RAW.value == "RAW"

    def test_filter_method_enum(self):
        """Test of the FILTER_METHOD enum."""
        assert issubclass(FILTER_METHOD, Enum)
        assert len(FILTER_METHOD) == 10
        assert FILTER_METHOD.MEAN_MAX_RATIO.value == "Mean to Max Ratio"

    def test_threshold_filter_state_enum(self):
        """Test of the THRESHOLD_FILTER_STATE enum."""
        assert issubclass(THRESHOLD_FILTER_STATE, Enum)
        assert len(THRESHOLD_FILTER_STATE) == 4
        assert THRESHOLD_FILTER_STATE.WITHIN_RANGE.value == "Within Range"

    # -------------------------------------------------------------------------
    # List constants
    # -------------------------------------------------------------------------

    def test_data_attributes_list(self):
        """Test of the DATA_ATTRIBUTES list."""
        assert isinstance(DATA_ATTRIBUTES, list)
        assert len(DATA_ATTRIBUTES) == 6

    def test_data_statistics_attributes_list(self):
        """Test of the DATA_STATISTICS_ATTRIBUTES list."""
        assert isinstance(DATA_STATISTICS_ATTRIBUTES, list)
        assert len(DATA_STATISTICS_ATTRIBUTES) == 6

    def test_parameters_attributes_list(self):
        """Test of the PARAMETERS_ATTRIBUTES list."""
        assert isinstance(PARAMETERS_ATTRIBUTES, list)
        assert len(PARAMETERS_ATTRIBUTES) == 4

    # -------------------------------------------------------------------------
    # Enum methods
    # -------------------------------------------------------------------------

    def test_threshold_filter_state_evaluate(self):
        """Test of the evaluate method of THRESHOLD_FILTER_STATE."""
        assert THRESHOLD_FILTER_STATE.evaluate(5, 0, 10) == THRESHOLD_FILTER_STATE.WITHIN_RANGE
        assert THRESHOLD_FILTER_STATE.evaluate(-1, 0, 10) == THRESHOLD_FILTER_STATE.BELOW_RANGE
        assert THRESHOLD_FILTER_STATE.evaluate(11, 0, 10) == THRESHOLD_FILTER_STATE.ABOVE_RANGE
