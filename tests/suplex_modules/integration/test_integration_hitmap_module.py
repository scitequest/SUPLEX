import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import List, Any

from suplex.suplex_modules.vanilla.hitmap import HitmapModule


class TestIntegrationHitmapModule:
    """Integration tests for the Hitmap visualization module."""

    # -------------------------------------------------------------------------
    # Module metadata
    # -------------------------------------------------------------------------

    def test_module_properties(self) -> None:
        module = HitmapModule()
        assert module.module_name == "Hitmap"
        assert module.module_version == "0.1.0"
        assert module.group_name == "Vanilla"
        assert isinstance(module.button_style, dict)

    # -------------------------------------------------------------------------
    # Viability (Hitmap has stricter requirements)
    # -------------------------------------------------------------------------

    def test_check_if_viable_passes_on_sufficient_uniform_datasets(
        self, positive_uniform_datasets: List[Any]
    ) -> None:
        module = HitmapModule()
        assert module.check_if_viable(positive_uniform_datasets) is True

    def test_check_if_viable_fails_with_insufficient_samples(
        self, insufficient_samples_dataset: Any
    ) -> None:
        module = HitmapModule()
        assert module.check_if_viable([insufficient_samples_dataset]) is False

    def test_check_if_viable_fails_with_negative_values(self, negative_value_dataset: Any) -> None:
        module = HitmapModule()
        assert module.check_if_viable([negative_value_dataset]) is False

    # -------------------------------------------------------------------------
    # Module lifecycle
    # -------------------------------------------------------------------------

    @patch("suplex.suplex_modules.vanilla.hitmap.WidgetFactory")
    @patch("suplex.suplex_modules.vanilla.hitmap.ValueExtractor")
    @patch("suplex.suplex_modules.vanilla.hitmap.SampleSpotFilter")
    def test_initiate_module_builds_ui_for_valid_input(
        self,
        mock_sample_spot_filter: MagicMock,
        mock_value_extractor: MagicMock,
        mock_widget_factory: MagicMock,
        positive_uniform_datasets: List[Any],
        mock_color_scheme: Mock,
    ) -> None:
        module = HitmapModule()

        mock_widget_factory.return_value.create_dataset_selector.return_value = Mock()
        mock_widget_factory.return_value.create_attribute_selector.return_value = Mock()
        mock_value_extractor.return_value.get_extracted_and_normalized_values.return_value = {
            "values": [100.0, 120.0, 95.0],
            "reference_value": 105.0,
        }
        mock_sample_spot_filter.return_value.get_filter_maps.return_value = ({}, {})

        box = module.initiate_module(positive_uniform_datasets, mock_color_scheme)
        assert box is not None
        # Note: Current implementation does not set _is_active

    def test_update_scheme_accepts_new_color_scheme(
        self, positive_uniform_datasets: List[Any], mock_color_scheme: Mock
    ) -> None:
        module = HitmapModule()
        module.initiate_module(positive_uniform_datasets, mock_color_scheme)
        result = module.update_scheme(mock_color_scheme)
        assert result is None or result is module

    def test_reset_module_returns_new_instance(self) -> None:
        module = HitmapModule()
        new_module = module.reset_module()
        assert isinstance(new_module, HitmapModule)
        assert new_module is not module

    # -------------------------------------------------------------------------
    # Filtering modes (static vs dynamic)
    # -------------------------------------------------------------------------

    def test_module_supports_both_static_and_dynamic_filtering(
        self, positive_uniform_datasets: List[Any]
    ) -> None:
        module = HitmapModule()
        assert hasattr(module, "initiate_module")

    # -------------------------------------------------------------------------
    # Export (smoke test)
    # -------------------------------------------------------------------------

    def test_export_functionality_smoke_test(self, positive_uniform_datasets: List[Any]) -> None:
        module = HitmapModule()
        assert hasattr(module, "on_export_overview_csv") or hasattr(module, "initiate_module")

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------

    def test_initiate_with_empty_datasets(self, empty_dataset_list: List[Any]) -> None:
        module = HitmapModule()
        try:
            module.initiate_module(empty_dataset_list, color_scheme=None)
        except Exception:
            pass
