from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from typing_extensions import Self
from ipywidgets import Box

from ..martin_interface.dataset import Dataset


class SuplexModuleInterface(ABC):
    """
    This abstract base class (abc) behaves like an interface and has to be implemented in all suplex-modules.
    Its purpose lies both in the detection and validation of modules.
    """

    @property
    @abstractmethod
    def module_name(self) -> str:
        """
        Returns module name.

        Returns:
            str: The name of the module.
        """
        ...

    @property
    @abstractmethod
    def module_version(self) -> str:
        """
        Returns the version of the module as a string.

        Returns:
            str: The version of the module (e.g., '1.0.0').
        """
        ...

    @property
    @abstractmethod
    def group_name(self) -> str:
        """
        Returns module group name.
        Modules are arranged into groups on the gui by their group name.

        Returns:
            str: The name of the group this module belongs to.
        """
        ...

    @property
    @abstractmethod
    def button_style(self) -> Dict[str, str]:
        """
        Returns the button style, including font color and button color.

        Returns:
            Dict[str, str]: A dictionary with keys 'font_color' and 'button_color',
                            each mapping to a color string (e.g., '#FFFFFF' for white).
        """
        ...

    @abstractmethod
    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        """
        Checks if the module is viable for the provided datasets.
        If the datasets are not viable for the module it should be disabled.

        Args:
            datasets (List[Dataset]): A list of Dataset instances to check compatibility with.

        Returns:
            bool: True if the module is viable for the given datasets, False otherwise.
        """
        ...

    @abstractmethod
    def get_module_hover_text(self) -> str:
        """
        Returns information on the module when hovering with the mouse cursor over its button.
        This may also be used to inform the user on why a module is not viable to be used with a selected dataset.

        Returns:
            str: info text about the module.
        """
        ...

    @abstractmethod
    def initiate_module(self, datasets: List[Dataset], ui: Box) -> None:
        """
        Initiates module by loading datasets and generating the user interface.

        Args:
            datasets (List[Dataset]): A list of Dataset instances to be loaded into the module.
            ui (ipywidgets.Box): Container for graphical representation and user interface of the module.
        """
        ...

    @abstractmethod
    def reset_module(self) -> Optional[Self]:
        """
        Resets module to its initial state.
        We strongly recommend to let this method return a new instance of the module instead of resetting the current objects attributes.

        Returns:
            New instance of the module.
            None if reset is done with the same object (not recommended!)
        """
        ...
