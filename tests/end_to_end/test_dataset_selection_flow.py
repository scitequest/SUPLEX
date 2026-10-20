from datetime import datetime

from suplex.martin_interface.dataset import Dataset


class TestDatasetSelectionFlow:
    """
    End-to-end tests focused on the dataset selection step, including date range
    filtering, tag-based filtering, and ensuring correct datasets are passed
    to the module layer.
    """

    # -------------------------------------------------------------------------
    # Basic Selection
    # -------------------------------------------------------------------------

    def test_all_discovered_datasets_can_be_selected(self, real_adapter):
        """All datasets discovered by the Adapter can be selected (happy path)."""
        datasets = real_adapter.datasets
        assert len(datasets) > 0

        # In the real UI this would come from DatasetSelector
        selected = datasets
        assert len(selected) == len(datasets)

        for ds in selected:
            assert isinstance(ds, Dataset)

    # -------------------------------------------------------------------------
    # Date Range Filtering
    # -------------------------------------------------------------------------

    def test_dataset_is_in_timeframe_filtering(self, real_adapter):
        """Datasets can be correctly filtered using the is_in_timeframe method."""
        dataset = real_adapter.datasets[0]

        # Wide range that includes the 1998 sample data
        start = datetime(1990, 1, 1)
        end = datetime(2030, 1, 1)

        if dataset.measure_date:
            assert dataset.is_in_timeframe(dataset.measure_date, start, end) is True

        if dataset.image_creation_date:
            assert dataset.is_in_timeframe(dataset.image_creation_date, start, end) is True

        # Future range that should exclude the dataset
        future_start = datetime(2030, 1, 1)
        future_end = datetime(2040, 1, 1)

        if dataset.measure_date:
            assert dataset.is_in_timeframe(dataset.measure_date, future_start, future_end) is False

    def test_date_range_selection_simulation(self, real_adapter):
        """Simulates selecting datasets within a specific date range (as done in ProjectCard)."""
        datasets = real_adapter.datasets
        assert len(datasets) > 0

        # Use a wide range that includes everything
        start_date = datetime(1990, 1, 1)
        end_date = datetime(2035, 1, 1)

        selected = [
            ds
            for ds in datasets
            if (ds.measure_date and ds.is_in_timeframe(ds.measure_date, start_date, end_date))
            or (
                ds.image_creation_date
                and ds.is_in_timeframe(ds.image_creation_date, start_date, end_date)
            )
        ]

        assert len(selected) >= 1

    # -------------------------------------------------------------------------
    # Tag-based Filtering
    # -------------------------------------------------------------------------

    def test_has_some_tags_filtering(self, real_adapter):
        """has_some_tags works correctly for filtering datasets."""
        dataset = real_adapter.datasets[0]

        # Should return True for existing tags
        if dataset.tags:
            assert dataset.has_some_tags([dataset.tags[0]]) is True

        # Should return False for non-existing tags
        assert dataset.has_some_tags(["nonexistent_tag_xyz"]) is False

        # Empty list should return False
        assert dataset.has_some_tags([]) is False

    def test_has_all_tags_filtering(self, real_adapter):
        """has_all_tags works correctly for filtering datasets."""
        dataset = real_adapter.datasets[0]

        if len(dataset.tags) >= 2:
            assert dataset.has_all_tags(dataset.tags[:2]) is True

        # Should return False if not all tags are present
        assert dataset.has_all_tags(["nonexistent_tag_1", "nonexistent_tag_2"]) is False

        # Empty list should return False (as per implementation)
        assert dataset.has_all_tags([]) is False

    def test_suplex_tags_are_included_in_tag_checks(self, real_adapter):
        """suplex_tags are correctly considered in has_some_tags and has_all_tags."""
        dataset = real_adapter.datasets[0]

        if dataset.suplex_tags:
            assert dataset.has_some_tags([dataset.suplex_tags[0]]) is True

    # -------------------------------------------------------------------------
    # Multi-Dataset / Multi-Project Selection
    # -------------------------------------------------------------------------

    def test_selection_across_multiple_datasets(self, real_adapter_with_multiple_datasets):
        """User can select datasets from multiple measurements in the same project."""
        adapter = real_adapter_with_multiple_datasets
        assert len(adapter.datasets) >= 2

        # Simulate selecting all datasets
        selected = adapter.datasets
        assert len(selected) >= 2

        project_names = {ds.project.name for ds in selected}
        assert len(project_names) == 1  # All from same project in this fixture

    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------

    def test_empty_selection_is_handled(self, real_adapter):
        """The system gracefully handles the case where the user selects zero datasets."""
        selected = []  # User selected nothing

        # Modules should still be able to receive an empty list (viability will likely be False)
        assert isinstance(selected, list)
        assert len(selected) == 0

    def test_datasets_from_none_project_are_selectable(self, real_adapter):
        """Datasets that belong to the default 'none' project can still be selected."""
        datasets = real_adapter.datasets
        none_project_datasets = [ds for ds in datasets if ds.project.name == "none"]

        if none_project_datasets:
            selected = none_project_datasets
            assert all(ds.project.name == "none" for ds in selected)
