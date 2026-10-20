import ipywidgets as widgets

from suplex.ui.pages.about_page import AboutPage


class TestAboutPage:
    """Tests for the AboutPage – a stateless informational page showing
    SUPLEX mission, license, version info, and credits.
    """

    # -------------------------------------------------------------------------
    # UI Rendering
    # -------------------------------------------------------------------------
    def test_about_page_renders_without_error(self, about_page, mock_scheme):
        """get_ui() returns a valid widget without raising exceptions."""
        ui = about_page.get_ui(mock_scheme)

        assert ui is not None
        assert isinstance(ui, widgets.VBox)

    def test_about_page_contains_all_sections(self, about_page, mock_scheme):
        """The main content VBox contains 7 real sections.
        WidgetFactory.vbox() inserts gap placeholders, so total children = 13.
        """
        ui = about_page.get_ui(mock_scheme)

        # Top-level container returned by get_ui() (the VBox from WidgetFactory.vbox)
        assert isinstance(ui, widgets.VBox)

        # 7 real sections + 6 gap placeholders = 13 children
        assert len(ui.children) == 13

    def test_reset_returns_new_instance(self):
        """reset() returns a fresh AboutPage instance (stateless page)."""
        page1 = AboutPage()
        page2 = page1.reset()

        assert isinstance(page2, AboutPage)
        assert page2 is not page1

    # -------------------------------------------------------------------------
    # Internal section builders (smoke tests)
    # -------------------------------------------------------------------------
    def test_create_section_title(self, about_page, mock_scheme):
        """create_section_title() produces a styled HTML label containing the title."""
        title = about_page.create_section_title("Test Title", mock_scheme)

        assert isinstance(title, widgets.HTML)
        assert "Test Title" in title.value
        assert "<h2" in title.value.lower()

    def test_create_about_section_contains_links(self, about_page, mock_scheme):
        """About section includes hyperlinks to GitHub and the MARTin paper."""
        section = about_page.create_about_section(mock_scheme)

        assert isinstance(section, widgets.HTML)
        assert "SUPLEX" in section.value
        assert "MARTin" in section.value
        assert "doi.org" in section.value  # paper link
