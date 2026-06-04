import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets

from suplex_modules.submodules.attribute_selector import (
    extract_value_list_from_dataset,
    get_flat_value_list,
    flatten_list,
    AttributeSelector,
)
from suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
)
from src.martin_interface.dataset import Dataset


class TestAttributeSelector:
    """Tests for the AttributeSelector module (extraction functions + widget logic)."""

    # -------------------------------------------------------------------------
    # Value extraction helper functions
    # -------------------------------------------------------------------------

    def test_extract_value_list_from_dataset_basic(self, mock_dataset):
        """Test extraction of basic data attributes (returns nested list per sample)."""
        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
        assert len(values) == len(mock_dataset.samples)
        assert all(isinstance(sublist, list) for sublist in values)

    def test_extract_value_list_from_dataset_statistics(self, mock_dataset):
        """Test extraction of dataset-level statistics attributes."""
        for sample in mock_dataset.samples:
            sample.data_statistics = Mock(adjusted_average=100.0)

        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.ADJUSTED_AVERAGE)
        assert len(values) == len(mock_dataset.samples)
        assert all(isinstance(val, float) for val in values)

    def test_extract_value_list_from_dataset_parameters(self, mock_dataset):
        """Test extraction of spot parameters (e.g. coordinates)."""
        for sample in mock_dataset.samples:
            for spot in sample.spots:
                spot.spot_parameters = Mock(coordinates=[Mock(x=1.0), Mock(x=2.0)])

        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.SPOT_COORDINATES_X)
        assert len(values) == len(mock_dataset.samples)
        assert all(isinstance(sublist, list) for sublist in values)

    def test_extract_value_list_from_dataset_missing_parameters(self, mock_dataset):
        """Test graceful handling when parameters are missing."""
        for sample in mock_dataset.samples:
            for spot in sample.spots:
                spot.spot_parameters = None

        values = extract_value_list_from_dataset(mock_dataset, DATASET_ATTRIBUTE.SPOT_COORDINATES_X)
        assert values == []

    def test_extract_value_list_from_dataset_unknown_attribute(self, mock_dataset):
        """Test handling of unknown attribute (should log warning and return empty)."""
        with patch("suplex_modules.submodules.attribute_selector.logger.warning") as mock_warning:
            values = extract_value_list_from_dataset(mock_dataset, Mock(value="UNKNOWN"))
            assert values == []
            mock_warning.assert_called()

    def test_get_flat_value_list(self, mock_nested_value_list):
        """Test flattening of nested value lists returned by extract_value_list_from_dataset."""
        with patch(
            "suplex_modules.submodules.attribute_selector.extract_value_list_from_dataset",
            return_value=mock_nested_value_list,
        ):
            flat = get_flat_value_list(Mock(), DATASET_ATTRIBUTE.MEAN_MINUS_MIN)
            assert len(flat) == 4
            assert flat == [100.0, 200.0, 150.0, 50.0]

    def test_flatten_list(self):
        """Test the recursive flatten_list helper function."""
        nested = [[[1, 2], [3]], [[4]]]
        flat = flatten_list(nested)
        assert flat == [1, 2, 3, 4]

    # -------------------------------------------------------------------------
    # AttributeSelector widget class
    # -------------------------------------------------------------------------

    def test_attribute_selector_init(self):
        """Test instantiation of AttributeSelector."""
        selector = AttributeSelector()
        assert selector._widgets == []

    def test_get_dropdown_widget(self):
        """Test creation of dropdown widget."""
        selector = AttributeSelector()
        dropdown = selector.get_dropdown_widget(DATA_ATTRIBUTES, layout=widgets.Layout())
        assert isinstance(dropdown, widgets.Dropdown)
        assert len(selector._widgets) == 1

    def test_get_checkbox_widgets(self):
        """Test creation of checkbox widgets."""
        selector = AttributeSelector()
        checkboxes = selector.get_checkbox_widgets(DATA_ATTRIBUTES, layout=widgets.Layout())
        assert len(checkboxes) == len(DATA_ATTRIBUTES)
        assert all(isinstance(cb, widgets.Checkbox) for cb in checkboxes)

    def test_get_radio_button_widgets(self):
        """Test creation of radio button widgets."""
        selector = AttributeSelector()
        radios = selector.get_radio_button_widgets(DATA_ATTRIBUTES, layout=widgets.Layout())
        assert len(radios) == len(DATA_ATTRIBUTES)
        assert all(
            isinstance(rb, widgets.RadioButtons) or isinstance(rb, widgets.Checkbox)
            for rb in radios
        )

    # -------------------------------------------------------------------------
    # get_selected_values tests
    # -------------------------------------------------------------------------

    def test_get_selected_values_checkboxes_multiple(self, attribute_selector, mock_dataset):
        """Test get_selected_values with multiple checkboxes selected."""
        selector = attribute_selector
        selector.get_checkbox_widgets(DATA_ATTRIBUTES, layout=widgets.Layout())

        for widget in selector._widgets:
            if isinstance(widget, widgets.Checkbox):
                if widget.description in [
                    DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value,
                    DATASET_ATTRIBUTE.NORMALIZED_MEAN.value,
                ]:
                    widget.value = True

        selected = selector.get_selected_values(mock_dataset)

        assert len(selected) == 2
        assert DATASET_ATTRIBUTE.MEAN_MINUS_MIN in selected
        assert DATASET_ATTRIBUTE.NORMALIZED_MEAN in selected
        assert isinstance(selected[DATASET_ATTRIBUTE.MEAN_MINUS_MIN], list)
        assert isinstance(selected[DATASET_ATTRIBUTE.NORMALIZED_MEAN], list)

    def test_get_selected_values_dropdown_single(self, attribute_selector, mock_dataset):
        """Test get_selected_values when using dropdown (single selection)."""
        selector = attribute_selector
        dropdown = selector.get_dropdown_widget(DATA_ATTRIBUTES, layout=widgets.Layout())
        dropdown.value = DATASET_ATTRIBUTE.MEAN_MINUS_MIN.value

        selected = selector.get_selected_values(mock_dataset)

        assert len(selected) == 1
        assert DATASET_ATTRIBUTE.MEAN_MINUS_MIN in selected
        assert isinstance(selected[DATASET_ATTRIBUTE.MEAN_MINUS_MIN], list)

    def test_get_selected_values_radio_buttons(self, attribute_selector, mock_dataset):
        """Test get_selected_values with radio buttons (single selection)."""
        selector = attribute_selector
        radios = selector.get_radio_button_widgets(DATA_ATTRIBUTES, layout=widgets.Layout())
        radios[0].value = True

        selected = selector.get_selected_values(mock_dataset)

        assert len(selected) == 1
        assert list(selected.keys())[0] in DATA_ATTRIBUTES

    def test_get_selected_values_nothing_selected(self, attribute_selector, mock_dataset):
        """Test that nothing is returned when no widget is selected."""
        selector = attribute_selector
        selector.get_checkbox_widgets(DATA_ATTRIBUTES, layout=widgets.Layout())

        selected = selector.get_selected_values(mock_dataset)
        assert selected == {}

    def test_get_selected_values_empty_dataset(self, attribute_selector):
        """Test behavior with completely empty dataset."""
        empty_dataset = Mock(spec=Dataset)
        empty_dataset.samples = []

        selector = attribute_selector
        selector.get_checkbox_widgets([DATASET_ATTRIBUTE.MEAN_MINUS_MIN], layout=widgets.Layout())
        for widget in selector._widgets:
            if isinstance(widget, widgets.Checkbox):
                widget.value = True

        selected = selector.get_selected_values(empty_dataset)
        assert len(selected) == 1
        assert selected[DATASET_ATTRIBUTE.MEAN_MINUS_MIN] == []

    def test_get_selected_values_unknown_attribute(self, attribute_selector, mock_dataset):
        """Test graceful handling of unknown attribute in selected fields."""
        selector = attribute_selector
        # Manually simulate a corrupted widget state
        bad_widget = Mock(spec=widgets.Checkbox)
        bad_widget.description = "UNKNOWN_ATTRIBUTE"
        bad_widget.value = True
        selector._widgets = [bad_widget]

        with pytest.raises(ValueError, match="UNKNOWN_ATTRIBUTE' is not a valid DATASET_ATTRIBUTE"):
            selector.get_selected_values(mock_dataset)

    def test_widgets_list_is_reset_after_get_selected_values(self, attribute_selector):
        """Ensure that get_selected_values does NOT clear the internal widget list (important for reuse)."""
        selector = attribute_selector
        selector.get_checkbox_widgets(DATA_ATTRIBUTES, layout=widgets.Layout())
        initial_widget_count = len(selector._widgets)
        selector.get_selected_values(Mock(spec=Dataset))
        assert len(selector._widgets) == initial_widget_count
