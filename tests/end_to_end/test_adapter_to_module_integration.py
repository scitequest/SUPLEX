from suplex.martin_interface.dataset import Dataset


class TestAdapterToModuleIntegration:
    """
    Direct integration tests between the martin_interface layer (Adapter + Dataset)
    and the suplex_modules layer.
    """

    # -------------------------------------------------------------------------
    # Basic Data Contract
    # -------------------------------------------------------------------------

    def test_real_dataset_has_expected_interface(self, real_adapter):
        dataset = real_adapter.datasets[0]
        assert isinstance(dataset, Dataset)
        assert hasattr(dataset, "samples")
        assert hasattr(dataset, "metadata")
        assert hasattr(dataset, "general_parameters")
        assert hasattr(dataset, "tags")
        assert hasattr(dataset, "suplex_tags")
        assert hasattr(dataset, "measure_date")
        assert hasattr(dataset, "image_creation_date")
        assert len(dataset.samples) > 0

    def test_multiple_real_datasets_have_consistent_interface(
        self, real_adapter_with_multiple_datasets
    ):
        for dataset in real_adapter_with_multiple_datasets.datasets:
            assert isinstance(dataset, Dataset)
            assert len(dataset.samples) > 0
            assert dataset.metadata is not None

    # -------------------------------------------------------------------------
    # Viability Check with Real Data
    # -------------------------------------------------------------------------

    def test_modules_can_evaluate_viability_on_real_datasets(
        self, available_modules, selected_datasets
    ):
        for module in available_modules:
            result = module.check_if_viable(selected_datasets)
            assert isinstance(result, bool)

    def test_viable_module_accepts_real_datasets(self, viable_module, selected_datasets):
        assert viable_module.check_if_viable(selected_datasets) is True

    # -------------------------------------------------------------------------
    # Module Initiation with Real Data
    # -------------------------------------------------------------------------

    def test_module_initiation_with_real_single_dataset(
        self, viable_module, selected_datasets, mock_color_scheme
    ):
        module = viable_module.reset_module()
        result = module.initiate_module(
            datasets=[selected_datasets[0]], color_scheme=mock_color_scheme
        )
        assert result is not None or getattr(module, "processed", False)

    def test_module_initiation_with_multiple_real_datasets(
        self, viable_module, real_adapter_with_multiple_datasets, mock_color_scheme
    ):
        datasets = real_adapter_with_multiple_datasets.datasets
        assert len(datasets) >= 2

        module = viable_module.reset_module()
        result = module.initiate_module(datasets=datasets, color_scheme=mock_color_scheme)
        assert result is not None or getattr(module, "processed", False)

    # -------------------------------------------------------------------------
    # Data Accessibility Inside Modules
    # -------------------------------------------------------------------------

    def test_dataset_properties_are_usable_by_modules(
        self, viable_module, selected_datasets, mock_color_scheme
    ):
        dataset = selected_datasets[0]
        _ = dataset.id
        _ = dataset.name
        _ = dataset.tags
        _ = dataset.suplex_tags
        _ = len(dataset.samples)
        _ = dataset.general_parameters
        _ = dataset.metadata

        module = viable_module.reset_module()
        module.initiate_module(datasets=selected_datasets, color_scheme=mock_color_scheme)

    # -------------------------------------------------------------------------
    # "none" Project
    # -------------------------------------------------------------------------

    def test_modules_work_with_none_project_datasets(
        self, real_adapter_none_project, viable_module, mock_color_scheme
    ):
        """Modules can process datasets from the default 'none' project."""
        none_datasets = real_adapter_none_project.datasets
        assert len(none_datasets) > 0
        assert none_datasets[0].project.name == "none"

        module = viable_module.reset_module()
        module.initiate_module(datasets=none_datasets, color_scheme=mock_color_scheme)

    # -------------------------------------------------------------------------
    # Overall Integration Sanity
    # -------------------------------------------------------------------------

    def test_end_to_end_adapter_to_module_handoff(self, full_workflow_setup):
        adapter = full_workflow_setup["adapter"]
        selected_datasets = full_workflow_setup["selected_datasets"]
        color_scheme = full_workflow_setup["color_scheme"]
        module = full_workflow_setup["module"]

        assert len(adapter.datasets) > 0
        assert len(selected_datasets) > 0
        assert module.check_if_viable(selected_datasets) is True

        fresh_module = module.reset_module()
        result = fresh_module.initiate_module(datasets=selected_datasets, color_scheme=color_scheme)
        assert result is not None or getattr(fresh_module, "processed", False) is True
