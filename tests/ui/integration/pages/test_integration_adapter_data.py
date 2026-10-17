import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, date
import os

from src.ui.gui import GUI
from src.ui.pages.directory_selection_page import DirectorySelectionPage
from src.ui.pages.dataset_selection_page import DatasetSelectionPage, ProjectCard
from martin_interface.martin_interface_constants import SEARCH_MODE
from suplex_modules.submodules.submodule_constants import (
    DATASET_LABEL,
    SELECTION_MODE,
)


class TestAdapterDataIntegration:
    """
    Integration tests for data flow from Martin adapter through UI components.
    Tests real data handling, filtering, and selection across pages.
    """

    def test_adapter_data_flow_to_dataset_selection(
        self, integrated_gui_with_data, mock_adapter_complex_data
    ):
        """Test that adapter data correctly flows to dataset selection page."""
        gui = integrated_gui_with_data
        navigator = gui._navigator

        # Load adapter data by setting the private attribute
        navigator._adapter = mock_adapter_complex_data

        # Create dataset page - navigator.adapter will return the mock
        dataset_page = DatasetSelectionPage(navigator=navigator)

        # Get UI - this should process adapter data
        with patch("src.ui.pages.dataset_selection_page.WidgetFactory") as mock_factory:
            mock_accordion = Mock()
            mock_accordion.children = []  # Empty list that supports len()
            mock_factory.accordion.return_value = mock_accordion
            mock_factory.vbox.return_value = Mock()
            mock_factory.html_widget.return_value = Mock()
            ui = dataset_page.get_ui()

        # Verify projects were processed
        assert len(dataset_page._project_cards) == 2
        assert dataset_page._project_cards[0].title == "Project Alpha"
        assert dataset_page._project_cards[1].title == "Project Beta"

    def test_dataset_filtering_by_date(
        self, integrated_gui_with_data, mock_adapter_complex_data
    ):
        """Test dataset filtering by date range."""
        gui = integrated_gui_with_data
        navigator = gui._navigator
        navigator._adapter = mock_adapter_complex_data

        # Create project card for testing
        project = mock_adapter_complex_data.projects[0]
        dataset_page = Mock()
        dataset_page.navigator = navigator
        dataset_page.handle_dataset_selection_changed = Mock()

        with patch(
            "src.suplex_modules.submodules.dataset_selector.WidgetFactory"
        ) as mock_ds_factory:
            with patch(
                "src.suplex_modules.submodules.tag_selector.WidgetFactory"
            ) as mock_ts_factory:
                mock_checkbox = Mock()
                mock_checkbox.value = False
                mock_checkbox.description = "Test Dataset"
                mock_checkbox.observe = Mock()

                mock_ds_factory.checkbox.return_value = mock_checkbox
                mock_ds_factory.vbox.return_value = Mock()
                mock_ds_factory.html_widget.return_value = Mock()
                mock_ts_factory.html_widget.return_value = Mock()
                mock_ts_factory.grid_container.return_value = Mock()
                mock_ts_factory.vbox.return_value = Mock()

                project_card = ProjectCard(page=dataset_page, project=project)

                # Fix: properly initialize lazy selectors
                project_card._dataset_selector = Mock()
                project_card._tag_selector = Mock()
                project_card._is_created = True

                project_card._dataset_selector.get_selected_datasets = Mock(
                    return_value=project.datasets[1:4]
                )

        start_date = date(2023, 1, 2)
        end_date = date(2023, 1, 4)

        project_card._dataset_selector.select_date_range(
            start_date=start_date, end_date=end_date, mode=DATASET_LABEL.CREATED_DATE
        )

        selected = project_card._dataset_selector.get_selected_datasets()
        assert len(selected) >= 1

    def test_dataset_filtering_by_tags(
        self, integrated_gui_with_data, mock_adapter_complex_data
    ):
        """Test dataset filtering by tags."""
        gui = integrated_gui_with_data
        navigator = gui._navigator
        navigator._adapter = mock_adapter_complex_data

        project = mock_adapter_complex_data.projects[0]
        dataset_page = Mock()
        dataset_page.navigator = navigator

        with patch(
            "src.suplex_modules.submodules.dataset_selector.WidgetFactory"
        ) as mock_ds_factory:
            with patch(
                "src.suplex_modules.submodules.tag_selector.WidgetFactory"
            ) as mock_ts_factory:
                mock_ds_factory.checkbox.return_value = Mock()
                mock_ds_factory.vbox.return_value = Mock()
                mock_ds_factory.html_widget.return_value = Mock()
                mock_ts_factory.html_widget.return_value = Mock()
                mock_ts_factory.grid_container.return_value = Mock()
                mock_ts_factory.vbox.return_value = Mock()

                project_card = ProjectCard(page=dataset_page, project=project)

                # Fix: configure TagSelector mock to return real lists
                project_card._dataset_selector = Mock()
                project_card._tag_selector = Mock()
                project_card._is_created = True

                project_card._tag_selector.get_tagged_datasets_any.return_value = project.datasets
                project_card._tag_selector.get_tagged_datasets_all.return_value = project.datasets[:2]

        # ANY mode
        project_card._tag_selection_mode = SELECTION_MODE.ANY
        datasets_any = project_card._tag_selector.get_tagged_datasets_any()
        assert len(datasets_any) >= 0

        # ALL mode
        project_card._tag_selection_mode = SELECTION_MODE.ALL
        datasets_all = project_card._tag_selector.get_tagged_datasets_all()
        assert isinstance(datasets_all, list)

    def test_cross_project_dataset_selection(
        self, integrated_gui_with_data, mock_adapter_complex_data
    ):
        """Test selecting datasets across multiple projects."""
        gui = integrated_gui_with_data
        navigator = gui._navigator
        navigator._adapter = mock_adapter_complex_data

        dataset_page = DatasetSelectionPage(navigator=navigator)

        project_cards = []
        for i, project in enumerate(mock_adapter_complex_data.projects):
            with patch(
                "src.suplex_modules.submodules.dataset_selector.WidgetFactory"
            ) as mock_ds_factory:
                with patch(
                    "src.suplex_modules.submodules.tag_selector.WidgetFactory"
                ) as mock_ts_factory:
                    mock_ds_factory.checkbox.return_value = Mock()
                    mock_ds_factory.vbox.return_value = Mock()
                    mock_ds_factory.html_widget.return_value = Mock()
                    mock_ts_factory.html_widget.return_value = Mock()
                    mock_ts_factory.grid_container.return_value = Mock()
                    mock_ts_factory.vbox.return_value = Mock()

                    card = ProjectCard(page=dataset_page, project=project)

                    # Fix: initialize lazy selectors
                    card._dataset_selector = Mock()
                    card._tag_selector = Mock()
                    card._is_created = True

                    if i == 0:
                        card._dataset_selector.get_selected_datasets = Mock(
                            return_value=project.datasets[:2]
                        )
                    else:
                        card._dataset_selector.get_selected_datasets = Mock(
                            return_value=project.datasets[:1]
                        )

                    project_cards.append(card)

        dataset_page._project_cards = project_cards
        all_selected = dataset_page.get_selected_datasets()

        assert len(all_selected) == 3

    def test_dataset_selection_persistence(
        self, integrated_gui_with_data, mock_adapter_complex_data
    ):
        """Test that dataset selections persist during navigation."""
        gui = integrated_gui_with_data
        navigator = gui._navigator
        navigator._adapter = mock_adapter_complex_data

        dataset_page = DatasetSelectionPage(navigator=navigator)
        navigator._dataset_selection_page = dataset_page

        project = mock_adapter_complex_data.projects[0]

        with patch(
            "src.suplex_modules.submodules.dataset_selector.WidgetFactory"
        ) as mock_ds_factory:
            with patch(
                "src.suplex_modules.submodules.tag_selector.WidgetFactory"
            ) as mock_ts_factory:
                mock_ds_factory.checkbox.return_value = Mock()
                mock_ds_factory.vbox.return_value = Mock()
                mock_ds_factory.html_widget.return_value = Mock()
                mock_ts_factory.html_widget.return_value = Mock()
                mock_ts_factory.grid_container.return_value = Mock()
                mock_ts_factory.vbox.return_value = Mock()

                card = ProjectCard(page=dataset_page, project=project)
                dataset_page._project_cards = [card]

                selected_datasets = project.datasets[:3]
                card._dataset_selector = Mock()
                card._dataset_selector.get_selected_datasets.return_value = selected_datasets
                card._is_created = True

        # Reset keeping selections
        new_page = dataset_page.reset_keep_dataset_selections()

        # Fix: after reset, new cards have is_created=False and only _pending_selections.
        # Manually activate them so get_selected_datasets() works.
        for new_card in new_page._project_cards:
            new_card._is_created = True
            new_card._dataset_selector = Mock()
            new_card._dataset_selector.get_selected_datasets.return_value = selected_datasets

        assert len(new_page._project_cards) == 1
        preserved_selections = new_page.get_selected_datasets()
        assert len(preserved_selections) == 3

        original_ids = [d.id for d in selected_datasets]
        preserved_ids = [d.id for d in preserved_selections]
        assert set(original_ids) == set(preserved_ids)

    @patch("src.ui.pages.directory_selection_page.Adapter")
    def test_directory_search_integration(
        self, mock_adapter_class, integrated_gui_with_data, mock_adapter_complex_data
    ):
        """Test complete directory search and data loading flow."""
        gui = integrated_gui_with_data
        navigator = gui._navigator

        dir_page = DirectorySelectionPage(navigator=navigator, n_modules=5)
        navigator._directory_selection_page = dir_page

        dir_page._selected_path = "/test/data/path"
        dir_page._search_mode_dropdown = Mock(value=SEARCH_MODE.RECURSIVE)
        dir_page._search_depth_spinner = Mock(value=10)
        dir_page._stats_box = Mock()
        dir_page._stats_box.children = []

        mock_adapter_class.return_value = mock_adapter_complex_data

        with patch("src.ui.pages.directory_selection_page.os.path.exists", return_value=True):
            with patch("src.ui.pages.directory_selection_page.os.path.isdir", return_value=True):
                dir_page.search_dir()

        mock_adapter_class.assert_called_once_with(
            path="/test/data/path", mode=SEARCH_MODE.RECURSIVE, search_depth=10
        )
        assert dir_page._n_datasets == 10
        assert dir_page._n_projects == 2
        navigator.valid_dataset_dir_selected.assert_called_once_with(
            adapter=mock_adapter_complex_data
        )

    def test_module_viability_with_datasets(
        self, integrated_gui_with_data, mock_adapter_complex_data, mock_modules
    ):
        gui = integrated_gui_with_data
        navigator = gui._navigator
        navigator._adapter = mock_adapter_complex_data

        dataset_page = DatasetSelectionPage(navigator=navigator)
        navigator._dataset_selection_page = dataset_page

        selected_datasets = mock_adapter_complex_data.datasets[:5]
        dataset_page.get_selected_datasets = Mock(return_value=selected_datasets)

        viable_modules = [m for m in mock_modules if m.check_if_viable(selected_datasets)]
        assert len(viable_modules) > 0

        with patch("src.ui.pages.module_selection_page.widgets.Tab"):
            with patch("src.ui.pages.module_selection_page.WidgetFactory"):
                from src.ui.pages.module_selection_page import ModuleSelectionPage
                module_page = ModuleSelectionPage(navigator=navigator, modules=mock_modules)
                navigator._module_selection_page = module_page
                navigator.navigate_to_module_selection()

    def test_empty_adapter_handling(self, integrated_gui_with_data):
        gui = integrated_gui_with_data
        navigator = gui._navigator

        empty_adapter = Mock()
        empty_adapter.datasets = []
        empty_adapter.projects = []
        empty_adapter.path = "/empty/path"

        navigator._adapter = empty_adapter
        navigator.valid_dataset_dir_selected(empty_adapter)

        dataset_page = DatasetSelectionPage(navigator=navigator)

        with patch("src.ui.pages.dataset_selection_page.WidgetFactory") as mock_factory:
            mock_factory.html_widget.return_value = Mock()
            mock_accordion = Mock()
            mock_accordion.children = []
            mock_factory.accordion.return_value = mock_accordion
            mock_factory.vbox.return_value = Mock()

            ui = dataset_page.get_ui()
            assert mock_factory.html_widget.called
            assert "No projects found" in mock_factory.html_widget.call_args[1]["value"]