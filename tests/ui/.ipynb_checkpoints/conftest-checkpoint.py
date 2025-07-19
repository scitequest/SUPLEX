import pytest
import logging
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path
from datetime import datetime, date
import ipywidgets as widgets

from src.ui.gui import GUI
from src.ui.ui_constants import PAGE
from src.ui.pages.about_page import AboutPage
from src.ui.pages.module_selection_page import ModuleSelectionPage
from src.ui.pages.directory_selection_page import DirectorySelectionPage, SEARCH_MODE
from src.ui.pages.dataset_selection_page import DatasetSelectionPage, ProjectCard
from src.ui.elements.popup_log_system import PopupLogger, PopupLogHandler
from src.ui.elements.navigator import Navigator
from src.ui.elements.header import Header

@pytest.fixture
def mock_scheme_class():
    scheme_class = type("TestScheme", (), {})
    scheme_class.__module__ = "test_module"
    scheme_class.NAME = "TestScheme"

    text_class = type("TEXT", (), {})
    text_class.FONT = {"MAIN_TITLE": "Arial", "DEFAULT": "Helvetica"}
    text_class.SIZE = {"MAIN_TITLE": "24px", "DEFAULT": "14px"}
    text_class.WEIGHT = {"BOLD": "bold", "DEFAULT": "normal"}
    text_class.STYLE = {"DEFAULT": "normal", "ITALIC": "italic"}
    text_class.COLOR = {"DEFAULT": "#000000", "EMPHASIZE": "#0066CC"}
    scheme_class.TEXT = text_class

    layout_color_class = type("LAYOUT_COLOR", (), {})
    layout_color_class.BACKGROUND = "#FFFFFF"
    scheme_class.LAYOUT_COLOR = layout_color_class

    icon_class = type("ICON", (), {})
    icon_class.DEFAULT = "📄"
    scheme_class.ICON = icon_class

    opacity_class = type("OPACITY", (), {})
    opacity_class.FULL = 1.0
    scheme_class.OPACITY = opacity_class

    return scheme_class


@pytest.fixture
def mock_scheme():
    scheme = Mock()
    scheme.NAME = "TestScheme"

    scheme.TEXT = Mock()
    scheme.TEXT.FONT = Mock()
    scheme.TEXT.FONT.MAIN_TITLE = "Arial"
    scheme.TEXT.FONT.HEADER = "Arial"
    scheme.TEXT.FONT.SUB_HEADER = "Arial"
    scheme.TEXT.FONT.SUB_SUB_HEADER = "Arial"
    scheme.TEXT.FONT.DEFAULT = "Helvetica"
    scheme.TEXT.FONT.LABEL = "Helvetica"

    scheme.TEXT.SIZE = Mock()
    scheme.TEXT.SIZE.MAIN_TITLE = "24px"
    scheme.TEXT.SIZE.HEADER = "20px"
    scheme.TEXT.SIZE.SUB_HEADER = "18px"
    scheme.TEXT.SIZE.SUB_SUB_HEADER = "16px"
    scheme.TEXT.SIZE.DEFAULT = "14px"
    scheme.TEXT.SIZE.LABEL = "12px"
    scheme.TEXT.SIZE.POPUP_LOGGER_CLOSE_ICON = "16px"

    scheme.TEXT.WEIGHT = Mock()
    scheme.TEXT.WEIGHT.BOLD = "bold"
    scheme.TEXT.WEIGHT.MEDIUM = "500"
    scheme.TEXT.WEIGHT.DEFAULT = "normal"
    scheme.TEXT.WEIGHT.LIGHT = "300"

    scheme.TEXT.STYLE = Mock()
    scheme.TEXT.STYLE.DEFAULT = "normal"
    scheme.TEXT.STYLE.ITALIC = "italic"
    scheme.TEXT.STYLE.OBLIQUE = "oblique"

    scheme.TEXT.COLOR = Mock()
    scheme.TEXT.COLOR.MAIN_TITLE = "#000000"
    scheme.TEXT.COLOR.HEADER = "#111111"
    scheme.TEXT.COLOR.SUB_HEADER = "#222222"
    scheme.TEXT.COLOR.SUB_SUB_HEADER = "#333333"
    scheme.TEXT.COLOR.DEFAULT = "#444444"
    scheme.TEXT.COLOR.LABEL = "#555555"
    scheme.TEXT.COLOR.LOGGER_TITLE = "#666666"
    scheme.TEXT.COLOR.LOGGER_LOG_TEXT = "#777777"
    scheme.TEXT.COLOR.LOGGER_CLOSE_BUTTON = "#888888"
    scheme.TEXT.COLOR.EMPHASIZE = "#0066CC"
    scheme.TEXT.COLOR.SUBTLE = "#999999"
    scheme.TEXT.COLOR.MUTED = "#AAAAAA"
    scheme.TEXT.COLOR.HYPERLINK = "#0099FF"
    scheme.TEXT.COLOR.LIGHT = "#EEEEEE"
    scheme.TEXT.COLOR.LIGHT_ALT = "#F5F5F5"

    scheme.TEXT.COLOR.NAVIGATOR = Mock()
    scheme.TEXT.COLOR.NAVIGATOR.ARROW = "#555555"
    scheme.TEXT.COLOR.NAVIGATOR.STEP = "#666666"

    scheme.TEXT.COLOR.INFO_FIELD = Mock()
    scheme.TEXT.COLOR.INFO_FIELD.DEFAULT = "#000000"
    scheme.TEXT.COLOR.INFO_FIELD.INFO = "#0000FF"
    scheme.TEXT.COLOR.INFO_FIELD.SUCCESS = "#00FF00"
    scheme.TEXT.COLOR.INFO_FIELD.WARNING = "#FFFF00"
    scheme.TEXT.COLOR.INFO_FIELD.ERROR = "#FF0000"
    scheme.TEXT.COLOR.INFO_FIELD.CRITICAL = "#FF00FF"
    scheme.TEXT.COLOR.INFO_FIELD.DEBUG = "#00FFFF"

    scheme.TEXT.COLOR.WIDGET = Mock()
    scheme.TEXT.COLOR.WIDGET.BUTTON = Mock()
    scheme.TEXT.COLOR.WIDGET.BUTTON.NAVIGATION = "#FFFFFF"
    scheme.TEXT.COLOR.WIDGET.BUTTON.DEFAULT = "#000000"
    scheme.TEXT.COLOR.WIDGET.BUTTON.EMPHASIS = "#FFFFFF"
    scheme.TEXT.COLOR.WIDGET.BUTTON.SUCCESS = "#FFFFFF"
    scheme.TEXT.COLOR.WIDGET.BUTTON.DANGER = "#FFFFFF"
    scheme.TEXT.COLOR.WIDGET.BUTTON.WARNING = "#000000"
    scheme.TEXT.COLOR.WIDGET.BUTTON.OPTIONS_LIGHT = "#000000"
    scheme.TEXT.COLOR.WIDGET.BUTTON.OPTIONS_DARK = "#FFFFFF"
    scheme.TEXT.COLOR.WIDGET.BUTTON.INACTIVE = "#999999"

    scheme.TEXT.COLOR.WIDGET.INPUT = Mock()
    scheme.TEXT.COLOR.WIDGET.INPUT.DEFAULT = "#000000"
    scheme.TEXT.COLOR.WIDGET.INPUT.DISABLED = "#999999"
    scheme.TEXT.COLOR.WIDGET.INPUT.PLACEHOLDER = "#CCCCCC"

    scheme.TEXT.COLOR.WIDGET.TAB = Mock()
    scheme.TEXT.COLOR.WIDGET.TAB.TITLE = "#000000"
    scheme.TEXT.COLOR.WIDGET.TAB.BODY = "#333333"

    scheme.TEXT.COLOR.WIDGET.ACCORDION = "#000000"
    scheme.TEXT.COLOR.WIDGET.OUTPUT = "#000000"
    scheme.TEXT.COLOR.WIDGET.DROPDOWN = "#000000"

    scheme.LAYOUT_COLOR = Mock()
    scheme.LAYOUT_COLOR.BACKGROUND = "#FFFFFF"
    scheme.LAYOUT_COLOR.HEADER = "#F0F0F0"
    scheme.LAYOUT_COLOR.HEADER_GRADIENT = "#E0E0E0"
    scheme.LAYOUT_COLOR.BODY = "#FAFAFA"
    scheme.LAYOUT_COLOR.CONTRAST = "#000000"

    scheme.LAYOUT_COLOR.NAVIGATOR = Mock()
    scheme.LAYOUT_COLOR.NAVIGATOR.BACKGROUND = "#F5F5F5"
    scheme.LAYOUT_COLOR.NAVIGATOR.PANEL = "#EEEEEE"
    scheme.LAYOUT_COLOR.NAVIGATOR.BORDER = "#DDDDDD"
    scheme.LAYOUT_COLOR.NAVIGATOR.SHADOW = "#000000"
    scheme.LAYOUT_COLOR.NAVIGATOR.GLOW = "#FFFFFF"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP = Mock()
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.COMPLETED = "#00AA00"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.ACTIVE = "#0066FF"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.AVAILABLE = "#FFA500"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.LOCKED = "#CCCCCC"

    scheme.LAYOUT_COLOR.POPUP_LOGGER = Mock()
    scheme.LAYOUT_COLOR.POPUP_LOGGER.BACKGROUND = "#FFFFFF"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.PANEL = "#F9F9F9"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.BORDER = "#DDDDDD"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.SHADOW = "#000000"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.GLOW = "#FFFFFF"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LAYOUT_LINE = "#EEEEEE"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LINE = "#F0F0F0"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL = Mock()
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEFAULT = "#CCCCCC"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.INFO = "#0099FF"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.SUCCESS = "#00CC00"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.WARNING = "#FF9900"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.ERROR = "#FF3333"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.CRITICAL = "#FF0066"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEBUG = "#9966FF"

    scheme.LAYOUT_COLOR.INFO_FIELD = Mock()
    scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT = "#F0F0F0"
    scheme.LAYOUT_COLOR.INFO_FIELD.INFO = "#E6F3FF"
    scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS = "#E6FFE6"
    scheme.LAYOUT_COLOR.INFO_FIELD.WARNING = "#FFF3E6"
    scheme.LAYOUT_COLOR.INFO_FIELD.ERROR = "#FFE6E6"
    scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL = "#FFE6F3"
    scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG = "#F3E6FF"

    scheme.LAYOUT_COLOR.WIDGET = Mock()
    scheme.LAYOUT_COLOR.WIDGET.BUTTON = Mock()
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT = "#F0F0F0"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS = "#0066CC"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS = "#00AA00"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER = "#CC0000"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING = "#FF9900"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.OPTIONS_LIGHT = "#FFFFFF"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.OPTIONS_DARK = "#333333"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.INACTIVE = "#CCCCCC"

    scheme.LAYOUT_COLOR.WIDGET.INPUT = Mock()
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND = Mock()
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DEFAULT = "#FFFFFF"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DISABLED = "#F5F5F5"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.FOCUS = "#FAFAFA"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER = Mock()
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.DEFAULT = "#CCCCCC"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS = "#0066CC"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.ERROR = "#CC0000"

    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX = Mock()
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.BACKGROUND = "#FFFFFF"
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.BORDER = "#CCCCCC"
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.CHECKED = "#0066CC"
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.FOCUS = "#0099FF"

    scheme.LAYOUT_COLOR.WIDGET.SLIDER = Mock()
    scheme.LAYOUT_COLOR.WIDGET.SLIDER.TRACK = "#DDDDDD"
    scheme.LAYOUT_COLOR.WIDGET.SLIDER.HANDLE = "#0066CC"
    scheme.LAYOUT_COLOR.WIDGET.SLIDER.RANGE = "#0099FF"

    scheme.LAYOUT_COLOR.WIDGET.PROGRESS = Mock()
    scheme.LAYOUT_COLOR.WIDGET.PROGRESS.BACKGROUND = "#EEEEEE"
    scheme.LAYOUT_COLOR.WIDGET.PROGRESS.BAR = "#0066CC"

    scheme.LAYOUT_COLOR.WIDGET.TAB = Mock()
    scheme.LAYOUT_COLOR.WIDGET.TAB.BACKGROUND = "#F5F5F5"
    scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE = "#0066CC"
    scheme.LAYOUT_COLOR.WIDGET.TAB.HOVER = "#E0E0E0"
    scheme.LAYOUT_COLOR.WIDGET.TAB.PANEL = "#FFFFFF"

    scheme.LAYOUT_COLOR.WIDGET.ACCORDION = Mock()
    scheme.LAYOUT_COLOR.WIDGET.ACCORDION.PANEL = "#FFFFFF"
    scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#DDDDDD"

    scheme.LAYOUT_COLOR.WIDGET.OUTPUT = Mock()
    scheme.LAYOUT_COLOR.WIDGET.OUTPUT.BACKGROUND = "#F9F9F9"
    scheme.LAYOUT_COLOR.WIDGET.OUTPUT.BORDER = "#DDDDDD"

    scheme.LAYOUT_COLOR.WIDGET.DROPDOWN = Mock()
    scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BACKGROUND = "#FFFFFF"
    scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BORDER = "#CCCCCC"

    # Icons
    scheme.ICON = Mock()
    scheme.ICON.DEFAULT = "📄"
    scheme.ICON.INFO = "ℹ️"
    scheme.ICON.SUCCESS = "✅"
    scheme.ICON.WARNING = "⚠️"
    scheme.ICON.ERROR = "❌"
    scheme.ICON.CRITICAL = "🚨"
    scheme.ICON.DEBUG = "🐛"
    scheme.ICON.CLEAR = "🗑️"
    scheme.ICON.STORE = "💾"
    scheme.ICON.SAVE = "📥"
    scheme.ICON.CLOSE = "✖️"
    scheme.ICON.FORWARD = "▶"
    scheme.ICON.BACKWARD = "◀"
    scheme.ICON.SEPARATOR = "|"
    scheme.ICON.CALENDAR = "📅"

    scheme.ICON.PAGE = Mock()
    scheme.ICON.PAGE.DIRECTORY_SELECTION = "📁"
    scheme.ICON.PAGE.DATASET_SELECTION = "📊"
    scheme.ICON.PAGE.MODULE_SELECTION = "📦"
    scheme.ICON.PAGE.MODULE = "🔧"

    scheme.ICON.IMAGE_PATH = Mock()
    scheme.ICON.IMAGE_PATH.SUPLEX = "/path/to/suplex.png"
    scheme.ICON.IMAGE_PATH.MARTIN = "/path/to/martin.png"

    scheme.ICON.SVG = Mock()
    scheme.ICON.SVG.GITHUB = "<svg>GitHub</svg>"
    scheme.ICON.SVG.X = "<svg>X</svg>"

    scheme.OPACITY = Mock()
    scheme.OPACITY.FULL = 1.0
    scheme.OPACITY.STRONG = 0.9
    scheme.OPACITY.MEDIUM = 0.7
    scheme.OPACITY.MODERATE = 0.5
    scheme.OPACITY.SUBTLE = 0.3
    scheme.OPACITY.FAINT = 0.15
    scheme.OPACITY.BARELY = 0.05
    scheme.OPACITY.HIDDEN = 0.0

    return scheme


@pytest.fixture
def alt_mock_scheme():
    scheme = Mock()
    scheme.NAME = "Dark"

    scheme.TEXT = Mock()
    scheme.TEXT.FONT = Mock()
    scheme.TEXT.FONT.MAIN_TITLE = "Roboto"
    scheme.TEXT.FONT.HEADER = "Roboto"
    scheme.TEXT.FONT.SUB_HEADER = "Roboto"
    scheme.TEXT.FONT.SUB_SUB_HEADER = "Roboto"
    scheme.TEXT.FONT.DEFAULT = "Verdana"
    scheme.TEXT.FONT.LABEL = "Verdana"

    scheme.TEXT.SIZE = Mock()
    scheme.TEXT.SIZE.MAIN_TITLE = "26px"
    scheme.TEXT.SIZE.HEADER = "22px"
    scheme.TEXT.SIZE.SUB_HEADER = "19px"
    scheme.TEXT.SIZE.SUB_SUB_HEADER = "17px"
    scheme.TEXT.SIZE.DEFAULT = "15px"
    scheme.TEXT.SIZE.LABEL = "13px"
    scheme.TEXT.SIZE.POPUP_LOGGER_CLOSE_ICON = "18px"

    scheme.TEXT.WEIGHT = Mock()
    scheme.TEXT.WEIGHT.BOLD = "700"
    scheme.TEXT.WEIGHT.MEDIUM = "600"
    scheme.TEXT.WEIGHT.DEFAULT = "400"
    scheme.TEXT.WEIGHT.LIGHT = "200"

    scheme.TEXT.STYLE = Mock()
    scheme.TEXT.STYLE.DEFAULT = "normal"
    scheme.TEXT.STYLE.ITALIC = "italic"
    scheme.TEXT.STYLE.OBLIQUE = "oblique"

    scheme.TEXT.COLOR = Mock()
    scheme.TEXT.COLOR.MAIN_TITLE = "#1A1A1A"
    scheme.TEXT.COLOR.HEADER = "#2B2B2B"
    scheme.TEXT.COLOR.SUB_HEADER = "#3C3C3C"
    scheme.TEXT.COLOR.SUB_SUB_HEADER = "#4D4D4D"
    scheme.TEXT.COLOR.DEFAULT = "#5E5E5E"
    scheme.TEXT.COLOR.LABEL = "#6F6F6F"
    scheme.TEXT.COLOR.LOGGER_TITLE = "#808080"
    scheme.TEXT.COLOR.LOGGER_LOG_TEXT = "#919191"
    scheme.TEXT.COLOR.LOGGER_CLOSE_BUTTON = "#A2A2A2"
    scheme.TEXT.COLOR.EMPHASIZE = "#0077DD"
    scheme.TEXT.COLOR.SUBTLE = "#BBBBBB"
    scheme.TEXT.COLOR.MUTED = "#CCCCCC"
    scheme.TEXT.COLOR.HYPERLINK = "#00AAFF"
    scheme.TEXT.COLOR.LIGHT = "#F0F0F0"
    scheme.TEXT.COLOR.LIGHT_ALT = "#F8F8F8"

    scheme.TEXT.COLOR.NAVIGATOR = Mock()
    scheme.TEXT.COLOR.NAVIGATOR.ARROW = "#666666"
    scheme.TEXT.COLOR.NAVIGATOR.STEP = "#777777"

    scheme.TEXT.COLOR.INFO_FIELD = Mock()
    scheme.TEXT.COLOR.INFO_FIELD.DEFAULT = "#1A1A1A"
    scheme.TEXT.COLOR.INFO_FIELD.INFO = "#0000CC"
    scheme.TEXT.COLOR.INFO_FIELD.SUCCESS = "#00CC00"
    scheme.TEXT.COLOR.INFO_FIELD.WARNING = "#CCCC00"
    scheme.TEXT.COLOR.INFO_FIELD.ERROR = "#CC0000"
    scheme.TEXT.COLOR.INFO_FIELD.CRITICAL = "#CC00CC"
    scheme.TEXT.COLOR.INFO_FIELD.DEBUG = "#00CCCC"

    scheme.TEXT.COLOR.WIDGET = Mock()
    scheme.TEXT.COLOR.WIDGET.BUTTON = Mock()
    scheme.TEXT.COLOR.WIDGET.BUTTON.NAVIGATION = "#F0F0F0"
    scheme.TEXT.COLOR.WIDGET.BUTTON.DEFAULT = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.BUTTON.EMPHASIS = "#F0F0F0"
    scheme.TEXT.COLOR.WIDGET.BUTTON.SUCCESS = "#F0F0F0"
    scheme.TEXT.COLOR.WIDGET.BUTTON.DANGER = "#F0F0F0"
    scheme.TEXT.COLOR.WIDGET.BUTTON.WARNING = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.BUTTON.OPTIONS_LIGHT = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.BUTTON.OPTIONS_DARK = "#F0F0F0"
    scheme.TEXT.COLOR.WIDGET.BUTTON.INACTIVE = "#BBBBBB"

    scheme.TEXT.COLOR.WIDGET.INPUT = Mock()
    scheme.TEXT.COLOR.WIDGET.INPUT.DEFAULT = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.INPUT.DISABLED = "#BBBBBB"
    scheme.TEXT.COLOR.WIDGET.INPUT.PLACEHOLDER = "#DDDDDD"

    scheme.TEXT.COLOR.WIDGET.TAB = Mock()
    scheme.TEXT.COLOR.WIDGET.TAB.TITLE = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.TAB.BODY = "#4D4D4D"

    scheme.TEXT.COLOR.WIDGET.ACCORDION = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.OUTPUT = "#1A1A1A"
    scheme.TEXT.COLOR.WIDGET.DROPDOWN = "#1A1A1A"

    scheme.LAYOUT_COLOR = Mock()
    scheme.LAYOUT_COLOR.BACKGROUND = "#F8F8F8"
    scheme.LAYOUT_COLOR.HEADER = "#E8E8E8"
    scheme.LAYOUT_COLOR.HEADER_GRADIENT = "#D8D8D8"
    scheme.LAYOUT_COLOR.BODY = "#F5F5F5"
    scheme.LAYOUT_COLOR.CONTRAST = "#1A1A1A"

    scheme.LAYOUT_COLOR.NAVIGATOR = Mock()
    scheme.LAYOUT_COLOR.NAVIGATOR.BACKGROUND = "#F0F0F0"
    scheme.LAYOUT_COLOR.NAVIGATOR.PANEL = "#E5E5E5"
    scheme.LAYOUT_COLOR.NAVIGATOR.BORDER = "#D0D0D0"
    scheme.LAYOUT_COLOR.NAVIGATOR.SHADOW = "#1A1A1A"
    scheme.LAYOUT_COLOR.NAVIGATOR.GLOW = "#F8F8F8"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP = Mock()
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.COMPLETED = "#00CC00"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.ACTIVE = "#0077DD"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.AVAILABLE = "#FFBB00"
    scheme.LAYOUT_COLOR.NAVIGATOR.STEP.LOCKED = "#BBBBBB"

    scheme.LAYOUT_COLOR.POPUP_LOGGER = Mock()
    scheme.LAYOUT_COLOR.POPUP_LOGGER.BACKGROUND = "#F8F8F8"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.PANEL = "#F0F0F0"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.BORDER = "#D0D0D0"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.SHADOW = "#1A1A1A"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.GLOW = "#F8F8F8"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LAYOUT_LINE = "#E5E5E5"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LINE = "#E8E8E8"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL = Mock()
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEFAULT = "#BBBBBB"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.INFO = "#00AAFF"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.SUCCESS = "#00BB00"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.WARNING = "#FFAA00"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.ERROR = "#FF4444"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.CRITICAL = "#FF0077"
    scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEBUG = "#AA66FF"

    scheme.LAYOUT_COLOR.INFO_FIELD = Mock()
    scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT = "#E8E8E8"
    scheme.LAYOUT_COLOR.INFO_FIELD.INFO = "#E0F0FF"
    scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS = "#E0FFE0"
    scheme.LAYOUT_COLOR.INFO_FIELD.WARNING = "#FFF0E0"
    scheme.LAYOUT_COLOR.INFO_FIELD.ERROR = "#FFE0E0"
    scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL = "#FFE0F0"
    scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG = "#F0E0FF"

    scheme.LAYOUT_COLOR.WIDGET = Mock()
    scheme.LAYOUT_COLOR.WIDGET.BUTTON = Mock()
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT = "#E8E8E8"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS = "#0077DD"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS = "#00BB00"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER = "#BB0000"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING = "#FFAA00"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.OPTIONS_LIGHT = "#F8F8F8"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.OPTIONS_DARK = "#4D4D4D"
    scheme.LAYOUT_COLOR.WIDGET.BUTTON.INACTIVE = "#BBBBBB"

    scheme.LAYOUT_COLOR.WIDGET.INPUT = Mock()
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND = Mock()
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DEFAULT = "#F8F8F8"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DISABLED = "#F0F0F0"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.FOCUS = "#F5F5F5"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER = Mock()
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.DEFAULT = "#BBBBBB"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS = "#0077DD"
    scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.ERROR = "#BB0000"

    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX = Mock()
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.BACKGROUND = "#F8F8F8"
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.BORDER = "#BBBBBB"
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.CHECKED = "#0077DD"
    scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.FOCUS = "#00AAFF"

    scheme.LAYOUT_COLOR.WIDGET.SLIDER = Mock()
    scheme.LAYOUT_COLOR.WIDGET.SLIDER.TRACK = "#D0D0D0"
    scheme.LAYOUT_COLOR.WIDGET.SLIDER.HANDLE = "#0077DD"
    scheme.LAYOUT_COLOR.WIDGET.SLIDER.RANGE = "#00AAFF"

    scheme.LAYOUT_COLOR.WIDGET.PROGRESS = Mock()
    scheme.LAYOUT_COLOR.WIDGET.PROGRESS.BACKGROUND = "#E5E5E5"
    scheme.LAYOUT_COLOR.WIDGET.PROGRESS.BAR = "#0077DD"

    scheme.LAYOUT_COLOR.WIDGET.TAB = Mock()
    scheme.LAYOUT_COLOR.WIDGET.TAB.BACKGROUND = "#F0F0F0"
    scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE = "#0077DD"
    scheme.LAYOUT_COLOR.WIDGET.TAB.HOVER = "#D8D8D8"
    scheme.LAYOUT_COLOR.WIDGET.TAB.PANEL = "#F8F8F8"

    scheme.LAYOUT_COLOR.WIDGET.ACCORDION = Mock()
    scheme.LAYOUT_COLOR.WIDGET.ACCORDION.PANEL = "#F8F8F8"
    scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#D0D0D0"

    scheme.LAYOUT_COLOR.WIDGET.OUTPUT = Mock()
    scheme.LAYOUT_COLOR.WIDGET.OUTPUT.BACKGROUND = "#F0F0F0"
    scheme.LAYOUT_COLOR.WIDGET.OUTPUT.BORDER = "#D0D0D0"

    scheme.LAYOUT_COLOR.WIDGET.DROPDOWN = Mock()
    scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BACKGROUND = "#F8F8F8"
    scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BORDER = "#BBBBBB"

    scheme.ICON = Mock()
    scheme.ICON.DEFAULT = "📝"
    scheme.ICON.INFO = "ℹ️"
    scheme.ICON.SUCCESS = "✔️"
    scheme.ICON.WARNING = "⚠️"
    scheme.ICON.ERROR = "🚫"
    scheme.ICON.CRITICAL = "🔥"
    scheme.ICON.DEBUG = "🛠️"
    scheme.ICON.CLEAR = "🧹"
    scheme.ICON.STORE = "💿"
    scheme.ICON.SAVE = "📤"
    scheme.ICON.CLOSE = "❌"
    scheme.ICON.FORWARD = "➡️"
    scheme.ICON.BACKWARD = "⬅️"
    scheme.ICON.SEPARATOR = "│"
    scheme.ICON.CALENDAR = "🗓️"

    scheme.ICON.PAGE = Mock()
    scheme.ICON.PAGE.DIRECTORY_SELECTION = "📂"
    scheme.ICON.PAGE.DATASET_SELECTION = "📈"
    scheme.ICON.PAGE.MODULE_SELECTION = "📥"
    scheme.ICON.PAGE.MODULE = "⚙️"

    scheme.ICON.IMAGE_PATH = Mock()
    scheme.ICON.IMAGE_PATH.SUPLEX = "/path/to/alt_suplex.png"
    scheme.ICON.IMAGE_PATH.MARTIN = "/path/to/alt_martin.png"

    scheme.ICON.SVG = Mock()
    scheme.ICON.SVG.GITHUB = "<svg>AltGitHub</svg>"
    scheme.ICON.SVG.X = "<svg>AltX</svg>"

    scheme.OPACITY = Mock()
    scheme.OPACITY.FULL = 1.0
    scheme.OPACITY.STRONG = 0.85
    scheme.OPACITY.MEDIUM = 0.65
    scheme.OPACITY.MODERATE = 0.45
    scheme.OPACITY.SUBTLE = 0.25
    scheme.OPACITY.FAINT = 0.1
    scheme.OPACITY.BARELY = 0.03
    scheme.OPACITY.HIDDEN = 0.0

    return scheme


@pytest.fixture
def mock_schemes(mock_scheme, alt_mock_scheme):
    return {"Default": mock_scheme, "Dark": alt_mock_scheme}


@pytest.fixture
def mock_widgets():
    with patch("ipywidgets") as mock:
        # Create mock widget classes that behave like real widgets
        def create_widget_mock(widget_type):
            widget = MagicMock()
            widget._dom_classes = []
            widget.layout = MagicMock()
            widget.children = []
            widget.add_class = MagicMock(
                side_effect=lambda x: widget._dom_classes.append(x)
            )
            widget.remove_class = MagicMock(
                side_effect=lambda x: (
                    widget._dom_classes.remove(x) if x in widget._dom_classes else None
                )
            )

            if widget_type in ["IntText", "FloatText"]:
                widget.min = 0 if "Int" in widget_type else 0.0
                widget.max = 100 if "Int" in widget_type else 100.0
                widget.step = 1 if "Int" in widget_type else 0.1
                widget.value = 0 if "Int" in widget_type else 0.0
            elif widget_type == "Button":
                widget.click = MagicMock()
                widget.on_click = MagicMock()
                widget.description = ""
                widget.disabled = False
                widget.icon = ""
                widget.tooltip = ""
            elif widget_type in ["Text", "Textarea", "Password"]:
                widget.value = ""
                widget.placeholder = ""
                widget.description = ""
                widget.disabled = False
            elif widget_type == "Dropdown":
                widget.options = ()
                widget.value = None
                widget.description = ""
                widget.observe = MagicMock()
            elif widget_type == "Checkbox":
                widget.value = False
                widget.description = ""
                widget.indent = False
            elif widget_type in ["IntSlider", "FloatSlider"]:
                widget.value = 50 if "Int" in widget_type else 50.0
                widget.min = 0 if "Int" in widget_type else 0.0
                widget.max = 100 if "Int" in widget_type else 100.0
                widget.step = 1 if "Int" in widget_type else 1.0
                widget.orientation = "horizontal"
            elif widget_type == "DatePicker":
                widget.value = None
                widget.description = ""
            elif widget_type in ["IntProgress", "FloatProgress"]:
                widget.value = 0 if "Int" in widget_type else 0.0
                widget.min = 0 if "Int" in widget_type else 0.0
                widget.max = 100 if "Int" in widget_type else 100.0
            elif widget_type in ["Tab", "Accordion"]:
                widget.children = []
                widget.get_title = MagicMock(return_value="Title")
                widget.set_title = MagicMock()
            elif widget_type == "HTML":
                widget.value = ""

            return widget

        mock.Button = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Button")
        )
        mock.Text = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Text")
        )
        mock.Textarea = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Textarea")
        )
        mock.Password = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Password")
        )
        mock.IntText = MagicMock(
            side_effect=lambda **kwargs: create_widget_mock("IntText")
        )
        mock.FloatText = MagicMock(
            side_effect=lambda **kwargs: create_widget_mock("FloatText")
        )
        mock.Dropdown = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Dropdown")
        )
        mock.Checkbox = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Checkbox")
        )
        mock.IntSlider = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("IntSlider")
        )
        mock.FloatSlider = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("FloatSlider")
        )
        mock.DatePicker = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("DatePicker")
        )
        mock.IntProgress = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("IntProgress")
        )
        mock.FloatProgress = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("FloatProgress")
        )
        mock.Tab = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Tab")
        )
        mock.Accordion = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Accordion")
        )
        mock.Output = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Output")
        )
        mock.HTML = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("HTML")
        )
        mock.HBox = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("HBox")
        )
        mock.VBox = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("VBox")
        )
        mock.Box = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Box")
        )
        mock.Label = MagicMock(
            side_effect=lambda *args, **kwargs: create_widget_mock("Label")
        )
        mock.Layout = MagicMock(side_effect=lambda *args, **kwargs: MagicMock())
        yield mock


@pytest.fixture
def gui(mock_modules, mock_schemes, mock_content, mock_popup_logger):
    gui = GUI(mock_modules, mock_schemes, mock_content, mock_popup_logger)
    return gui


@pytest.fixture
def mock_content():
    content = Mock(spec=widgets.Box)
    content.children = []
    content.layout = Mock()
    return content


@pytest.fixture
def mock_popup_logger():
    logger = Mock()

    logger.toggle_button = Mock(spec=widgets.Button)
    logger.toggle_button._dom_classes = []
    logger.toggle_button.model_id = "mock_button_id_123"
    logger.toggle_button.add_class = Mock(
        side_effect=lambda x: logger.toggle_button._dom_classes.append(x)
    )
    logger.toggle_button.remove_class = Mock(
        side_effect=lambda x: (
            logger.toggle_button._dom_classes.remove(x)
            if x in logger.toggle_button._dom_classes
            else None
        )
    )
    logger.toggle_button.description = "Toggle Logger"
    logger.toggle_button.disabled = False
    logger.toggle_button.click = Mock()
    logger.toggle_button.on_click = Mock()

    logger.popup_panel = Mock(spec=widgets.Box)
    logger.popup_panel._dom_classes = []
    logger.popup_panel.model_id = "mock_panel_id_123"  # Füge model_id hinzu
    logger.popup_panel.children = []
    logger.popup_panel.add_class = Mock(
        side_effect=lambda x: logger.popup_panel._dom_classes.append(x)
    )
    logger.popup_panel.remove_class = Mock(
        side_effect=lambda x: (
            logger.popup_panel._dom_classes.remove(x)
            if x in logger.popup_panel._dom_classes
            else None
        )
    )

    return logger


@pytest.fixture
def mock_gui():
    gui = Mock()
    gui.update_content_holder = Mock()
    gui.set_info_field_state = Mock()
    gui.clear_hover_text = Mock()
    gui.update_info_field = Mock()
    gui.update_scheme = Mock()
    gui.update_layout = Mock()
    gui.current_scheme = Mock()
    return gui


@pytest.fixture
def mock_navigator():
    navigator = Mock()
    navigator.set_info_field_state = Mock()
    navigator.clear_hover_text = Mock()
    navigator.update_info_field = Mock()
    navigator.invalid_dataset_dir_selected = Mock()
    navigator.valid_dataset_dir_selected = Mock()
    navigator.navigate_to_dataset_selection = Mock()
    navigator.navigate_to_module = Mock()
    navigator.navigate_to_about_page = Mock()
    navigator.navigate_to_dir_selection = Mock()
    navigator.navigate_to_module_selection = Mock()
    navigator.adapter = Mock()
    navigator.current_scheme = Mock()

    navigator._directory_selection_page = Mock()
    navigator._directory_selection_page.reset = Mock()
    navigator._dataset_selection_page = Mock()
    navigator._dataset_selection_page.reset_keep_dataset_selections = Mock()

    navigator._back_button = Mock()
    navigator._back_button.disabled = False
    navigator._forward_button = Mock()
    navigator._forward_button.disabled = False

    return navigator


@pytest.fixture
def navigator(mock_gui, mock_scheme, mock_modules):
    """Create a real Navigator instance with mocked dependencies for testing."""
    with patch("src.ui.elements.navigator.widgets.Button") as mock_button:
        with patch("src.ui.elements.navigator.widgets.HBox") as mock_hbox:
            with patch("src.ui.elements.navigator.widgets.HTML") as mock_html:
                with patch(
                    "src.ui.elements.navigator.get_navigator_styles"
                ) as mock_styles:
                    with patch(
                        "src.ui.elements.navigator.AboutPage"
                    ) as mock_about_page:
                        with patch(
                            "src.ui.elements.navigator.DirectorySelectionPage"
                        ) as mock_dir_page:
                            with patch(
                                "src.ui.elements.navigator.DatasetSelectionPage"
                            ) as mock_dataset_page:
                                with patch(
                                    "src.ui.elements.navigator.ModuleSelectionPage"
                                ) as mock_module_page:
                                    mock_about_instance = Mock()
                                    mock_about_instance.get_ui = Mock(
                                        return_value=Mock()
                                    )
                                    mock_about_page.return_value = mock_about_instance

                                    mock_dir_instance = Mock()
                                    mock_dir_instance.get_ui = Mock(return_value=Mock())
                                    mock_dir_instance.reset = Mock()
                                    mock_dir_page.return_value = mock_dir_instance

                                    mock_dataset_instance = Mock()
                                    mock_dataset_instance.get_ui = Mock(
                                        return_value=Mock()
                                    )
                                    mock_dataset_instance.reset_keep_dataset_selections = (
                                        Mock()
                                    )
                                    mock_dataset_instance.get_selected_datasets = Mock(
                                        return_value=[]
                                    )
                                    mock_dataset_page.return_value = (
                                        mock_dataset_instance
                                    )

                                    mock_module_instance = Mock()
                                    mock_module_instance.get_ui = Mock(
                                        return_value=Mock()
                                    )
                                    mock_module_page.return_value = mock_module_instance

                                    mock_back_button = Mock()
                                    mock_back_button.disabled = False
                                    mock_forward_button = Mock()
                                    mock_forward_button.disabled = False

                                    button_instances = [
                                        mock_back_button,
                                        mock_forward_button,
                                    ]
                                    mock_button.side_effect = lambda *args, **kwargs: (
                                        button_instances.pop(0)
                                        if button_instances
                                        else Mock()
                                    )

                                    mock_container = Mock()
                                    mock_container.children = []
                                    mock_hbox.return_value = mock_container

                                    from src.ui.elements.navigator import Navigator

                                    navigator = Navigator(
                                        mock_gui, mock_scheme, mock_modules
                                    )

                                    navigator.update_breadcrumb = Mock()
                                    navigator.update_navigation_state = Mock()
                                    navigator.navigate_to_about_page = Mock()
                                    navigator.navigate_to_dir_selection = Mock()
                                    navigator.navigate_to_dataset_selection = Mock()
                                    navigator.navigate_to_module_selection = Mock()
                                    navigator.navigate_to_module = Mock()
                                    navigator.invalid_dataset_dir_selected = Mock()
                                    navigator.valid_dataset_dir_selected = Mock()

                                    navigator._back_button = mock_back_button
                                    navigator._forward_button = mock_forward_button
                                    navigator._nav_container = mock_container

                                    return navigator


@pytest.fixture
def header(mock_gui, mock_schemes):
    with patch.object(Header, "update_ui_element"):
        header = Header(mock_gui, mock_schemes)
        return header


@pytest.fixture
def popup_logger(mock_scheme):
    with patch("src.ui.elements.popup_log_system.widgets"):
        with patch("src.ui.elements.popup_log_system.get_popup_logger_styles"):
            logger = PopupLogger(
                scheme=mock_scheme, max_messages=100, min_log_level=logging.INFO
            )
            return logger


@pytest.fixture
def about_page():
    with patch("src.ui.pages.about_page.hex_to_rgba") as mock_hex_to_rgba:
        mock_hex_to_rgba.return_value = "rgba(230, 243, 255, 0.8)"
        page = AboutPage()
        return page


@pytest.fixture
def module_selection_page(mock_navigator, mock_modules):
    return ModuleSelectionPage(navigator=mock_navigator, modules=mock_modules)


@pytest.fixture
def dir_selection_page(mock_navigator):
    return DirectorySelectionPage(
        navigator=mock_navigator,
        n_modules=5,
        search_mode=SEARCH_MODE.RECURSIVE,
        search_depth=3,
        selected_path="/test/path",
        n_datasets=10,
        n_projects=2,
    )


@pytest.fixture
def dataset_selection_page(mock_navigator):
    return DatasetSelectionPage(navigator=mock_navigator)


@pytest.fixture
def mock_project():
    project = Mock()
    project.name = "Test Project"
    project.description = "Test project description"
    project.datasets = []
    return project


@pytest.fixture
def mock_dataset():
    dataset = Mock()
    dataset.id = "test_dataset_001"
    dataset.name = "Test Dataset"
    dataset.image_creation_date = datetime(2023, 1, 1, 12, 0, 0)
    dataset.measure_date = datetime(2023, 1, 2, 14, 30, 0)
    dataset.tags = ["tag1", "tag2", "tag3"]
    return dataset


@pytest.fixture
def mock_modules():
    module1 = Mock()
    module1.module_name = "Module 1"
    module1.module_version = "1.0.0"
    module1.group_name = "Group A"
    module1.button_style = {"button_color": "#FF0000", "font_color": "#FFFFFF"}
    module1.check_if_viable = Mock(return_value=True)
    module1.get_module_hover_text = Mock(return_value="Module 1 description")

    module2 = Mock()
    module2.module_name = "Module 2"
    module2.module_version = "2.0.0"
    module2.group_name = "Group A"
    module2.button_style = {"button_color": "#00FF00", "font_color": "#000000"}
    module2.check_if_viable = Mock(return_value=False)
    module2.get_module_hover_text = Mock(return_value="Module 2 description")

    module3 = Mock()
    module3.module_name = "Module 3"
    module3.module_version = "1.5.0"
    module3.group_name = "Group B"
    module3.button_style = {"button_color": "#0000FF", "font_color": "#FFFFFF"}
    module3.check_if_viable = Mock(return_value=True)
    module3.get_module_hover_text = Mock(return_value="Module 3 description")

    return [module1, module2, module3]


@pytest.fixture
def mock_adapter():
    adapter = Mock()
    adapter.path = "/test/path"
    adapter.datasets = []
    adapter.projects = []
    return adapter


@pytest.fixture
def sample_hex_colors():
    return {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "white": "#FFFFFF",
        "black": "#000000",
        "gray": "#808080",
    }


@pytest.fixture
def sample_rgb_colors():
    return {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "gray": (128, 128, 128),
    }


@pytest.fixture
def temp_scheme_dir(tmp_path):
    scheme_dir = tmp_path / "schemes"
    scheme_dir.mkdir()
    return scheme_dir


@pytest.fixture
def mock_page():
    page = Mock()
    page.navigator = Mock()
    page.navigator.current_scheme = Mock()
    page.navigator.current_scheme.LAYOUT_COLOR = Mock()
    page.navigator.current_scheme.LAYOUT_COLOR.WIDGET = Mock()
    page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION = Mock()
    page.navigator.current_scheme.LAYOUT_COLOR.WIDGET.ACCORDION.LINES = "#CCCCCC"
    page.handle_dataset_selection_changed = Mock()
    return page


@pytest.fixture
def mock_project_with_datasets():
    project = Mock()
    project.name = "Test Project"
    project.description = "Test Description"

    # Create mock datasets
    dataset1 = Mock()
    dataset1.image_creation_date = datetime(2023, 1, 1)
    dataset1.measure_date = datetime(2023, 1, 2)

    dataset2 = Mock()
    dataset2.image_creation_date = datetime(2023, 2, 1)
    dataset2.measure_date = datetime(2023, 2, 2)

    project.datasets = [dataset1, dataset2]
    return project


@pytest.fixture
def mock_project_with_datasets():
    project = Mock()
    project.name = "Test Project"
    project.description = "Test project for widget integration"

    datasets = []
    for i in range(5):
        dataset = Mock()
        dataset.id = f"DS_{i:03d}"
        dataset.name = f"Dataset {i}"
        dataset.image_creation_date = Mock()
        dataset.image_creation_date.date.return_value = date(2023, 1, i + 1)
        dataset.measure_date = Mock()
        dataset.measure_date.date.return_value = date(2023, 1, i + 2)
        dataset.tags = [f"tag_{i}", "common_tag"]
        datasets.append(dataset)

    project.datasets = datasets
    return project


@pytest.fixture
def project_card(mock_page, mock_project_with_datasets):
    """Create ProjectCard instance."""
    with patch("src.ui.pages.dataset_selection_page.DatasetSelector"):
        with patch("src.ui.pages.dataset_selection_page.TagSelector"):
            return ProjectCard(page=mock_page, project=mock_project_with_datasets)


@pytest.fixture
def mock_adapter_complex_data():
    """Create a mock adapter with complex, realistic data structure."""
    adapter = Mock()

    datasets = []
    for i in range(10):
        dataset = Mock()
        dataset.id = f"DS_{i:03d}"
        dataset.name = f"Dataset {i}"
        dataset.image_creation_date = datetime(2023, 1, i + 1, 10, 0, 0)
        dataset.measure_date = datetime(2023, 1, i + 2, 14, 30, 0)
        dataset.tags = [f"tag_{i%3}", f"tag_{i%4}", "common"]
        dataset.suplex_tags = [f"suplex_tag_{i%2}"]
        dataset.metadata = Mock()
        dataset.metadata.name = f"Dataset {i}"
        dataset.metadata.pat_id = f"PAT_{i:03d}"
        datasets.append(dataset)

    project1 = Mock()
    project1.name = "Project Alpha"
    project1.description = "First test project with 6 datasets"
    project1.datasets = datasets[:6]

    project2 = Mock()
    project2.name = "Project Beta"
    project2.description = "Second test project with 4 datasets"
    project2.datasets = datasets[6:]

    adapter.datasets = datasets
    adapter.projects = [project1, project2]
    adapter.path = "/test/data/path"
    adapter.mode = SEARCH_MODE.RECURSIVE
    adapter.search_depth = 5

    return adapter


@pytest.fixture
def integrated_gui_with_data(mock_modules, mock_schemes, mock_popup_logger):
    content = Mock()
    content.children = []
    content.layout = Mock()

    gui = GUI(mock_modules, mock_schemes, content, mock_popup_logger)

    with patch.object(gui, "build_gui"):
        mock_navigator = Mock()

        def get_adapter(self):
            return getattr(self, "_adapter", None)

        type(mock_navigator).adapter = property(get_adapter)
        mock_navigator._adapter = None
        mock_navigator.current_scheme = mock_schemes["Default"]
        mock_navigator.set_info_field_state = Mock()
        mock_navigator.update_info_field = Mock()
        mock_navigator.clear_hover_text = Mock()
        mock_navigator.valid_dataset_dir_selected = Mock()
        mock_navigator.invalid_dataset_dir_selected = Mock()
        mock_navigator.navigate_to_dataset_selection = Mock()
        mock_navigator.navigate_to_module_selection = Mock()
        gui._navigator = mock_navigator

    return gui


@pytest.fixture
def integrated_logging_setup(mock_schemes):
    popup_logger = PopupLogger(
        scheme=mock_schemes["Default"], max_messages=100, min_log_level=logging.DEBUG
    )

    log_handler = PopupLogHandler(popup_logger)
    log_handler.setLevel(logging.DEBUG)

    test_logger = logging.getLogger("test_integration")
    test_logger.setLevel(logging.DEBUG)
    test_logger.addHandler(log_handler)

    return popup_logger, log_handler, test_logger


@pytest.fixture
def gui_with_logging(mock_modules, mock_schemes, integrated_logging_setup):
    popup_logger, log_handler, test_logger = integrated_logging_setup

    content = Mock(spec=["children", "layout"])
    content.children = []
    content.layout = Mock()

    gui = GUI(mock_modules, mock_schemes, content, popup_logger)

    mock_navigator = Mock()
    mock_navigator.current_scheme = mock_schemes["Default"]
    mock_navigator.set_info_field_state = Mock()
    gui._navigator = mock_navigator

    return gui, popup_logger, test_logger


@pytest.fixture
def integrated_gui(mock_modules, mock_schemes, mock_popup_logger):
    content = Mock(spec=widgets.Box)
    content.children = []
    content.layout = Mock()

    gui = GUI(mock_modules, mock_schemes, content, mock_popup_logger)
    with patch("src.ui.elements.header.Header.load_icon", return_value="<img>"):
        with patch("src.ui.elements.navigator.widgets"):
            with patch("src.ui.gui.widgets"):
                gui.build_gui()

    return gui


@pytest.fixture
def mock_adapter_with_data():
    adapter = Mock()

    dataset1 = Mock()
    dataset1.id = "dataset_001"
    dataset1.name = "Test Dataset 1"
    dataset1.image_creation_date = datetime(2023, 1, 15, 10, 0, 0)
    dataset1.measure_date = datetime(2023, 1, 16, 14, 30, 0)
    dataset1.tags = ["tag1", "tag2"]
    dataset1.suplex_tags = ["suplex_tag1", "suplex_tag2"]
    dataset1.metadata = Mock()
    dataset1.metadata.name = "Test Dataset 1"
    dataset1.metadata.pat_id = "PAT_001"

    dataset2 = Mock()
    dataset2.id = "dataset_002"
    dataset2.name = "Test Dataset 2"
    dataset2.image_creation_date = datetime(2023, 1, 17, 10, 0, 0)
    dataset2.measure_date = datetime(2023, 1, 18, 14, 30, 0)
    dataset2.tags = ["tag2", "tag3"]
    dataset2.suplex_tags = ["suplex_tag2", "suplex_tag3"]
    dataset2.metadata = Mock()
    dataset2.metadata.name = "Test Dataset 2"
    dataset2.metadata.pat_id = "PAT_002"

    project = Mock()
    project.name = "Test Project"
    project.description = "Test project description"
    project.datasets = [dataset1, dataset2]

    adapter.datasets = [dataset1, dataset2]
    adapter.projects = [project]
    adapter.path = "/test/path"

    return adapter
