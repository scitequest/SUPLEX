import pytest
import math
from unittest.mock import Mock

from suplex.suplex_modules.submodules.submodule_utils import (
    calculate_step_size,
    apply_normalization,
)
from suplex.suplex_modules.submodules.submodule_constants import NORMALIZATION
from suplex.martin_interface.dataset import Dataset


class TestSubmoduleUtils:
    """Tests for the utility functions in submodule_utils.py."""

    # -------------------------------------------------------------------------
    # calculate_step_size
    # -------------------------------------------------------------------------

    def test_calculate_step_size_valid_range(self):
        """Test step size calculation for valid range."""
        step, decimals = calculate_step_size(0, 100)
        assert step == 1.0
        assert decimals == 0

        step, decimals = calculate_step_size(0, 10)
        assert step == 0.1
        assert decimals == 1

        step, decimals = calculate_step_size(0, 0.01)
        assert step == 0.0001
        assert decimals == 4

    def test_calculate_step_size_invalid_range(self):
        """Test for invalid range (delta <= 0)."""
        step, decimals = calculate_step_size(100, 0)
        assert step == 1.0
        assert decimals == 0

        step, decimals = calculate_step_size(5, 5)
        assert step == 1.0
        assert decimals == 0

    def test_calculate_step_size_with_max_step(self):
        """Test with max_step cap."""
        step, decimals = calculate_step_size(0, 1000, max_step=10)
        assert step == 10
        assert decimals == 0

    def test_calculate_step_size_small_values(self):
        """Test for very small values."""
        step, decimals = calculate_step_size(0, 1e-10)
        assert step == 1e-12
        assert decimals == 12

    # -------------------------------------------------------------------------
    # apply_normalization
    # -------------------------------------------------------------------------

    def test_apply_normalization_raw(self):
        """Test RAW normalization (no change)."""
        mock_ds = Mock(spec=Dataset)
        value_sets = {mock_ds: [100, 200]}
        result = apply_normalization(value_sets, NORMALIZATION.RAW, 1.0)
        assert result == value_sets

    def test_apply_normalization_global(self):
        """Test GLOBAL normalization."""
        mock_ds1 = Mock(spec=Dataset)
        mock_ds2 = Mock(spec=Dataset)
        value_sets = {mock_ds1: [100, 200], mock_ds2: [50, 300]}
        result = apply_normalization(value_sets, NORMALIZATION.GLOBAL, 1.0)
        assert max(max(values) for values in result.values()) == 1.0

    def test_apply_normalization_internal(self):
        """Test INTERNAL normalization."""
        mock_ds1 = Mock(spec=Dataset)
        mock_ds2 = Mock(spec=Dataset)
        value_sets = {mock_ds1: [100, 200], mock_ds2: [50, 300]}
        result = apply_normalization(value_sets, NORMALIZATION.INTERNAL, 1.0)
        assert result[mock_ds1] == [0.5, 1.0]
        assert result[mock_ds2] == [50 / 300, 1.0]

    def test_apply_normalization_custom(self):
        """Test CUSTOM normalization."""
        mock_ds = Mock(spec=Dataset)
        value_sets = {mock_ds: [100, 200]}
        result = apply_normalization(value_sets, NORMALIZATION.CUSTOM, 50.0)
        assert result[mock_ds] == [2.0, 4.0]

    def test_apply_normalization_zero_division(self):
        """Test prevention of division by zero."""
        mock_ds = Mock(spec=Dataset)
        value_sets = {mock_ds: [0, 0]}
        result = apply_normalization(value_sets, NORMALIZATION.INTERNAL, 0)
        assert result[mock_ds] == [0, 0]  # No normalization applied
