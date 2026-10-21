"""Application start-up: everything the Voilà notebook used to do inline."""

import logging

import ipywidgets as widgets
from IPython.display import display

from suplex.paths import ensure_user_dirs, user_modules_dir, user_schemes_dir
from suplex.suplex_modules.module_constants import DEFAULT_SEARCH_DEPTH, SEARCH_MODE
from suplex.suplex_modules.module_loader import load_modules
from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface
from suplex.ui.elements.popup_log_system import PopupLogger, PopupLogHandler
from suplex.ui.gui import GUI
from suplex.ui.styles.scheme_loader import get_schemes, load_all_schemes
from suplex.ui.styles.schemes.default_scheme import DEFAULT_SCHEME

logger = logging.getLogger(__name__)


def setup_logging() -> PopupLogger:
    """Route all log records into the in-app popup logger."""
    popup_logger = PopupLogger(max_messages=1000, min_log_level=logging.INFO)
    popup_handler = PopupLogHandler(popup_logger)
    logging.basicConfig(level=logging.DEBUG, format="%(message)s", handlers=[popup_handler])
    return popup_logger


def load_all_modules() -> list[SuplexModuleInterface]:
    """Load the built-in modules plus any modules from the user directory."""
    modules_dir = user_modules_dir()
    modules = load_modules(max_depth=DEFAULT_SEARCH_DEPTH, mode=SEARCH_MODE.RECURSIVE)
    user_modules = load_modules(
        dir_path=str(modules_dir), max_depth=DEFAULT_SEARCH_DEPTH, mode=SEARCH_MODE.RECURSIVE
    )
    if user_modules:
        logger.info("Loaded %d user module(s) from %s", len(user_modules), modules_dir)
    return modules + user_modules


def load_schemes() -> dict:
    """Load the built-in colour schemes plus any schemes from the user directory."""
    schemes_dir = user_schemes_dir()
    schemes = get_schemes()
    user_schemes = load_all_schemes(schemes_dir)
    if user_schemes:
        logger.info("Loaded %d user scheme(s) from %s", len(user_schemes), schemes_dir)
    schemes.update(user_schemes)
    if not schemes:
        schemes[DEFAULT_SCHEME.NAME] = DEFAULT_SCHEME
    return schemes


def create_content_container() -> widgets.Box:
    """Grid box that tolerates placing widgets on top of one another."""
    content = widgets.Box(
        layout=widgets.Layout(
            display="grid",
            grid_template_rows="1fr",
            grid_template_columns="1fr",
        )
    )
    content.add_class("gui-content-container")
    return content


def main() -> GUI:
    """Build and display the SUPLEX GUI. Called from the notebook rendered by Voilà."""
    popup_logger = setup_logging()
    ensure_user_dirs()
    modules = load_all_modules()
    schemes = load_schemes()

    content = create_content_container()
    # Needed to allow dynamic updates to widgets
    output = widgets.Output()
    display(content, output)

    gui = GUI(modules, schemes, content, popup_logger)
    gui.build_gui()
    return gui
