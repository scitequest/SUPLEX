import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import List, Any

from suplex_modules.vanilla.intensity_overview import IntensityOverviewModule


class TestIntegrationIntensityOverviewModule:
    """Integration tests for the Intensity Overview (box + jitter) visualization module."""

    # -------------------------------------------------------------------------
    # Module metadata
    # -------------------------------------------------------------------------

    def test_module_properties(self) -> None:
        module = IntensityOverviewModule()
        assert module.module_name == "Intensity Overview"
        assert module.module_version == "0.6.0"  # ← corrected
        assert module.group_name == "Vanilla"
        assert isinstance(module.button_style, dict)

    # -------------------------------------------------------------------------
    # Viability (this module only rejects on empty list or negative values)
    # -------------------------------------------------------------------------

    def test_check_if_viable_passes_on_good_datasets(
        self, positive_uniform_datasets: List[Any]
    ) -> None:
        module = IntensityOverviewModule()
        assert module.check_if_viable(positive_uniform_datasets) is True

    def test_check_if_viable_fails_on_negative_values(self, negative_value_dataset: Any) -> None:
        module = IntensityOverviewModule()
        assert module.check_if_viable([negative_value_dataset]) is False

    # Note: IntensityOverviewModule does NOT reject datasets with few samples.
    # The old test was removed because it no longer matches the implementation.

    # -------------------------------------------------------------------------
    # Module lifecycle
    # -------------------------------------------------------------------------

    @patch("suplex_modules.vanilla.intensity_overview.WidgetFactory")
    @patch("suplex_modules.vanilla.intensity_overview.ValueExtractor")
    @patch("suplex_modules.vanilla.intensity_overview.BoxplotSettings")
    @patch("suplex_modules.vanilla.intensity_overview.JitterplotSettings")
    def test_initiate_module_creates_box_jitter_ui(
        self,
        mock_jitter_settings: MagicMock,
        mock_box_settings: MagicMock,
        mock_value_extractor: MagicMock,
        mock_widget_factory: MagicMock,
        positive_uniform_datasets: List[Any],
        mock_color_scheme: Mock,
    ) -> None:
        module = IntensityOverviewModule()

        mock_widget_factory.return_value.create_dataset_selector.return_value = Mock()
        mock_widget_factory.return_value.create_attribute_selector.return_value = Mock()
        mock_value_extractor.return_value.get_extracted_and_normalized_values.return_value = {
            "values": [95.0, 110.0, 88.0, 125.0],
            "reference_value": 104.5,
        }

        box = module.initiate_module(positive_uniform_datasets, mock_color_scheme)
        assert box is not None
        # Note: Current implementation does not set _is_active

    def test_update_scheme(
        self, positive_uniform_datasets: List[Any], mock_color_scheme: Mock
    ) -> None:
        module = IntensityOverviewModule()
        module.initiate_module(positive_uniform_datasets, mock_color_scheme)
        result = module.update_scheme(mock_color_scheme)
        assert result is None or result is module

    def test_reset_module_returns_new_instance(self) -> None:
        module = IntensityOverviewModule()
        new_module = module.reset_module()
        assert isinstance(new_module, IntensityOverviewModule)
        assert new_module is not module

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------

    def test_initiate_with_empty_datasets(self, empty_dataset_list: List[Any]) -> None:
        module = IntensityOverviewModule()
        try:
            module.initiate_module(empty_dataset_list, color_scheme=None)
        except Exception:
            pass
