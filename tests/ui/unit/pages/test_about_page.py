import pytest
from src.ui.pages.about_page import AboutPage
import ipywidgets as widgets
from unittest.mock import patch


class TestAboutPage:
    """
    Since the about page is just styled text which provides almost no interactivity (save for hyperlinks) testing is kept to a bare minimum.
    """

    def test_about_page_renders_without_error(self, mock_scheme):
        page = AboutPage()
        ui = page.get_ui(mock_scheme)
        assert ui is not None

    def test_about_page_contains_all_sections(self, mock_scheme):
        page = AboutPage()
        ui = page.get_ui(mock_scheme)

        assert isinstance(ui, widgets.VBox)
        assert len(ui.children) == 1

        main_content = ui.children[0]
        assert isinstance(main_content, widgets.VBox)

        sections = main_content.children
        assert len(sections) == 7
