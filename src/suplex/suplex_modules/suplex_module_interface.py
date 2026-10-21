from abc import ABC, abstractmethod
from typing import Any, Self

from ipywidgets import widgets

from suplex.martin_interface.dataset import Dataset


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
    def button_style(self) -> dict[str, str]:
        """
        Returns the button style, including font color and button color.

        Returns:
            Dict[str, str]: A dictionary with keys 'font_color', 'button_color'
                            each mapping to a color string (e.g., '#FFFFFF' for white).
                            The dictionary may also contain a 'button_icon',
                            its value may both be an emoji or the path to an actual image.
        """
        ...

    @abstractmethod
    def check_if_viable(self, datasets: list[Dataset]) -> bool:
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
    def initiate_module(self, datasets: list[Dataset], color_scheme: Any) -> widgets.Box:
        """
        Initiates module by loading datasets and generating the user interface.

        Args:
            datasets (List[Dataset]): A list of Dataset instances to be loaded into the module.
            color_scheme (Any): A color scheme class object, used to design the module.

        Returns:
            Container with graphical representation and user interface of the module.
        """
        ...

    @abstractmethod
    def update_scheme(self, new_scheme) -> Self | None:
        """
        Updates module color scheme.
        Only elements which are not part of the widget factory have to be adjusted manually.
        In most cases this means that this method can be kept empty.

        The main use of this method is to allow for free style customization.

        Args:
            new_scheme: new color scheme to be loaded into the module.
        """
        ...

    @abstractmethod
    def reset_module(self) -> Self | None:
        """
        Resets module to its initial state.
        We strongly recommend to let this method return a new instance of the module instead of resetting the current objects attributes.

        Returns:
            New instance of the module.
            None if reset is done with the same object (not recommended!)
        """
        ...
