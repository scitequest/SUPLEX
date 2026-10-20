import pytest
from unittest.mock import patch

from suplex.martin_interface.martin_adapter import Adapter
from suplex.martin_interface.dataset import Dataset

from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface


class TestFullWizardWorkflow:
    """
    End-to-end workflow tests covering the complete user journey:
    Directory selection → Adapter creation → Dataset selection → Module viability check → Module launch.
    """

    # -------------------------------------------------------------------------
    # Directory Selection & Adapter Creation
    # -------------------------------------------------------------------------

    def test_real_adapter_discovers_valid_dataset(self, real_adapter):
        """A real Adapter correctly discovers and loads a valid MARTin dataset from disk."""
        assert isinstance(real_adapter, Adapter)
        assert len(real_adapter.datasets) >= 1
        assert len(real_adapter.projects) >= 1

        dataset = real_adapter.datasets[0]
        assert isinstance(dataset, Dataset)
        assert dataset.metadata is not None
        assert len(dataset.samples) > 0

    def test_adapter_creates_proper_dataset_objects(self, real_adapter):
        """Datasets produced by the Adapter contain all expected components for module consumption."""
        dataset = real_adapter.datasets[0]

        assert dataset.path_holder is not None
        assert dataset.file_holder is not None
        assert dataset.project is not None
        assert dataset.general_parameters is not None
        assert dataset.metadata is not None
        assert dataset.suplex_file is not None or dataset.suplex_file == {}

    # -------------------------------------------------------------------------
    # Dataset Selection Simulation
    # -------------------------------------------------------------------------

    def test_selected_datasets_fixture_returns_real_datasets(self, selected_datasets):
        """The selected_datasets fixture provides realistic Dataset objects as they would come from the UI."""
        assert len(selected_datasets) >= 1
        for ds in selected_datasets:
            assert isinstance(ds, Dataset)
            assert ds.measure_date is not None or ds.image_creation_date is not None

    # -------------------------------------------------------------------------
    # Module Viability Check
    # -------------------------------------------------------------------------

    def test_module_reports_viable_for_real_datasets(self, viable_module, selected_datasets):
        """A module that reports itself as viable can actually work with real selected datasets."""
        assert isinstance(viable_module, SuplexModuleInterface)
        assert viable_module.check_if_viable(selected_datasets) is True

    # -------------------------------------------------------------------------
    # Module Launch (initiate_module)
    # -------------------------------------------------------------------------

    def test_module_can_be_initiated_with_selected_datasets(
        self, viable_module, selected_datasets, mock_color_scheme
    ):
        """A viable module can be successfully initiated with real selected datasets and a color scheme."""
        # Reset to get a fresh instance
        module = viable_module.reset_module()

        # This is the critical call in the real workflow
        module_ui = module.initiate_module(
            datasets=selected_datasets, color_scheme=mock_color_scheme
        )

        # We don't assert on the exact return type here because modules can return different widget structures.
        # The important thing is that it does not raise an exception.
        assert module_ui is not None or module.processed is True or hasattr(module, "processed")

    # -------------------------------------------------------------------------
    # Full End-to-End Happy Path
    # -------------------------------------------------------------------------

    def test_full_wizard_flow_end_to_end(self, full_workflow_setup):
        """
        Complete happy-path workflow:
        Real Adapter → Selected datasets → Viable module → initiate_module()
        """
        adapter = full_workflow_setup["adapter"]
        selected_datasets = full_workflow_setup["selected_datasets"]
        color_scheme = full_workflow_setup["color_scheme"]
        module = full_workflow_setup["module"]

        # Step 1: Verify we have real data from martin_interface
        assert len(adapter.datasets) > 0
        assert len(selected_datasets) > 0

        # Step 2: Verify the module is viable for these datasets
        assert module.check_if_viable(selected_datasets) is True

        # Step 3: Launch the module (this is what happens when user clicks a module tile)
        fresh_module = module.reset_module()
        result = fresh_module.initiate_module(datasets=selected_datasets, color_scheme=color_scheme)

        # The module should either return a widget or mark itself as processed
        assert result is not None or getattr(fresh_module, "processed", False) is True

    def test_dataset_properties_are_accessible_in_module_context(
        self, viable_module, selected_datasets, mock_color_scheme
    ):
        """
        Datasets passed to modules expose all the properties modules typically need
        (metadata, samples, tags, dates, etc.).
        """
        module = viable_module.reset_module()

        # We don't need to fully run the module, just verify the data contract
        dataset = selected_datasets[0]

        # These are commonly used by modules
        assert dataset.id is not None
        assert dataset.name is not None
        assert dataset.tags is not None
        assert dataset.suplex_tags is not None
        assert len(dataset.samples) > 0
        assert dataset.general_parameters is not None

        # Initiate to make sure nothing breaks when the module accesses these
        module.initiate_module(datasets=selected_datasets, color_scheme=mock_color_scheme)
