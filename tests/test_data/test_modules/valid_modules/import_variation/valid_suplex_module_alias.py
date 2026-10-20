from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface as SMI
from typing import Dict, List, Optional, Any
import ipywidgets


class ValidSuplexModuleAlias(SMI):
    @property
    def module_name(self) -> str:
        return "ValidTestModuleAlias"

    @property
    def module_version(self) -> str:
        return "1.0.0"

    @property
    def group_name(self):
        return "test"

    @property
    def button_style(self) -> Dict[str, str]:
        return {"font_color": "#000000", "button_color": "#FFFFFF"}

    def check_if_viable(self, datasets: List[Any]) -> bool:
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        return "This is a valid test module implementation"

    def initiate_module(self, datasets: List[Any], color_scheme: Any) -> None:
        print(f"Module initiated with {len(datasets)} datasets")

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional["ValidSuplexModule"]:
        return ValidSuplexModule()
