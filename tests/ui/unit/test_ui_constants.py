import pytest
from enum import Enum

from ui.ui_constants import PAGE, SCHEME_FIELDS


class TestUIConstants:
    """Tests for the UI constants module (PAGE enum and SCHEME_FIELDS schema definition)."""

    # -------------------------------------------------------------------------
    # PAGE Enum
    # -------------------------------------------------------------------------
    def test_page_enum(self):
        """PAGE is a proper Enum with exactly the expected members and values."""
        assert issubclass(PAGE, Enum)

        assert PAGE.ABOUT.value == "about"
        assert PAGE.DIRECTORY_SELECTION.value == "directory_selection"
        assert PAGE.DATASET_SELECTION.value == "dataset_selection"
        assert PAGE.MODULE_SELECTION.value == "module_selection"
        assert PAGE.MODULE.value == "module"

        assert len(PAGE) == 5
        assert {member.value for member in PAGE} == {
            "about",
            "directory_selection",
            "dataset_selection",
            "module_selection",
            "module",
        }

    # -------------------------------------------------------------------------
    # SCHEME_FIELDS – High-level structure
    # -------------------------------------------------------------------------
    def test_scheme_fields_is_dict_with_all_top_level_keys(self):
        """SCHEME_FIELDS is a dict containing all required top-level sections."""
        assert isinstance(SCHEME_FIELDS, dict)

        expected_top_level = {"NAME", "TEXT", "LAYOUT_COLOR", "ICON", "OPACITY"}
        assert set(SCHEME_FIELDS.keys()) == expected_top_level

        assert SCHEME_FIELDS["NAME"] == str

    # -------------------------------------------------------------------------
    # TEXT section
    # -------------------------------------------------------------------------
    def test_scheme_fields_text_structure(self):
        """TEXT section contains all required font, size, weight, style and color sub-structures."""
        text_fields = SCHEME_FIELDS["TEXT"]

        assert isinstance(text_fields, dict)
        assert {"FONT", "SIZE", "WEIGHT", "STYLE", "COLOR"}.issubset(text_fields.keys())

        # FONT
        font = text_fields["FONT"]
        assert all(
            font[key] == str
            for key in ("MAIN_TITLE", "HEADER", "SUB_HEADER", "SUB_SUB_HEADER", "DEFAULT", "LABEL")
        )

        # COLOR – nested structures
        color = text_fields["COLOR"]
        assert isinstance(color["INFO_FIELD"], dict)
        assert isinstance(color["WIDGET"], dict)
        assert isinstance(color["NAVIGATOR"], dict)

    # -------------------------------------------------------------------------
    # LAYOUT_COLOR section
    # -------------------------------------------------------------------------
    def test_scheme_fields_layout_color_structure(self):
        """LAYOUT_COLOR contains all required layout and widget color definitions."""
        layout = SCHEME_FIELDS["LAYOUT_COLOR"]

        # Top-level layout colors
        for key in ("BACKGROUND", "HEADER", "HEADER_GRADIENT", "BODY", "CONTRAST"):
            assert layout[key] == str

        # Nested sections
        assert isinstance(layout["NAVIGATOR"], dict)
        assert isinstance(layout["POPUP_LOGGER"], dict)
        assert isinstance(layout["INFO_FIELD"], dict)
        assert isinstance(layout["WIDGET"], dict)

        # NAVIGATOR
        nav = layout["NAVIGATOR"]
        for key in ("BACKGROUND", "PANEL", "BORDER", "SHADOW", "GLOW"):
            assert nav[key] == str
        assert isinstance(nav["STEP"], dict)

        # WIDGET
        widget = layout["WIDGET"]
        for section in (
            "BUTTON",
            "INPUT",
            "CHECKBOX",
            "SLIDER",
            "PROGRESS",
            "TAB",
            "ACCORDION",
            "OUTPUT",
            "DROPDOWN",
        ):
            assert isinstance(widget[section], dict)

    # -------------------------------------------------------------------------
    # ICON section
    # -------------------------------------------------------------------------
    def test_scheme_fields_icon_structure(self):
        """ICON section defines all required icons and nested icon groups."""
        icon = SCHEME_FIELDS["ICON"]

        simple_icons = {
            "DEFAULT",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "DEBUG",
            "CLEAR",
            "STORE",
            "SAVE",
            "CLOSE",
            "FORWARD",
            "BACKWARD",
            "SEPARATOR",
            "CALENDAR",
        }
        for name in simple_icons:
            assert icon[name] == str

        assert isinstance(icon["PAGE"], dict)
        assert isinstance(icon["IMAGE_PATH"], dict)
        assert isinstance(icon["SVG"], dict)

        page = icon["PAGE"]
        assert page["DIRECTORY_SELECTION"] == str
        assert page["DATASET_SELECTION"] == str
        assert page["MODULE_SELECTION"] == str
        assert page["MODULE"] == str

    # -------------------------------------------------------------------------
    # OPACITY section
    # -------------------------------------------------------------------------
    def test_scheme_fields_opacity_structure(self):
        """OPACITY section contains all required float values."""
        opacity = SCHEME_FIELDS["OPACITY"]

        expected_opacities = {
            "FULL",
            "STRONG",
            "MEDIUM",
            "MODERATE",
            "SUBTLE",
            "FAINT",
            "BARELY",
            "HIDDEN",
        }
        assert set(opacity.keys()) == expected_opacities

        for key in expected_opacities:
            assert opacity[key] == float

    # -------------------------------------------------------------------------
    # Completeness checks (deeper validation)
    # -------------------------------------------------------------------------
    def test_scheme_fields_widget_button_colors(self):
        """All button color variants are defined under TEXT.COLOR.WIDGET.BUTTON."""
        button_colors = SCHEME_FIELDS["TEXT"]["COLOR"]["WIDGET"]["BUTTON"]
        expected = {
            "NAVIGATION",
            "DEFAULT",
            "EMPHASIS",
            "SUCCESS",
            "DANGER",
            "WARNING",
            "OPTIONS_LIGHT",
            "OPTIONS_DARK",
            "INACTIVE",
        }
        assert set(button_colors.keys()) == expected
        assert all(v == str for v in button_colors.values())

    def test_scheme_fields_info_field_colors(self):
        """All info field status colors are defined under both TEXT.COLOR.INFO_FIELD and LAYOUT_COLOR.INFO_FIELD."""
        # TEXT section
        text_info = SCHEME_FIELDS["TEXT"]["COLOR"]["INFO_FIELD"]
        expected = {"DEFAULT", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL", "DEBUG"}
        assert set(text_info.keys()) == expected
        assert all(v == str for v in text_info.values())

        # LAYOUT_COLOR section
        layout_info = SCHEME_FIELDS["LAYOUT_COLOR"]["INFO_FIELD"]
        assert set(layout_info.keys()) == expected
        assert all(v == str for v in layout_info.values())

    def test_scheme_fields_widget_input_structure(self):
        """INPUT widget colors have the expected nested BACKGROUND and BORDER structures."""
        input_def = SCHEME_FIELDS["LAYOUT_COLOR"]["WIDGET"]["INPUT"]

        assert isinstance(input_def["BACKGROUND"], dict)
        assert isinstance(input_def["BORDER"], dict)

        for key in ("DEFAULT", "DISABLED", "FOCUS"):
            assert input_def["BACKGROUND"][key] == str

        for key in ("DEFAULT", "FOCUS", "ERROR"):
            assert input_def["BORDER"][key] == str
