import logging
from typing import Optional, List
import ipywidgets as widgets
from enum import Enum
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.settings.submodule_settings_constants import OPTION_INSET, ANNOTATION_COLOR, LINE_COLOR, CBAR_ORIENTATION, CBAR_TICK_MODE

logger = logging.getLogger(__name__)

class HeatmapSettings:
    """
    Settings for heatmap-specific options.
    """
    def __init__(
        self,
        square: Optional[bool] = None,
        symmetric_scaling: Optional[bool] = None,
        annot: Optional[bool] = None,
        annot_fontsize: Optional[float] = None,
        annot_digits: Optional[int] = None,
        annot_color: Optional[str] = None,
        linewidths: Optional[float] = None,
        linecolor: Optional[str] = None,
        robust: Optional[bool] = None,
        cbar_options: Optional[List[CBAR_ORIENTATION]] = None,
        cbar_tick_options: Optional[List[CBAR_TICK_MODE]] = None,
        use_letter_annotation_x: Optional[bool] = None,
        use_letter_annotation_y: Optional[bool] = None,
        start_at_index_0: Optional[bool] = None,
        n_cols: Optional[int] = None,
        col_labels: Optional[str] = None,
        row_labels: Optional[str] = None,
        use_custom_col_labels: Optional[bool] = None,
        use_custom_row_labels: Optional[bool] = None,
        highlight_reference_points: Optional[bool] = None,
        highlight_colors: Optional[List[str]] = None,
        cell_size: Optional[float] = None,
        show_all_options: bool = False
    ) -> None:
        """
        Initialize HeatmapSettings with optional parameters.

        Args:
            square (bool): Whether to make cells square.
            symmetric_scaling (bool): Whether to use symmetric scaling around center.
            annot (bool): Whether to annotate values.
            annot_fontsize (float): Font size for annotations.
            annot_digits (int): Number of decimal places for annotations.
            annot_color (str): Color for annotations.
            linewidths (float): Width of grid lines.
            linecolor (str): Color of grid lines.
            robust (bool): Whether to use robust scaling.
            cbar_options (List[CBAR_ORIENTATION]): Orientation of cbar.
            use_letter_annotation_x (bool): Whether to use letter annotation for X axis.
            use_letter_annotation_y (bool): Whether to use letter annotation for Y axis.
            start_at_index_0 (bool): Whether to start indexing at 0.
            n_cols (int): Number of columns for 2D heatmaps.
            col_labels (str): Column labels.
            row_labels (str): Row labels.
            use_custom_col_labels (bool): Whether to use custom column labels.
            use_custom_row_labels (bool): Whether to use custom row labels.
            highlight_colors (List[str]): List of allowed highlight colors. Defaults to all ANNOTATION_COLOR values if None.
            cell_size (float): Size of the cells.
            show_all_options (bool): Whether to show all options with defaults.
        """
        logger.debug("Initializing HeatmapSettings")

        self._square_enabled = square is not None
        square = square if self._square_enabled else False

        self._symmetric_scaling_enabled = symmetric_scaling is not None
        symmetric_scaling = symmetric_scaling if self._symmetric_scaling_enabled else True

        self._annot_enabled = annot is not None
        annot = annot if self._annot_enabled else False

        self._annot_fontsize_enabled = annot_fontsize is not None
        annot_fontsize = annot_fontsize if self._annot_fontsize_enabled else 10.0

        self._annot_digits_enabled = annot_digits is not None
        annot_digits = annot_digits if self._annot_digits_enabled else 2

        self._annot_color_enabled = annot_color is not None
        self._annot_color = ANNOTATION_COLOR(annot_color) if annot_color and annot_color in [e.value for e in ANNOTATION_COLOR] else ANNOTATION_COLOR.BLACK
        annot_color = self._annot_color.value

        self._linewidths_enabled = linewidths is not None
        linewidths = linewidths if self._linewidths_enabled else 0

        self._linecolor_enabled = linecolor is not None
        self._linecolor = LINE_COLOR(linecolor) if linecolor and linecolor in [e.value for e in LINE_COLOR] else LINE_COLOR.WHITE
        linecolor = self._linecolor.value

        self._robust_enabled = robust is not None
        robust = robust if self._robust_enabled else False

        self._cbar_enabled = cbar_options is not None
        cbar_orientations = cbar_options if self._cbar_enabled else list(CBAR_ORIENTATION)

        self._cbar_tick_modes_enabled = cbar_tick_options is not None
        cbar_tick_options = cbar_tick_options if self._cbar_tick_modes_enabled else list(CBAR_TICK_MODE)

        self._use_letter_annotation_x_enabled = use_letter_annotation_x is not None
        use_letter_annotation_x = use_letter_annotation_x if self._use_letter_annotation_x_enabled else False

        self._use_letter_annotation_y_enabled = use_letter_annotation_y is not None
        use_letter_annotation_y = use_letter_annotation_y if self._use_letter_annotation_y_enabled else False

        self._start_at_index_0_enabled = start_at_index_0 is not None
        start_at_index_0 = start_at_index_0 if self._start_at_index_0_enabled else True

        self._n_cols_enabled = n_cols is not None
        n_cols = n_cols if self._n_cols_enabled else 10

        self._col_labels_enabled = col_labels is not None
        col_labels = col_labels if self._col_labels_enabled else ""

        self._row_labels_enabled = row_labels is not None
        row_labels = row_labels if self._row_labels_enabled else ""

        self._use_custom_col_labels_enabled = use_custom_col_labels is not None
        use_custom_col_labels = use_custom_col_labels if self._use_custom_col_labels_enabled else False

        self._use_custom_row_labels_enabled = use_custom_row_labels is not None
        use_custom_row_labels = use_custom_row_labels if self._use_custom_row_labels_enabled else False

        self._highlight_reference_points_enabled = highlight_reference_points is not None
        highlight_reference_points = bool(highlight_reference_points)
        
        self._highlight_color_enabled = bool(highlight_colors)
        enabled_highlight_colors = list(ANNOTATION_COLOR)
        if self._highlight_color_enabled:
            enabled_highlight_colors = highlight_colors
        

        self._cell_size_enabled = cell_size is not None
        cell_size = cell_size if self._cell_size_enabled else 0.1
        
        self._show_all_options = show_all_options

        self.create_widgets(
            square=square,
            symmetric_scaling=symmetric_scaling,
            annot=annot,
            annot_fontsize=annot_fontsize,
            annot_digits=annot_digits,
            annot_color=annot_color,
            linewidths=linewidths,
            linecolor=linecolor,
            robust=robust,
            cbar_orientations=cbar_orientations,
            cbar_tick_options = cbar_tick_options,
            use_letter_annotation_x=use_letter_annotation_x,
            use_letter_annotation_y=use_letter_annotation_y,
            start_at_index_0=start_at_index_0,
            n_cols=n_cols,
            col_labels=col_labels,
            row_labels=row_labels,
            use_custom_col_labels=use_custom_col_labels,
            use_custom_row_labels=use_custom_row_labels,
            highlight_reference_points=highlight_reference_points,
            highlight_colors=enabled_highlight_colors,
            cell_size=cell_size
        )

    def create_widgets(
        self,
        square: bool,
        symmetric_scaling: bool,
        annot: bool,
        annot_fontsize: float,
        annot_digits: int,
        annot_color: str,
        linewidths: float,
        linecolor: str,
        robust: bool,
        cbar_orientations: List[CBAR_ORIENTATION],
        cbar_tick_options: List[CBAR_TICK_MODE],
        use_letter_annotation_x: bool,
        use_letter_annotation_y: bool,
        start_at_index_0: bool,
        n_cols: int,
        col_labels: str,
        row_labels: str,
        use_custom_col_labels: bool,
        use_custom_row_labels: bool,
        highlight_reference_points: bool,
        highlight_colors: List[ANNOTATION_COLOR],
        cell_size: float
    ) -> None:
        """
        Create widgets for heatmap settings.
        """
        logger.debug("Creating widgets for HeatmapSettings")

        self._square_widget = WidgetFactory.checkbox(
            value=square,
            description="Square Cells",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._symmetric_scaling_widget = WidgetFactory.checkbox(
            value=symmetric_scaling,
            description="Symmetric Scaling around Center",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._highlight_reference_points_widget = WidgetFactory.checkbox(
            value=highlight_reference_points,
            description="Highlight Reference Points",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )
        self._highlight_reference_points_widget.observe(self.update_heatmap_settings_display, names='value')

        self._highlight_color_widget = WidgetFactory.dropdown(
            options=[e.value for e in highlight_colors],
            value=highlight_colors[0].value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            disabled=not highlight_reference_points
        )

        self._annot_widget = WidgetFactory.checkbox(
            value=annot,
            description="Annotate Values",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )
        self._annot_widget.observe(self.update_heatmap_settings_display, names='value')

        self._annot_fontsize_widget = WidgetFactory.float_number_input( 
            value=annot_fontsize,
            min_value=0.01,
            max_value=50.0,
            step=0.01,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            disabled=not annot
        )

        self._annot_digits_widget = WidgetFactory.number_input(
            value=annot_digits,
            min_value=0,
            max_value=5,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            disabled=not annot
        )

        self._annot_color_widget = WidgetFactory.dropdown(
            options=[e.value for e in ANNOTATION_COLOR],
            value=annot_color,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            disabled=not annot
        )

        self._cell_size_widget = WidgetFactory.float_number_input(
            value=cell_size,
            min_value=0.01,
            max_value=10.0,
            step=0.01,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._linewidths_widget = WidgetFactory.number_input(
            value=linewidths,
            min_value=0.0,
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._linecolor_widget = WidgetFactory.dropdown(
            options=[e.value for e in LINE_COLOR],
            value=linecolor,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._robust_widget = WidgetFactory.checkbox(
            value=robust,
            description="Robust Scaling",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        cbar_options = [c_option.value for c_option in cbar_orientations]
        self._cbar_mode_widget = WidgetFactory.dropdown(
            options= cbar_options,
            value=cbar_options[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        cbar_tick_modes = [c_option.value for c_option in cbar_tick_options]
        self._cbar_tick_mode_widget = WidgetFactory.dropdown(
            options= cbar_tick_modes,
            value=cbar_tick_modes[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._use_letter_annotation_x_widget = WidgetFactory.checkbox(
            value=use_letter_annotation_x,
            description="Use Letter Annotation X",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._use_letter_annotation_y_widget = WidgetFactory.checkbox(
            value=use_letter_annotation_y,
            description="Use Letter Annotation Y",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._start_at_index_0_widget = WidgetFactory.checkbox(
            value=start_at_index_0,
            description="Start at Index 0",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._n_cols_widget = WidgetFactory.number_input(
            value=n_cols,
            min_value=1,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._use_custom_col_labels_widget = WidgetFactory.checkbox(
            value=use_custom_col_labels,
            description="Use Custom Column Labels",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )
        self._use_custom_col_labels_widget.observe(self.update_heatmap_settings_display, names='value')

        self._use_custom_row_labels_widget = WidgetFactory.checkbox(
            value=use_custom_row_labels,
            description="Use Custom Row Labels",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )
        self._use_custom_row_labels_widget.observe(self.update_heatmap_settings_display, names='value')

        self._col_labels_widget = WidgetFactory.text_input(
            value=col_labels,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            disabled=not use_custom_col_labels
        )

        self._row_labels_widget = WidgetFactory.text_input(
            value=row_labels,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            disabled=not use_custom_row_labels
        )

        self.update_heatmap_settings_display()

    def update_heatmap_settings_display(self, change=None) -> None:
        """
        Update the display based on selected options.
        """
        logger.debug("Updating heatmap display")

        self._annot_fontsize_widget.disabled = not self._annot_widget.value
        self._annot_digits_widget.disabled = not self._annot_widget.value
        self._annot_color_widget.disabled = not self._annot_widget.value

        self._col_labels_widget.disabled = not self._use_custom_col_labels_widget.value
        self._row_labels_widget.disabled = not self._use_custom_row_labels_widget.value

        self._highlight_color_widget.disabled = not self._highlight_reference_points_widget.value or not self._highlight_color_enabled
        self._highlight_reference_points_widget.disabled = not self._highlight_color_enabled

    def get_active_widgets(self) -> List[widgets.Widget]:
        """
        Get a list of all interactive widgets for heatmap settings.

        Returns:
            List[widgets.Widget]: A list of all interactive widgets for heatmap settings.
        """
        logger.debug("Collecting active widgets for HeatmapSettings")
        active_widgets = []

        if self._square_enabled or self._show_all_options:
            active_widgets.append(self._square_widget)
        if self._symmetric_scaling_enabled or self._show_all_options:
            active_widgets.append(self._symmetric_scaling_widget)
        if self._highlight_reference_points_enabled or self._show_all_options:
            active_widgets.append(self._highlight_reference_points_widget)
        if self._highlight_color_enabled or self._show_all_options:
            active_widgets.append(self._highlight_color_widget)
        if self._annot_enabled or self._show_all_options:
            active_widgets.append(self._annot_widget)
        if self._annot_fontsize_enabled or self._show_all_options:
            active_widgets.append(self._annot_fontsize_widget)
        if self._annot_digits_enabled or self._show_all_options:
            active_widgets.append(self._annot_digits_widget)
        if self._annot_color_enabled or self._show_all_options:
            active_widgets.append(self._annot_color_widget)
        if self._cell_size_enabled or self._show_all_options:
            active_widgets.append(self._cell_size_widget)
        if self._linewidths_enabled or self._show_all_options:
            active_widgets.append(self._linewidths_widget)
        if self._linecolor_enabled or self._show_all_options:
            active_widgets.append(self._linecolor_widget)
        if self._robust_enabled or self._show_all_options:
            active_widgets.append(self._robust_widget)
        if self._cbar_enabled or self._show_all_options:
            active_widgets.append(self._cbar_mode_widget)
        if self._cbar_tick_modes_enabled or self._show_all_options:
            active_widgets.append(self._cbar_tick_mode_widget)
        if self._use_letter_annotation_x_enabled or self._show_all_options:
            active_widgets.append(self._use_letter_annotation_x_widget)
        if self._use_letter_annotation_y_enabled or self._show_all_options:
            active_widgets.append(self._use_letter_annotation_y_widget)
        if self._start_at_index_0_enabled or self._show_all_options:
            active_widgets.append(self._start_at_index_0_widget)
        if self._n_cols_enabled or self._show_all_options:
            active_widgets.append(self._n_cols_widget)
        if self._use_custom_col_labels_enabled or self._show_all_options:
            active_widgets.append(self._use_custom_col_labels_widget)
        if self._use_custom_row_labels_enabled or self._show_all_options:
            active_widgets.append(self._use_custom_row_labels_widget)
        if self._col_labels_enabled or self._show_all_options:
            active_widgets.append(self._col_labels_widget)
        if self._row_labels_enabled or self._show_all_options:
            active_widgets.append(self._row_labels_widget)

        return active_widgets

    def get_ui(self) -> widgets.Widget:
        """
        Get the UI widget for heatmap settings.

        Returns:
            widgets.Widget: The VBox widget containing all heatmap options.
        """
        logger.debug("Getting UI for HeatmapSettings")
        
        title_widget = WidgetFactory.html_widget(value="<h3>Heatmap Options</h3>")

        heatmap_widgets = [title_widget]  # Starte mit dem Titel, da er immer da ist

        # Basic checkboxes
        basic_checkboxes = []
        if self._square_enabled or self._show_all_options:
            basic_checkboxes.append(self._square_widget)
        if self._robust_enabled or self._show_all_options:
            basic_checkboxes.append(self._robust_widget)
        if basic_checkboxes:
            basic_checkboxes_container = WidgetFactory.vbox(
                children=basic_checkboxes,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(basic_checkboxes_container)

        # Label checkboxes (use letter annotation x & y, start at index 0)
        label_checkboxes = []
        if self._use_letter_annotation_x_enabled or self._show_all_options:
            label_checkboxes.append(self._use_letter_annotation_x_widget)
        if self._use_letter_annotation_y_enabled or self._show_all_options:
            label_checkboxes.append(self._use_letter_annotation_y_widget)
        if self._start_at_index_0_enabled or self._show_all_options:
            label_checkboxes.append(self._start_at_index_0_widget)
        if label_checkboxes:
            label_options_box = WidgetFactory.vbox(
                children=label_checkboxes,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(label_options_box)

        # Number of columns (moved above custom labels)
        if self._n_cols_enabled or self._show_all_options:
            n_cols_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Number of Columns:"),
                    WidgetFactory.vbox(
                        children=[self._n_cols_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(n_cols_container)

        # Custom labels (now with separate checkboxes)
        custom_labels_children = []
        if self._use_custom_col_labels_enabled or self._show_all_options:
            custom_labels_children.append(self._use_custom_col_labels_widget)
        if self._col_labels_enabled or self._show_all_options:
            col_labels_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Column Labels:"),
                    WidgetFactory.vbox(
                        children=[self._col_labels_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            custom_labels_children.append(col_labels_container)
        if self._use_custom_row_labels_enabled or self._show_all_options:
            custom_labels_children.append(self._use_custom_row_labels_widget)
        if self._row_labels_enabled or self._show_all_options:
            row_labels_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Row Labels:"),
                    WidgetFactory.vbox(
                        children=[self._row_labels_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            custom_labels_children.append(row_labels_container)
        if custom_labels_children:
            custom_labels_vbox = WidgetFactory.vbox(
                children=custom_labels_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(custom_labels_vbox)

        # Grid options (un-nested, on same level as number of columns)
        if self._cell_size_enabled or self._show_all_options:
            cell_size_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Cell Size:"),
                    WidgetFactory.vbox(
                        children=[self._cell_size_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(cell_size_container)

        if self._linewidths_enabled or self._show_all_options:
            linewidths_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Line Widths:"),
                    WidgetFactory.vbox(
                        children=[self._linewidths_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(linewidths_container)
        if self._linecolor_enabled or self._show_all_options:
            linecolor_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Line Color:"),
                    WidgetFactory.vbox(
                        children=[self._linecolor_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(linecolor_container)

            
        c_bar_children = []
        if self._cbar_enabled or self._show_all_options:
            c_bar_children.append(WidgetFactory.label(value="Colorbar:"))
            c_bar_children.append(
                    WidgetFactory.vbox(
                        children=[self._cbar_mode_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                )

        if self._cbar_tick_modes_enabled or self._show_all_options:
            c_bar_children.append(WidgetFactory.label(value="Colorbar Ticks:"))
            c_bar_children.append(WidgetFactory.vbox(
                        children=[self._cbar_tick_mode_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                )
        
        if c_bar_children:
            cbar_container = WidgetFactory.vbox(
                children=c_bar_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(cbar_container)

        # Annotation section (moved outside and above diverging)
        annot_children = []
        if self._annot_enabled or self._show_all_options:
            annot_children.append(self._annot_widget)
        if self._annot_fontsize_enabled or self._show_all_options:
            annot_fontsize_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Annotation Fontsize:"),
                    WidgetFactory.vbox(
                        children=[self._annot_fontsize_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            annot_children.append(annot_fontsize_container)
        if self._annot_digits_enabled or self._show_all_options:
            annot_digits_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Annotation Digits:"),
                    WidgetFactory.vbox(
                        children=[self._annot_digits_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            annot_children.append(annot_digits_container)
        if self._annot_color_enabled or self._show_all_options:
            annot_color_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Annotation Color:"),
                    WidgetFactory.vbox(
                        children=[self._annot_color_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            annot_children.append(annot_color_container)
            
        if annot_children:
            annot_container = WidgetFactory.vbox(
                children=annot_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(annot_container)

        # Diverging section (diverging colormap)
        diverging_children = []

        if self._highlight_reference_points_enabled or self._show_all_options:
            diverging_children.append(self._highlight_reference_points_widget)

        if self._highlight_color_enabled or self._show_all_options:
            highlight_color_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Highlight Color:"),
                    WidgetFactory.vbox(
                        children=[self._highlight_color_widget],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            diverging_children.append(highlight_color_container)

        if self._symmetric_scaling_enabled or self._show_all_options:
            diverging_children.append(self._symmetric_scaling_widget)

        if diverging_children:
            diverging_container = WidgetFactory.vbox(
                children=diverging_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            heatmap_widgets.append(diverging_container)
        
        return WidgetFactory.vbox(
            children=heatmap_widgets,
            gap="5px",
            overflow="visible",
            height="auto"
        )

    @property
    def square(self) -> bool:
        return self._square_widget.value

    def get_square_widget(self) -> widgets.Checkbox:
        return self._square_widget

    @property
    def symmetric_scaling(self) -> bool:
        return self._symmetric_scaling_widget.value

    def get_symmetric_scaling_widget(self) -> widgets.Checkbox:
        return self._symmetric_scaling_widget

    @property
    def annot(self) -> bool:
        return self._annot_widget.value

    def get_annot_widget(self) -> widgets.Checkbox:
        return self._annot_widget

    @property
    def annot_fontsize(self) -> float:
        return self._annot_fontsize_widget.value

    def get_annot_fontsize_widget(self) -> widgets.BoundedFloatText:
        return self._annot_fontsize_widget

    @property
    def annot_digits(self) -> int:
        return self._annot_digits_widget.value

    def get_annot_digits_widget(self) -> widgets.IntText:
        return self._annot_digits_widget

    @property
    def annot_color(self) -> ANNOTATION_COLOR:
        return ANNOTATION_COLOR(self._annot_color_widget.value)

    def get_annot_color_widget(self) -> widgets.Dropdown:
        return self._annot_color_widget

    @property
    def cell_size(self) -> float:
        return self._cell_size_widget.value

    def get_cell_size_widget(self) -> widgets.BoundedFloatText:
        return self._cell_size_widget

    @property
    def linewidths(self) -> float:
        return self._linewidths_widget.value

    def get_linewidths_widget(self) -> widgets.FloatText:
        return self._linewidths_widget

    @property
    def linecolor(self) -> str:
        return self._linecolor_widget.value

    def get_linecolor_widget(self) -> widgets.Dropdown:
        return self._linecolor_widget

    @property
    def robust(self) -> bool:
        return self._robust_widget.value

    def get_robust_widget(self) -> widgets.Checkbox:
        return self._robust_widget


    @property
    def cbar_orientation(self) -> CBAR_ORIENTATION:
        return CBAR_ORIENTATION(self._cbar_mode_widget.value)

    def get_cbar_mode_widget(self) -> widgets.Dropdown:
        return self._cbar_mode_widget

    @property
    def cbar_tick_mode(self) -> CBAR_TICK_MODE:
        return CBAR_TICK_MODE(self._cbar_tick_mode_widget.value)

    def get_cbar_tick_mode_widget(self) -> widgets.Dropdown:
        return self._cbar_tick_mode_widget

    @property
    def use_letter_annotation_x(self) -> bool:
        return self._use_letter_annotation_x_widget.value

    def get_use_letter_annotation_x_widget(self) -> widgets.Checkbox:
        return self._use_letter_annotation_x_widget

    @property
    def use_letter_annotation_y(self) -> bool:
        return self._use_letter_annotation_y_widget.value

    def get_use_letter_annotation_y_widget(self) -> widgets.Checkbox:
        return self._use_letter_annotation_y_widget

    @property
    def start_at_index_0(self) -> bool:
        return self._start_at_index_0_widget.value

    def get_start_at_index_0_widget(self) -> widgets.Checkbox:
        return self._start_at_index_0_widget

    @property
    def n_cols(self) -> int:
        return self._n_cols_widget.value

    def get_n_cols_widget(self) -> widgets.IntText:
        return self._n_cols_widget

    @property
    def use_custom_col_labels(self) -> bool:
        return self._use_custom_col_labels_widget.value

    def get_use_custom_col_labels_widget(self) -> widgets.Checkbox:
        return self._use_custom_col_labels_widget

    @property
    def use_custom_row_labels(self) -> bool:
        return self._use_custom_row_labels_widget.value

    def get_use_custom_row_labels_widget(self) -> widgets.Checkbox:
        return self._use_custom_row_labels_widget

    @property
    def col_labels(self) -> str:
        return self._col_labels_widget.value

    def get_col_labels_widget(self) -> widgets.Text:
        return self._col_labels_widget

    @property
    def row_labels(self) -> str:
        return self._row_labels_widget.value

    def get_row_labels_widget(self) -> widgets.Text:
        return self._row_labels_widget

    @property
    def highlight_reference_points(self) -> bool:
        return self._highlight_reference_points_widget.value

    def get_highlight_reference_points_widget(self) -> widgets.Checkbox:
        return self._highlight_reference_points_widget

    @property
    def highlight_color(self) -> ANNOTATION_COLOR:
        return ANNOTATION_COLOR(self._highlight_color_widget.value)

    def get_highlight_color_widget(self) -> widgets.Dropdown:
        return self._highlight_color_widget