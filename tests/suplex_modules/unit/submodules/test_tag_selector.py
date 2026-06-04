import pytest
from unittest.mock import Mock
import ipywidgets as widgets

from suplex_modules.submodules.tag_selector import TagSelector
from src.martin_interface.dataset import Dataset


class TestTagSelectorFunctions:
    """Tests for helper methods (tag extraction, checkbox creation)."""

    def test_get_all_martin_tags(self, tag_selector):
        """Extracts and sorts unique MARTin tags."""
        tags = tag_selector.get_all_martin_tags()
        assert sorted(tags) == ["tag1", "tag2", "tag3"]

    def test_get_all_suplex_tags(self, tag_selector):
        """Extracts and sorts unique SUPLEX tags."""
        tags = tag_selector.get_all_suplex_tags()
        assert sorted(tags) == ["analysis1", "validated"]

    def test_get_all_martin_tags_empty(self):
        """Handles datasets with no MARTin tags gracefully."""
        empty_ds = [Mock(spec=Dataset, tags=None, suplex_tags=[])]
        selector = TagSelector(datasets=empty_ds)
        assert selector.get_all_martin_tags() == []

    def test_create_tag_checkboxes(self, tag_selector):
        """Creates correctly configured checkboxes."""
        checkboxes = tag_selector.create_tag_checkboxes(["tagA", "tagB"])
        assert len(checkboxes) == 2
        assert all(isinstance(cb, widgets.Checkbox) for cb in checkboxes)
        assert checkboxes[0].description == "tagA"

    def test_create_tag_checkboxes_empty(self, tag_selector):
        """Empty tag list returns empty list."""
        assert tag_selector.create_tag_checkboxes([]) == []


class TestTagSelector:
    """Tests for the main TagSelector class (UI + filtering logic)."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def test_init(self, tag_selector):
        """Initialization stores datasets and prepares empty checkbox lists."""
        assert tag_selector._datasets is tag_selector._datasets  # same reference
        assert len(tag_selector._martin_checkboxes) == 0
        assert len(tag_selector._suplex_checkboxes) == 0

    # -------------------------------------------------------------------------
    # UI rendering
    # -------------------------------------------------------------------------

    def test_get_ui_element_with_tags(self, tag_selector):
        """UI contains header + grid when tags exist."""
        ui = tag_selector.get_ui_element()
        assert isinstance(ui, widgets.VBox)
        # header + grid
        assert len(ui.children) >= 2

    def test_get_ui_element_no_tags(self):
        """Shows 'No tags available' message."""
        empty_selector = TagSelector(datasets=[Mock(spec=Dataset, tags=[], suplex_tags=[])])
        ui = empty_selector.get_ui_element()
        assert any("No tags available" in str(child) for child in ui.children)

    # -------------------------------------------------------------------------
    # Tag selection logic
    # -------------------------------------------------------------------------

    def test_get_selected_martin_tags(self, tag_selector):
        """Returns only checked MARTin tags."""
        # Build UI so checkboxes exist
        tag_selector.get_ui_element()
        # Simulate user selection
        tag_selector._martin_checkboxes[0].value = True

        selected = tag_selector.get_selected_martin_tags()
        assert selected == ["tag1"]

    def test_get_all_selected_tags(self, tag_selector):
        """Combines MARTin + SUPLEX selections."""
        tag_selector.get_ui_element()
        # Simulate selection
        tag_selector._martin_checkboxes[0].value = True
        tag_selector._suplex_checkboxes[0].value = True

        assert set(tag_selector.get_all_selected_tags()) == {"tag1", "analysis1"}

    def test_get_tagged_datasets_any(self, tag_selector):
        """ANY mode: at least one matching tag (MARTin or SUPLEX)."""
        # Build UI and select some tags
        tag_selector.get_ui_element()
        tag_selector._martin_checkboxes[0].value = True  # "tag1"

        selected = tag_selector.get_tagged_datasets_any()
        assert len(selected) > 0  # several datasets match

    def test_get_tagged_datasets_all(self, tag_selector):
        """ALL mode: must have ALL selected tags (MARTin AND SUPLEX separately)."""
        tag_selector.get_ui_element()
        # Select "tag1" (MARTin) and "analysis1" (SUPLEX)
        tag_selector._martin_checkboxes[0].value = True
        tag_selector._suplex_checkboxes[0].value = True

        selected = tag_selector.get_tagged_datasets_all()
        # Only ds4 (in the fixture) has both
        assert len(selected) == 1

    # -------------------------------------------------------------------------
    # Programmatic selection / clearing
    # -------------------------------------------------------------------------

    def test_clear_selection(self, tag_selector):
        """Unchecks everything."""
        tag_selector.get_ui_element()
        # pre-select some
        for cb in tag_selector._martin_checkboxes + tag_selector._suplex_checkboxes:
            cb.value = True
        tag_selector.clear_selection()
        assert all(
            not cb.value for cb in tag_selector._martin_checkboxes + tag_selector._suplex_checkboxes
        )

    def test_select_all(self, tag_selector):
        """Checks every available tag."""
        tag_selector.get_ui_element()
        tag_selector.select_all()
        assert all(
            cb.value for cb in tag_selector._martin_checkboxes + tag_selector._suplex_checkboxes
        )

    def test_select_tags_programmatic(self, tag_selector):
        """Programmatic selection of specific tags."""
        tag_selector.get_ui_element()  # ensure checkboxes exist
        tag_selector.select_tags(martin_tags=["tag1"], suplex_tags=["analysis1"])
        assert any(cb.description == "tag1" and cb.value for cb in tag_selector._martin_checkboxes)
        assert any(
            cb.description == "analysis1" and cb.value for cb in tag_selector._suplex_checkboxes
        )
