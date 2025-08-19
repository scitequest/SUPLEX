import logging
from typing import Optional, List, Tuple
import ipywidgets as widgets
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.settings.submodule_settings_constants import OPTION_INSET, SCALE_TYPE, INTERPOLATION_TYPE, GRID_STYLE, LEGEND_POSITION, ASPECT_RATIO, SEQUENTIAL_COLOR_SCHEME, DIVERGENT_COLOR_SCHEME, OPTION_WIDGETS_MAX_WIDTH

logger = logging.getLogger(__name__)

class GeneralGraphSettings:
    """
    Settings for general graph options.
    """
    def __init__(
        self,
        # Axis settings
        col_descriptor: Optional[str] = None,
        row_descriptor: Optional[str] = None,
        z_descriptor: Optional[str] = None,
        invert_x_axis: Optional[bool] = None,
        invert_y_axis: Optional[bool] = None,
        invert_z_axis: Optional[bool] = None,
        swap_axes: Optional[bool] = None,
        
        # Display settings
        show_axis_ticks: Optional[bool] = None,
        show_axis_labels: Optional[bool] = None,
        show_grid: Optional[bool] = None,
        show_legend: Optional[bool] = None,
        show_title: Optional[bool] = None,
        include_empty_datasets: Optional[bool] = None,
        
        # Appearance settings
        sequential_color_scheme: Optional[SEQUENTIAL_COLOR_SCHEME] = None,
        divergent_color_scheme: Optional[DIVERGENT_COLOR_SCHEME] = None,
        resolution: Optional[Tuple[int, int]] = None,
        dpi: Optional[int] = None,
        transparency: Optional[float] = None,
        
        # Labels and titles
        title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        z_label: Optional[str] = None,
        max_label_length: Optional[int] = None,
        
        # Scale settings
        x_scale: Optional[SCALE_TYPE] = None,
        y_scale: Optional[SCALE_TYPE] = None,
        z_scale: Optional[SCALE_TYPE] = None,
        
        # Range settings
        x_range: Optional[Tuple[float, float]] = None,
        y_range: Optional[Tuple[float, float]] = None,
        z_range: Optional[Tuple[float, float]] = None,
        
        # Additional options
        marker_size: Optional[float] = None,
        line_width: Optional[float] = None,
        base_font_size: Optional[int] = None,
        title_font_size: Optional[int] = None,
        label_font_size: Optional[int] = None,
        tick_font_size: Optional[int] = None,
        aspect_ratio: Optional[ASPECT_RATIO] = None,
        interpolation: Optional[INTERPOLATION_TYPE] = None,
        show_colorbar: Optional[bool] = None,
        colorbar_label: Optional[str] = None,
        grid_style: Optional[GRID_STYLE] = None,
        legend_position: Optional[LEGEND_POSITION] = None,
        show_all_options: bool = False
    ) -> None:
        """
        Initialize GeneralGraphSettings with optional parameters.

        Args:
            ... (all parameters listed above)
            show_all_options (bool): Whether to show all options with defaults.
        """
        logger.debug("Initializing GeneralGraphSettings")

        self._col_descriptor_enabled = col_descriptor is not None
        col_descriptor = col_descriptor if self._col_descriptor_enabled else "Column"

        self._row_descriptor_enabled = row_descriptor is not None
        row_descriptor = row_descriptor if self._row_descriptor_enabled else "Row"

        self._z_descriptor_enabled = z_descriptor is not None
        z_descriptor = z_descriptor if self._z_descriptor_enabled else "Z"

        self._invert_x_axis_enabled = invert_x_axis is not None
        invert_x_axis = invert_x_axis if self._invert_x_axis_enabled else False

        self._invert_y_axis_enabled = invert_y_axis is not None
        invert_y_axis = invert_y_axis if self._invert_y_axis_enabled else False

        self._invert_z_axis_enabled = invert_z_axis is not None
        invert_z_axis = invert_z_axis if self._invert_z_axis_enabled else False

        self._swap_axes_enabled = swap_axes is not None
        swap_axes = swap_axes if self._swap_axes_enabled else False

        self._show_axis_ticks_enabled = show_axis_ticks is not None
        show_axis_ticks = show_axis_ticks if self._show_axis_ticks_enabled else True

        self._show_axis_labels_enabled = show_axis_labels is not None
        show_axis_labels = show_axis_labels if self._show_axis_labels_enabled else True

        self._show_grid_enabled = show_grid is not None
        show_grid = show_grid if self._show_grid_enabled else True

        self._show_legend_enabled = show_legend is not None
        show_legend = show_legend if self._show_legend_enabled else True

        self._show_title_enabled = show_title is not None
        show_title = show_title if self._show_title_enabled else True

        self._include_empty_datasets_enabled = include_empty_datasets is not None
        include_empty_datasets = include_empty_datasets if self._include_empty_datasets_enabled else False

        self._sequential_color_scheme_enabled = sequential_color_scheme is not None
        self._sequential_color_scheme = sequential_color_scheme if self._sequential_color_scheme_enabled and sequential_color_scheme in SEQUENTIAL_COLOR_SCHEME else SEQUENTIAL_COLOR_SCHEME.VIRIDIS
        sequential_color_scheme = self._sequential_color_scheme

        self._divergent_color_scheme_enabled = divergent_color_scheme is not None
        self._divergent_color_scheme = divergent_color_scheme if self._divergent_color_scheme_enabled and divergent_color_scheme in DIVERGENT_COLOR_SCHEME else DIVERGENT_COLOR_SCHEME.COOLWARM
        divergent_color_scheme = self._divergent_color_scheme

        self._resolution_enabled = resolution is not None
        resolution = resolution if self._resolution_enabled else (800, 600)

        self._dpi_enabled = dpi is not None
        dpi = dpi if self._dpi_enabled else 100

        self._transparency_enabled = transparency is not None
        transparency = transparency if self._transparency_enabled else 1.0

        self._title_enabled = title is not None
        title = title if self._title_enabled else ""

        self._x_label_enabled = x_label is not None
        x_label = x_label if self._x_label_enabled else ""

        self._y_label_enabled = y_label is not None
        y_label = y_label if self._y_label_enabled else ""

        self._z_label_enabled = z_label is not None
        z_label = z_label if self._z_label_enabled else ""

        self._max_label_length_enabled = max_label_length is not None
        max_label_length = max_label_length if self._max_label_length_enabled else 20

        self._x_scale_enabled = x_scale is not None
        self._x_scale = x_scale if self._x_scale_enabled and x_scale in SCALE_TYPE else SCALE_TYPE.LINEAR
        x_scale = self._x_scale

        self._y_scale_enabled = y_scale is not None
        self._y_scale = y_scale if self._y_scale_enabled and y_scale in SCALE_TYPE else SCALE_TYPE.LINEAR
        y_scale = self._y_scale

        self._z_scale_enabled = z_scale is not None
        self._z_scale = z_scale if self._z_scale_enabled and z_scale in SCALE_TYPE else SCALE_TYPE.LINEAR
        z_scale = self._z_scale

        self._x_range_enabled = x_range is not None
        x_range = x_range if self._x_range_enabled else (0.0, 1.0)

        self._y_range_enabled = y_range is not None
        y_range = y_range if self._y_range_enabled else (0.0, 1.0)

        self._z_range_enabled = z_range is not None
        z_range = z_range if self._z_range_enabled else (0.0, 1.0)

        self._marker_size_enabled = marker_size is not None
        marker_size = marker_size if self._marker_size_enabled else 5.0

        self._line_width_enabled = line_width is not None
        line_width = line_width if self._line_width_enabled else 1.5

        self._base_font_size_enabled = base_font_size is not None
        base_font_size = base_font_size if self._base_font_size_enabled else 12

        self._title_font_size_enabled = title_font_size is not None
        title_font_size = title_font_size if self._title_font_size_enabled else 14

        self._label_font_size_enabled = label_font_size is not None
        label_font_size = label_font_size if self._label_font_size_enabled else 12

        self._tick_font_size_enabled = tick_font_size is not None
        tick_font_size = tick_font_size if self._tick_font_size_enabled else 10

        self._aspect_ratio_enabled = aspect_ratio is not None
        self._aspect_ratio = aspect_ratio if self._aspect_ratio_enabled and aspect_ratio in ASPECT_RATIO else ASPECT_RATIO.AUTO
        aspect_ratio = self._aspect_ratio

        self._interpolation_enabled = interpolation is not None
        self._interpolation = interpolation if self._interpolation_enabled and interpolation in INTERPOLATION_TYPE else INTERPOLATION_TYPE.NEAREST
        interpolation = self._interpolation

        self._show_colorbar_enabled = show_colorbar is not None
        show_colorbar = show_colorbar if self._show_colorbar_enabled else True

        self._colorbar_label_enabled = colorbar_label is not None
        colorbar_label = colorbar_label if self._colorbar_label_enabled else ""

        self._grid_style_enabled = grid_style is not None
        self._grid_style = grid_style if self._grid_style_enabled and grid_style in GRID_STYLE else GRID_STYLE.DARKGRID
        grid_style = self._grid_style

        self._legend_position_enabled = legend_position is not None
        self._legend_position = legend_position if self._legend_position_enabled and legend_position in LEGEND_POSITION else LEGEND_POSITION.BEST
        legend_position = self._legend_position

        # Easy method to enable all options with default values
        self._show_all_options = show_all_options

        # Regardless of settings widgets will always be generated 
        self.create_widgets(
            col_descriptor=col_descriptor,
            row_descriptor=row_descriptor,
            z_descriptor=z_descriptor,
            invert_x_axis=invert_x_axis,
            invert_y_axis=invert_y_axis,
            invert_z_axis=invert_z_axis,
            swap_axes=swap_axes,
            show_axis_ticks=show_axis_ticks,
            show_axis_labels=show_axis_labels,
            show_grid=show_grid,
            show_legend=show_legend,
            show_title=show_title,
            include_empty_datasets=include_empty_datasets,
            sequential_color_scheme=sequential_color_scheme,
            divergent_color_scheme=divergent_color_scheme,
            resolution=resolution,
            dpi=dpi,
            transparency=transparency,
            title=title,
            x_label=x_label,
            y_label=y_label,
            z_label=z_label,
            max_label_length=max_label_length,
            x_scale=x_scale,
            y_scale=y_scale,
            z_scale=z_scale,
            x_range=x_range,
            y_range=y_range,
            z_range=z_range,
            marker_size=marker_size,
            line_width=line_width,
            base_font_size=base_font_size,
            title_font_size=title_font_size,
            label_font_size=label_font_size,
            tick_font_size=tick_font_size,
            aspect_ratio=aspect_ratio,
            interpolation=interpolation,
            show_colorbar=show_colorbar,
            colorbar_label=colorbar_label,
            grid_style=grid_style,
            legend_position=legend_position
        )
        
    def create_widgets(
        self,
        col_descriptor: str,
        row_descriptor: str,
        z_descriptor: str,
        invert_x_axis: bool,
        invert_y_axis: bool,
        invert_z_axis: bool,
        swap_axes: bool,
        show_axis_ticks: bool,
        show_axis_labels: bool,
        show_grid: bool,
        show_legend: bool,
        show_title: bool,
        include_empty_datasets: bool,
        sequential_color_scheme: SEQUENTIAL_COLOR_SCHEME,
        divergent_color_scheme: DIVERGENT_COLOR_SCHEME,
        resolution: Tuple[int, int],
        dpi: int,
        transparency: float,
        title: str,
        x_label: str,
        y_label: str,
        z_label: str,
        max_label_length: int,
        x_scale: SCALE_TYPE,
        y_scale: SCALE_TYPE,
        z_scale: SCALE_TYPE,
        x_range: Tuple[float, float],
        y_range: Tuple[float, float],
        z_range: Tuple[float, float],
        marker_size: float,
        line_width: float,
        base_font_size: int,
        title_font_size: int,
        label_font_size: int,
        tick_font_size: int,
        aspect_ratio: ASPECT_RATIO,
        interpolation: INTERPOLATION_TYPE,
        show_colorbar: bool,
        colorbar_label: str,
        grid_style: GRID_STYLE,
        legend_position: LEGEND_POSITION
    ) -> None:
        """
        Create widgets for general graph settings.

        Args:
            ... (all initial values)
        """
        logger.debug("Creating widgets for GeneralGraphSettings")

        self._col_descriptor_widget = WidgetFactory.text_input(
            value=col_descriptor,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._row_descriptor_widget = WidgetFactory.text_input(
            value=row_descriptor,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._z_descriptor_widget = WidgetFactory.text_input(
            value=z_descriptor,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._invert_x_axis_widget = WidgetFactory.checkbox(
            value=invert_x_axis,
            description="Invert X Axis",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._invert_y_axis_widget = WidgetFactory.checkbox(
            value=invert_y_axis,
            description="Invert Y Axis",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._invert_z_axis_widget = WidgetFactory.checkbox(
            value=invert_z_axis,
            description="Invert Z Axis",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._swap_axes_widget = WidgetFactory.checkbox(
            value=swap_axes,
            description="Swap Axes",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._show_axis_ticks_widget = WidgetFactory.checkbox(
            value=show_axis_ticks,
            description="Show Axis Ticks",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._show_axis_labels_widget = WidgetFactory.checkbox(
            value=show_axis_labels,
            description="Show Axis Labels",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._show_grid_widget = WidgetFactory.checkbox(
            value=show_grid,
            description="Show Grid",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._show_legend_widget = WidgetFactory.checkbox(
            value=show_legend,
            description="Show Legend",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._show_title_widget = WidgetFactory.checkbox(
            value=show_title,
            description="Show Title",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._include_empty_datasets_widget = WidgetFactory.checkbox(
            value=include_empty_datasets,
            description="Include Empty Datasets",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._show_colorbar_widget = WidgetFactory.checkbox(
            value=show_colorbar,
            description="Show Colorbar",
            indent=False,
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        seq_schemes = [scheme.value for scheme in SEQUENTIAL_COLOR_SCHEME]
        self._sequential_color_scheme_dropdown = WidgetFactory.dropdown(
            options=seq_schemes,
            value=sequential_color_scheme.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        div_schemes = [scheme.value for scheme in DIVERGENT_COLOR_SCHEME]
        self._divergent_color_scheme_dropdown = WidgetFactory.dropdown(
            options=div_schemes,
            value=divergent_color_scheme.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._resolution_width_widget = WidgetFactory.number_input(
            value=resolution[0],
            min_value=100,
            max_value=4000,
            step=100,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._resolution_height_widget = WidgetFactory.number_input(
            value=resolution[1],
            min_value=100,
            max_value=4000,
            step=100,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._dpi_widget = WidgetFactory.number_input(
            value=dpi,
            min_value=50,
            max_value=10000,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._transparency_widget = WidgetFactory.number_input(
            value=transparency,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._title_widget = WidgetFactory.text_input(
            value=title,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._x_label_widget = WidgetFactory.text_input(
            value=x_label,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._y_label_widget = WidgetFactory.text_input(
            value=y_label,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._z_label_widget = WidgetFactory.text_input(
            value=z_label,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._colorbar_label_widget = WidgetFactory.text_input(
            value=colorbar_label,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._max_label_length_widget = WidgetFactory.number_input(
            value=max_label_length,
            min_value=1,
            max_value=100,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        scale_types = [stype.value for stype in SCALE_TYPE]
        self._x_scale_dropdown = WidgetFactory.dropdown(
            options=scale_types,
            value=x_scale.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._y_scale_dropdown = WidgetFactory.dropdown(
            options=scale_types,
            value=y_scale.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._z_scale_dropdown = WidgetFactory.dropdown(
            options=scale_types,
            value=z_scale.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        self._x_range_min_widget = WidgetFactory.float_number_input(
            value=x_range[0],
            step=1,
            min_value = x_range[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._x_range_max_widget = WidgetFactory.float_number_input(
            value=x_range[1],
            step=1,
            max_value = x_range[1],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._y_range_min_widget = WidgetFactory.float_number_input(
            value=y_range[0],
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._y_range_max_widget = WidgetFactory.float_number_input(
            value=y_range[1],
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._z_range_min_widget = WidgetFactory.float_number_input(
            value=z_range[0],
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._z_range_max_widget = WidgetFactory.float_number_input(
            value=z_range[1],
            step=0.1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._marker_size_widget = WidgetFactory.float_number_input(
            value=marker_size,
            min_value=1.0,
            max_value=50.0,
            step=1.0,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._line_width_widget = WidgetFactory.float_number_input(
            value=line_width,
            min_value=0.5,
            max_value=10.0,
            step=0.5,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._base_font_size_widget = WidgetFactory.float_number_input(
            value=base_font_size,
            min_value=6,
            max_value=36,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._title_font_size_widget = WidgetFactory.number_input(
            value=title_font_size,
            min_value=6,
            max_value=36,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._label_font_size_widget = WidgetFactory.number_input(
            value=label_font_size,
            min_value=6,
            max_value=36,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._tick_font_size_widget = WidgetFactory.number_input(
            value=tick_font_size,
            min_value=6,
            max_value=36,
            step=1,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        aspect_ratios = [ar.name for ar in ASPECT_RATIO]
        self._aspect_ratio_dropdown = WidgetFactory.dropdown(
            options=aspect_ratios,
            value=aspect_ratio.name,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        interp_types = [itype.value for itype in INTERPOLATION_TYPE]
        self._interpolation_dropdown = WidgetFactory.dropdown(
            options=interp_types,
            value=interpolation.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        grid_styles = [gstyle.value for gstyle in GRID_STYLE]
        self._grid_style_dropdown = WidgetFactory.dropdown(
            options=grid_styles,
            value=grid_style.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

        leg_positions = [lpos.value for lpos in LEGEND_POSITION]
        self._legend_position_dropdown = WidgetFactory.dropdown(
            options=leg_positions,
            value=legend_position.value,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding=OPTION_INSET.PRIMARY)
        )

    @property
    def col_descriptor(self) -> str:
        return self._col_descriptor_widget.value

    def get_col_descriptor_widget(self) -> widgets.Text:
        return self._col_descriptor_widget

    @property
    def row_descriptor(self) -> str:
        return self._row_descriptor_widget.value

    def get_row_descriptor_widget(self) -> widgets.Text:
        return self._row_descriptor_widget

    @property
    def z_descriptor(self) -> str:
        return self._z_descriptor_widget.value

    def get_z_descriptor_widget(self) -> widgets.Text:
        return self._z_descriptor_widget

    @property
    def invert_x_axis(self) -> bool:
        return self._invert_x_axis_widget.value

    def get_invert_x_axis_widget(self) -> widgets.Checkbox:
        return self._invert_x_axis_widget

    @property
    def invert_y_axis(self) -> bool:
        return self._invert_y_axis_widget.value

    def get_invert_y_axis_widget(self) -> widgets.Checkbox:
        return self._invert_y_axis_widget

    @property
    def invert_z_axis(self) -> bool:
        return self._invert_z_axis_widget.value

    def get_invert_z_axis_widget(self) -> widgets.Checkbox:
        return self._invert_z_axis_widget

    @property
    def swap_axes(self) -> bool:
        return self._swap_axes_widget.value

    def get_swap_axes_widget(self) -> widgets.Checkbox:
        return self._swap_axes_widget

    @property
    def show_axis_ticks(self) -> bool:
        return self._show_axis_ticks_widget.value

    def get_show_axis_ticks_widget(self) -> widgets.Checkbox:
        return self._show_axis_ticks_widget

    @property
    def show_axis_labels(self) -> bool:
        return self._show_axis_labels_widget.value

    def get_show_axis_labels_widget(self) -> widgets.Checkbox:
        return self._show_axis_labels_widget

    @property
    def show_grid(self) -> bool:
        return self._show_grid_widget.value

    def get_show_grid_widget(self) -> widgets.Checkbox:
        return self._show_grid_widget

    @property
    def show_legend(self) -> bool:
        return self._show_legend_widget.value

    def get_show_legend_widget(self) -> widgets.Checkbox:
        return self._show_legend_widget

    @property
    def show_title(self) -> bool:
        return self._show_title_widget.value

    def get_show_title_widget(self) -> widgets.Checkbox:
        return self._show_title_widget

    @property
    def include_empty_datasets(self) -> bool:
        return self._include_empty_datasets_widget.value

    def get_include_empty_datasets_widget(self) -> widgets.Checkbox:
        return self._include_empty_datasets_widget

    @property
    def show_colorbar(self) -> bool:
        return self._show_colorbar_widget.value

    def get_show_colorbar_widget(self) -> widgets.Checkbox:
        return self._show_colorbar_widget

    @property
    def sequential_color_scheme(self) -> SEQUENTIAL_COLOR_SCHEME:
        return SEQUENTIAL_COLOR_SCHEME(self._sequential_color_scheme_dropdown.value)

    def get_sequential_color_scheme_dropdown(self) -> widgets.Dropdown:
        return self._sequential_color_scheme_dropdown

    @property
    def divergent_color_scheme(self) -> DIVERGENT_COLOR_SCHEME:
        return DIVERGENT_COLOR_SCHEME(self._divergent_color_scheme_dropdown.value)

    def get_divergent_color_scheme_dropdown(self) -> widgets.Dropdown:
        return self._divergent_color_scheme_dropdown

    @property
    def resolution(self) -> Tuple[int, int]:
        return (self._resolution_width_widget.value, self._resolution_height_widget.value)

    def get_resolution_width_widget(self) -> widgets.IntText:
        return self._resolution_width_widget

    def get_resolution_height_widget(self) -> widgets.IntText:
        return self._resolution_height_widget

    @property
    def dpi(self) -> int:
        return self._dpi_widget.value

    def get_dpi_widget(self) -> widgets.IntText:
        return self._dpi_widget

    @property
    def transparency(self) -> float:
        return self._transparency_widget.value

    def get_transparency_widget(self) -> widgets.FloatText:
        return self._transparency_widget

    @property
    def title(self) -> str:
        return self._title_widget.value

    def get_title_widget(self) -> widgets.Text:
        return self._title_widget

    @property
    def x_label(self) -> str:
        return self._x_label_widget.value

    def get_x_label_widget(self) -> widgets.Text:
        return self._x_label_widget

    @property
    def y_label(self) -> str:
        return self._y_label_widget.value

    def get_y_label_widget(self) -> widgets.Text:
        return self._y_label_widget

    @property
    def z_label(self) -> str:
        return self._z_label_widget.value

    def get_z_label_widget(self) -> widgets.Text:
        return self._z_label_widget

    @property
    def colorbar_label(self) -> str:
        return self._colorbar_label_widget.value

    def get_colorbar_label_widget(self) -> widgets.Text:
        return self._colorbar_label_widget

    @property
    def max_label_length(self) -> int:
        return self._max_label_length_widget.value

    def get_max_label_length_widget(self) -> widgets.IntText:
        return self._max_label_length_widget

    @property
    def x_scale(self) -> SCALE_TYPE:
        return SCALE_TYPE(self._x_scale_dropdown.value)

    def get_x_scale_dropdown(self) -> widgets.Dropdown:
        return self._x_scale_dropdown

    @property
    def y_scale(self) -> SCALE_TYPE:
        return SCALE_TYPE(self._y_scale_dropdown.value)

    def get_y_scale_dropdown(self) -> widgets.Dropdown:
        return self._y_scale_dropdown

    @property
    def z_scale(self) -> SCALE_TYPE:
        return SCALE_TYPE(self._z_scale_dropdown.value)

    def get_z_scale_dropdown(self) -> widgets.Dropdown:
        return self._z_scale_dropdown

    @property
    def x_range(self) -> Tuple[float, float]:
        return (self._x_range_min_widget.value, self._x_range_max_widget.value)

    def get_x_range_min_widget(self) -> widgets.FloatText:
        return self._x_range_min_widget

    def get_x_range_max_widget(self) -> widgets.FloatText:
        return self._x_range_max_widget

    @property
    def y_range(self) -> Tuple[float, float]:
        return (self._y_range_min_widget.value, self._y_range_max_widget.value)

    def get_y_range_min_widget(self) -> widgets.FloatText:
        return self._y_range_min_widget

    def get_y_range_max_widget(self) -> widgets.FloatText:
        return self._y_range_max_widget

    @property
    def z_range(self) -> Tuple[float, float]:
        return (self._z_range_min_widget.value, self._z_range_max_widget.value)

    def get_z_range_min_widget(self) -> widgets.FloatText:
        return self._z_range_min_widget

    def get_z_range_max_widget(self) -> widgets.FloatText:
        return self._z_range_max_widget

    @property
    def marker_size(self) -> float:
        return self._marker_size_widget.value

    def get_marker_size_widget(self) -> widgets.FloatText:
        return self._marker_size_widget

    @property
    def line_width(self) -> float:
        return self._line_width_widget.value

    def get_line_width_widget(self) -> widgets.FloatText:
        return self._line_width_widget

    @property
    def base_font_size(self) -> int:
        return self._base_font_size_widget.value

    def get_base_font_size_widget(self) -> widgets.IntText:
        return self._base_font_size_widget

    @property
    def title_font_size(self) -> int:
        return self._title_font_size_widget.value

    def get_title_font_size_widget(self) -> widgets.IntText:
        return self._title_font_size_widget

    @property
    def label_font_size(self) -> int:
        return self._label_font_size_widget.value

    def get_label_font_size_widget(self) -> widgets.IntText:
        return self._label_font_size_widget

    @property
    def tick_font_size(self) -> int:
        return self._tick_font_size_widget.value

    def get_tick_font_size_widget(self) -> widgets.IntText:
        return self._tick_font_size_widget

    @property
    def aspect_ratio(self) -> ASPECT_RATIO:
        return ASPECT_RATIO[self._aspect_ratio_dropdown.value]

    def get_aspect_ratio_dropdown(self) -> widgets.Dropdown:
        return self._aspect_ratio_dropdown

    @property
    def interpolation(self) -> INTERPOLATION_TYPE:
        return INTERPOLATION_TYPE(self._interpolation_dropdown.value)

    def get_interpolation_dropdown(self) -> widgets.Dropdown:
        return self._interpolation_dropdown

    @property
    def grid_style(self) -> GRID_STYLE:
        return GRID_STYLE(self._grid_style_dropdown.value)

    def get_grid_style_dropdown(self) -> widgets.Dropdown:
        return self._grid_style_dropdown

    @property
    def legend_position(self) -> LEGEND_POSITION:
        return LEGEND_POSITION(self._legend_position_dropdown.value)

    def get_legend_position_dropdown(self) -> widgets.Dropdown:
        return self._legend_position_dropdown
    
    def get_active_widgets(self) -> List[widgets.Widget]:
        """
        Get a list of all interactive widgets for general graph settings.
    
        Returns:
            List[widgets.Widget]: A list of all interactive widgets for general graph settings.
        """
        logger.debug("Collecting all interactive widgets for GeneralGraphSettings")
        active_widgets = []
    
        if self._col_descriptor_enabled or self._show_all_options:
            active_widgets.append(self._col_descriptor_widget)
        if self._row_descriptor_enabled or self._show_all_options:
            active_widgets.append(self._row_descriptor_widget)
        if self._z_descriptor_enabled or self._show_all_options:
            active_widgets.append(self._z_descriptor_widget)
        if self._invert_x_axis_enabled or self._show_all_options:
            active_widgets.append(self._invert_x_axis_widget)
        if self._invert_y_axis_enabled or self._show_all_options:
            active_widgets.append(self._invert_y_axis_widget)
        if self._invert_z_axis_enabled or self._show_all_options:
            active_widgets.append(self._invert_z_axis_widget)
        if self._swap_axes_enabled or self._show_all_options:
            active_widgets.append(self._swap_axes_widget)
        if self._show_axis_ticks_enabled or self._show_all_options:
            active_widgets.append(self._show_axis_ticks_widget)
        if self._show_axis_labels_enabled or self._show_all_options:
            active_widgets.append(self._show_axis_labels_widget)
        if self._show_grid_enabled or self._show_all_options:
            active_widgets.append(self._show_grid_widget)
        if self._show_legend_enabled or self._show_all_options:
            active_widgets.append(self._show_legend_widget)
        if self._show_title_enabled or self._show_all_options:
            active_widgets.append(self._show_title_widget)
        if self._include_empty_datasets_enabled or self._show_all_options:
            active_widgets.append(self._include_empty_datasets_widget)
        if self._show_colorbar_enabled or self._show_all_options:
            active_widgets.append(self._show_colorbar_widget)
        if self._sequential_color_scheme_enabled or self._show_all_options:
            active_widgets.append(self._sequential_color_scheme_dropdown)
        if self._divergent_color_scheme_enabled or self._show_all_options:
            active_widgets.append(self._divergent_color_scheme_dropdown)
        if self._resolution_enabled or self._show_all_options:
            active_widgets.append(self._resolution_width_widget)
            active_widgets.append(self._resolution_height_widget)
        if self._dpi_enabled or self._show_all_options:
            active_widgets.append(self._dpi_widget)
        if self._transparency_enabled or self._show_all_options:
            active_widgets.append(self._transparency_widget)
        if self._title_enabled or self._show_all_options:
            active_widgets.append(self._title_widget)
        if self._x_label_enabled or self._show_all_options:
            active_widgets.append(self._x_label_widget)
        if self._y_label_enabled or self._show_all_options:
            active_widgets.append(self._y_label_widget)
        if self._z_label_enabled or self._show_all_options:
            active_widgets.append(self._z_label_widget)
        if self._colorbar_label_enabled or self._show_all_options:
            active_widgets.append(self._colorbar_label_widget)
        if self._max_label_length_enabled or self._show_all_options:
            active_widgets.append(self._max_label_length_widget)
        if self._x_scale_enabled or self._show_all_options:
            active_widgets.append(self._x_scale_dropdown)
        if self._y_scale_enabled or self._show_all_options:
            active_widgets.append(self._y_scale_dropdown)
        if self._z_scale_enabled or self._show_all_options:
            active_widgets.append(self._z_scale_dropdown)
        if self._x_range_enabled or self._show_all_options:
            active_widgets.append(self._x_range_min_widget)
            active_widgets.append(self._x_range_max_widget)
        if self._y_range_enabled or self._show_all_options:
            active_widgets.append(self._y_range_min_widget)
            active_widgets.append(self._y_range_max_widget)
        if self._z_range_enabled or self._show_all_options:
            active_widgets.append(self._z_range_min_widget)
            active_widgets.append(self._z_range_max_widget)
        if self._marker_size_enabled or self._show_all_options:
            active_widgets.append(self._marker_size_widget)
        if self._line_width_enabled or self._show_all_options:
            active_widgets.append(self._line_width_widget)
        if self._base_font_size_enabled or self._show_all_options:
            active_widgets.append(self._base_font_size_widget)
        if self._title_font_size_enabled or self._show_all_options:
            active_widgets.append(self._title_font_size_widget)
        if self._label_font_size_enabled or self._show_all_options:
            active_widgets.append(self._label_font_size_widget)
        if self._tick_font_size_enabled or self._show_all_options:
            active_widgets.append(self._tick_font_size_widget)
        if self._aspect_ratio_enabled or self._show_all_options:
            active_widgets.append(self._aspect_ratio_dropdown)
        if self._interpolation_enabled or self._show_all_options:
            active_widgets.append(self._interpolation_dropdown)
        if self._grid_style_enabled or self._show_all_options:
            active_widgets.append(self._grid_style_dropdown)
        if self._legend_position_enabled or self._show_all_options:
            active_widgets.append(self._legend_position_dropdown)
    
        return active_widgets
        
    def get_ui(self) -> widgets.Widget:
        """
        Get the UI widget for general graph settings.

        Returns:
            widgets.Widget: The VBox widget containing all general graph options.
        """
        logger.debug("Getting UI for GeneralGraphSettings")
        general_widgets = []
        general_widgets.append(WidgetFactory.html_widget(
            value="<h3>General Graph Options</h3>"
        ))

        # Axis Descriptors
        descriptor_children = []
        if self._col_descriptor_enabled or self._show_all_options:
            col_descriptor_box = WidgetFactory.vbox(children = [self._col_descriptor_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            descriptor_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Column Descriptor:"),
                    col_descriptor_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._row_descriptor_enabled or self._show_all_options:
            row_descriptor_box = WidgetFactory.vbox(children = [self._row_descriptor_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            descriptor_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Row Descriptor:"),
                    row_descriptor_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._z_descriptor_enabled or self._show_all_options:
            z_descriptor_box = WidgetFactory.vbox(children = [self._z_descriptor_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            descriptor_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Z Descriptor:"),
                    z_descriptor_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if descriptor_children:
            general_widgets.append(WidgetFactory.vbox(
                children=descriptor_children,
                gap="15px",
                overflow="visible",
                height="auto"
            ))

        # Invert and Swap Checkboxes
        invert_children = []
        if self._invert_x_axis_enabled or self._show_all_options:
            invert_children.append(self._invert_x_axis_widget)
        if self._invert_y_axis_enabled or self._show_all_options:
            invert_children.append(self._invert_y_axis_widget)
        if self._invert_z_axis_enabled or self._show_all_options:
            invert_children.append(self._invert_z_axis_widget)
        if self._swap_axes_enabled or self._show_all_options:
            invert_children.append(self._swap_axes_widget)
        if invert_children:
            general_widgets.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Axis Options:"),
                    WidgetFactory.vbox(
                        children=invert_children,
                        gap="5px",
                        overflow="visible",
                        height="auto"
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))

        # Display Checkboxes
        display_children = []
        if self._show_axis_ticks_enabled or self._show_all_options:
            display_children.append(self._show_axis_ticks_widget)
        if self._show_axis_labels_enabled or self._show_all_options:
            display_children.append(self._show_axis_labels_widget)
        if self._show_grid_enabled or self._show_all_options:
            display_children.append(self._show_grid_widget)
        if self._show_legend_enabled or self._show_all_options:
            display_children.append(self._show_legend_widget)
        if self._show_title_enabled or self._show_all_options:
            display_children.append(self._show_title_widget)
        if self._include_empty_datasets_enabled or self._show_all_options:
            display_children.append(self._include_empty_datasets_widget)
        if self._show_colorbar_enabled or self._show_all_options:
            display_children.append(self._show_colorbar_widget)
        if display_children:
            general_widgets.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Display Options:"),
                    WidgetFactory.vbox(
                        children=display_children,
                        gap="5px",
                        overflow="visible",
                        height="auto"
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))

        # Appearance
        appearance_children = []
        if self._sequential_color_scheme_enabled or self._show_all_options:
            appearance_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Sequential Color Scheme:"),
                    self._sequential_color_scheme_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._divergent_color_scheme_enabled or self._show_all_options:
            appearance_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Divergent Color Scheme:"),
                    self._divergent_color_scheme_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._resolution_enabled or self._show_all_options:
            appearance_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Resolution:"),
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.vbox(
                                children=[
                                    WidgetFactory.label(value="Width:"),
                                    WidgetFactory.vbox(
                                        children=[self._resolution_width_widget],
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
                            ),
                            WidgetFactory.vbox(
                                children=[
                                    WidgetFactory.label(value="Height:"),
                                    WidgetFactory.vbox(
                                        children=[self._resolution_height_widget],
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
                        ],
                        gap="15px",
                        overflow="visible",
                        height="auto"
                    )
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._dpi_enabled or self._show_all_options:
            appearance_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="DPI:"),
                    WidgetFactory.vbox(
                        children=[self._dpi_widget],
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
            ))
        if self._transparency_enabled or self._show_all_options:
            appearance_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Transparency:"),
                    WidgetFactory.vbox(
                        children=[self._transparency_widget],
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
            ))
        if appearance_children:
            general_widgets.append(WidgetFactory.vbox(
                children=appearance_children,
                gap="5px",
                overflow="visible",
                height="auto"
            ))

        # Labels and Titles
        labels_children = []
        if self._title_enabled or self._show_all_options:
            title_box = WidgetFactory.vbox(children = [self._title_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            labels_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Title:"),
                    title_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._x_label_enabled or self._show_all_options:
            x_label_box = WidgetFactory.vbox(children = [self._x_label_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            labels_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="X Label:"),
                    x_label_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._y_label_enabled or self._show_all_options:
            y_label_box = WidgetFactory.vbox(children = [self._y_label_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            labels_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Y Label:"),
                    y_label_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._z_label_enabled or self._show_all_options:
            z_label_box = WidgetFactory.vbox(children = [self._z_label_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            labels_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Z Label:"),
                    z_label_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._colorbar_label_enabled or self._show_all_options:
            colorbar_label_box = WidgetFactory.vbox(children = [self._colorbar_label_widget],layout=widgets.Layout(padding=OPTION_INSET.PRIMARY))
            labels_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Colorbar Label:"),
                    colorbar_label_box
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._max_label_length_enabled or self._show_all_options:
            labels_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Max Label Length:"),
                    WidgetFactory.vbox(
                        children=[self._max_label_length_widget],
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
            ))
        if labels_children:
            general_widgets.append(WidgetFactory.vbox(
                children=labels_children,
                gap="5px",
                overflow="visible",
                height="auto"
            ))

        # Scale and Range
        scale_children = []
        if self._x_scale_enabled or self._show_all_options:
            scale_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="X Scale:"),
                    self._x_scale_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._y_scale_enabled or self._show_all_options:
            scale_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Y Scale:"),
                    self._y_scale_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._z_scale_enabled or self._show_all_options:
            scale_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Z Scale:"),
                    self._z_scale_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if scale_children:
            general_widgets.append(WidgetFactory.vbox(
                children=scale_children,
                gap="15px",
                overflow="visible",
                height="auto"
            ))

        range_children = []
        if self._x_range_enabled or self._show_all_options:
            range_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.label(value="X Range Min:"),
                            WidgetFactory.vbox(
                                children=[self._x_range_min_widget],
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
                    ),
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.label(value="X Range Max:"),
                            WidgetFactory.vbox(
                                children=[self._x_range_max_widget],
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
                ],
                gap="5px",
                overflow="visible",
                height="auto"
            ))
        if self._y_range_enabled or self._show_all_options:
            range_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.label(value="Y Range Min:"),
                            WidgetFactory.vbox(
                                children=[self._y_range_min_widget],
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
                    ),
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.label(value="Y Range Max:"),
                            WidgetFactory.vbox(
                                children=[self._y_range_max_widget],
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
                ],
                gap="5px",
                overflow="visible",
                height="auto"
            ))
        if self._z_range_enabled or self._show_all_options:
            range_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.label(value="Z Range Min:"),
                            WidgetFactory.vbox(
                                children=[self._z_range_min_widget],
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
                    ),
                    WidgetFactory.vbox(
                        children=[
                            WidgetFactory.label(value="Z Range Max:"),
                            WidgetFactory.vbox(
                                children=[self._z_range_max_widget],
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
                ],
                gap="5px",
                overflow="visible",
                height="auto"
            ))
        if range_children:
            general_widgets.append(WidgetFactory.vbox(
                children=range_children,
                gap="15px",
                overflow="visible",
                height="auto"
            ))

        # Additional Options
        additional_children = []
        if self._marker_size_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Marker Size:"),
                    WidgetFactory.vbox(
                        children=[self._marker_size_widget],
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
            ))
        if self._line_width_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Line Width:"),
                    WidgetFactory.vbox(
                        children=[self._line_width_widget],
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
            ))
        if self._base_font_size_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Base Font Size:"),
                    WidgetFactory.vbox(
                        children=[self._base_font_size_widget],
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
            ))
        if self._title_font_size_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Title Font Size:"),
                    WidgetFactory.vbox(
                        children=[self._title_font_size_widget],
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
            ))
        if self._label_font_size_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Label Font Size:"),
                    WidgetFactory.vbox(
                        children=[self._label_font_size_widget],
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
            ))
        if self._tick_font_size_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Tick Font Size:"),
                    WidgetFactory.vbox(
                        children=[self._tick_font_size_widget],
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
            ))
        if self._aspect_ratio_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Aspect Ratio:"),
                    self._aspect_ratio_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._interpolation_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Interpolation:"),
                    self._interpolation_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._grid_style_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Grid Style:"),
                    self._grid_style_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if self._legend_position_enabled or self._show_all_options:
            additional_children.append(WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Legend Position:"),
                    self._legend_position_dropdown
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            ))
        if additional_children:
            general_widgets.append(WidgetFactory.vbox(
                children=additional_children,
                gap="5px",
                overflow="visible",
                height="auto"
            ))

        return WidgetFactory.vbox(
            children=general_widgets,
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(max_width=OPTION_WIDGETS_MAX_WIDTH)
        )