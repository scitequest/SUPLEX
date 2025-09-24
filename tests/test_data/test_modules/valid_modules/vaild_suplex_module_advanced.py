from src.suplex_modules.suplex_module_interface import SuplexModuleInterface
from typing import Dict, List, Optional, Any
import ipywidgets
from abc import ABC
import logging


class LoggerMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def log_info(self, message: str):
        self.logger.info(message)


class ConfigurableModule(ABC):
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.settings = {}

    def load_config(self):
        self.settings = {"theme": "dark", "timeout": 30}


class AdvancedSuplexModule(LoggerMixin, SuplexModuleInterface, ConfigurableModule):
    def __init__(self, config_path: str = None):
        super().__init__(config_path=config_path)
        self.log_info("AdvancedSuplexModule initialized")

    @property
    def module_name(self) -> str:
        return "AdvancedMultiInheritanceModule"

    @property
    def module_version(self) -> str:
        return "2.1.0"

    @property
    def group_name(self):
        return "test"

    @property
    def button_style(self) -> Dict[str, str]:
        theme = self.settings.get("theme", "light")
        if theme == "dark":
            return {"font_color": "#FFFFFF", "button_color": "#2D2D2D"}
        return {"font_color": "#000000", "button_color": "#F0F0F0"}

    def check_if_viable(self, datasets: List[Any]) -> bool:
        self.log_info(f"Checking viability for {len(datasets)} datasets")
        return len(datasets) > 0 and all(d.is_valid() for d in datasets)

    def get_module_hover_text(self) -> str:
        return f"Advanced module with multiple inheritance (Theme: {self.settings.get('theme', 'default')})"

    def initiate_module(self, datasets: List[Any], color_scheme: Any) -> None:
        self.load_config()
        self.log_info(
            f"Module initiated with {len(datasets)} datasets and config from {self.config_path}"
        )

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional["AdvancedSuplexModule"]:
        self.log_info("Resetting module")
        return AdvancedSuplexModule(self.config_path)

    def get_current_config(self) -> Dict:
        return self.settings.copy()
