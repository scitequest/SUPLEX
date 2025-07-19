import pytest
from enum import Enum

from ui.ui_constants import PAGE, SCHEME_FIELDS


class TestUIConstants:
    def test_page_enum(self):
        assert issubclass(PAGE, Enum)

        assert PAGE.ABOUT.value == "about"
        assert PAGE.DIRECTORY_SELECTION.value == "directory_selection"
        assert PAGE.DATASET_SELECTION.value == "dataset_selection"
        assert PAGE.MODULE_SELECTION.value == "module_selection"
        assert PAGE.MODULE.value == "module"

        assert len(PAGE) == 5

    def test_scheme_fields_structure(self):
        assert isinstance(SCHEME_FIELDS, dict)

        assert "NAME" in SCHEME_FIELDS
        assert "TEXT" in SCHEME_FIELDS
        assert "LAYOUT_COLOR" in SCHEME_FIELDS
        assert "ICON" in SCHEME_FIELDS
        assert "OPACITY" in SCHEME_FIELDS

        assert SCHEME_FIELDS["NAME"] == str
        assert isinstance(SCHEME_FIELDS["TEXT"], dict)
        assert isinstance(SCHEME_FIELDS["LAYOUT_COLOR"], dict)
        assert isinstance(SCHEME_FIELDS["ICON"], dict)
        assert isinstance(SCHEME_FIELDS["OPACITY"], dict)

    def test_scheme_fields_text_structure(self):
        text_fields = SCHEME_FIELDS["TEXT"]

        assert "FONT" in text_fields
        assert "SIZE" in text_fields
        assert "WEIGHT" in text_fields
        assert "STYLE" in text_fields
        assert "COLOR" in text_fields

        font_fields = text_fields["FONT"]
        assert font_fields["MAIN_TITLE"] == str
        assert font_fields["HEADER"] == str
        assert font_fields["SUB_HEADER"] == str
        assert font_fields["SUB_SUB_HEADER"] == str
        assert font_fields["DEFAULT"] == str
        assert font_fields["LABEL"] == str

        color_fields = text_fields["COLOR"]
        assert isinstance(color_fields["INFO_FIELD"], dict)
        assert isinstance(color_fields["WIDGET"], dict)
        assert isinstance(color_fields["NAVIGATOR"], dict)

    def test_scheme_fields_layout_color_structure(self):
        layout_fields = SCHEME_FIELDS["LAYOUT_COLOR"]

        assert layout_fields["BACKGROUND"] == str
        assert layout_fields["HEADER"] == str
        assert layout_fields["HEADER_GRADIENT"] == str
        assert layout_fields["BODY"] == str
        assert layout_fields["CONTRAST"] == str

        assert isinstance(layout_fields["NAVIGATOR"], dict)
        assert isinstance(layout_fields["POPUP_LOGGER"], dict)
        assert isinstance(layout_fields["INFO_FIELD"], dict)
        assert isinstance(layout_fields["WIDGET"], dict)

        nav_fields = layout_fields["NAVIGATOR"]
        assert nav_fields["BACKGROUND"] == str
        assert nav_fields["PANEL"] == str
        assert nav_fields["BORDER"] == str
        assert nav_fields["SHADOW"] == str
        assert nav_fields["GLOW"] == str
        assert isinstance(nav_fields["STEP"], dict)

        widget_fields = layout_fields["WIDGET"]
        assert isinstance(widget_fields["BUTTON"], dict)
        assert isinstance(widget_fields["INPUT"], dict)
        assert isinstance(widget_fields["CHECKBOX"], dict)
        assert isinstance(widget_fields["SLIDER"], dict)
        assert isinstance(widget_fields["PROGRESS"], dict)
        assert isinstance(widget_fields["TAB"], dict)
        assert isinstance(widget_fields["ACCORDION"], dict)
        assert isinstance(widget_fields["OUTPUT"], dict)
        assert isinstance(widget_fields["DROPDOWN"], dict)

    def test_scheme_fields_icon_structure(self):
        icon_fields = SCHEME_FIELDS["ICON"]

        assert icon_fields["DEFAULT"] == str
        assert icon_fields["INFO"] == str
        assert icon_fields["SUCCESS"] == str
        assert icon_fields["WARNING"] == str
        assert icon_fields["ERROR"] == str
        assert icon_fields["CRITICAL"] == str
        assert icon_fields["DEBUG"] == str
        assert icon_fields["CLEAR"] == str
        assert icon_fields["STORE"] == str
        assert icon_fields["SAVE"] == str
        assert icon_fields["CLOSE"] == str
        assert icon_fields["FORWARD"] == str
        assert icon_fields["BACKWARD"] == str
        assert icon_fields["SEPARATOR"] == str
        assert icon_fields["CALENDAR"] == str

        assert isinstance(icon_fields["PAGE"], dict)
        assert isinstance(icon_fields["IMAGE_PATH"], dict)
        assert isinstance(icon_fields["SVG"], dict)

        page_icons = icon_fields["PAGE"]
        assert page_icons["DIRECTORY_SELECTION"] == str
        assert page_icons["DATASET_SELECTION"] == str
        assert page_icons["MODULE_SELECTION"] == str
        assert page_icons["MODULE"] == str

    def test_scheme_fields_opacity_structure(self):
        opacity_fields = SCHEME_FIELDS["OPACITY"]

        assert opacity_fields["FULL"] == float
        assert opacity_fields["STRONG"] == float
        assert opacity_fields["MEDIUM"] == float
        assert opacity_fields["MODERATE"] == float
        assert opacity_fields["SUBTLE"] == float
        assert opacity_fields["FAINT"] == float
        assert opacity_fields["BARELY"] == float
        assert opacity_fields["HIDDEN"] == float

    def test_scheme_fields_completeness(self):
        text_widget_colors = SCHEME_FIELDS["TEXT"]["COLOR"]["WIDGET"]
        assert isinstance(text_widget_colors["BUTTON"], dict)
        assert isinstance(text_widget_colors["INPUT"], dict)
        assert isinstance(text_widget_colors["TAB"], dict)

        button_colors = text_widget_colors["BUTTON"]
        expected_button_types = [
            "NAVIGATION",
            "DEFAULT",
            "EMPHASIS",
            "SUCCESS",
            "DANGER",
            "WARNING",
            "OPTIONS_LIGHT",
            "OPTIONS_DARK",
            "INACTIVE",
        ]
        for button_type in expected_button_types:
            assert button_type in button_colors
            assert button_colors[button_type] == str

        # Info field colors
        info_colors = SCHEME_FIELDS["TEXT"]["COLOR"]["INFO_FIELD"]
        expected_info_types = [
            "DEFAULT",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "DEBUG",
        ]
        for info_type in expected_info_types:
            assert info_type in info_colors
            assert info_colors[info_type] == str

    def test_scheme_fields_widget_input_structure(self):
        input_colors = SCHEME_FIELDS["LAYOUT_COLOR"]["WIDGET"]["INPUT"]
        assert isinstance(input_colors["BACKGROUND"], dict)
        assert isinstance(input_colors["BORDER"], dict)

        bg_states = input_colors["BACKGROUND"]
        assert bg_states["DEFAULT"] == str
        assert bg_states["DISABLED"] == str
        assert bg_states["FOCUS"] == str

        border_states = input_colors["BORDER"]
        assert border_states["DEFAULT"] == str
        assert border_states["FOCUS"] == str
        assert border_states["ERROR"] == str
