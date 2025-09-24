from enum import Enum

"""
A collection of constants generally associatet with the user interface.
"""


class PAGE(Enum):
    """
    Enumeration of page identifiers used to swap between them.
    Pages and modules both fill the content holder of `gui`.

    Defines the strategies for searching directories:
    - ABOUT: page containing information on the SUPLEX project.
    - DIRECTORY_SELECTION: page allows users to select a directory to search MARTin datasets in.
    - DATASET_SELECTION: page for sub-selecting MARTin datasets.
    - MODULE_SELECTION: this page allows to load modules with the subselected datasets.
    - MODULE: signifies that a module is active.
    """

    ABOUT = "about"
    DIRECTORY_SELECTION = "directory_selection"
    DATASET_SELECTION = "dataset_selection"
    MODULE_SELECTION = "module_selection"
    MODULE = "module"


# Abstract format of color scheme files.
# In order for a scheme to be usable it has to adhere to this format.
SCHEME_FIELDS = {
    "NAME": str,
    "TEXT": {
        "FONT": {
            "MAIN_TITLE": str,
            "HEADER": str,
            "SUB_HEADER": str,
            "SUB_SUB_HEADER": str,
            "DEFAULT": str,
            "LABEL": str,
        },
        "SIZE": {
            "MAIN_TITLE": str,
            "HEADER": str,
            "SUB_HEADER": str,
            "SUB_SUB_HEADER": str,
            "DEFAULT": str,
            "LABEL": str,
            "POPUP_LOGGER_CLOSE_ICON": str,
        },
        "WEIGHT": {"BOLD": str, "MEDIUM": str, "DEFAULT": str, "LIGHT": str},
        "STYLE": {"DEFAULT": str, "ITALIC": str, "OBLIQUE": str},
        "COLOR": {
            "MAIN_TITLE": str,
            "HEADER": str,
            "SUB_HEADER": str,
            "SUB_SUB_HEADER": str,
            "DEFAULT": str,
            "LABEL": str,
            "LOGGER_TITLE": str,
            "LOGGER_LOG_TEXT": str,
            "LOGGER_CLOSE_BUTTON": str,
            "EMPHASIZE": str,
            "SUBTLE": str,
            "MUTED": str,
            "HYPERLINK": str,
            "LIGHT": str,
            "LIGHT_ALT": str,
            "NAVIGATOR_ARROW": str,
            "NAVIGATOR_STEP": str,
            "NAVIGATOR": {"ARROW": str, "STEP": str},
            "INFO_FIELD": {
                "DEFAULT": str,
                "INFO": str,
                "SUCCESS": str,
                "WARNING": str,
                "ERROR": str,
                "CRITICAL": str,
                "DEBUG": str,
            },
            "WIDGET": {
                "BUTTON": {
                    "NAVIGATION": str,
                    "DEFAULT": str,
                    "EMPHASIS": str,
                    "SUCCESS": str,
                    "DANGER": str,
                    "WARNING": str,
                    "OPTIONS_LIGHT": str,
                    "OPTIONS_DARK": str,
                    "INACTIVE": str,
                },
                "INPUT": {"DEFAULT": str, "DISABLED": str, "PLACEHOLDER": str},
                "TAB": {"TITLE": str, "BODY": str},
                "ACCORDION": str,
                "OUTPUT": str,
                "DROPDOWN": str,
            },
            "TABLE": {
                "HEAD": str,
                "BODY": str,
                "EMPHASIS": str,
            },
        },
    },
    "LAYOUT_COLOR": {
        "BACKGROUND": str,
        "HEADER": str,
        "HEADER_GRADIENT": str,
        "BODY": str,
        "CONTRAST": str,
        "NAVIGATOR": {
            "BACKGROUND": str,
            "PANEL": str,
            "BORDER": str,
            "SHADOW": str,
            "GLOW": str,
            "STEP": {"COMPLETED": str, "ACTIVE": str, "AVAILABLE": str, "LOCKED": str},
        },
        "POPUP_LOGGER": {
            "BACKGROUND": str,
            "PANEL": str,
            "BORDER": str,
            "SHADOW": str,
            "GLOW": str,
            "LAYOUT_LINE": str,
            "LOG_LINE": str,
            "LOG_LEVEL": {
                "DEFAULT": str,
                "INFO": str,
                "SUCCESS": str,
                "WARNING": str,
                "ERROR": str,
                "CRITICAL": str,
                "DEBUG": str,
            },
        },
        "INFO_FIELD": {
            "DEFAULT": str,
            "INFO": str,
            "SUCCESS": str,
            "WARNING": str,
            "ERROR": str,
            "CRITICAL": str,
            "DEBUG": str,
        },
        "WIDGET": {
            "BUTTON": {
                "DEFAULT": str,
                "EMPHASIS": str,
                "SUCCESS": str,
                "DANGER": str,
                "WARNING": str,
                "OPTIONS_LIGHT": str,
                "OPTIONS_DARK": str,
                "INACTIVE": str,
            },
            "INPUT": {
                "BACKGROUND": {"DEFAULT": str, "DISABLED": str, "FOCUS": str},
                "BORDER": {"DEFAULT": str, "FOCUS": str, "ERROR": str},
            },
            "CHECKBOX": {
                "BACKGROUND": str,
                "BORDER": str,
                "CHECKED": str,
                "FOCUS": str,
            },
            "SLIDER": {"TRACK": str, "HANDLE": str, "RANGE": str},
            "PROGRESS": {"BACKGROUND": str, "BAR": str},
            "TAB": {"BACKGROUND": str, "ACTIVE": str, "HOVER": str, "PANEL": str},
            "ACCORDION": {"PANEL": str, "LINES": str},
            "OUTPUT": {"BACKGROUND": str, "BORDER": str},
            "DROPDOWN": {"BACKGROUND": str, "BORDER": str},
        },
        "TABLE": {
            "HEAD": str,
            "LINES": str,
        },
    },
    "ICON": {
        "DEFAULT": str,
        "INFO": str,
        "SUCCESS": str,
        "WARNING": str,
        "ERROR": str,
        "CRITICAL": str,
        "DEBUG": str,
        "CLEAR": str,
        "STORE": str,
        "SAVE": str,
        "CLOSE": str,
        "FORWARD": str,
        "BACKWARD": str,
        "SEPARATOR": str,
        "CALENDAR": str,
        "PAGE": {
            "DIRECTORY_SELECTION": str,
            "DATASET_SELECTION": str,
            "MODULE_SELECTION": str,
            "MODULE": str,
        },
        "IMAGE_PATH": {"SUPLEX": str, "MARTIN": str},
        "SVG": {
            "GITHUB": str,
            "X": str,
        },
    },
    "OPACITY": {
        "FULL": float,
        "STRONG": float,
        "MEDIUM": float,
        "MODERATE": float,
        "SUBTLE": float,
        "FAINT": float,
        "BARELY": float,
        "HIDDEN": float,
    },
}
