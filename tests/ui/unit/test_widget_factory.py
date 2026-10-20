import pytest
from unittest.mock import Mock, patch
import ipywidgets as widgets
from datetime import date

from suplex.ui.widget_factory import WidgetFactory


class TestWidgetFactory:
    """Tests for the WidgetFactory – a static factory that creates consistently styled
    ipywidgets (buttons, inputs, containers, sliders, etc.) with proper CSS classes.
    """

    # -------------------------------------------------------------------------
    # Button methods
    # -------------------------------------------------------------------------
    def test_button_default(self):
        """button_default() creates a properly styled Button with all passed parameters."""
        button = WidgetFactory.button_default(
            description="Test Button",
            disabled=False,
            icon="check",
            tooltip="Test tooltip",
            width="100px",
            height="40px",
        )

        assert isinstance(button, widgets.Button)
        assert button.description == "Test Button"
        assert button.disabled is False
        assert button.icon == "check"
        assert button.tooltip == "Test tooltip"
        assert button.layout.width == "100px"
        assert button.layout.height == "40px"
        assert "styled-widget" in button._dom_classes
        assert "styled-button" in button._dom_classes
        assert "button-default" in button._dom_classes

    def test_button_default_with_click_handler(self):
        """on_click handler is correctly attached to default button."""
        mock_handler = Mock()
        with patch.object(widgets.Button, "on_click") as mock_on_click:
            button = WidgetFactory.button_default(description="Click me", on_click=mock_handler)
            mock_on_click.assert_called_once_with(mock_handler)

    @pytest.mark.parametrize(
        "factory_method, expected_class",
        [
            (WidgetFactory.button_emphasis, "button-emphasis"),
            (WidgetFactory.button_success, "button-success"),
            (WidgetFactory.button_danger, "button-danger"),
            (WidgetFactory.button_warning, "button-warning"),
        ],
    )
    def test_specialized_buttons(self, factory_method, expected_class):
        """All specialized button factories apply the correct CSS class."""
        button = factory_method(description="Special Button")

        assert isinstance(button, widgets.Button)
        assert expected_class in button._dom_classes

    def test_toggle_button(self):
        """toggle_button() starts in the correct state and has toggle handler attached."""
        button = WidgetFactory.toggle_button(description="Toggle", toggled=True)

        assert isinstance(button, widgets.Button)
        assert button._toggled is True
        assert "button-emphasis" in button._dom_classes
        assert "button-default" not in button._dom_classes

    def test_custom_radio_buttons(self):
        """custom_radio_buttons() creates mutually exclusive buttons with correct initial state."""
        buttons = WidgetFactory.custom_radio_buttons(
            number=3,
            description=["Option 1", "Option 2", "Option 3"],
            i_toggled=1,
        )

        assert len(buttons) == 3
        assert all(isinstance(b, widgets.Button) for b in buttons)
        assert "button-emphasis" in buttons[1]._dom_classes
        assert "button-default" in buttons[0]._dom_classes

    def test_custom_radio_buttons_invalid_number(self):
        """Returns empty list when number < 1."""
        buttons = WidgetFactory.custom_radio_buttons(number=0)
        assert buttons == []

    # -------------------------------------------------------------------------
    # Input field methods
    # -------------------------------------------------------------------------
    def test_text_input(self):
        """text_input() creates a styled Text widget with all parameters applied."""
        text = WidgetFactory.text_input(
            value="initial",
            placeholder="Enter text",
            description="Name:",
            disabled=False,
            width="200px",
        )

        assert isinstance(text, widgets.Text)
        assert text.value == "initial"
        assert text.placeholder == "Enter text"
        assert text.description == "Name:"
        assert text.disabled is False
        assert text.layout.width == "200px"
        assert "styled-input" in text._dom_classes

    def test_text_input_with_change_handler(self):
        """on_change observer is attached for text inputs."""
        mock_handler = Mock()
        text = WidgetFactory.text_input(value="test", on_change=mock_handler)

        text.value = "new value"
        mock_handler.assert_called()

    def test_password_input(self):
        """password_input() creates a styled Password widget."""
        password = WidgetFactory.password_input(
            value="secret", placeholder="Enter password", description="Password:"
        )

        assert isinstance(password, widgets.Password)
        assert password.value == "secret"
        assert password.placeholder == "Enter password"
        assert "styled-input" in password._dom_classes

    def test_textarea_input(self):
        """textarea_input() creates a styled Textarea with correct dimensions."""
        textarea = WidgetFactory.textarea_input(
            value="Multi\nline\ntext",
            placeholder="Enter description",
            width="400px",
            height="150px",
        )

        assert isinstance(textarea, widgets.Textarea)
        assert textarea.value == "Multi\nline\ntext"
        assert textarea.layout.width == "400px"
        assert textarea.layout.height == "150px"
        assert "styled-textarea" in textarea._dom_classes

    @pytest.mark.parametrize(
        "value, expected_type",
        [(42, widgets.BoundedIntText), (3.14, widgets.BoundedFloatText)],
    )
    def test_number_input(self, value, expected_type):
        """number_input() chooses Int or Float widget based on value type."""
        number = WidgetFactory.number_input(
            value=value, min_value=0, max_value=100, step=1, description="Count:"
        )

        assert isinstance(number, expected_type)
        assert number.value == value

    def test_int_number_input(self):
        """int_number_input() always returns BoundedIntText."""
        widget = WidgetFactory.int_number_input(value=10, min_value=0, max_value=100)
        assert isinstance(widget, widgets.BoundedIntText)

    def test_float_number_input(self):
        """float_number_input() always returns BoundedFloatText."""
        widget = WidgetFactory.float_number_input(value=3.14, step=0.1)
        assert isinstance(widget, widgets.BoundedFloatText)

    # -------------------------------------------------------------------------
    # Selection widgets
    # -------------------------------------------------------------------------
    def test_dropdown(self):
        """dropdown() creates a styled Dropdown with correct options and value."""
        dropdown = WidgetFactory.dropdown(
            options=["Option 1", "Option 2", "Option 3"],
            value="Option 2",
            description="Choose:",
            width="150px",
        )

        assert isinstance(dropdown, widgets.Dropdown)
        assert dropdown.value == "Option 2"
        assert dropdown.description == "Choose:"
        assert dropdown.layout.width == "150px"
        assert "styled-dropdown" in dropdown._dom_classes

    def test_dropdown_with_tuples(self):
        """Dropdown supports (label, value) tuples."""
        dropdown = WidgetFactory.dropdown(
            options=[("First", 1), ("Second", 2), ("Third", 3)], value=2
        )
        assert dropdown.value == 2

    def test_checkbox(self):
        """checkbox() creates a styled Checkbox."""
        checkbox = WidgetFactory.checkbox(
            value=True, description="Enable feature", disabled=False, indent=True
        )

        assert isinstance(checkbox, widgets.Checkbox)
        assert checkbox.value is True
        assert checkbox.description == "Enable feature"
        assert checkbox.indent is True
        assert "styled-checkbox" in checkbox._dom_classes

    def test_radio_buttons(self):
        """radio_buttons() creates mutually exclusive checkboxes acting as radio buttons."""
        radios = WidgetFactory.radio_buttons(options=["Red", "Green", "Blue"], i_selected=1)

        assert len(radios) == 3
        assert all(isinstance(r, widgets.Checkbox) for r in radios)
        assert radios[1].value is True

        # Simulate selection change
        radios[0].value = True
        assert radios[0].value is True
        assert radios[1].value is False

    # -------------------------------------------------------------------------
    # Slider & range widgets
    # -------------------------------------------------------------------------
    def test_int_slider(self):
        """int_slider() creates a styled IntSlider."""
        slider = WidgetFactory.int_slider(
            value=50, min_value=0, max_value=100, step=5, description="Volume:"
        )

        assert isinstance(slider, widgets.IntSlider)
        assert slider.value == 50
        assert slider.min == 0
        assert slider.max == 100
        assert slider.step == 5
        assert "styled-slider" in slider._dom_classes

    def test_float_slider(self):
        """float_slider() creates a styled FloatSlider with orientation."""
        slider = WidgetFactory.float_slider(
            value=0.5, min_value=0.0, max_value=1.0, step=0.1, orientation="vertical"
        )

        assert isinstance(slider, widgets.FloatSlider)
        assert slider.orientation == "vertical"

    def test_date_picker(self):
        """date_picker() creates a styled DatePicker."""
        today = date.today()
        picker = WidgetFactory.date_picker(value=today, description="Date:", width="180px")

        assert isinstance(picker, widgets.DatePicker)
        assert picker.value == today
        assert "styled-date-picker" in picker._dom_classes

    @pytest.mark.parametrize("value_type", [int, float])
    def test_progress_bar(self, value_type):
        """progress_bar() creates IntProgress or FloatProgress based on value type."""
        value = 75 if value_type is int else 0.75
        progress = WidgetFactory.progress_bar(
            value=value, min_value=0, max_value=100 if value_type is int else 1.0
        )

        expected = widgets.IntProgress if value_type is int else widgets.FloatProgress
        assert isinstance(progress, expected)
        assert progress.value == value
        assert "styled-progress" in progress._dom_classes

    # -------------------------------------------------------------------------
    # Complex containers & layout widgets
    # -------------------------------------------------------------------------
    def test_tab(self):
        """tab() creates a styled Tab widget."""
        child1 = widgets.Label("Content 1")
        child2 = widgets.Label("Content 2")

        tab = WidgetFactory.tab(
            children=[child1, child2],
            titles=["Tab 1", "Tab 2"],
            width="500px",
            height="300px",
        )

        assert isinstance(tab, widgets.Tab)
        assert len(tab.children) == 2
        assert tab.get_title(0) == "Tab 1"
        assert "styled-tab" in tab._dom_classes

    def test_accordion(self):
        """accordion() creates a styled Accordion with titles."""
        child1 = widgets.Label("Section 1")
        child2 = widgets.Label("Section 2")

        accordion = WidgetFactory.accordion(children=[child1, child2], titles=["First", "Second"])

        assert isinstance(accordion, widgets.Accordion)
        assert len(accordion.children) == 2
        assert accordion.get_title(0) == "First"
        assert "styled-accordion" in accordion._dom_classes

    def test_output_widget(self):
        """output_widget() creates a styled Output."""
        output = WidgetFactory.output_widget(width="400px", height="250px")

        assert isinstance(output, widgets.Output)
        assert output.layout.width == "400px"
        assert output.layout.height == "250px"
        assert "styled-output" in output._dom_classes

    def test_label(self):
        """label() creates an HTML widget styled as a label (with optional emphasis)."""
        label = WidgetFactory.label(value="Important:", emphasis=True)

        assert isinstance(label, widgets.HTML)
        assert label.value == "Important:"
        assert "styled-label" in label._dom_classes
        assert "label-emphasis" in label._dom_classes

    def test_html_widget(self):
        """html_widget() creates a styled HTML widget."""
        html = WidgetFactory.html_widget(
            value="<h1>Title</h1><p>Content</p>", width="100%", height="auto"
        )

        assert isinstance(html, widgets.HTML)
        assert html.value == "<h1>Title</h1><p>Content</p>"
        assert "styled-html" in html._dom_classes

    # -------------------------------------------------------------------------
    # Container methods
    # -------------------------------------------------------------------------
    def test_hbox(self):
        """hbox() creates a styled HBox with gap placeholders inserted between children."""
        child1 = widgets.Label("Child 1")
        child2 = widgets.Label("Child 2")

        hbox = WidgetFactory.hbox(
            children=[child1, child2],
            width="100%",
            gap="10px",
            align_items="center",
        )

        assert isinstance(hbox, widgets.HBox)
        # 2 real children + 1 gap placeholder between them = 3 total
        assert len(hbox.children) == 3
        assert hbox.layout.width == "100%"
        assert hbox.layout.align_items == "center"
        assert "styled-hbox" in hbox._dom_classes

    def test_vbox(self):
        """vbox() creates a styled VBox with gap placeholders inserted between children."""
        child1 = widgets.Label("Child 1")
        child2 = widgets.Label("Child 2")

        vbox = WidgetFactory.vbox(
            children=[child1, child2],
            height="500px",
            gap="5px",
            justify_content="space-between",
        )

        assert isinstance(vbox, widgets.VBox)
        # 2 real children + 1 gap placeholder between them = 3 total
        assert len(vbox.children) == 3
        assert vbox.layout.height == "500px"
        assert vbox.layout.justify_content == "space-between"
        assert "styled-vbox" in vbox._dom_classes

    def test_grid_container(self):
        """grid_container() creates a flex-based grid using HBox."""
        children = [widgets.Label(f"Item {i}") for i in range(6)]

        grid = WidgetFactory.grid_container(children=children, padding="10px", width="600px")

        assert isinstance(grid, widgets.HBox)
        assert grid.layout.display == "flex"
        assert grid.layout.flex_flow == "row wrap"
        assert "styled-grid-container" in grid._dom_classes

    # -------------------------------------------------------------------------
    # Info field helpers
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "factory_method, expected_class",
        [
            (WidgetFactory.info_field_default, "info-field-default"),
            (WidgetFactory.info_field_info, "info-field-info"),
            (WidgetFactory.info_field_success, "info-field-success"),
            (WidgetFactory.info_field_warning, "info-field-warning"),
            (WidgetFactory.info_field_error, "info-field-error"),
            (WidgetFactory.info_field_critical, "info-field-critical"),
            (WidgetFactory.info_field_debug, "info-field-debug"),
        ],
    )
    def test_info_field_variants(self, factory_method, expected_class):
        """All info_field_* helpers apply the correct CSS class."""
        field = factory_method(children=[widgets.Label("Test")], width="300px")

        assert expected_class in field._dom_classes

    # -------------------------------------------------------------------------
    # Overflow & edge-case styling
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("container_factory", [WidgetFactory.hbox, WidgetFactory.vbox])
    def test_overflow_classes(self, container_factory):
        """Containers apply the correct overflow CSS classes when requested."""
        container = container_factory(
            children=[],
            overflow="hidden",
            overflow_x="hidden",
            overflow_y="hidden",
        )

        assert "styled-overflow-hidden" in container._dom_classes
        assert "styled-overflow-x-hidden" in container._dom_classes
        assert "styled-overflow-y-hidden" in container._dom_classes
