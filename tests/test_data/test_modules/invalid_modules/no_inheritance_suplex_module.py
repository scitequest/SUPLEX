from typing import Dict, List, Optional
import ipywidgets
from martin_interface.dataset import Dataset


class NoInheritanceSuplexModule:
    @property
    def module_name(self) -> str:
        return "StandaloneModule"

    @property
    def module_version(self) -> str:
        return "2.0.0"

    @property
    def group_name(self):
        return "test"

    @property
    def button_style(self) -> Dict[str, str]:
        return {"font_color": "#FF0000", "button_color": "#00FF00"}

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        return True

    def get_module_hover_text(self) -> str:
        return "Standalone module without inheritance"

    def initiate_module(self, datasets: List[Dataset], ui: ipywidgets.Box) -> None:
        print("Standalone module initiated")

    def reset_module(self) -> Optional["StandaloneModule"]:
        return StandaloneModule()

    def additional_method(self):
        return "This module has all required methods but doesn't inherit from SuplexModuleInterface"
