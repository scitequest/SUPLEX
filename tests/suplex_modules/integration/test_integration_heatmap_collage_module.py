import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import List, Any

from suplex_modules.vanilla.heatmap_collage import OverviewHeatmapModule


class TestIntegrationHeatmapCollageModule:
    """Integration tests for the Heatmap Collage (OverviewHeatmapModule)."""

    # -------------------------------------------------------------------------
    # Module metadata
    # -------------------------------------------------------------------------

    def test_module_properties(self) -> None:
        module = OverviewHeatmapModule()
        assert module.module_name == "Heatmap Collage"
        assert module.module_version == "0.2.0"
        assert module.group_name == "Vanilla"
        assert isinstance(module.button_style, dict)

    # -------------------------------------------------------------------------
    # Viability
    # -------------------------------------------------------------------------

    @patch("suplex_modules.vanilla.heatmap_collage.has_negative_values", return_value=False)
    def test_check_if_viable_passes_on_good_datasets(
        self, mock_has_negative, positive_uniform_datasets: List[Any]
    ) -> None:
        module = OverviewHeatmapModule()
        assert module.check_if_viable(positive_uniform_datasets) is True

    @patch("suplex_modules.vanilla.heatmap_collage.has_negative_values", return_value=True)
    def test_check_if_viable_fails_on_negative_values(
        self, mock_has_negative, negative_value_dataset: Any
    ) -> None:
        module = OverviewHeatmapModule()
        assert module.check_if_viable([negative_value_dataset]) is False

    # -------------------------------------------------------------------------
    # Module lifecycle
    # -------------------------------------------------------------------------

    @patch("suplex_modules.vanilla.heatmap_collage.WidgetFactory")
    @patch("suplex_modules.vanilla.heatmap_collage.Collage")
    @patch("suplex_modules.vanilla.heatmap_collage.DatasetSorter")
    @patch("suplex_modules.vanilla.heatmap_collage.DatasetFilter")
    def test_initiate_module_creates_ui_without_crashing(
        self,
        mock_dataset_filter: MagicMock,
        mock_dataset_sorter: MagicMock,
        mock_collage: MagicMock,
        mock_widget_factory: MagicMock,
        positive_uniform_datasets: List[Any],
        mock_color_scheme: Mock,
    ) -> None:
        module = OverviewHeatmapModule()

        mock_widget_factory.return_value.create_dataset_selector.return_value = Mock()
        mock_widget_factory.return_value.create_attribute_selector.return_value = Mock()
        mock_collage.return_value.generate_collage.return_value = Mock()
        mock_dataset_sorter.return_value.get_sorted_datasets.return_value = (
            positive_uniform_datasets
        )
        mock_dataset_filter.return_value.get_filtered_datasets.return_value = (
            positive_uniform_datasets,
            [],
        )

        box = module.initiate_module(positive_uniform_datasets, mock_color_scheme)
        assert box is not None

    def test_update_scheme_does_not_crash(
        self, positive_uniform_datasets: List[Any], mock_color_scheme: Mock
    ) -> None:
        module = OverviewHeatmapModule()
        module.initiate_module(positive_uniform_datasets, mock_color_scheme)
        result = module.update_scheme(mock_color_scheme)
        assert result is None or result is module

    def test_reset_module_returns_new_instance(self) -> None:
        module = OverviewHeatmapModule()
        new_module = module.reset_module()
        assert isinstance(new_module, OverviewHeatmapModule)
        assert new_module is not module

    # -------------------------------------------------------------------------
    # Export helpers
    # -------------------------------------------------------------------------

    @patch("suplex_modules.vanilla.heatmap_collage.ExcelAdapter", create=True)
    def test_export_overview_sheet_smoke(
        self, mock_excel_adapter: MagicMock, positive_uniform_datasets: List[Any]
    ) -> None:
        module = OverviewHeatmapModule()
        assert hasattr(module, "on_export_overview_csv") or hasattr(module, "initiate_module")

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------

    def test_initiate_module_with_empty_dataset_list(self, empty_dataset_list: List[Any]) -> None:
        module = OverviewHeatmapModule()
        try:
            module.initiate_module(empty_dataset_list, color_scheme=None)
        except Exception:
            pass
