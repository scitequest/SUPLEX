import logging
from typing import Optional, List
import ipywidgets as widgets
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.settings.submodule_settings_constants import (
    OPTION_INSET,
    WHISKER_MODE,
)

logger = logging.getLogger(__name__)


class BoxplotSettings:
    """
    Settings for boxplot-specific options.
    """

    def __init__(
        self,
        show_boxplot: Optional[bool] = None,
        show_outliers: Optional[bool] = None,
        whisker_mode: Optional[WHISKER_MODE] = None,
        iqr_factor: Optional[float] = None,
        percentile_min: Optional[int] = None,
        percentile_max: Optional[int] = None,
        box_alpha: Optional[float] = None,
        box_width: Optional[float] = None,
        show_all_options: bool = False,
    ) -> None:
        """
        Initialize BoxplotSettings with optional parameters.

        Args:
            show_boxplot (bool): Whether to show the boxplot.
            show_outliers (bool): Whether to show outliers.
            whisker_mode (WHISKER_MODE): Mode for whiskers.
            iqr_factor (float): Factor for IQR whisker mode.
            percentile_min (int): Minimum percentile for percentile whisker mode.
            percentile_max (int): Maximum percentile for percentile whisker mode.
            box_alpha (float): Alpha transparency for the box.
            box_width (float): Width of the box.
            show_all_options (bool): Whether to show all options with defaults.
        """
        logger.debug(
            "Initializing BoxplotSettings with show_boxplot=%s, show_outliers=%s, whisker_mode=%s, iqr_factor=%s, percentile_min=%s, percentile_max=%s, box_alpha=%s, box_width=%s, show_all_options=%s",
            show_boxplot,
            show_outliers,
            whisker_mode,
            iqr_factor,
            percentile_min,
            percentile_max,
            box_alpha,
            box_width,
            show_all_options,
        )

        self._show_boxplot_enabled = show_boxplot is not None
        show_boxplot = show_boxplot if self._show_boxplot_enabled else True

        self._show_outliers_enabled = show_outliers is not None
        show_outliers = show_outliers if self._show_outliers_enabled else True

        self._whisker_mode_enabled = whisker_mode is not None
        self._whisker_mode = (
            whisker_mode
            if self._whisker_mode_enabled and whisker_mode in WHISKER_MODE
            else WHISKER_MODE.IQR
        )
        whisker_mode = self._whisker_mode

        self._iqr_factor_enabled = iqr_factor is not None
        iqr_factor = iqr_factor if self._iqr_factor_enabled else 1.5

        self._percentile_min_enabled = percentile_min is not None
        percentile_min = percentile_min if self._percentile_min_enabled else 5

        self._percentile_max_enabled = percentile_max is not None
        percentile_max = percentile_max if self._percentile_max_enabled else 95

        self._box_alpha_enabled = box_alpha is not None
        box_alpha = box_alpha if self._box_alpha_enabled else 0.7

        self._box_width_enabled = box_width is not None
        box_width = box_width if self._box_width_enabled else 0.5

        # Easy method to enable all options with default values
        self._show_all_options = show_all_options

        # Regardless of settings widgets will always be generated
        self.create_widgets(
            show_boxplot=show_boxplot,
            show_outliers=show_outliers,
            whisker_mode=whisker_mode,
            iqr_factor=iqr_factor,
            percentile_min=percentile_min,
            percentile_max=percentile_max,
            box_alpha=box_alpha,
            box_width=box_width,
        )

    def create_widgets(
        self,
        show_boxplot: bool,
        show_outliers: bool,
        whisker_mode: WHISKER_MODE,
        iqr_factor: float,
        percentile_min: int,
        percentile_max: int,
        box_alpha: float,
        box_width: float,
    ) -> None:
        """
        Create widgets for boxplot settings.

        Args:
            show_boxplot (bool): Initial value for show boxplot.
            show_outliers (bool): Initial value for show outliers.
            whisker_mode (WHISKER_MODE): Initial whisker mode.
            iqr_factor (float): Initial IQR factor.
            percentile_min (int): Initial minimum percentile.
            percentile_max (int): Initial maximum percentile.
            box_alpha (float): Initial box alpha.
            box_width (float): Initial box width.
        """
        logger.debug(
            "Creating widgets for BoxplotSettings with show_boxplot=%s, show_outliers=%s, whisker_mode=%s, iqr_factor=%s, percentile_min=%s, percentile_max=%s, box_alpha=%s, box_width=%s",
            show_boxplot,
            show_outliers,
            whisker_mode,
            iqr_factor,
            percentile_min,
            percentile_max,
            box_alpha,
            box_width,
        )

        self._show_boxplot_widget = WidgetFactory.checkbox(
            value=show_boxplot,
            description="Show Boxplot",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._show_outliers_widget = WidgetFactory.checkbox(
            value=show_outliers,
            description="Show Outliers",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        modes = [mode.value for mode in WHISKER_MODE]
        self._whisker_mode_radio = WidgetFactory.custom_radio_buttons(
            number=len(modes),
            description=modes,
            i_toggled=modes.index(self._whisker_mode.value),
        )

        self._iqr_factor_widget = WidgetFactory.number_input(
            value=iqr_factor,
            min_value=0.0,
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._percentile_min_widget = WidgetFactory.number_input(
            value=percentile_min,
            min_value=0,
            max_value=100,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._percentile_max_widget = WidgetFactory.number_input(
            value=percentile_max,
            min_value=0,
            max_value=100,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._box_alpha_widget = WidgetFactory.number_input(
            value=box_alpha,
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._box_width_widget = WidgetFactory.number_input(
            value=box_width,
            min_value=0.1,
            max_value=1.0,
            step=0.05,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
        )

        self._iqr_container = WidgetFactory.vbox(
            children=[
                WidgetFactory.label(value="IQR Factor:"),
                WidgetFactory.vbox(
                    children=[self._iqr_factor_widget],
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

        self._perc_min_container = WidgetFactory.vbox(
            children=[
                WidgetFactory.label(value="Min Percentile:"),
                WidgetFactory.vbox(
                    children=[self._percentile_min_widget],
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

        self._perc_max_container = WidgetFactory.vbox(
            children=[
                WidgetFactory.label(value="Max Percentile:"),
                WidgetFactory.vbox(
                    children=[self._percentile_max_widget],
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

        # Placeholder will be re-initialized in get_ui
        self._whisker_inputs_vbox = WidgetFactory.vbox(children=[])
        for button in self._whisker_mode_radio:
            button.on_click(lambda b: self.update_whisker_display(b.description))

        self.update_whisker_display(whisker_mode.value)

    def update_whisker_display(self, mode_str: str) -> None:
        """
        Update the whisker display based on the selected mode.

        Args:
            mode_str (str): String representation of the whisker mode.
        """
        logger.debug("Updating whisker display to mode: %s", mode_str)
        self._whisker_mode = WHISKER_MODE(mode_str)
        if self._whisker_mode == WHISKER_MODE.IQR:
            if self._iqr_factor_enabled or self._show_all_options:
                self._whisker_inputs_vbox.children = [self._iqr_container]
            else:
                self._whisker_inputs_vbox.children = []
        elif self._whisker_mode == WHISKER_MODE.PERCENTILES:
            perc_children = []
            if self._percentile_min_enabled or self._show_all_options:
                perc_children.append(self._perc_min_container)
            if self._percentile_max_enabled or self._show_all_options:
                perc_children.append(self._perc_max_container)
            if perc_children:
                perc_hbox = WidgetFactory.hbox(
                    children=perc_children,
                    gap="15px",
                    overflow="visible",
                    height="auto",
                )
                percentile_container = WidgetFactory.vbox(
                    children=[perc_hbox],
                    gap="5px",
                    overflow="visible",
                    height="auto",
                    layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                )
                self._whisker_inputs_vbox.children = [percentile_container]
            else:
                self._whisker_inputs_vbox.children = []
        else:
            self._whisker_inputs_vbox.children = []

    def get_active_widgets(self) -> List[widgets.Widget]:
        """
        Get a list of all interactive widgets for boxplot settings.

        Returns:
            List[widgets.Widget]: A list of all interactive widgets for boxplot settings.
        """
        logger.debug("Collecting all interactive widgets for BoxplotSettings")
        active_widgets = []

        if self._show_boxplot_enabled or self._show_all_options:
            active_widgets.append(self._show_boxplot_widget)
        if self._show_outliers_enabled or self._show_all_options:
            active_widgets.append(self._show_outliers_widget)
        if self._whisker_mode_enabled or self._show_all_options:
            active_widgets.extend(self._whisker_mode_radio)
        if self._whisker_mode == WHISKER_MODE.IQR and (
            self._iqr_factor_enabled or self._show_all_options
        ):
            active_widgets.append(self._iqr_factor_widget)
        if self._whisker_mode == WHISKER_MODE.PERCENTILES and (
            self._percentile_min_enabled or self._show_all_options
        ):
            active_widgets.append(self._percentile_min_widget)
        if self._whisker_mode == WHISKER_MODE.PERCENTILES and (
            self._percentile_max_enabled or self._show_all_options
        ):
            active_widgets.append(self._percentile_max_widget)
        if self._box_alpha_enabled or self._show_all_options:
            active_widgets.append(self._box_alpha_widget)
        if self._box_width_enabled or self._show_all_options:
            active_widgets.append(self._box_width_widget)

        return active_widgets

    def get_ui(self) -> widgets.Widget:
        """
        Get the UI widget for boxplot settings.

        Returns:
            widgets.Widget: The VBox widget containing all boxplot options.
        """
        logger.debug("Getting UI for BoxplotSettings")
        boxplot_widgets = []
        boxplot_widgets.append(WidgetFactory.html_widget(value="<h3>Boxplot Options</h3>"))

        checkboxes = []
        if self._show_boxplot_enabled or self._show_all_options:
            checkboxes.append(self._show_boxplot_widget)
        if self._show_outliers_enabled or self._show_all_options:
            checkboxes.append(self._show_outliers_widget)
        if checkboxes:
            checkboxes_container = WidgetFactory.vbox(
                children=checkboxes,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            boxplot_widgets.append(checkboxes_container)

        if self._whisker_mode_enabled or self._show_all_options:
            whisker_mode_label = WidgetFactory.label(value="Whisker Mode:")
            whisker_radio_hbox = WidgetFactory.hbox(
                children=self._whisker_mode_radio,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            whisker_mode_container = WidgetFactory.vbox(
                children=[whisker_mode_label, whisker_radio_hbox],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            boxplot_widgets.append(whisker_mode_container)

            self._whisker_inputs_vbox = WidgetFactory.vbox(
                children=self._whisker_inputs_vbox.children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            boxplot_widgets.append(self._whisker_inputs_vbox)

        if self._box_alpha_enabled or self._show_all_options:
            box_alpha_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Box Alpha:"),
                    WidgetFactory.vbox(
                        children=[self._box_alpha_widget],
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
            boxplot_widgets.append(box_alpha_container)

        if self._box_width_enabled or self._show_all_options:
            box_width_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Box Width:"),
                    WidgetFactory.vbox(
                        children=[self._box_width_widget],
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
            boxplot_widgets.append(box_width_container)

        return WidgetFactory.vbox(
            children=boxplot_widgets, gap="5px", overflow="visible", height="auto"
        )

    @property
    def show_boxplot(self) -> bool:
        """
        Whether to show the boxplot.

        Returns:
            bool: The value of the show_boxplot widget.
        """
        return self._show_boxplot_widget.value

    def get_show_boxplot_widget(self) -> widgets.Checkbox:
        """
        Get the show_boxplot widget.

        Returns:
            widgets.Checkbox: The show_boxplot checkbox widget.
        """
        return self._show_boxplot_widget

    @property
    def show_outliers(self) -> bool:
        """
        Whether to show outliers.

        Returns:
            bool: The value of the show_outliers widget.
        """
        return self._show_outliers_widget.value

    def get_show_outliers_widget(self) -> widgets.Checkbox:
        """
        Get the show_outliers widget.

        Returns:
            widgets.Checkbox: The show_outliers checkbox widget.
        """
        return self._show_outliers_widget

    @property
    def whisker_mode(self) -> WHISKER_MODE:
        """
        The whisker mode.

        Returns:
            WHISKER_MODE: The selected whisker mode.
        """
        return self._whisker_mode

    def get_whisker_mode_radio(self) -> list:
        """
        Get the whisker_mode radio buttons.

        Returns:
            list: List of radio button widgets for whisker mode.
        """
        return self._whisker_mode_radio

    @property
    def iqr_factor(self) -> float:
        """
        The IQR factor.

        Returns:
            float: The value of the iqr_factor widget.
        """
        return self._iqr_factor_widget.value

    def get_iqr_factor_widget(self) -> widgets.FloatText:
        """
        Get the iqr_factor widget.

        Returns:
            widgets.FloatText: The iqr_factor number input widget.
        """
        return self._iqr_factor_widget

    @property
    def percentile_min(self) -> int:
        """
        The minimum percentile.

        Returns:
            int: The value of the percentile_min widget.
        """
        return self._percentile_min_widget.value

    def get_percentile_min_widget(self) -> widgets.IntText:
        """
        Get the percentile_min widget.

        Returns:
            widgets.IntText: The percentile_min number input widget.
        """
        return self._percentile_min_widget

    @property
    def percentile_max(self) -> int:
        """
        The maximum percentile.

        Returns:
            int: The value of the percentile_max widget.
        """
        return self._percentile_max_widget.value

    def get_percentile_max_widget(self) -> widgets.IntText:
        """
        Get the percentile_max widget.

        Returns:
            widgets.IntText: The percentile_max number input widget.
        """
        return self._percentile_max_widget

    @property
    def box_alpha(self) -> float:
        """
        The box alpha.

        Returns:
            float: The value of the box_alpha widget.
        """
        return self._box_alpha_widget.value

    def get_box_alpha_widget(self) -> widgets.FloatText:
        """
        Get the box_alpha widget.

        Returns:
            widgets.FloatText: The box_alpha number input widget.
        """
        return self._box_alpha_widget

    @property
    def box_width(self) -> float:
        """
        The box width.

        Returns:
            float: The value of the box_width widget.
        """
        return self._box_width_widget.value

    def get_box_width_widget(self) -> widgets.FloatText:
        """
        Get the box_width widget.

        Returns:
            widgets.FloatText: The box_width number input widget.
        """
        return self._box_width_widget
