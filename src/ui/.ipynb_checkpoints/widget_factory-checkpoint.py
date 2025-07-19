import logging
from typing import Optional, List, Dict, Any, Union, Callable

import ipywidgets as widgets

logger = logging.getLogger(__name__)


class WidgetFactory:
    """
    Factory class for creating styled IPython widgets with consistent styling and behavior.
    
    This class provides static methods for creating various types of widgets including buttons,
    input fields, containers, and complex components. All widgets are created with consistent
    CSS classes and styling to maintain a unified look across the application.
    """
    
    # BUTTON METHODS
    
    @staticmethod
    def button_default(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Button:
        """
        Create a default styled button widget.
        
        Args:
            description: Text to display on the button
            disabled: Whether the button should be disabled
            icon: Icon to display on the button
            tooltip: Tooltip text to show on hover
            width: CSS width of the button
            height: CSS height of the button
            on_click: Callback function to execute when clicked
            **kwargs: Additional arguments passed to the Button widget
            
        Returns:
            Configured Button widget with default styling
        """
        logger.debug("Creating default button: description='%s', disabled=%s", description, disabled)
        
        try:
            button = widgets.Button(
                description=description,
                disabled=disabled,
                icon=icon,
                tooltip=tooltip,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            button.add_class("styled-widget")
            button.add_class("styled-button")
            button.add_class("button-default")
            
            if on_click:
                button.on_click(on_click)
                logger.debug("Added click handler to button: %s", description)
            
            logger.debug("Successfully created default button")
            return button
            
        except Exception as e:
            logger.error("Failed to create default button: %s", e, exc_info=True)
            raise

    @staticmethod
    def button_emphasis(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Button:
        """
        Create an emphasis styled button widget (highlighted/primary button).
        
        Args:
            description: Text to display on the button
            disabled: Whether the button should be disabled
            icon: Icon to display on the button
            tooltip: Tooltip text to show on hover
            width: CSS width of the button
            height: CSS height of the button
            on_click: Callback function to execute when clicked
            **kwargs: Additional arguments passed to the Button widget
            
        Returns:
            Configured Button widget with emphasis styling
        """
        logger.debug("Creating emphasis button: description='%s'", description)
        
        try:
            button = widgets.Button(
                description=description,
                disabled=disabled,
                icon=icon,
                tooltip=tooltip,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            button.add_class("styled-widget")
            button.add_class("styled-button")
            button.add_class("button-emphasis")
            
            if on_click:
                button.on_click(on_click)
            
            return button
            
        except Exception as e:
            logger.error("Failed to create emphasis button: %s", e, exc_info=True)
            raise

    @staticmethod
    def button_success(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Button:
        """
        Create a success styled button widget (typically green/positive actions).
        
        Args:
            description: Text to display on the button
            disabled: Whether the button should be disabled
            icon: Icon to display on the button
            tooltip: Tooltip text to show on hover
            width: CSS width of the button
            height: CSS height of the button
            on_click: Callback function to execute when clicked
            **kwargs: Additional arguments passed to the Button widget
            
        Returns:
            Configured Button widget with success styling
        """
        logger.debug("Creating success button: description='%s'", description)
        
        try:
            button = widgets.Button(
                description=description,
                disabled=disabled,
                icon=icon,
                tooltip=tooltip,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            button.add_class("styled-widget")
            button.add_class("styled-button")
            button.add_class("button-success")
            
            if on_click:
                button.on_click(on_click)
            
            return button
            
        except Exception as e:
            logger.error("Failed to create success button: %s", e, exc_info=True)
            raise

    @staticmethod
    def button_danger(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Button:
        """
        Create a danger styled button widget (typically red/destructive actions).
        
        Args:
            description: Text to display on the button
            disabled: Whether the button should be disabled
            icon: Icon to display on the button
            tooltip: Tooltip text to show on hover
            width: CSS width of the button
            height: CSS height of the button
            on_click: Callback function to execute when clicked
            **kwargs: Additional arguments passed to the Button widget
            
        Returns:
            Configured Button widget with danger styling
        """
        logger.debug("Creating danger button: description='%s'", description)
        
        try:
            button = widgets.Button(
                description=description,
                disabled=disabled,
                icon=icon,
                tooltip=tooltip,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            button.add_class("styled-widget")
            button.add_class("styled-button")
            button.add_class("button-danger")
            
            if on_click:
                button.on_click(on_click)
            
            return button
            
        except Exception as e:
            logger.error("Failed to create danger button: %s", e, exc_info=True)
            raise

    @staticmethod
    def button_warning(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Button:
        """
        Create a warning styled button widget (typically orange/caution actions).
        
        Args:
            description: Text to display on the button
            disabled: Whether the button should be disabled
            icon: Icon to display on the button
            tooltip: Tooltip text to show on hover
            width: CSS width of the button
            height: CSS height of the button
            on_click: Callback function to execute when clicked
            **kwargs: Additional arguments passed to the Button widget
            
        Returns:
            Configured Button widget with warning styling
        """
        logger.debug("Creating warning button: description='%s'", description)
        
        try:
            button = widgets.Button(
                description=description,
                disabled=disabled,
                icon=icon,
                tooltip=tooltip,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            button.add_class("styled-widget")
            button.add_class("styled-button")
            button.add_class("button-warning")
            
            if on_click:
                button.on_click(on_click)
            
            return button
            
        except Exception as e:
            logger.error("Failed to create warning button: %s", e, exc_info=True)
            raise
        
    @staticmethod
    def toggle_button(
        description: str = "",
        disabled: bool = False,
        icon: str = "",
        tooltip: str = "",
        width: str = "auto",
        height: str = "32px",
        toggled: bool = False,
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Button:
        """
        Create a toggle button widget that switches between active/inactive states.
        Replaces the regular toggle button widget since its easier to handle it like this.
        
        Args:
            description: Text to display on the button
            disabled: Whether the button should be disabled
            icon: Icon to display on the button
            tooltip: Tooltip text to show on hover
            width: CSS width of the button
            height: CSS height of the button
            toggled: Initial toggle state
            on_click: Callback function to execute when clicked
            **kwargs: Additional arguments passed to the Button widget
            
        Returns:
            Configured Button widget with toggle functionality
        """
        logger.debug("Creating toggle button: description='%s', initial_state=%s", description, toggled)
        
        try:
            button = widgets.Button(
                description=description,
                disabled=disabled,
                icon=icon,
                tooltip=tooltip,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
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
                logger.debug("Toggle button state changed to: %s", b._toggled)
        
            def set_toggled(toggled_state: bool):
                button._toggled = toggled_state
                update_appearance()
        
            def get_toggled() -> bool:
                return button._toggled
            
            if on_click:
                button.on_click(on_click)
            button.on_click(toggle_handler)
            
            return button
            
        except Exception as e:
            logger.error("Failed to create toggle button: %s", e, exc_info=True)
            raise

    @staticmethod
    def custom_radio_buttons(
        number: int = 2,
        description: Optional[List[str]] = None,
        i_toggled: int = 0,
        width: str = "auto",
        height: str = "32px"
    ) -> List[widgets.Button]:
        """
        Create a set of custom radio buttons using styled buttons.
        Basically this is a set of toggle buttons which are able to disable one another.
        
        Args:
            number: Number of radio buttons to create
            description: List of descriptions for each button
            i_toggled: Index of initially selected button
            width: CSS width for each button
            height: CSS height for each button
            
        Returns:
            List of Button widgets configured as radio buttons
        """
        logger.debug("Creating custom radio buttons: count=%d, selected=%d", number, i_toggled)
        
        if number < 1:
            logger.warning("Invalid number of radio buttons requested: %d", number)
            return []

        if description is None:
            description = []
        
        if len(description) < number:
            description += [""] * (number - len(description))

        try:
            buttons = []
            for i in range(number):
                button = widgets.Button(
                    description=description[i],
                    layout=widgets.Layout(width=width, height=height),
                )
                button.add_class("styled-widget")
                button.add_class("styled-button")
                if i == i_toggled:
                    button.add_class("button-emphasis")
                else:
                    button.add_class("button-default")
                buttons.append(button)

            def toggle_handler(b):
                for button in buttons:
                    button.remove_class("button-emphasis")
                    button.add_class("button-default")
                b.remove_class("button-default")
                b.add_class("button-emphasis")
                logger.debug("Radio button selection changed")
            
            for button in buttons:
                button.on_click(toggle_handler)

            logger.debug("Successfully created %d radio buttons", len(buttons))
            return buttons
            
        except Exception as e:
            logger.error("Failed to create radio buttons: %s", e, exc_info=True)
            raise
        
    # INPUT FIELD METHODS

    @staticmethod
    def text_input(
        value: str = "",
        placeholder: str = "",
        description: str = "",
        disabled: bool = False,
        width: str = "300px",
        height: str = "32px",
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Text:
        """
        Create a styled text input widget.
        
        Args:
            value: Initial text value
            placeholder: Placeholder text when empty
            description: Label text for the input
            disabled: Whether the input should be disabled
            width: CSS width of the input
            height: CSS height of the input
            on_change: Callback function for value changes
            **kwargs: Additional arguments passed to the Text widget
            
        Returns:
            Configured Text widget with styling
        """
        logger.debug("Creating text input: description='%s', placeholder='%s'", description, placeholder)
        
        try:
            text = widgets.Text(
                value=value,
                placeholder=placeholder,
                description=description,
                disabled=disabled,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            text.add_class("styled-widget")
            text.add_class("styled-input")
            
            if on_change:
                text.observe(on_change, names='value')
                logger.debug("Added change handler to text input")
            
            return text
            
        except Exception as e:
            logger.error("Failed to create text input: %s", e, exc_info=True)
            raise

    @staticmethod
    def password_input(
        value: str = "",
        placeholder: str = "",
        description: str = "",
        disabled: bool = False,
        width: str = "300px",
        height: str = "32px",
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Password:
        """
        Create a styled password input widget.
        
        Args:
            value: Initial password value
            placeholder: Placeholder text when empty
            description: Label text for the input
            disabled: Whether the input should be disabled
            width: CSS width of the input
            height: CSS height of the input
            on_change: Callback function for value changes
            **kwargs: Additional arguments passed to the Password widget
            
        Returns:
            Configured Password widget with styling
        """
        logger.debug("Creating password input: description='%s'", description)
        
        try:
            password = widgets.Password(
                value=value,
                placeholder=placeholder,
                description=description,
                disabled=disabled,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            password.add_class("styled-widget")
            password.add_class("styled-input")
            
            if on_change:
                password.observe(on_change, names='value')
            
            return password
            
        except Exception as e:
            logger.error("Failed to create password input: %s", e, exc_info=True)
            raise

    @staticmethod
    def textarea_input(
        value: str = "",
        placeholder: str = "",
        description: str = "",
        disabled: bool = False,
        width: str = "400px",
        height: str = "120px",
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Textarea:
        """
        Create a styled textarea input widget for multi-line text.
        
        Args:
            value: Initial text value
            placeholder: Placeholder text when empty
            description: Label text for the textarea
            disabled: Whether the textarea should be disabled
            width: CSS width of the textarea
            height: CSS height of the textarea
            on_change: Callback function for value changes
            **kwargs: Additional arguments passed to the Textarea widget
            
        Returns:
            Configured Textarea widget with styling
        """
        logger.debug("Creating textarea input: description='%s', size=%sx%s", description, width, height)
        
        try:
            textarea = widgets.Textarea(
                value=value,
                placeholder=placeholder,
                description=description,
                disabled=disabled,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            textarea.add_class("styled-widget")
            textarea.add_class("styled-textarea")
            
            if on_change:
                textarea.observe(on_change, names='value')
            
            return textarea
            
        except Exception as e:
            logger.error("Failed to create textarea input: %s", e, exc_info=True)
            raise

    @staticmethod
    def number_input(
        value: Union[int, float] = 0,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        step: Union[int, float] = 1,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        on_change: Optional[Callable] = None,
        **kwargs
    ):
        """
        Create a styled number input widget (integer or float based on input types).
        
        Args:
            value: Initial numeric value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            step: Step increment for the input
            description: Label text for the input
            disabled: Whether the input should be disabled
            width: CSS width of the input
            height: CSS height of the input
            on_change: Callback function for value changes
            **kwargs: Additional arguments passed to the widget
            
        Returns:
            Configured BoundedIntText or BoundedFloatText widget with styling
        """
        logger.debug("Creating number input: description='%s', value=%s, type=%s, min_value=%s, max_value=%s", 
                     description, value, type(value).__name__, min_value, max_value)
        
        try:
            if isinstance(value, int) and isinstance(step, int):
                widget = widgets.BoundedIntText(
                    value=value,
                    min=min_value if min_value is not None else 0,
                    max=max_value if max_value is not None else 100,
                    step=step,
                    description=description,
                    disabled=disabled,
                    layout=widgets.Layout(width=width, height=height),
                    **kwargs
                )
            else:
                widget = widgets.BoundedFloatText(
                    value=float(value),
                    min=min_value if min_value is not None else 0.0,
                    max=max_value if max_value is not None else 100.0,
                    step=float(step),
                    description=description,
                    disabled=disabled,
                    layout=widgets.Layout(width=width, height=height),
                    **kwargs
                )
            
            widget.add_class("styled-widget")
            widget.add_class("styled-input")
            
            if on_change:
                widget.observe(on_change, names="value")
            
            logger.debug("Created widget traits: %s", widget.trait_names())
            return widget
            
        except Exception as e:
            logger.error("Failed to create number input: %s", e, exc_info=True)
            raise

    # DROPDOWN METHODS

    @staticmethod
    def dropdown(
        options: Optional[List[Union[str, tuple]]] = None,
        value: Optional[Any] = None,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Dropdown:
        """
        Create a styled dropdown selection widget.
        
        Args:
            options: List of options (strings or tuples of (label, value))
            value: Initial selected value
            description: Label text for the dropdown
            disabled: Whether the dropdown should be disabled
            width: CSS width of the dropdown
            height: CSS height of the dropdown
            on_change: Callback function for selection changes
            **kwargs: Additional arguments passed to the Dropdown widget
            
        Returns:
            Configured Dropdown widget with styling
        """
        if options is None:
            options = []
            
        logger.debug("Creating dropdown: description='%s', options_count=%d", description, len(options))
        
        try:
            dropdown_widget = widgets.Dropdown(
                options=options,
                value=value,
                description=description,
                disabled=disabled,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            dropdown_widget.add_class("styled-widget")
            dropdown_widget.add_class("styled-dropdown")
            
            if on_change:
                dropdown_widget.observe(on_change, names='value')
            
            return dropdown_widget
            
        except Exception as e:
            logger.error("Failed to create dropdown: %s", e, exc_info=True)
            raise

    # CHECKBOX METHODS

    @staticmethod
    def checkbox(
        value: bool = False,
        description: str = "",
        disabled: bool = False,
        indent: bool = True,
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> widgets.Checkbox:
        """
        Create a styled checkbox widget.
        
        Args:
            value: Initial checked state
            description: Label text for the checkbox
            disabled: Whether the checkbox should be disabled
            indent: Whether to indent the checkbox
            on_change: Callback function for state changes
            **kwargs: Additional arguments passed to the Checkbox widget
            
        Returns:
            Configured Checkbox widget with styling
        """
        logger.debug("Creating checkbox: description='%s', value=%s", description, value)
        
        try:
            checkbox_widget = widgets.Checkbox(
                value=value,
                description=description,
                disabled=disabled,
                indent=indent,
                **kwargs
            )
            checkbox_widget.add_class("styled-widget")
            checkbox_widget.add_class("styled-checkbox")
            
            if on_change:
                checkbox_widget.observe(on_change, names='value')
            
            return checkbox_widget
            
        except Exception as e:
            logger.error("Failed to create checkbox: %s", e, exc_info=True)
            raise

    @staticmethod
    def radio_buttons(
        options: List[str],
        i_selected: int,
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> List[widgets.Checkbox]:
        """
        Create a set of radio buttons using checkboxes with mutually exclusive selection.
        Doing this is easier than using the actual ipywidgets radio button.
        
        Args:
            options: List of option labels
            i_selected: Index of initially selected option
            on_change: Callback function for selection changes
            **kwargs: Additional arguments passed to checkbox widgets
            
        Returns:
            List of Checkbox widgets configured as radio buttons
        """
        logger.debug("Creating radio buttons: options_count=%d, selected=%d", len(options), i_selected)
        
        try:
            checkboxes = []
            
            for i, option in enumerate(options):
                value = (i == i_selected)
                checkbox = WidgetFactory.checkbox(
                    value=value,
                    description=option,
                    **kwargs
                )
                checkboxes.append(checkbox)

            # Using a list allows us to store a mutable ignore flag
            ignore_event = [False]

            def on_checkbox_change(change):
                if ignore_event[0]:
                    return
                ignore_event[0] = True
                
                for checkbox in checkboxes:
                    checkbox.value = False
                    
                change["owner"].value = True
                ignore_event[0] = False
                logger.debug("Radio button selection changed")

            for checkbox in checkboxes:
                checkbox.observe(on_checkbox_change, names="value")
            
            if on_change:
                for checkbox in checkboxes:
                    checkbox.observe(on_change, names="value")
            
            return checkboxes
            
        except Exception as e:
            logger.error("Failed to create radio buttons: %s", e, exc_info=True)
            raise

    # SLIDER METHODS

    @staticmethod
    def slider(
        value: Union[int, float] = 0,
        min_value: Union[int, float] = 0,
        max_value: Union[int, float] = 100,
        step: Union[int, float] = 1,
        description: str = "",
        disabled: bool = False,
        orientation: str = "horizontal",
        width: str = "300px",
        height: str = "auto",
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> Union[widgets.IntSlider, widgets.FloatSlider]:
        """
        Create a styled slider widget (integer or float based on input types).
        
        Args:
            value: Initial slider value
            min_value: Minimum slider value
            max_value: Maximum slider value
            step: Step increment for the slider
            description: Label text for the slider
            disabled: Whether the slider should be disabled
            orientation: Slider orientation ('horizontal' or 'vertical')
            width: CSS width of the slider
            height: CSS height of the slider
            on_change: Callback function for value changes
            **kwargs: Additional arguments passed to the widget
            
        Returns:
            Configured IntSlider or FloatSlider widget with styling
        """
        logger.debug("Creating slider: description='%s', range=%s-%s, orientation=%s", 
                    description, min_value, max_value, orientation)
        
        try:
            if isinstance(value, int) and isinstance(step, int):
                slider_widget = widgets.IntSlider(
                    value=value,
                    min=min_value,
                    max=max_value,
                    step=step,
                    description=description,
                    disabled=disabled,
                    orientation=orientation,
                    layout=widgets.Layout(width=width, height=height),
                    **kwargs
                )
            else:
                slider_widget = widgets.FloatSlider(
                    value=float(value),
                    min=float(min_value),
                    max=float(max_value),
                    step=float(step),
                    description=description,
                    disabled=disabled,
                    orientation=orientation,
                    layout=widgets.Layout(width=width, height=height),
                    **kwargs
                )
            
            slider_widget.add_class("styled-widget")
            slider_widget.add_class("styled-slider")
            
            if on_change:
                slider_widget.observe(on_change, names='value')
            
            return slider_widget
            
        except Exception as e:
            logger.error("Failed to create slider: %s", e, exc_info=True)
            raise

    # DATE PICKER METHODS

    @staticmethod
    def date_picker(
        value: Optional[Any] = None,
        description: str = "",
        disabled: bool = False,
        width: str = "200px",
        height: str = "32px",
        layout: Optional[widgets.Layout] = None,
        on_change: Optional[Callable] = None,
        **kwargs
    ) -> widgets.DatePicker:
        """
        Create a styled date picker widget.
        
        Args:
            value: Initial date value
            description: Label text for the date picker
            disabled: Whether the date picker should be disabled
            width: CSS width of the date picker
            height: CSS height of the date picker
            layout: Custom layout (overrides width/height if provided)
            on_change: Callback function for date changes
            **kwargs: Additional arguments passed to the DatePicker widget
            
        Returns:
            Configured DatePicker widget with styling
        """
        logger.debug("Creating date picker: description='%s'", description)
        
        if layout is None:
            layout = widgets.Layout(width=width, height=height)
        
        try:
            date_picker_widget = widgets.DatePicker(
                value=value,
                description=description,
                disabled=disabled,
                layout=layout,
                **kwargs
            )
            date_picker_widget.add_class("styled-widget")
            date_picker_widget.add_class("styled-date-picker")
            
            if on_change:
                date_picker_widget.observe(on_change, names='value')
            
            return date_picker_widget
            
        except Exception as e:
            logger.error("Failed to create date picker: %s", e, exc_info=True)
            raise

    # PROGRESS BAR METHODS

    @staticmethod
    def progress_bar(
        value: Union[int, float] = 0,
        min_value: Union[int, float] = 0,
        max_value: Union[int, float] = 100,
        description: str = "",
        width: str = "300px",
        height: str = "20px",
        **kwargs
    ) -> Union[widgets.IntProgress, widgets.FloatProgress]:
        """
        Create a styled progress bar widget.
        
        Args:
            value: Current progress value
            min_value: Minimum progress value
            max_value: Maximum progress value
            description: Label text for the progress bar
            width: CSS width of the progress bar
            height: CSS height of the progress bar
            **kwargs: Additional arguments passed to the progress widget
            
        Returns:
            Configured IntProgress or FloatProgress widget with styling
        """
        logger.debug("Creating progress bar: description='%s', value=%s/%s", description, value, max_value)
        
        try:
            if isinstance(value, int):
                progress = widgets.IntProgress(
                    value=value,
                    min=min_value,
                    max=max_value,
                    description=description,
                    layout=widgets.Layout(width=width, height=height),
                    **kwargs
                )
            else:
                progress = widgets.FloatProgress(
                    value=float(value),
                    min=float(min_value),
                    max=float(max_value),
                    description=description,
                    layout=widgets.Layout(width=width, height=height),
                    **kwargs
                )
            
            progress.add_class("styled-widget")
            progress.add_class("styled-progress")
            
            return progress
            
        except Exception as e:
            logger.error("Failed to create progress bar: %s", e, exc_info=True)
            raise

    # TAB METHODS

    @staticmethod
    def tab(
        children: Optional[List[widgets.Widget]] = None,
        titles: Optional[List[str]] = None,
        width: str = "100%",
        height: str = "100%",
        **kwargs
    ) -> widgets.Tab:
        """
        Create a styled tab widget.
        
        Args:
            children: List of widgets to display in each tab
            titles: List of titles for each tab
            width: CSS width of the tab widget
            height: CSS height of the tab widget
            **kwargs: Additional arguments passed to the Tab widget
            
        Returns:
            Configured Tab widget with styling
        """
        if children is None:
            children = []
        if titles is None:
            titles = []
        
        logger.debug("Creating tab widget: children_count=%d, titles_count=%d", len(children), len(titles))
        
        try:
            tab_widget = widgets.Tab(
                children=children,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            
            # Set titles if provided
            for i, title in enumerate(titles):
                if i < len(children):
                    tab_widget.set_title(i, title)
                    logger.debug("Set tab title %d: %s", i, title)
            
            tab_widget.add_class("styled-widget")
            tab_widget.add_class("styled-tab")
            
            return tab_widget
            
        except Exception as e:
            logger.error("Failed to create tab widget: %s", e, exc_info=True)
            raise

    # ACCORDION METHODS

    @staticmethod
    def accordion(
        children: Optional[List[widgets.Widget]] = None,
        titles: Optional[List[str]] = None,
        width: str = "100%",
        height: str = "auto",
        **kwargs
    ) -> widgets.Accordion:
        """
        Create a styled accordion widget.
        
        Args:
            children: List of widgets to display in each accordion section
            titles: List of titles for each accordion section
            width: CSS width of the accordion widget
            height: CSS height of the accordion widget
            **kwargs: Additional arguments passed to the Accordion widget
            
        Returns:
            Configured Accordion widget with styling
        """
        if children is None:
            children = []
        if titles is None:
            titles = []
            
        logger.debug("Creating accordion widget: children_count=%d, titles_count=%d", len(children), len(titles))
        
        try:
            accordion_widget = widgets.Accordion(
                children=children,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            
            # Set titles if provided
            for i, title in enumerate(titles):
                if i < len(children):
                    accordion_widget.set_title(i, title)
                    logger.debug("Set accordion title %d: %s", i, title)
            
            accordion_widget.add_class("styled-widget")
            accordion_widget.add_class("styled-accordion")
            
            return accordion_widget
            
        except Exception as e:
            logger.error("Failed to create accordion widget: %s", e, exc_info=True)
            raise

    # OUTPUT METHODS

    @staticmethod
    def output_widget(
        width: str = "100%",
        height: str = "200px",
        **kwargs
    ) -> widgets.Output:
        """
        Create a styled output widget for displaying output content.
        
        Args:
            width: CSS width of the output widget
            height: CSS height of the output widget
            **kwargs: Additional arguments passed to the Output widget
            
        Returns:
            Configured Output widget with styling
        """
        logger.debug("Creating output widget: size=%sx%s", width, height)
        
        try:
            output = widgets.Output(
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            output.add_class("styled-widget")
            output.add_class("styled-output")
            
            return output
            
        except Exception as e:
            logger.error("Failed to create output widget: %s", e, exc_info=True)
            raise

    # HTML WIDGET METHODS

    @staticmethod
    def label(
        value: str = "",
        emphasis: bool = False,
        **kwargs
    ) -> widgets.HTML:
        """
        Create a styled label widget using HTML.
        Lables are small descriptors used to tag other elements.
        
        Args:
            value: Text content for the label
            emphasis: Whether to apply emphasis styling
            **kwargs: Additional arguments passed to the HTML widget
            
        Returns:
            Configured HTML widget styled as a label
        """
        logger.debug("Creating label: value='%s', emphasis=%s", value, emphasis)
        
        try:
            label_widget = widgets.HTML(
                value=value,
                **kwargs
            )
            label_widget.add_class("styled-widget")
            label_widget.add_class("styled-label")
            
            if emphasis:
                label_widget.add_class("label-emphasis")
            
            return label_widget
            
        except Exception as e:
            logger.error("Failed to create label: %s", e, exc_info=True)
            raise

    @staticmethod
    def html_widget(
        value: str = "",
        width: str = "100%",
        height: str = "auto",
        **kwargs
    ) -> widgets.HTML:
        """
        Create a styled HTML widget for displaying HTML content.
        
        Args:
            value: HTML content to display
            width: CSS width of the HTML widget
            height: CSS height of the HTML widget
            **kwargs: Additional arguments passed to the HTML widget
            
        Returns:
            Configured HTML widget with styling
        """
        logger.debug("Creating HTML widget: content_length=%d", len(value))
        
        try:
            html = widgets.HTML(
                value=value,
                layout=widgets.Layout(width=width, height=height),
                **kwargs
            )
            html.add_class("styled-widget")
            html.add_class("styled-html")
            
            return html
            
        except Exception as e:
            logger.error("Failed to create HTML widget: %s", e, exc_info=True)
            raise

    # CONTAINER METHODS

    @staticmethod
    def hbox(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "center",
        justify_content: str = "flex-start",
        overflow: str = "auto",
        overflow_y: str = "auto",
        overflow_x: str = "auto",
        **kwargs
    ) -> widgets.HBox:
        """
        Create a styled horizontal box container.
        
        Args:
            children: List of child widgets to contain
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            overflow: CSS overflow property
            overflow_y: CSS overflow-y property
            overflow_x: CSS overflow-x property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured HBox widget with styling
        """
        if children is None:
            children = []

        logger.debug("Creating HBox: children_count=%d, size=%sx%s", len(children), width, height)
        
        try:
            hbox_widget = widgets.HBox(
                children=children,
                layout=widgets.Layout(
                    width=width,
                    height=height,
                    align_items=align_items,
                    justify_content=justify_content,
                    overflow=overflow,
                    overflow_y=overflow_y,
                    overflow_x=overflow_x,
                    **kwargs
                )
            )
            hbox_widget.add_class("styled-widget")
            hbox_widget.add_class("styled-hbox")
            
            if overflow == "hidden":
               hbox_widget.add_class("styled-overflow-hidden")
            if overflow_x == "hidden":
               hbox_widget.add_class("styled-overflow-x-hidden")
            if overflow_y == "hidden":
               hbox_widget.add_class("styled-overflow-y-hidden")
            
            # Add gap using CSS margin on children if specified
            if gap and children:
                for i, child in enumerate(children[:-1]):  # All except last child
                    if hasattr(child, 'layout') and hasattr(child.layout, 'margin'):
                        child.layout.margin = f"{child.layout.margin or '0'} {gap} 0 0"
            
            return hbox_widget
            
        except Exception as e:
            logger.error("Failed to create HBox: %s", e, exc_info=True)
            raise

    @staticmethod
    def vbox(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        overflow: str = "auto",
        overflow_y: str = "auto",
        overflow_x: str = "auto",
        **kwargs
    ) -> widgets.VBox:
        """
        Create a styled vertical box container.
        
        Args:
            children: List of child widgets to contain
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            overflow: CSS overflow property
            overflow_y: CSS overflow-y property
            overflow_x: CSS overflow-x property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with styling
        """
        if children is None:
            children = []
        
        logger.debug("Creating VBox: children_count=%d, size=%sx%s", len(children), width, height)
        
        try:
            vbox_widget = widgets.VBox(
                children=children,
                layout=widgets.Layout(
                    width=width,
                    height=height,
                    align_items=align_items,
                    justify_content=justify_content,
                    overflow=overflow,
                    overflow_y=overflow_y,
                    overflow_x=overflow_x,
                    **kwargs
                )
            )
            vbox_widget.add_class("styled-widget")
            vbox_widget.add_class("styled-vbox")
            
            if overflow == "hidden":
               vbox_widget.add_class("styled-overflow-hidden")
            if overflow_x == "hidden":
               vbox_widget.add_class("styled-overflow-x-hidden")
            if overflow_y == "hidden":
               vbox_widget.add_class("styled-overflow-y-hidden")
            
            # Add gap using CSS margin on children if specified
            if gap and children:
                for i, child in enumerate(children[:-1]):  # All except last child
                    if hasattr(child, 'layout') and hasattr(child.layout, 'margin'):
                        child.layout.margin = f"0 0 {gap} 0"
            
            return vbox_widget
            
        except Exception as e:
            logger.error("Failed to create VBox: %s", e, exc_info=True)
            raise

    @staticmethod
    def grid_container(
        children: Optional[List[widgets.Widget]] = None,
        padding: str = "5px",
        width: str = "100%",
        height: str = "100%",
        **kwargs
    ) -> widgets.HBox:
        """
        Create a styled grid container using flexbox layout.
        
        Args:
            children: List of child widgets to arrange in grid
            padding: Padding around the container
            width: CSS width of the container
            height: CSS height of the container
            **kwargs: Additional layout arguments
            
        Returns:
            Configured HBox widget with grid-like flexbox styling
        """
        if children is None:
            children = []
        
        logger.debug("Creating grid container: children_count=%d, size=%sx%s", len(children), width, height)
        
        try:
            # Flexbox Layout Properties
            layout_props = {
                "display": "flex",
                "flex_flow": "row wrap",
                "align_items": "flex-start",
                "align_content": "flex-start",
                "overflow_y": "auto",
                "overflow_x": "hidden",
                "width": width,
                "height": height,
                "padding": padding,
            }
            
            layout_props.update(kwargs)
            
            container = widgets.HBox(
                children=children,
                layout=widgets.Layout(**layout_props)
            )
            
            container.add_class("styled-widget")
            container.add_class("styled-grid-container")
            
            return container
            
        except Exception as e:
            logger.error("Failed to create grid container: %s", e, exc_info=True)
            raise

    # INFO FIELD METHODS

    @staticmethod
    def info_field_default(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create a default styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with default info field styling
        """
        if children is None:
            children = []

        logger.debug("Creating default info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-default")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create default info field: %s", e, exc_info=True)
            raise

    @staticmethod
    def info_field_info(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create an info styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with info styling
        """
        if children is None:
            children = []

        logger.debug("Creating info info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-info")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create info info field: %s", e, exc_info=True)
            raise

    @staticmethod
    def info_field_success(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create a success styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with success styling
        """
        if children is None:
            children = []

        logger.debug("Creating success info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-success")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create success info field: %s", e, exc_info=True)
            raise

    @staticmethod
    def info_field_warning(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create a warning styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with warning styling
        """
        if children is None:
            children = []
            
        logger.debug("Creating warning info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-warning")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create warning info field: %s", e, exc_info=True)
            raise

    @staticmethod
    def info_field_error(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create an error styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with error styling
        """
        if children is None:
            children = []

        logger.debug("Creating error info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-error")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create error info field: %s", e, exc_info=True)
            raise

    @staticmethod
    def info_field_critical(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create a critical styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with critical styling
        """
        if children is None:
            children = []

        logger.debug("Creating critical info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-critical")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create critical info field: %s", e, exc_info=True)
            raise

    @staticmethod
    def info_field_debug(
        children: Optional[List[widgets.Widget]] = None,
        width: str = "100%",
        height: str = "auto",
        gap: str = "5px",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        **kwargs
    ) -> widgets.VBox:
        """
        Create a debug styled info field container.
        Basically this is just a styled box to put other widgets into.
        
        Args:
            children: List of child widgets
            width: CSS width of the container
            height: CSS height of the container
            gap: Gap between child elements
            align_items: CSS align-items property
            justify_content: CSS justify-content property
            **kwargs: Additional layout arguments
            
        Returns:
            Configured VBox widget with debug styling
        """
        if children is None:
            children = []
        
        logger.debug("Creating debug info field: children_count=%d", len(children))
        
        try:
            info_field = WidgetFactory.vbox(
                children=children,
                width=width,
                height=height,
                gap=gap,
                align_items=align_items,
                justify_content=justify_content,
                **kwargs
            )
            info_field.add_class("info-field-debug")
            return info_field
            
        except Exception as e:
            logger.error("Failed to create debug info field: %s", e, exc_info=True)
            raise