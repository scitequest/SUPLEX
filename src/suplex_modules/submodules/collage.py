import logging
from typing import List, Optional, Union, Dict, Any
import ipywidgets as widgets
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt

import svgutils.transform as sg
import tempfile
import os

from suplex_modules.submodules.submodule_utils import get_color_tuple
from suplex_modules.submodules.submodule_constants import (
    COLLAGE_LAYOUT,
    COLOR,
    READING_ORDER,
    TITLE_POSITION,
    SCALE_OPTION
)
from suplex_modules.submodules.settings.submodule_settings_constants import (
    OPTION_INSET
)
from ui.widget_factory import WidgetFactory

logger = logging.getLogger(__name__)

def format_image_to_svg(input_item: Union[Image.Image, plt.Figure], dpi: int = 300) -> sg.SVGFigure:
    """
    Formats PIL image or Matplotlib figure to SVGFigure.
    """
    try:
        if isinstance(input_item, Image.Image):
            img_array = np.array(input_item)
            if img_array.ndim == 2:
                img_array = np.stack([img_array] * 3, axis=-1)
            elif img_array.shape[2] not in (3, 4):
                raise ValueError("Unsupported channel count")

            width_px, height_px = img_array.shape[1], img_array.shape[0]
            width_in = width_px / dpi
            height_in = height_px / dpi
            fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)
            ax = fig.add_subplot(111)
            ax.imshow(img_array, aspect="equal")
            ax.axis("off")
            plt.tight_layout(pad=0)
            input_item = fig

        if isinstance(input_item, plt.Figure):
            tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            input_item.savefig(tmpfile.name, format="svg", dpi=dpi)
            tmpfile.close()
            svg_fig = sg.fromfile(tmpfile.name)
            plt.close(input_item)
            os.remove(tmpfile.name)
            return svg_fig

        # Return svg's as is
        if isinstance(input_item, sg.SVGFigure):
            return input_item

        raise ValueError("Unsupported input type")
    except Exception as e:
        logger.error(f"Failed to convert input to SVGFigure: {e}")
        raise ValueError("Conversion to figure failed")

def scale_svgs(svgs: List[sg.SVGFigure], scale_option: SCALE_OPTION) -> List[sg.SVGFigure]:
    """
    Scale SVGFigures according to the specified scale option while preserving or ignoring aspect ratio.
    """
    logger.debug(f"Scaling SVGs with option: {scale_option}")
    if scale_option == SCALE_OPTION.NO_SCALE:
        return svgs

    widths = [float(svg.width.rstrip("ptpx")) for svg in svgs]
    heights = [float(svg.height.rstrip("ptpx")) for svg in svgs]
    height_min, height_max = min(heights), max(heights)
    width_min, width_max = min(widths), max(widths)

    scaled_svgs = []
    for svg in svgs:
        h = float(svg.height.rstrip("ptpx"))
        w = float(svg.width.rstrip("ptpx"))
        aspect_ratio = w / h if h != 0 else 1.0

        new_w = w
        new_h = h

        if scale_option == SCALE_OPTION.DOWNSCALE_TO_WIDTH:
            new_w = width_min
            new_h = new_w / aspect_ratio if aspect_ratio != 0 else h
        elif scale_option == SCALE_OPTION.UPSCALE_TO_WIDTH:
            new_w = width_max
            new_h = new_w / aspect_ratio if aspect_ratio != 0 else h
        elif scale_option == SCALE_OPTION.DOWNSCALE_TO_HEIGHT:
            new_h = height_min
            new_w = new_h * aspect_ratio
        elif scale_option == SCALE_OPTION.UPSCALE_TO_HEIGHT:
            new_h = height_max
            new_w = new_h * aspect_ratio
        elif scale_option == SCALE_OPTION.STRETCH_TO_MIN_WIDTH:
            new_w = width_min
            new_h = h
        elif scale_option == SCALE_OPTION.STRETCH_TO_MAX_WIDTH:
            new_w = width_max
            new_h = h
        elif scale_option == SCALE_OPTION.STRETCH_TO_MIN_HEIGHT:
            new_h = height_min
            new_w = w
        elif scale_option == SCALE_OPTION.STRETCH_TO_MAX_HEIGHT:
            new_h = height_max
            new_w = w
        elif scale_option == SCALE_OPTION.STRETCH_TO_MIN_SIZE:
            new_w = width_min
            new_h = height_min
        elif scale_option == SCALE_OPTION.STRETCH_TO_MAX_SIZE:
            new_w = width_max
            new_h = height_max
        else:
            logger.warning(f"Unknown scale option: {scale_option}, returning original SVG")
            scaled_svgs.append(svg)
            continue

        scale_factor_x = new_w / w if w != 0 else 1.0
        scale_factor_y = new_h / h if h != 0 else 1.0

        new_fig = sg.SVGFigure(f"{new_w}pt", f"{new_h}pt")
        # Without set size width and height become None
        new_fig.set_size((f"{new_w}pt", f"{new_h}pt"))
            
        svg_root = svg.getroot()
        svg_root.scale(scale_factor_x, scale_factor_y)
        new_fig.append(svg_root)
        scaled_svgs.append(new_fig)

    return scaled_svgs

def add_padding_to_svgs(svgs: List[sg.SVGFigure], horizontal_padding: int = 0, vertical_padding: int = 0) -> List[sg.SVGFigure]:
    """
    Add padding to SVGFigures by adjusting size and positions.
    """
    logger.debug(f"Adding padding to SVGs: horizontal={horizontal_padding}, vertical={vertical_padding}")
    if horizontal_padding == 0 and vertical_padding == 0:
        return svgs

    padded_svgs = []
    for svg in svgs:
        current_width = float(svg.width.rstrip("ptpx"))
        current_height = float(svg.height.rstrip("ptpx"))

        new_width = current_width + 2 * horizontal_padding
        new_height = current_height + 2 * vertical_padding

        new_fig = sg.SVGFigure(f"{new_width}pt", f"{new_height}pt")
        new_fig.set_size((f"{new_width}pt", f"{new_height}pt"))
        
        svg_root = svg.getroot()
        svg_root.moveto(horizontal_padding, vertical_padding)
        new_fig.append(svg_root)
        padded_svgs.append(new_fig)

    return padded_svgs

def get_gridded_svgs(
    svgs: List[sg.SVGFigure],
    layout: COLLAGE_LAYOUT
) -> List[sg.SVGFigure]:
    """
    Adjust sizes of SVGFigures based on layout by adding padding to equalize dimensions.
    """
    logger.debug(f"Adjusting SVG sizes for layout: {layout}")
    if not svgs:
        return svgs

    widths = [float(svg.width.rstrip("ptpx")) for svg in svgs]
    heights = [float(svg.height.rstrip("ptpx")) for svg in svgs]
    max_width = max(widths) if widths else 1.0
    max_height = max(heights) if heights else 1.0

    gridded_svgs = []
    for svg in svgs:
        current_width = float(svg.width.rstrip("ptpx"))
        current_height = float(svg.height.rstrip("ptpx"))
        if layout in [COLLAGE_LAYOUT.GRID_EQUAL_ALL, COLLAGE_LAYOUT.MOSAIC_EQUAL_ALL]:
            delta_width = (max_width - current_width) / 2
            delta_height = (max_height - current_height) / 2
        elif layout in [COLLAGE_LAYOUT.GRID_EQUAL_WIDTH, COLLAGE_LAYOUT.MOSAIC_EQUAL_WIDTH]:
            delta_width = (max_width - current_width) / 2
            delta_height = 0
        elif layout in [COLLAGE_LAYOUT.GRID_EQUAL_HEIGHT, COLLAGE_LAYOUT.MOSAIC_EQUAL_HEIGHT]:
            delta_width = 0
            delta_height = (max_height - current_height) / 2
        else:
            logger.warning(f"Unknown layout: {layout}, no size adjustment applied")
            delta_width = 0
            delta_height = 0

        grid_svg = add_padding_to_svgs(
            [svg],
            horizontal_padding=delta_width,
            vertical_padding=delta_height
        )[0]
        gridded_svgs.append(grid_svg)

    return gridded_svgs

def get_svg_array_for_svgs(
    svgs: List[sg.SVGFigure],
    n_cols: int,
    layout: COLLAGE_LAYOUT,
    reading_order: READING_ORDER
) -> List[List[Optional[sg.SVGFigure]]]:
    """
    Creates a 2D array representing the collage layout with SVGFigures and spacers.
    """
    logger.debug(f"Creating SVG array: n_cols={n_cols}, layout={layout}, reading_order={reading_order}")
    n_cols = min(len(svgs), n_cols)

    layout_is_mosaic = layout in [
        COLLAGE_LAYOUT.MOSAIC_EQUAL_ALL,
        COLLAGE_LAYOUT.MOSAIC_EQUAL_WIDTH,
        COLLAGE_LAYOUT.MOSAIC_EQUAL_HEIGHT
    ]

    n_rows = (len(svgs) + n_cols - 1) // n_cols
    array_cols = n_cols

    if layout_is_mosaic:
        array_cols = 2 * n_cols + 1

    # 2D-Array with None as placeholder
    svg_array = [[None for _ in range(array_cols)] for _ in range(n_rows)]

    image_positions = []
    if layout_is_mosaic:
        for row in range(n_rows):
            row_offset = row % 2
            for col in range(n_cols):
                array_col = row_offset + 2 * col + 1
                if array_col < array_cols:
                    image_positions.append((row, array_col))
    else:
        for row in range(n_rows):
            for col in range(n_cols):
                image_positions.append((row, col))

    sort_key_map = {
        READING_ORDER.LEFT_RIGHT_TOP_BOTTOM: lambda pos: (pos[0], pos[1]),
        READING_ORDER.RIGHT_LEFT_TOP_BOTTOM: lambda pos: (pos[0], -pos[1]),
        READING_ORDER.LEFT_RIGHT_BOTTOM_TOP: lambda pos: (-pos[0], pos[1]),
        READING_ORDER.RIGHT_LEFT_BOTTOM_TOP: lambda pos: (-pos[0], -pos[1]),
        READING_ORDER.TOP_BOTTOM_LEFT_RIGHT: lambda pos: (pos[1], pos[0]),
        READING_ORDER.TOP_BOTTOM_RIGHT_LEFT: lambda pos: (-pos[1], pos[0]),
        READING_ORDER.BOTTOM_TOP_LEFT_RIGHT: lambda pos: (pos[1], -pos[0]),
        READING_ORDER.BOTTOM_TOP_RIGHT_LEFT: lambda pos: (-pos[1], -pos[0])
    }
    get_sort_key = sort_key_map.get(reading_order, lambda pos: (pos[0], pos[1]))
    sorted_positions = sorted(image_positions, key=get_sort_key)

    # Fill array with SVGs and None spacers if mosaic
    for i, (row, col) in enumerate(sorted_positions):
        if i < len(svgs):
            svg_array[row][col] = svgs[i]

    return svg_array

def generate_collage_figure(
    collage_array: List[List[Optional[sg.SVGFigure]]],
    reading_order: READING_ORDER,
    title: str,
    title_position: TITLE_POSITION,
    title_color: COLOR,
    font_size: int,
    dpi: int = 300
) -> sg.SVGFigure:
    logger.debug(f"Generating collage figure: title='{title}', position={title_position}, font_size={font_size}")

    n_rows = len(collage_array)
    n_cols = len(collage_array[0]) if n_rows > 0 else 0

    if n_rows == 0 or n_cols == 0:
        logger.warning("Empty collage array provided.")
        return sg.SVGFigure("1pt", "1pt")

    # Calculate max widths and heights for each row and col
    max_widths_per_col = []
    max_heights_per_row = []
    for col in range(n_cols):
        col_widths = []
        for row in range(n_rows):
            item = collage_array[row][col]
            if item is not None:
                width = float(item.width.rstrip("ptpx"))
                col_widths.append(width)
        max_widths_per_col.append(max(col_widths) if col_widths else 1.0)

    for row in range(n_rows):
        row_heights = []
        for col in range(n_cols):
            item = collage_array[row][col]
            if item is not None:
                height = float(item.height.rstrip("ptpx"))
                row_heights.append(height)
        max_heights_per_row.append(max(row_heights) if row_heights else 1.0)

    total_width = sum(max_widths_per_col)
    total_height = sum(max_heights_per_row)

    # Add space for title
    title_gap = 10
    title_height = font_size + 10 if title else 0
    if title_position in [TITLE_POSITION.TOP, TITLE_POSITION.BOTTOM]:
        total_height += title_height
    elif title_position in [TITLE_POSITION.RIGHT, TITLE_POSITION.LEFT]:
        total_width += title_height

    # Create SVG figure
    fig = sg.SVGFigure(f"{total_width}pt", f"{total_height}pt")
    fig.set_size((f"{total_width}pt", f"{total_height}pt"))

    elements = []

    # Place individual SVGs
    y_offset = title_height if title_position == TITLE_POSITION.TOP else 0
    for row in range(n_rows):
        x_offset = title_height if title_position == TITLE_POSITION.LEFT else 0
        for col in range(n_cols):
            item = collage_array[row][col]
            if item is not None:
                plot = item.getroot()
                plot.moveto(x_offset, y_offset)
                elements.append(plot)
            x_offset += max_widths_per_col[col]
        y_offset += max_heights_per_row[row]

    # Add title
    if title:
        title_color_tuple = get_color_tuple(title_color, use_alpha=True)
        title_color_rgb = f"rgb({title_color_tuple[0]},{title_color_tuple[1]},{title_color_tuple[2]})"
        title_opacity = title_color_tuple[3] / 255.0 if len(title_color_tuple) > 3 else 1.0

        if title_position == TITLE_POSITION.TOP:
            title_x = total_width / 2
            title_y = title_height - (title_gap / 2)
            elements.append(
                sg.TextElement(title_x, title_y, title, size=font_size, color=title_color_rgb,
                              anchor="middle", weight="normal")
            )
        elif title_position == TITLE_POSITION.BOTTOM:
            title_x = total_width / 2
            title_y = total_height - (title_gap / 2)
            elements.append(
                sg.TextElement(title_x, title_y, title, size=font_size, color=title_color_rgb,
                              anchor="middle", weight="normal")
            )
        elif title_position == TITLE_POSITION.LEFT:
            title_x = title_gap / 2
            title_y = total_height / 2
            title_elem = sg.TextElement(title_x, title_y, title, size=font_size, color=title_color_rgb,
                                       anchor="start", weight="normal")
            title_elem.rotate(90, title_x, title_y)
            elements.append(title_elem)
        elif title_position == TITLE_POSITION.RIGHT:
            title_x = total_width - (title_gap / 2)
            title_y = total_height / 2
            title_elem = sg.TextElement(title_x, title_y, title, size=font_size, color=title_color_rgb,
                                       anchor="end", weight="normal")
            title_elem.rotate(-90, title_x, title_y)
            elements.append(title_elem)
        elif title_position == TITLE_POSITION.CENTER:
            title_x = total_width / 2
            title_y = total_height / 2
            elements.append(
                sg.TextElement(title_x, title_y, title, size=font_size, color=title_color_rgb,
                              anchor="middle", weight="normal")
            )

    fig.append(elements)
    return fig

def create_collage(
    images: List[Union[Image.Image, plt.Figure]],
    layout: COLLAGE_LAYOUT = COLLAGE_LAYOUT.GRID_EQUAL_ALL,
    reading_order: READING_ORDER = READING_ORDER.LEFT_RIGHT_TOP_BOTTOM,
    columns: int = 5,
    scale_option: SCALE_OPTION = SCALE_OPTION.DOWNSCALE_TO_WIDTH,
    padding_horizontal: int = 0,
    padding_vertical: int = 0,
    margin_horizontal: int = 0,
    margin_vertical: int = 0,
    title: str = "",
    title_position: TITLE_POSITION = TITLE_POSITION.TOP,
    title_color: COLOR = COLOR.BLACK,
    font_size: int = 12,
    dpi: int = 300
) -> sg.SVGFigure:
    """
    Create a collage from a list of images, using SVG from the start.
    """
    logger.debug("Creating collage")
    if not images:
        logger.warning("Empty image list provided for collage creation.")
        fig = sg.SVGFigure("1pt", "1pt")
        return fig

    # Format all inputs to SVGFigure
    svg_figures = [format_image_to_svg(img, dpi=dpi) for img in images]

    # Scale the figures
    scaled_svgs = scale_svgs(svg_figures, scale_option)

    # Add user-defined padding
    padded_svgs = add_padding_to_svgs(
        scaled_svgs,
        horizontal_padding=padding_horizontal,
        vertical_padding=padding_vertical
    )

    # Adjust sizes based on layout
    gridded_svgs = get_gridded_svgs(
        padded_svgs,
        layout
    )

    # Create collage array
    collage_array = get_svg_array_for_svgs(
        gridded_svgs,
        n_cols=columns,
        layout=layout,
        reading_order=reading_order
    )

    # Generate the collage
    collage = generate_collage_figure(
        collage_array=collage_array,
        reading_order=reading_order,
        title=title,
        title_position=title_position,
        title_color=title_color,
        font_size=font_size,
        dpi=dpi
    )
    collage_with_margins = add_padding_to_svgs([collage],horizontal_padding=margin_horizontal,vertical_padding=margin_vertical)[0]
        
    return collage_with_margins

# Collage Class (unverändert, aber generate_collage verwendet create_collage)
class Collage:
    def __init__(
        self,
        layouts: Optional[List[COLLAGE_LAYOUT]] = None,
        columns: Optional[int] = None,
        max_columns: Optional[int] = None,
        scaling: Optional[List[SCALE_OPTION]] = None,
        padding_horizontal: Optional[int] = None,
        max_padding_horizontal: Optional[int] = None,
        padding_vertical: Optional[int] = None,
        max_padding_vertical: Optional[int] = None,
        margin_vertical: Optional[int] = None,
        max_margin_vertical: Optional[int] = None,
        margin_horizontal: Optional[int] = None,
        max_margin_horizontal: Optional[int] = None,
        title: Optional[str] = "",
        title_positions: Optional[List[TITLE_POSITION]] = None,
        title_colors: Optional[List[COLOR]] = None,
        font_size: Optional[int] = None,
        max_font_size: Optional[int] = None,
        reading_orders: Optional[List[READING_ORDER]] = None,
        show_all_options: bool = False
    ) -> None:
        logger.debug("Initializing CollageSettings")

        self._layouts_enabled = layouts is not None
        enabled_layouts = layouts if self._layouts_enabled else list(COLLAGE_LAYOUT)

        self._columns_enabled = columns is not None
        columns = columns if self._columns_enabled else 1
        max_columns = max_columns if max_columns is not None else 10

        self._scaling_enabled = scaling is not None
        enabled_scaling = scaling if self._scaling_enabled else list(SCALE_OPTION)

        self._padding_horizontal_enabled = padding_horizontal is not None
        padding_horizontal = padding_horizontal if self._padding_horizontal_enabled else 0
        max_padding_horizontal = max_padding_horizontal if max_padding_horizontal is not None else 100

        self._padding_vertical_enabled = padding_vertical is not None
        padding_vertical = padding_vertical if self._padding_vertical_enabled else 0
        max_padding_vertical = max_padding_vertical if max_padding_vertical is not None else 100

        self._margin_vertical_enabled = margin_vertical is not None
        margin_vertical = margin_vertical if self._margin_vertical_enabled else 0
        max_margin_vertical = max_margin_vertical if max_margin_vertical is not None else 100

        self._margin_horizontal_enabled = margin_horizontal is not None
        margin_horizontal = margin_horizontal if self._margin_horizontal_enabled else 0
        max_margin_horizontal = max_margin_horizontal if max_margin_horizontal is not None else 100

        self._title_enabled = title != ""
        title = title if self._title_enabled else ""

        self._title_positions_enabled = title_positions is not None
        enabled_title_positions = title_positions if self._title_positions_enabled else list(TITLE_POSITION)

        self._title_colors_enabled = title_colors is not None
        enabled_title_colors = title_colors if self._title_colors_enabled else list(COLOR)

        self._font_size_enabled = font_size is not None
        font_size = font_size if self._font_size_enabled else 12
        max_font_size = max_font_size if max_font_size is not None else 50

        self._reading_orders_enabled = reading_orders is not None
        enabled_reading_orders = reading_orders if self._reading_orders_enabled else list(READING_ORDER)

        self._show_all_options = show_all_options

        self.create_widgets(
            layouts=enabled_layouts,
            columns=columns,
            max_columns=max_columns,
            scaling=enabled_scaling,
            padding_horizontal=padding_horizontal,
            max_padding_horizontal=max_padding_horizontal,
            padding_vertical=padding_vertical,
            max_padding_vertical=max_padding_vertical,
            margin_vertical=margin_vertical,
            max_margin_vertical=max_margin_vertical,
            margin_horizontal=margin_horizontal,
            max_margin_horizontal=max_margin_horizontal,
            title=title,
            title_positions=enabled_title_positions,
            title_colors=enabled_title_colors,
            font_size=font_size,
            max_font_size=max_font_size,
            reading_orders=enabled_reading_orders
        )

    def create_widgets(
        self,
        layouts: List[COLLAGE_LAYOUT],
        columns: int,
        max_columns: int,
        scaling: List[SCALE_OPTION],
        padding_horizontal: int,
        max_padding_horizontal: int,
        padding_vertical: int,
        max_padding_vertical: int,
        margin_vertical: int,
        max_margin_vertical: int,
        margin_horizontal: int,
        max_margin_horizontal: int,
        title: str,
        title_positions: List[TITLE_POSITION],
        title_colors: List[COLOR],
        font_size: int,
        max_font_size: int,
        reading_orders: List[READING_ORDER]
    ) -> None:
        layout_options = [layout.value for layout in layouts]
        self._layout_dropdown = WidgetFactory.dropdown(
            options=layout_options,
            value=layout_options[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._n_columns_input = WidgetFactory.int_number_input(
            value=columns,
            min_value=1,
            max_value=max_columns,
            description="",
            layout=widgets.Layout(height="30px", width="100%", margin="0px", padding="0px")
        )

        scale_options = [scale.value for scale in scaling]
        self._scale_dropdown = WidgetFactory.dropdown(
            options=scale_options,
            value=scale_options[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._padding_horizontal_input = WidgetFactory.int_number_input(
            value=padding_horizontal,
            min_value=0,
            max_value=max_padding_horizontal,
            description="",
            layout=widgets.Layout(height="30px", width="100%", margin="0px", padding="0px")
        )

        self._padding_vertical_input = WidgetFactory.int_number_input(
            value=padding_vertical,
            min_value=0,
            max_value=max_padding_vertical,
            description="",
            layout=widgets.Layout(height="30px", width="100%", margin="0px", padding="0px")
        )

        self._margin_vertical_input = WidgetFactory.int_number_input(
            value=margin_vertical,
            min_value=0,
            max_value=max_margin_vertical,
            description="",
            layout=widgets.Layout(height="30px", width="100%", margin="0px", padding="0px")
        )

        self._margin_horizontal_input = WidgetFactory.int_number_input(
            value=margin_horizontal,
            min_value=0,
            max_value=max_margin_horizontal,
            description="",
            layout=widgets.Layout(height="30px", width="100%", margin="0px", padding="0px")
        )

        self._title_input = WidgetFactory.text_input(
            value=title,
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        title_position_options = [title_position.value for title_position in title_positions]
        self._title_position_dropdown = WidgetFactory.dropdown(
            options=title_position_options,
            value=title_position_options[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        title_color_options = [title_color.value for title_color in title_colors]
        self._title_color_dropdown = WidgetFactory.dropdown(
            options=title_color_options,
            value=title_color_options[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

        self._font_size_input = WidgetFactory.int_number_input(
            value=font_size,
            min_value=0,
            max_value=max_font_size,
            description="",
            layout=widgets.Layout(height="30px", width="100%", margin="0px", padding="0px")
        )

        reading_order_options = [reading_order.value for reading_order in reading_orders]
        self._reading_order_dropdown = WidgetFactory.dropdown(
            options=reading_order_options,
            value=reading_order_options[0],
            description="",
            layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px")
        )

    @property
    def layout(self) -> COLLAGE_LAYOUT:
        return COLLAGE_LAYOUT(self._layout_dropdown.value)

    @property
    def columns(self) -> int:
        return self._n_columns_input.value

    @property
    def scale_option(self) -> SCALE_OPTION:
        return SCALE_OPTION(self._scale_dropdown.value)

    @property
    def padding_horizontal(self) -> int:
        return self._padding_horizontal_input.value

    @property
    def padding_vertical(self) -> int:
        return self._padding_vertical_input.value

    @property
    def horizontal_margin(self) -> int:
        return self._margin_horizontal_input.value

    @property
    def vertical_margin(self) -> int:
        return self._margin_vertical_input.value

    @property
    def title(self) -> str:
        return self._title_input.value

    @property
    def title_position(self) -> TITLE_POSITION:
        return TITLE_POSITION(self._title_position_dropdown.value)

    @property
    def title_color(self) -> COLOR:
        return COLOR(self._title_color_dropdown.value)

    @property
    def font_size(self) -> int:
        return self._font_size_input.value

    @property
    def reading_order(self) -> READING_ORDER:
        return READING_ORDER(self._reading_order_dropdown.value)

    def get_active_widgets(self) -> List[widgets.Widget]:
        active_widgets = []
        if self._layouts_enabled:
            active_widgets.append(self._layout_dropdown)
        if self._columns_enabled:
            active_widgets.append(self._n_columns_input)
        if self._scaling_enabled:
            active_widgets.append(self._scale_dropdown)
        if self._padding_horizontal_enabled:
            active_widgets.append(self._padding_horizontal_input)
        if self._padding_vertical_enabled:
            active_widgets.append(self._padding_vertical_input)
        if self._margin_vertical_enabled:
            active_widgets.append(self._margin_vertical_input)
        if self._margin_horizontal_enabled:
            active_widgets.append(self._margin_horizontal_input)
        if self._title_enabled:
            active_widgets.append(self._title_input)
        if self._title_positions_enabled:
            active_widgets.append(self._title_position_dropdown)
        if self._title_colors_enabled:
            active_widgets.append(self._title_color_dropdown)
        if self._font_size_enabled:
            active_widgets.append(self._font_size_input)
        if self._reading_orders_enabled:
            active_widgets.append(self._reading_order_dropdown)
        return active_widgets

    def get_layout_dropdown(self):
        """Returns the layout dropdown widget."""
        return self._layout_dropdown

    def get_columns_input(self):
        """Returns the columns number input widget."""
        return self._n_columns_input
    
    def get_scale_dropdown(self):
        """Returns the scale dropdown widget."""
        return self._scale_dropdown
    
    def get_padding_horizontal_input(self):
        """Returns the horizontal padding number input widget."""
        return self._padding_horizontal_input
    
    def get_padding_vertical_input(self):
        """Returns the vertical padding number input widget."""
        return self._padding_vertical_input
    
    def get_margin_vertical_input(self):
        """Returns the vertical margin number input widget."""
        return self._margin_vertical_input
    
    def get_margin_horizontal_input(self):
        """Returns the horizontal margin number input widget."""
        return self._margin_horizontal_input
    
    
    def get_title_input(self):
        """Returns the title text input widget."""
        return self._title_input
    
    def get_title_position_dropdown(self):
        """Returns the title position dropdown widget."""
        return self._title_position_dropdown
    
    def get_title_color_dropdown(self):
        """Returns the title color dropdown widget."""
        return self._title_color_dropdown
    
    def get_font_size_input(self):
        """Returns the font size number input widget."""
        return self._font_size_input
    
    def get_reading_order_dropdown(self):
        """Returns the reading order dropdown widget."""
        return self._reading_order_dropdown

    def get_ui(self) -> widgets.Widget:
        title_widget = WidgetFactory.html_widget(value="<h3>Collage Options</h3>")
    
        collage_widgets = [title_widget]
    
        layout_children = []
        if self._layouts_enabled or self._show_all_options:
            layout_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Layout:"),
                    WidgetFactory.vbox(
                        children=[self._layout_dropdown],
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
            layout_children.append(layout_container)
        if self._columns_enabled or self._show_all_options:
            columns_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Number of Columns:"),
                    WidgetFactory.vbox(
                        children=[self._n_columns_input],
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
            layout_children.append(columns_container)
        if layout_children:
            layout_vbox = WidgetFactory.vbox(
                children=layout_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            collage_widgets.append(layout_vbox)
    
        if self._scaling_enabled or self._show_all_options:
            scaling_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Scaling:"),
                    WidgetFactory.vbox(
                        children=[self._scale_dropdown],
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
            collage_widgets.append(scaling_container)
    
        padding_children = []
        if self._padding_horizontal_enabled or self._show_all_options:
            inner_h_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Inner Horizontal Padding:"),
                    WidgetFactory.vbox(
                        children=[self._padding_horizontal_input],
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
            padding_children.append(inner_h_container)
        if self._padding_vertical_enabled or self._show_all_options:
            inner_v_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Inner Vertical Padding:"),
                    WidgetFactory.vbox(
                        children=[self._padding_vertical_input],
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
            padding_children.append(inner_v_container)
        if padding_children:
            padding_vbox = WidgetFactory.vbox(
                children=padding_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            collage_widgets.append(padding_vbox)
    
        margins_children = []
        if self._margin_horizontal_enabled or self._show_all_options:
            margin_h_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Horizontal Margin:"),
                    WidgetFactory.vbox(
                        children=[self._margin_horizontal_input],
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
            margins_children.append(margin_h_container)
        if self._margin_vertical_enabled or self._show_all_options:
            margin_v_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Vertical Margin:"),
                    WidgetFactory.vbox(
                        children=[self._margin_vertical_input],
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
            margins_children.append(margin_v_container)
        if margins_children:
            margins_vbox = WidgetFactory.vbox(
                children=margins_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            collage_widgets.append(margins_vbox)
    
        title_children = []
        if self._title_enabled or self._show_all_options:
            title_input_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Title:"),
                    WidgetFactory.vbox(
                        children=[self._title_input],
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
            title_children.append(title_input_container)
        if self._title_positions_enabled or self._show_all_options:
            title_pos_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Title Position:"),
                    WidgetFactory.vbox(
                        children=[self._title_position_dropdown],
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
            title_children.append(title_pos_container)
        if self._title_colors_enabled or self._show_all_options:
            title_color_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Title Color:"),
                    WidgetFactory.vbox(
                        children=[self._title_color_dropdown],
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
            title_children.append(title_color_container)
        if self._font_size_enabled or self._show_all_options:
            font_size_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Font Size:"),
                    WidgetFactory.vbox(
                        children=[self._font_size_input],
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
            title_children.append(font_size_container)
        if title_children:
            title_vbox = WidgetFactory.vbox(
                children=title_children,
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY)
            )
            collage_widgets.append(title_vbox)
    
        if self._reading_orders_enabled or self._show_all_options:
            reading_order_container = WidgetFactory.vbox(
                children=[
                    WidgetFactory.label(value="Reading Order:"),
                    WidgetFactory.vbox(
                        children=[self._reading_order_dropdown],
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
            collage_widgets.append(reading_order_container)
    
        return WidgetFactory.vbox(
            children=collage_widgets,
            gap="5px",
            overflow="visible",
            height="auto"
        )
        

    def generate_collage(
        self,
        images: List[Union[Image.Image, plt.Figure]],
        layout: Optional[COLLAGE_LAYOUT] = None,
        columns: Optional[int] = None,
        scale_option: Optional[SCALE_OPTION] = None,
        padding_horizontal: Optional[int] = None,
        padding_vertical: Optional[int] = None,
        horizontal_margin: Optional[int] = None,
        vertical_margin: Optional[int] = None,
        title: Optional[str] = None,
        title_position: Optional[TITLE_POSITION] = None,
        title_color: Optional[COLOR] = None,
        font_size: Optional[int] = None,
        reading_order: Optional[READING_ORDER] = None,
        dpi = 300
    ) -> sg.SVGFigure:
        logger.debug("Generating collage")
        try:
            layout = layout or self.layout
            columns = columns or self.columns
            scale_option = scale_option or self.scale_option
            padding_horizontal = padding_horizontal if padding_horizontal is not None else self.padding_horizontal
            padding_vertical = padding_vertical if padding_vertical is not None else self.padding_vertical
            horizontal_margin = horizontal_margin if horizontal_margin is not None else self.horizontal_margin
            vertical_margin = vertical_margin if vertical_margin is not None else self.vertical_margin
            title = title or self.title
            title_position = title_position or self.title_position
            title_color = title_color or self.title_color
            font_size = font_size or self.font_size
            reading_order = reading_order or self.reading_order
            
            return create_collage(
                images=images,
                layout=layout,
                columns=columns,
                scale_option=scale_option,
                padding_horizontal=padding_horizontal,
                padding_vertical=padding_vertical,
                margin_horizontal=horizontal_margin,
                margin_vertical=vertical_margin,
                title=title,
                title_position=title_position,
                title_color=title_color,
                font_size=font_size,
                reading_order=reading_order,
                dpi = dpi
            )
        except Exception as e:
            logger.error(f"Failed to generate collage: {e}")
            raise