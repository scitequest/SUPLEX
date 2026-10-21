from typing import Any, Optional

from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface as SMI


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
    def button_style(self) -> dict[str, str]:
        return {"font_color": "#000000", "button_color": "#FFFFFF"}

    def check_if_viable(self, datasets: list[Any]) -> bool:
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        return "This is a valid test module implementation"

    def initiate_module(self, datasets: list[Any], color_scheme: Any) -> None:
        print(f"Module initiated with {len(datasets)} datasets")

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional["ValidSuplexModule"]:
        return ValidSuplexModule()
