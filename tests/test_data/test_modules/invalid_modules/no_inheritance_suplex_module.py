from typing import Optional

from suplex.martin_interface.dataset import Dataset


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
    def button_style(self) -> dict[str, str]:
        return {"font_color": "#FF0000", "button_color": "#00FF00"}

    def check_if_viable(self, datasets: list[Dataset]) -> bool:
        return True

    def get_module_hover_text(self) -> str:
        return "Standalone module without inheritance"

    def initiate_module(self, datasets: list[Dataset], color_scheme: Any) -> None:
        print("Standalone module initiated")

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional["StandaloneModule"]:
        return StandaloneModule()

    def additional_method(self):
        return "This module has all required methods but doesn't inherit from SuplexModuleInterface"
