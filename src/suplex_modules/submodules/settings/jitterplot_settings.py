import logging
from typing import Optional, List
import ipywidgets as widgets
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.settings.submodule_settings_constants import (
    OPTION_INSET,
    JITTER_TYPE,
)

logger = logging.getLogger(__name__)


class JitterplotSettings:
    """
    Settings for jitterplot-specific options.
    """

    def __init__(
        self,
        show_jitterplot: Optional[bool] = None,
        apply_jitter: Optional[bool] = None,
        point_size: Optional[int] = None,
        jitter_type: Optional[JITTER_TYPE] = None,
        jitter_strength: Optional[float] = None,
        point_alpha: Optional[float] = None,
        show_all_options: bool = False,
    ) -> None:
        """
        Initialize JitterplotSettings with optional parameters.

        Args:
            show_jitterplot (bool): Whether to show the jitterplot.
            apply_jitter (bool): Whether to apply jitter.
            point_size (int): Size of the points.
            jitter_type (JITTER_TYPE): Type of jitter to apply.
            jitter_strength (float): Strength of the jitter.
            point_alpha (float): Alpha transparency for points.
            show_all_options (bool): Whether to show all options with defaults.
        """
        logger.debug(
            "Initializing JitterplotSettings with show_jitterplot=%s, apply_jitter=%s, point_size=%s, jitter_type=%s, jitter_strength=%s, point_alpha=%s, show_all_options=%s",
            show_jitterplot,
            apply_jitter,
            point_size,
            jitter_type,
            jitter_strength,
            point_alpha,
            show_all_options,
        )

        self._show_jitterplot_enabled = show_jitterplot is not None
        show_jitterplot = show_jitterplot if self._show_jitterplot_enabled else True

        self._apply_jitter_enabled = apply_jitter is not None
        apply_jitter = apply_jitter if self._apply_jitter_enabled else False

        self._jitter_type_enabled = jitter_type is not None
        self._jitter_type = (
            jitter_type
            if self._jitter_type_enabled and jitter_type in JITTER_TYPE
            else JITTER_TYPE.UNIFORM
        )
        jitter_type = self._jitter_type

        self._jitter_strength_enabled = jitter_strength is not None
        jitter_strength = jitter_strength if self._jitter_strength_enabled else 0.2

        self._point_size_enabled = point_size is not None
        point_size = point_size if self._point_size_enabled else 10

        self._point_alpha_enabled = point_alpha is not None
        point_alpha = point_alpha if self._point_alpha_enabled else 0.6

        # Easy method to enable all options with default values
        self._show_all_options = show_all_options

        # Regardless of settings widgets will always be generated
        self.create_widgets(
            show_jitterplot=show_jitterplot,
            apply_jitter=apply_jitter,
            jitter_type=jitter_type,
            jitter_strength=jitter_strength,
            point_size=point_size,
            point_alpha=point_alpha,
        )

    def create_widgets(
        self,
        show_jitterplot: bool,
        apply_jitter: bool,
        jitter_type: JITTER_TYPE,
        jitter_strength: float,
        point_size: int,
        point_alpha: float,
    ) -> None:
        """
        Create widgets for jitterplot settings.

        Args:
            show_jitterplot (bool): Initial value for show jitterplot.
            apply_jitter (bool): Initial value for apply jitter.
            jitter_type (JITTER_TYPE): Initial jitter type.
            jitter_strength (float): Initial jitter strength.
            point_size (int): Initial point size.
            point_alpha (float): Initial point alpha.
        """
        logger.debug(
            "Creating widgets for JitterplotSettings with show_jitterplot=%s, apply_jitter=%s, jitter_type=%s, jitter_strength=%s, point_size=%s, point_alpha=%s",
            show_jitterplot,
            apply_jitter,
            jitter_type,
            jitter_strength,
            point_size,
            point_alpha,
        )

        self._show_jitterplot_widget = WidgetFactory.checkbox(
            value=show_jitterplot,
            description="Show Jitterplot",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._apply_jitter_widget = WidgetFactory.checkbox(
            value=apply_jitter,
            description="Apply Jitter",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        types = [jtype.value for jtype in JITTER_TYPE]
        self._jitter_type_radio = WidgetFactory.custom_radio_buttons(
            number=len(types),
            description=types,
            i_toggled=types.index(self._jitter_type.value),
        )

        self._jitter_strength_widget = WidgetFactory.number_input(
            value=jitter_strength,
            min_value=0.0,
            step=0.05,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._point_size_widget = WidgetFactory.number_input(
            value=point_size,
            min_value=1,
            max_value=100,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._point_alpha_widget = WidgetFactory.number_input(
            value=point_alpha,
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        for button in self._jitter_type_radio:
            button.on_click(lambda b: self.update_jitter_type(b.description))

        self.update_jitter_type(jitter_type.value)

    def update_jitter_type(self, type_str: str) -> None:
        """
        Update the jitter type based on the selected option.

        Args:
            type_str (str): String representation of the jitter type.
        """
        logger.debug("Updating jitter type to: %s", type_str)
        self._jitter_type = JITTER_TYPE(type_str)

    def get_active_widgets(self) -> List[widgets.Widget]:
        """
        Get a list of all interactive widgets for jitterplot settings.

        Returns:
            List[widgets.Widget]: A list of all interactive widgets for jitterplot settings.
        """
        logger.debug("Collecting all interactive widgets for JitterplotSettings")
        active_widgets = []

        if self._show_jitterplot_enabled or self._show_all_options:
            active_widgets.append(self._show_jitterplot_widget)
        if self._apply_jitter_enabled or self._show_all_options:
            active_widgets.append(self._apply_jitter_widget)
        if self._jitter_type_enabled or self._show_all_options:
            active_widgets.extend(self._jitter_type_radio)
        if self._jitter_strength_enabled or self._show_all_options:
            active_widgets.append(self._jitter_strength_widget)
        if self._point_size_enabled or self._show_all_options:
            active_widgets.append(self._point_size_widget)
        if self._point_alpha_enabled or self._show_all_options:
            active_widgets.append(self._point_alpha_widget)

        return active_widgets

    def get_ui(self) -> widgets.Widget:
        """
        Get the UI widget for jitterplot settings.

        Returns:
            widgets.Widget: The VBox widget containing all jitterplot options.
        """
        logger.debug("Getting UI for JitterplotSettings")
        jitterplot_widgets = []
        jitterplot_widgets.append(WidgetFactory.html_widget(value="<h3>Jitterplot Options</h3>"))

        checkboxes = []
        if self._show_jitterplot_enabled or self._show_all_options:
            checkboxes.append(self._show_jitterplot_widget)
        if self._apply_jitter_enabled or self._show_all_options:
            checkboxes.append(self._apply_jitter_widget)
        if checkboxes:
            checkboxes_container = WidgetFactory.vbox(
                children=checkboxes,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            jitterplot_widgets.append(checkboxes_container)

        if self._jitter_type_enabled or self._show_all_options:
            jitter_type_label = WidgetFactory.label(value="Jitter Type:")
            jitter_radio_hbox = WidgetFactory.hbox(
                children=self._jitter_type_radio,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            jitter_type_container = WidgetFactory.vbox(
                children=[jitter_type_label, jitter_radio_hbox],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            jitterplot_widgets.append(jitter_type_container)

        if self._jitter_strength_enabled or self._show_all_options:
            jitter_strength_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Jitter Strength:"),
                    WidgetFactory.vbox(
                        children=[self._jitter_strength_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            jitterplot_widgets.append(jitter_strength_container)

        if self._point_size_enabled or self._show_all_options:
            point_size_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Point Size:"),
                    WidgetFactory.vbox(
                        children=[self._point_size_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            jitterplot_widgets.append(point_size_container)

        if self._point_alpha_enabled or self._show_all_options:
            point_alpha_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Point Alpha:"),
                    WidgetFactory.vbox(
                        children=[self._point_alpha_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            jitterplot_widgets.append(point_alpha_container)

        return WidgetFactory.vbox(
            children=jitterplot_widgets, gap="5px", overflow="visible", height="auto"
        )

    @property
    def show_jitterplot(self) -> bool:
        """
        Whether to show the jitterplot.

        Returns:
            bool: The value of the show_jitterplot widget.
        """
        return self._show_jitterplot_widget.value

    def get_show_jitterplot_widget(self) -> widgets.Checkbox:
        """
        Get the show_jitterplot widget.

        Returns:
            widgets.Checkbox: The show_jitterplot checkbox widget.
        """
        return self._show_jitterplot_widget

    @property
    def apply_jitter(self) -> bool:
        """
        Whether to apply jitter.

        Returns:
            bool: The value of the apply_jitter widget.
        """
        return self._apply_jitter_widget.value

    def get_apply_jitter_widget(self) -> widgets.Checkbox:
        """
        Get the apply_jitter widget.

        Returns:
            widgets.Checkbox: The apply_jitter checkbox widget.
        """
        return self._apply_jitter_widget

    @property
    def jitter_type(self) -> JITTER_TYPE:
        """
        The jitter type.

        Returns:
            JITTER_TYPE: The selected jitter type.
        """
        return self._jitter_type

    def get_jitter_type_radio(self) -> list:
        """
        Get the jitter_type radio buttons.

        Returns:
            list: List of radio button widgets for jitter type.
        """
        return self._jitter_type_radio

    @property
    def jitter_strength(self) -> float:
        """
        The jitter strength.

        Returns:
            float: The value of the jitter_strength widget.
        """
        return self._jitter_strength_widget.value

    def get_jitter_strength_widget(self) -> widgets.FloatText:
        """
        Get the jitter_strength widget.

        Returns:
            widgets.FloatText: The jitter_strength number input widget.
        """
        return self._jitter_strength_widget

    @property
    def point_size(self) -> int:
        """
        The point size.

        Returns:
            int: The value of the point_size widget.
        """
        return self._point_size_widget.value

    def get_point_size_widget(self) -> widgets.IntText:
        """
        Get the point_size widget.

        Returns:
            widgets.IntText: The point_size number input widget.
        """
        return self._point_size_widget

    @property
    def point_alpha(self) -> float:
        """
        The point alpha.

        Returns:
            float: The value of the point_alpha widget.
        """
        return self._point_alpha_widget.value

    def get_point_alpha_widget(self) -> widgets.FloatText:
        """
        Get the point_alpha widget.

        Returns:
            widgets.FloatText: The point_alpha number input widget.
        """
        return self._point_alpha_widget
