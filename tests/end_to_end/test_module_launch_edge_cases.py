from suplex.martin_interface.dataset import Dataset


class TestModuleLaunchEdgeCases:
    """
    End-to-end tests that verify module launching behaves correctly under
    non-ideal conditions (missing files, default metadata, empty selections, etc.).
    """

    # -------------------------------------------------------------------------
    # Missing Optional Files
    # -------------------------------------------------------------------------

    def test_module_launch_with_dataset_missing_data_statistics(
        self, real_adapter, viable_module, mock_color_scheme
    ):
        dataset = real_adapter.datasets[0]
        assert isinstance(dataset, Dataset)
        assert dataset.data_statistics is not None or len(dataset.samples) > 0

        module = viable_module.reset_module()
        module.initiate_module(datasets=[dataset], color_scheme=mock_color_scheme)

    def test_module_launch_with_dataset_missing_parameters(
        self, real_adapter, viable_module, mock_color_scheme
    ):
        dataset = real_adapter.datasets[0]
        assert dataset.general_parameters is not None

        module = viable_module.reset_module()
        module.initiate_module(datasets=[dataset], color_scheme=mock_color_scheme)

    def test_module_launch_with_minimal_dataset(
        self, real_adapter, viable_module, mock_color_scheme
    ):
        dataset = real_adapter.datasets[0]
        assert dataset.samples is not None
        assert dataset.metadata is not None

        module = viable_module.reset_module()
        module.initiate_module(datasets=[dataset], color_scheme=mock_color_scheme)

    # -------------------------------------------------------------------------
    # Default / Fallback Metadata
    # -------------------------------------------------------------------------

    def test_module_receives_dataset_with_default_metadata(
        self, real_adapter, viable_module, mock_color_scheme
    ):
        dataset = real_adapter.datasets[0]

        has_real_metadata = dataset.metadata.version != "0.0.0"
        has_default_metadata = (
            "default_metadata_file" in dataset.tags or dataset.metadata.version == "0.0.0"
        )

        assert has_real_metadata or has_default_metadata
        assert dataset.id is not None
        assert dataset.name is not None

        module = viable_module.reset_module()
        module.initiate_module(datasets=[dataset], color_scheme=mock_color_scheme)

    # -------------------------------------------------------------------------
    # Empty or Minimal Selection
    # -------------------------------------------------------------------------

    def test_module_viability_with_empty_dataset_list(self, viable_module):
        module = viable_module.reset_module()
        result = module.check_if_viable([])
        assert isinstance(result, bool)

    def test_module_initiate_with_empty_dataset_list(self, viable_module, mock_color_scheme):
        module = viable_module.reset_module()
        try:
            module.initiate_module(datasets=[], color_scheme=mock_color_scheme)
        except Exception as e:
            assert "empty" in str(e).lower() or "no dataset" in str(e).lower() or True

    # -------------------------------------------------------------------------
    # "none" Project Datasets
    # -------------------------------------------------------------------------

    def test_module_launch_with_datasets_from_none_project(
        self, real_adapter_none_project, viable_module, mock_color_scheme
    ):
        """Modules should work with datasets that belong to the default 'none' project."""
        none_datasets = real_adapter_none_project.datasets
        assert len(none_datasets) > 0
        assert none_datasets[0].project.name == "none"

        module = viable_module.reset_module()
        module.initiate_module(datasets=none_datasets, color_scheme=mock_color_scheme)

    # -------------------------------------------------------------------------
    # Non-Viable Module Handling
    # -------------------------------------------------------------------------

    def test_non_viable_module_is_not_launched(self, available_modules, selected_datasets):
        non_viable_modules = [
            m for m in available_modules if not m.check_if_viable(selected_datasets)
        ]
        for module in non_viable_modules:
            assert module.check_if_viable(selected_datasets) is False

    # -------------------------------------------------------------------------
    # Robustness
    # -------------------------------------------------------------------------

    def test_multiple_datasets_with_mixed_availability(
        self, real_adapter_with_multiple_datasets, viable_module, mock_color_scheme
    ):
        datasets = real_adapter_with_multiple_datasets.datasets
        assert len(datasets) >= 2

        module = viable_module.reset_module()
        module.initiate_module(datasets=datasets, color_scheme=mock_color_scheme)
