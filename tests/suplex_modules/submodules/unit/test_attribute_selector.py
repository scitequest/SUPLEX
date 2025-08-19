# Angepasste Version von test_attribute_selector.py (verwendet SPOT_COORDINATES_X statt SPOT_SHAPE, keine neuen Konstanten)
import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets
from suplex_modules.submodules.attribute_selector import *
from suplex_modules.submodules.submodule_constants import DATASET_ATTRIBUTE, DATA_ATTRIBUTES, DATA_STATISTICS_ATTRIBUTES

class TestAttributeSelector:
    def test_extract_value_list_from_dataset_basic(self, mock_dataset):
        """Test extraction of basic data attributes."""
        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert len(values) == len(mock_dataset.samples)
        assert all(isinstance(sublist, list) for sublist in values)

    def test_extract_value_list_from_dataset_statistics(self, mock_dataset):
        """Test extraction of statistics attributes."""
        for sample in mock_dataset.samples:
            sample.data_statistics = Mock(adjusted_average=100.0)
        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.ADJUSTED_AVERAGE)
        assert len(values) == len(mock_dataset.samples)
        assert all(isinstance(val, float) for val in values)

    def test_extract_value_list_from_dataset_parameters(self, mock_dataset):
        """Test extraction of parameters (e.g. spot coordinates x)."""
        for sample in mock_dataset.samples:
            for spot in sample.spots:
                spot.spot_parameters = Mock(coordinates=[Mock(x=1.0), Mock(x=2.0)])
        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.SPOT_COORDINATES_X)
        assert len(values) == len(mock_dataset.samples)
        assert all(isinstance(sublist, list) for sublist in values)

    def test_extract_value_list_from_dataset_missing_parameters(self, mock_dataset):
        """Test when parameters are missing."""
        for sample in mock_dataset.samples:
            for spot in sample.spots:
                spot.spot_parameters = None
        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.SPOT_COORDINATES_X)
        assert values == []

    def test_extract_value_list_from_dataset_unknown_attribute(self, mock_dataset):
        """Test for unknown attribute."""
        with patch('suplex_modules.submodules.attribute_selector.logger.warning') as mock_warning:
            values = extract_value_list_from_dataset(mock_dataset, Mock(value="UNKNOWN"))
            assert values == []
            mock_warning.assert_called()

    def test_get_flat_value_list(self, mock_nested_value_list):
        """Test flattening of nested lists."""
        with patch('suplex_modules.submodules.attribute_selector.extract_value_list_from_dataset', return_value=mock_nested_value_list):
            flat = get_flat_value_list(Mock(), DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
            assert len(flat) == 4
            assert flat == [100.0, 200.0, 150.0, 50.0]

    def test_flatten_list(self):
        """Test of the flatten_list helper."""
        nested = [[[1,2], [3]], [[4]]]
        flat = flatten_list(nested)
        assert flat == [1,2,3,4]

    def test_attribute_selector_init(self):
        """Test instantiation of AttributeSelector."""
        selector = AttributeSelector()
        assert selector._widgets == []

    def test_get_dropdown_widget(self):
        """Test creation of dropdown widget."""
        selector = AttributeSelector()
        dropdown = selector.get_dropdown_widget(DATA_ATTRIBUTES)
        assert isinstance(dropdown, widgets.Dropdown)
        assert len(selector._widgets) == 1

    def test_get_checkbox_widgets(self):
        """Test creation of checkboxes."""
        selector = AttributeSelector()
        checkboxes = selector.get_checkbox_widgets(DATA_ATTRIBUTES)
        assert len(checkboxes) == len(DATA_ATTRIBUTES)
        assert all(isinstance(cb, widgets.Checkbox) for cb in checkboxes)

    def test_get_radio_button_widgets(self):
        """Test creation of radio buttons."""
        selector = AttributeSelector()
        radios = selector.get_radio_button_widgets(DATA_ATTRIBUTES)
        assert len(radios) == len(DATA_ATTRIBUTES)
        assert all(isinstance(rb, widgets.RadioButtons) or isinstance(rb, widgets.Checkbox) for rb in radios)  # Depending on implementation