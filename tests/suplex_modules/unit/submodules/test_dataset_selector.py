from datetime import datetime
from unittest.mock import Mock, patch

import ipywidgets as widgets

from suplex.suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex.suplex_modules.submodules.submodule_constants import (
    DATASET_LABEL,
    DATASET_SELECTOR_MODE,
)


class TestDatasetSelector:
    """Tests for the DatasetSelector class (UI + selection logic)."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def test_init_default_mode(self, mock_datasets_with_labels):
        """Default initialization uses MULTIPLE_UNBOUND mode."""
        selector = DatasetSelector(datasets=mock_datasets_with_labels)
        assert selector._mode == DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND
        assert len(selector._checkboxes) == len(mock_datasets_with_labels)

    def test_init_single_mode(self, mock_datasets_with_labels):
        """SINGLE mode forces checkbox_limit = 1."""
        selector = DatasetSelector(
            datasets=mock_datasets_with_labels,
            mode=DATASET_SELECTOR_MODE.SINGLE,
        )
        assert selector._checkbox_limit == 1

    def test_init_bounded_mode(self, mock_datasets_with_labels):
        """MULTIPLE_BOUND respects custom checkbox_limit."""
        selector = DatasetSelector(
            datasets=mock_datasets_with_labels,
            mode=DATASET_SELECTOR_MODE.MULTIPLE_BOUND,
            checkbox_limit=3,
        )
        assert selector._checkbox_limit == 3

    # -------------------------------------------------------------------------
    # Label generation
    # -------------------------------------------------------------------------

    def test_get_dataset_label_various_parts(self):
        """Label generation respects different DATASET_LABEL combinations."""
        # Create properly mocked dataset to avoid fixture Mock(name=...) gotcha
        # (metadata.name and .pat_id must be strings, not child Mocks)
        ds = Mock()
        metadata = Mock()
        metadata.name = "Patient A"
        metadata.pat_id = "PAT001"
        ds.metadata = metadata
        ds.image_creation_date = datetime(2024, 1, 15)
        ds.measure_date = datetime(2024, 1, 20)

        selector = DatasetSelector(
            datasets=[ds],
            label_parts=[DATASET_LABEL.NAME, DATASET_LABEL.ID],
        )
        label = selector.get_dataset_label(ds)
        assert "Patient A" in label
        assert "PAT001" in label

    # -------------------------------------------------------------------------
    # Checkbox setup and queue logic
    # -------------------------------------------------------------------------

    def test_setup_checkboxes_creates_correct_mapping(self, dataset_selector):
        """Checkboxes are created and mapped correctly to datasets."""
        assert len(dataset_selector._checkboxes) == len(dataset_selector._datasets)
        assert len(dataset_selector._checkbox_dataset_map) == len(dataset_selector._datasets)

    def test_checkbox_change_adds_to_queue(self, dataset_selector):
        """Checking a checkbox adds it to the selection queue."""
        checkbox = dataset_selector._checkboxes[0]
        checkbox.value = True
        assert checkbox in dataset_selector._checkbox_queue

    def test_checkbox_change_removes_from_queue_on_uncheck(self, dataset_selector):
        """Unchecking removes from queue."""
        checkbox = dataset_selector._checkboxes[0]
        checkbox.value = True
        checkbox.value = False
        assert checkbox not in dataset_selector._checkbox_queue

    def test_bounded_mode_queue_limit(self, bounded_dataset_selector):
        """Bounded mode enforces limit and removes oldest selection."""
        checkboxes = bounded_dataset_selector._checkboxes
        checkboxes[0].value = True
        checkboxes[1].value = True
        checkboxes[2].value = True  # should trigger removal of first

        assert len(bounded_dataset_selector._checkbox_queue) == 2
        assert checkboxes[0].value is False  # oldest removed

    def test_select_all_only_in_unbounded_mode(self, dataset_selector, bounded_dataset_selector):
        """select_all only works in MULTIPLE_UNBOUND mode."""
        dataset_selector.select_all()
        assert all(cb.value for cb in dataset_selector._checkboxes)

        bounded_dataset_selector.select_all()
        assert not any(cb.value for cb in bounded_dataset_selector._checkboxes)

    # -------------------------------------------------------------------------
    # Selection logic
    # -------------------------------------------------------------------------

    def test_get_selected_datasets(self, dataset_selector):
        """Returns selected Dataset objects in queue order."""
        dataset_selector._checkboxes[0].value = True
        dataset_selector._checkboxes[2].value = True

        selected = dataset_selector.get_selected_datasets()
        assert len(selected) == 2
        assert selected[0] == dataset_selector._datasets[0]

    def test_clear_selection(self, dataset_selector):
        """clear_selection unchecks everything."""
        for cb in dataset_selector._checkboxes[:2]:
            cb.value = True
        dataset_selector.clear_selection()
        assert all(not cb.value for cb in dataset_selector._checkboxes)

    def test_select_datasets_and_deselect_datasets(self, dataset_selector):
        """Programmatic select/deselect works via checkbox mapping."""
        target = dataset_selector._datasets[1]
        dataset_selector.select_datasets([target])
        assert dataset_selector.get_checkbox_of_dataset(target).value is True

        dataset_selector.deselect_datasets([target])
        assert dataset_selector.get_checkbox_of_dataset(target).value is False

    def test_select_date_range_and_deselect_date_range(self, dataset_selector):
        """Date-range selection/deselection filters correctly."""
        start = datetime(2024, 1, 1).date()
        end = datetime(2024, 2, 28).date()

        dataset_selector.select_date_range(start, end, DATASET_LABEL.MEASURE_DATE.value)
        selected = dataset_selector.get_selected_datasets()
        assert len(selected) >= 2  # PAT001 and PAT002 are in range

        dataset_selector.deselect_date_range(start, end, DATASET_LABEL.MEASURE_DATE.value)
        assert dataset_selector.get_selected_count() == 0

    # -------------------------------------------------------------------------
    # UI and widget behavior
    # -------------------------------------------------------------------------

    def test_get_ui_element(self, dataset_selector):
        """UI should return a VBox containing header and checkboxes."""
        ui = dataset_selector.get_ui_element()
        assert isinstance(ui, widgets.VBox)
        # WidgetFactory.vbox adds extra wrapper/layout elements → exact len(children) is brittle
        children = list(ui.children)
        assert any(isinstance(c, widgets.HTML) for c in children)  # header present
        checkbox_children = [c for c in children if isinstance(c, widgets.Checkbox)]
        assert len(checkbox_children) == len(dataset_selector._checkboxes)

    def test_update_dataset_labels(self, dataset_selector):
        """Changing label_parts updates all checkbox descriptions."""
        # Patch get_dataset_label to avoid fixture Mock issues and verify update logic
        with patch.object(dataset_selector, "get_dataset_label", return_value="Updated Label"):
            old_labels = [cb.description for cb in dataset_selector._checkboxes]
            dataset_selector.update_dataset_labels([DATASET_LABEL.ID, DATASET_LABEL.NAME])
            new_labels = [cb.description for cb in dataset_selector._checkboxes]

            assert old_labels != new_labels
            assert new_labels[0] == "Updated Label"

    def test_get_checkboxes_returns_copy(self, dataset_selector):
        """get_checkboxes returns a copy to prevent external mutation."""
        checkboxes = dataset_selector.get_checkboxes()
        assert checkboxes is not dataset_selector._checkboxes
        assert len(checkboxes) == len(dataset_selector._checkboxes)
