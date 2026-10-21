import logging
from collections.abc import Callable
from typing import Any

import ipywidgets as widgets

logger = logging.getLogger(__name__)


class WidgetFactory:
    """
    Factory class for creating styled IPython widgets with consistent styling and behavior.
    """

    @staticmethod
    def get_layout(
        layout: widgets.Layout | None = None,
        width: str = "auto",
        height: str = "auto",
        align_items: str | None = None,
        justify_content: str | None = None,
        overflow: str | None = None,
        overflow_y: str | None = None,
        overflow_x: str | None = None,
        **kwargs,
    ) -> widgets.Layout:
        if layout is None:
            layout = widgets.Layout()

        if not getattr(layout, "width", None):
            layout.width = width
        if not getattr(layout, "height", None):
            layout.height = height

        if align_items is not None and not getattr(layout, "align_items", None):
            layout.align_items = align_items
        if justify_content is not None and not getattr(layout, "justify_content", None):
            layout.justify_content = justify_content
        if overflow is not None and not getattr(layout, "overflow", None):
            layout.overflow = overflow
        if overflow_y is not None and not getattr(layout, "overflow_y", None):
            layout.overflow_y = overflow_y
        if overflow_x is not None and not getattr(layout, "overflow_x", None):
            layout.overflow_x = overflow_x

        for key, value in kwargs.items():
            if value is not None and not getattr(layout, key, None):
                setattr(layout, key, value)

        return layout

    # ===================== BUTTON METHODS =====================

    @staticmethod
    def button_default(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_click: Callable | None = None,
        **kwargs,
    ) -> widgets.Button:
        layout = WidgetFactory.get_layout(layout, width, height)
        button = widgets.Button(
            description=description,
            disabled=disabled,
            icon=icon,
            tooltip=tooltip,
            layout=layout,
            **kwargs,
        )
        button.add_class("styled-widget")
        button.add_class("styled-button")
        button.add_class("button-default")
        if on_click:
            button.on_click(on_click)
        return button

    @staticmethod
    def button_emphasis(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_click: Callable | None = None,
        **kwargs,
    ) -> widgets.Button:
        layout = WidgetFactory.get_layout(layout, width, height)
        button = widgets.Button(
            description=description,
            disabled=disabled,
            icon=icon,
            tooltip=tooltip,
            layout=layout,
            **kwargs,
        )
        button.add_class("styled-widget")
        button.add_class("styled-button")
        button.add_class("button-emphasis")
        if on_click:
            button.on_click(on_click)
        return button

    @staticmethod
    def button_success(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_click: Callable | None = None,
        **kwargs,
    ) -> widgets.Button:
        layout = WidgetFactory.get_layout(layout, width, height)
        button = widgets.Button(
            description=description,
            disabled=disabled,
            icon=icon,
            tooltip=tooltip,
            layout=layout,
            **kwargs,
        )
        button.add_class("styled-widget")
        button.add_class("styled-button")
        button.add_class("button-success")
        if on_click:
            button.on_click(on_click)
        return button

    @staticmethod
    def button_danger(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_click: Callable | None = None,
        **kwargs,
    ) -> widgets.Button:
        layout = WidgetFactory.get_layout(layout, width, height)
        button = widgets.Button(
            description=description,
            disabled=disabled,
            icon=icon,
            tooltip=tooltip,
            layout=layout,
            **kwargs,
        )
        button.add_class("styled-widget")
        button.add_class("styled-button")
        button.add_class("button-danger")
        if on_click:
            button.on_click(on_click)
        return button

    @staticmethod
    def button_warning(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_click: Callable | None = None,
        **kwargs,
    ) -> widgets.Button:
        layout = WidgetFactory.get_layout(layout, width, height)
        button = widgets.Button(
            description=description,
            disabled=disabled,
            icon=icon,
            tooltip=tooltip,
            layout=layout,
            **kwargs,
        )
        button.add_class("styled-widget")
        button.add_class("styled-button")
        button.add_class("button-warning")
        if on_click:
            button.on_click(on_click)
        return button

    @staticmethod
    def toggle_button(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        toggled: bool = False,
        layout: widgets.Layout | None = None,
        on_click: Callable | None = None,
        **kwargs,
    ) -> widgets.Button:
        layout = WidgetFactory.get_layout(layout, width, height)
        button = widgets.Button(
            description=description,
            disabled=disabled,
            icon=icon,
            tooltip=tooltip,
            layout=layout,
            **kwargs,
        )
        button.add_class("styled-widget")
        button.add_class("styled-button")

        if toggled:
            button.add_class("button-emphasis")
        else:
            button.add_class("button-default")

        button._toggled = toggled

        def update_appearance():
            if button._toggled:
                button.remove_class("button-default")
                button.add_class("button-emphasis")
            else:
                button.remove_class("button-emphasis")
                button.add_class("button-default")

        def toggle_handler(b):
            b._toggled = not b._toggled
            update_appearance()

        if on_click:
            button.on_click(on_click)
        button.on_click(toggle_handler)
        return button

    @staticmethod
    def custom_radio_buttons(
        number: int = 2,
        description: list[str] | None = None,
        i_toggled: int = 0,
        width: str = "auto",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> list[widgets.Button]:
        if number < 1:
            return []
        if description is None:
            description = []
        if len(description) < number:
            description += [""] * (number - len(description))

        layout = WidgetFactory.get_layout(layout, width, height)
        buttons = []
        for i in range(number):
            button = widgets.Button(description=description[i], layout=layout, **kwargs)
            button.add_class("styled-widget")
            button.add_class("styled-button")
            if i == i_toggled:
                button.add_class("button-emphasis")
            else:
                button.add_class("button-default")
            buttons.append(button)

        def toggle_handler(b):
            for btn in buttons:
                btn.remove_class("button-emphasis")
                btn.add_class("button-default")
            b.remove_class("button-default")
            b.add_class("button-emphasis")

        for button in buttons:
            button.on_click(toggle_handler)
        return buttons

    # ===================== INPUT FIELDS =====================

    @staticmethod
    def text_input(
        value: str = "",
        placeholder: str = "",
        description: str = "",
        disabled: bool = False,
        width: str = "300px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.Text:
        layout = WidgetFactory.get_layout(layout, width, height)
        text = widgets.Text(
            value=value,
            placeholder=placeholder,
            description=description,
            disabled=disabled,
            layout=layout,
            **kwargs,
        )
        text.add_class("styled-widget")
        text.add_class("styled-input")
        if on_change:
            text.observe(on_change, names="value")
        return text

    @staticmethod
    def password_input(
        value: str = "",
        placeholder: str = "",
        description: str = "",
        disabled: bool = False,
        width: str = "300px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.Password:
        layout = WidgetFactory.get_layout(layout, width, height)
        password = widgets.Password(
            value=value,
            placeholder=placeholder,
            description=description,
            disabled=disabled,
            layout=layout,
            **kwargs,
        )
        password.add_class("styled-widget")
        password.add_class("styled-input")
        if on_change:
            password.observe(on_change, names="value")
        return password

    @staticmethod
    def textarea_input(
        value: str = "",
        placeholder: str = "",
        description: str = "",
        disabled: bool = False,
        width: str = "400px",
        height: str = "120px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.Textarea:
        layout = WidgetFactory.get_layout(layout, width, height)
        textarea = widgets.Textarea(
            value=value,
            placeholder=placeholder,
            description=description,
            disabled=disabled,
            layout=layout,
            **kwargs,
        )
        textarea.add_class("styled-widget")
        textarea.add_class("styled-textarea")
        if on_change:
            textarea.observe(on_change, names="value")
        return textarea

    @staticmethod
    def number_input(
        value: int | float = 0,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        step: int | float = 1,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.BoundedIntText | widgets.BoundedFloatText:
        layout = WidgetFactory.get_layout(layout, width, height)
        if isinstance(value, int) and isinstance(step, int):
            widget = widgets.BoundedIntText(
                value=value,
                min=min_value or 0,
                max=max_value or 100,
                step=step,
                description=description,
                disabled=disabled,
                layout=layout,
                **kwargs,
            )
        else:
            widget = widgets.BoundedFloatText(
                value=float(value),
                min=min_value or 0.0,
                max=max_value or 100.0,
                step=float(step),
                description=description,
                disabled=disabled,
                layout=layout,
                **kwargs,
            )
        widget.add_class("styled-widget")
        widget.add_class("styled-input")
        if on_change:
            widget.observe(on_change, names="value")
        return widget

    @staticmethod
    def int_number_input(
        value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.BoundedIntText:
        layout = WidgetFactory.get_layout(layout, width, height)
        widget = widgets.BoundedIntText(
            value=value,
            min=min_value or 0,
            max=max_value or 100,
            step=step,
            description=description,
            disabled=disabled,
            layout=layout,
            **kwargs,
        )
        widget.add_class("styled-widget")
        widget.add_class("styled-input")
        if on_change:
            widget.observe(on_change, names="value")
        return widget

    @staticmethod
    def float_number_input(
        value: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 0.1,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.BoundedFloatText:
        layout = WidgetFactory.get_layout(layout, width, height)
        widget = widgets.BoundedFloatText(
            value=value,
            min=min_value or 0.0,
            max=max_value or 100.0,
            step=step,
            description=description,
            disabled=disabled,
            layout=layout,
            **kwargs,
        )
        widget.add_class("styled-widget")
        widget.add_class("styled-input")
        if on_change:
            widget.observe(on_change, names="value")
        return widget

    # ===================== DROPDOWN, CHECKBOX, RADIO =====================

    @staticmethod
    def dropdown(
        options: list[str | tuple] | None = None,
        value: Any | None = None,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.Dropdown:
        if options is None:
            options = []
        layout = WidgetFactory.get_layout(layout, width, height)
        dropdown_widget = widgets.Dropdown(
            options=options,
            value=value,
            description=description,
            disabled=disabled,
            layout=layout,
            **kwargs,
        )
        dropdown_widget.add_class("styled-widget")
        dropdown_widget.add_class("styled-dropdown")
        if on_change:
            dropdown_widget.observe(on_change, names="value")
        return dropdown_widget

    @staticmethod
    def checkbox(
        value: bool = False,
        description: str = "",
        disabled: bool = False,
        indent: bool = True,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.Checkbox:
        checkbox_widget = widgets.Checkbox(
            value=value, description=description, disabled=disabled, indent=indent, **kwargs
        )
        checkbox_widget.add_class("styled-widget")
        checkbox_widget.add_class("styled-checkbox")
        if on_change:
            checkbox_widget.observe(on_change, names="value")
        return checkbox_widget

    @staticmethod
    def radio_buttons(
        options: list[str],
        i_selected: int,
        on_change: Callable | None = None,
        **kwargs,
    ) -> list[widgets.Checkbox]:
        checkboxes = []
        for i, option in enumerate(options):
            cb = WidgetFactory.checkbox(value=(i == i_selected), description=option, **kwargs)
            checkboxes.append(cb)

        ignore_event = [False]

        def on_checkbox_change(change):
            if ignore_event[0]:
                return
            ignore_event[0] = True
            for cb in checkboxes:
                cb.value = False
            change["owner"].value = True
            ignore_event[0] = False

        for cb in checkboxes:
            cb.observe(on_checkbox_change, names="value")
            if on_change:
                cb.observe(on_change, names="value")
        return checkboxes

    # ===================== SLIDERS =====================

    @staticmethod
    def int_slider(
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        step: int = 1,
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        width: str = "300px",
        height: str = "auto",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.IntSlider:
        layout = WidgetFactory.get_layout(layout, width, height)
        slider = widgets.IntSlider(
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            description=description,
            disabled=disabled,
            orientation=orientation,
            layout=layout,
            **kwargs,
        )
        slider.add_class("styled-widget")
        slider.add_class("styled-slider")
        if on_change:
            slider.observe(on_change, names="value")
        return slider

    @staticmethod
    def float_slider(
        value: float = 0.0,
        min_value: float = 0.0,
        max_value: float = 100.0,
        step: float = 0.1,
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        width: str = "300px",
        height: str = "auto",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.FloatSlider:
        layout = WidgetFactory.get_layout(layout, width, height)
        slider = widgets.FloatSlider(
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            description=description,
            disabled=disabled,
            orientation=orientation,
            layout=layout,
            **kwargs,
        )
        slider.add_class("styled-widget")
        slider.add_class("styled-slider")
        if on_change:
            slider.observe(on_change, names="value")
        return slider

    @staticmethod
    def int_range_slider(
        value: list[int] | tuple[int, int] = [0, 100],
        min_value: int = 0,
        max_value: int = 100,
        step: int = 1,
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        width: str = "300px",
        height: str = "auto",
        continuous_update: bool = False,
        readout: bool = True,
        readout_format: str = "auto",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.IntRangeSlider:
        if isinstance(value, tuple):
            value = list(value)
        if readout_format == "auto":
            readout_format = "d"
        layout = WidgetFactory.get_layout(layout, width, height)
        slider = widgets.IntRangeSlider(
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            description=description,
            disabled=disabled,
            orientation=orientation,
            continuous_update=continuous_update,
            readout=readout,
            readout_format=readout_format,
            layout=layout,
            **kwargs,
        )
        slider.add_class("styled-widget")
        slider.add_class("styled-slider")
        if on_change:
            slider.observe(on_change, names="value")
        return slider

    @staticmethod
    def float_range_slider(
        value: list[float] | tuple[float, float] = [0.0, 100.0],
        min_value: float = 0.0,
        max_value: float = 100.0,
        step: float = 0.1,
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        width: str = "300px",
        height: str = "auto",
        continuous_update: bool = False,
        readout: bool = True,
        readout_format: str = "auto",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.FloatRangeSlider:
        if isinstance(value, tuple):
            value = list(value)
        if readout_format == "auto":
            readout_format = ".1f"
        layout = WidgetFactory.get_layout(layout, width, height)
        slider = widgets.FloatRangeSlider(
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            description=description,
            disabled=disabled,
            orientation=orientation,
            continuous_update=continuous_update,
            readout=readout,
            readout_format=readout_format,
            layout=layout,
            **kwargs,
        )
        slider.add_class("styled-widget")
        slider.add_class("styled-slider")
        if on_change:
            slider.observe(on_change, names="value")
        return slider

    # ===================== DATE PICKER & PROGRESS =====================

    @staticmethod
    def date_picker(
        value: Any | None = None,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        layout: widgets.Layout | None = None,
        on_change: Callable | None = None,
        **kwargs,
    ) -> widgets.DatePicker:
        layout = WidgetFactory.get_layout(layout, width, height)
        dp = widgets.DatePicker(
            value=value, description=description, disabled=disabled, layout=layout, **kwargs
        )
        dp.add_class("styled-widget")
        dp.add_class("styled-date-picker")
        if on_change:
            dp.observe(on_change, names="value")
        return dp

    @staticmethod
    def progress_bar(
        value: int | float = 0,
        min_value: int | float = 0,
        max_value: int | float = 100,
        description: str = "",
        width: str = "300px",
        height: str = "20px",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.IntProgress | widgets.FloatProgress:
        layout = WidgetFactory.get_layout(layout, width, height)
        if isinstance(value, int):
            progress = widgets.IntProgress(
                value=value,
                min=min_value,
                max=max_value,
                description=description,
                layout=layout,
                **kwargs,
            )
        else:
            progress = widgets.FloatProgress(
                value=float(value),
                min=float(min_value),
                max=float(max_value),
                description=description,
                layout=layout,
                **kwargs,
            )
        progress.add_class("styled-widget")
        progress.add_class("styled-progress")
        return progress

    # ===================== TAB, ACCORDION, OUTPUT =====================

    @staticmethod
    def tab(layout: widgets.Layout | None = None, **kwargs) -> widgets.Tab:
        layout = WidgetFactory.get_layout(layout, width="100%", height="auto")
        tab_widget = widgets.Tab(layout=layout, **kwargs)
        tab_widget.add_class("styled-widget")
        tab_widget.add_class("styled-tab")
        return tab_widget

    @staticmethod
    def accordion(
        children: list[widgets.Widget] | None = None,
        titles: list[str] | None = None,
        width: str = "100%",
        height: str = "auto",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.Accordion:
        if children is None:
            children = []
        if titles is None:
            titles = []
        layout = WidgetFactory.get_layout(layout, width, height)
        accordion_widget = widgets.Accordion(children=children, layout=layout, **kwargs)
        for i, title in enumerate(titles):
            if i < len(children):
                accordion_widget.set_title(i, title)
        accordion_widget.add_class("styled-widget")
        accordion_widget.add_class("styled-accordion")
        return accordion_widget

    @staticmethod
    def output_widget(
        width: str = "100%",
        height: str = "200px",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.Output:
        layout = WidgetFactory.get_layout(layout, width, height)
        output = widgets.Output(layout=layout, **kwargs)
        output.add_class("styled-widget")
        output.add_class("styled-output")
        return output

    # ===================== HTML / LABEL =====================

    @staticmethod
    def label(value: str = "", emphasis: bool = False, **kwargs) -> widgets.HTML:
        label_widget = widgets.HTML(value=value, **kwargs)
        label_widget.add_class("styled-widget")
        label_widget.add_class("styled-label")
        if emphasis:
            label_widget.add_class("label-emphasis")
        return label_widget

    @staticmethod
    def html_widget(
        value: str = "",
        width: str = "100%",
        height: str = "auto",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.HTML:
        layout = WidgetFactory.get_layout(layout, width, height)
        html = widgets.HTML(value=value, layout=layout, **kwargs)
        html.add_class("styled-widget")
        html.add_class("styled-html")
        return html

    # ===================== CONTAINERS (FIXED) =====================

    @staticmethod
    def hbox(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "center",
        justify_content: str = "flex-start",
        overflow: str = "auto",
        overflow_y: str = "auto",
        overflow_x: str = "auto",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.HBox:
        if children is None:
            children = []

        layout = WidgetFactory.get_layout(
            layout=layout,
            width=width,
            height=height,
            align_items=align_items,
            justify_content=justify_content,
            overflow=overflow,
            overflow_y=overflow_y,
            overflow_x=overflow_x,
        )

        if gap and len(children) > 1:
            gapped_children = []
            for i, child in enumerate(children):
                gapped_children.append(child)
                if i < len(children) - 1:
                    placeholder = widgets.HTML(
                        value="",
                        layout=widgets.Layout(
                            width=gap, height="100%", margin="0", padding="0", border="none"
                        ),
                    )
                    gapped_children.append(placeholder)
            children = gapped_children

        hbox_widget = widgets.HBox(children=children, layout=layout, **kwargs)
        hbox_widget.add_class("styled-widget")
        hbox_widget.add_class("styled-hbox")

        if overflow == "hidden":
            hbox_widget.add_class("styled-overflow-hidden")
        if overflow_x == "hidden":
            hbox_widget.add_class("styled-overflow-x-hidden")
        if overflow_y == "hidden":
            hbox_widget.add_class("styled-overflow-y-hidden")

        return hbox_widget

    @staticmethod
    def vbox(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        overflow: str = "auto",
        overflow_y: str = "auto",
        overflow_x: str = "auto",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []

        layout = WidgetFactory.get_layout(
            layout=layout,
            width=width,
            height=height,
            align_items=align_items,
            justify_content=justify_content,
            overflow=overflow,
            overflow_y=overflow_y,
            overflow_x=overflow_x,
        )

        if gap and len(children) > 1:
            gapped_children = []
            for i, child in enumerate(children):
                gapped_children.append(child)
                if i < len(children) - 1:
                    placeholder = widgets.HTML(
                        value="",
                        layout=widgets.Layout(
                            height=gap, width="100%", margin="0", padding="0", border="none"
                        ),
                    )
                    gapped_children.append(placeholder)
            children = gapped_children

        vbox_widget = widgets.VBox(children=children, layout=layout, **kwargs)
        vbox_widget.add_class("styled-widget")
        vbox_widget.add_class("styled-vbox")

        if overflow == "hidden":
            vbox_widget.add_class("styled-overflow-hidden")
        if overflow_x == "hidden":
            vbox_widget.add_class("styled-overflow-x-hidden")
        if overflow_y == "hidden":
            vbox_widget.add_class("styled-overflow-y-hidden")

        return vbox_widget

    @staticmethod
    def grid_container(
        children: list[widgets.Widget] | None = None,
        padding: str = "5px",
        width: str = "100%",
        height: str = "100%",
        overflow: str = "auto",
        overflow_y: str = "auto",
        overflow_x: str = "hidden",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.HBox:
        if children is None:
            children = []

        layout = WidgetFactory.get_layout(
            layout=layout,
            width=width,
            height=height,
            overflow=overflow,
            overflow_y=overflow_y,
            overflow_x=overflow_x,
        )

        if not getattr(layout, "display", None):
            layout.display = "flex"
        if not getattr(layout, "flex_flow", None):
            layout.flex_flow = "row wrap"
        if not getattr(layout, "align_items", None):
            layout.align_items = "flex-start"
        if not getattr(layout, "align_content", None):
            layout.align_content = "flex-start"
        if not getattr(layout, "padding", None):
            layout.padding = padding

        container = widgets.HBox(children=children, layout=layout, **kwargs)
        container.add_class("styled-widget")
        container.add_class("styled-grid-container")

        if overflow == "hidden":
            container.add_class("styled-overflow-hidden")
        if overflow_x == "hidden":
            container.add_class("styled-overflow-x-hidden")
        if overflow_y == "hidden":
            container.add_class("styled-overflow-y-hidden")

        return container

    # ===================== INFO FIELDS =====================

    @staticmethod
    def info_field_default(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-default")
        return info_field

    @staticmethod
    def info_field_info(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-info")
        return info_field

    @staticmethod
    def info_field_success(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-success")
        return info_field

    @staticmethod
    def info_field_warning(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-warning")
        return info_field

    @staticmethod
    def info_field_error(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-error")
        return info_field

    @staticmethod
    def info_field_critical(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-critical")
        return info_field

    @staticmethod
    def info_field_debug(
        children: list[widgets.Widget] | None = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        layout: widgets.Layout | None = None,
        **kwargs,
    ) -> widgets.VBox:
        if children is None:
            children = []
        info_field = WidgetFactory.vbox(
            children=children,
            width=width,
            height=height,
            gap=gap,
            align_items=align_items,
            justify_content=justify_content,
            layout=layout,
            **kwargs,
        )
        info_field.add_class("info-field-debug")
        return info_field
