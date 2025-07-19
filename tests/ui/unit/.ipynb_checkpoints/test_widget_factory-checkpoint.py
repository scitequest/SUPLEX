import pytest
from unittest.mock import Mock, patch, MagicMock
import ipywidgets as widgets

from src.ui.widget_factory import WidgetFactory

class TestWidgetFactory:
    def test_button_default(self):
        button = WidgetFactory.button_default(
            description="Test Button",
            disabled=False,
            icon="check",
            tooltip="Test tooltip",
            width="100px",
            height="40px"
        )
        
        assert isinstance(button, widgets.Button)
        assert button.description == "Test Button"
        assert button.disabled == False
        assert button.icon == "check"
        assert button.tooltip == "Test tooltip"
        assert button.layout.width == "100px"
        assert button.layout.height == "40px"
        assert "styled-widget" in button._dom_classes
        assert "styled-button" in button._dom_classes
        assert "button-default" in button._dom_classes
    
    def test_button_with_click_handler(self):
        mock_handler = Mock()
        button = WidgetFactory.button_default(
            description="Click me",
            on_click=mock_handler
        )
        
        button.click()
        mock_handler.assert_called_once()
    
    def test_button_emphasis(self):
        button = WidgetFactory.button_emphasis(description="Important")
        
        assert isinstance(button, widgets.Button)
        assert "button-emphasis" in button._dom_classes
    
    def test_button_success(self):
        button = WidgetFactory.button_success(description="Save")
        
        assert isinstance(button, widgets.Button)
        assert "button-success" in button._dom_classes
    
    def test_button_danger(self):
        button = WidgetFactory.button_danger(description="Delete")
        
        assert isinstance(button, widgets.Button)
        assert "button-danger" in button._dom_classes
    
    def test_button_warning(self):
        button = WidgetFactory.button_warning(description="Caution")
        
        assert isinstance(button, widgets.Button)
        assert "button-warning" in button._dom_classes
    
    def test_toggle_button(self):
        button = WidgetFactory.toggle_button(
            description="Toggle",
            toggled=True
        )
        
        assert isinstance(button, widgets.Button)
        assert button._toggled == True
        assert "button-emphasis" in button._dom_classes
        
        button.click()
        assert button._toggled == False
        assert "button-default" in button._dom_classes
        assert "button-emphasis" not in button._dom_classes
    
    def test_custom_radio_buttons(self):
        buttons = WidgetFactory.custom_radio_buttons(
            number=3,
            description=["Option 1", "Option 2", "Option 3"],
            i_toggled=1
        )
        
        assert len(buttons) == 3
        assert all(isinstance(b, widgets.Button) for b in buttons)
        assert buttons[0].description == "Option 1"
        assert buttons[1].description == "Option 2"
        assert buttons[2].description == "Option 3"
        assert "button-default" in buttons[0]._dom_classes
        assert "button-emphasis" in buttons[1]._dom_classes
        assert "button-default" in buttons[2]._dom_classes
        
        buttons[0].click()
        assert "button-emphasis" in buttons[0]._dom_classes
        assert "button-default" in buttons[1]._dom_classes
    
    def test_custom_radio_buttons_invalid_number(self):
        buttons = WidgetFactory.custom_radio_buttons(number=0)
        assert buttons == []
    
    
    def test_text_input(self):
        text = WidgetFactory.text_input(
            value="initial",
            placeholder="Enter text",
            description="Name:",
            disabled=False,
            width="200px"
        )
        
        assert isinstance(text, widgets.Text)
        assert text.value == "initial"
        assert text.placeholder == "Enter text"
        assert text.description == "Name:"
        assert text.disabled == False
        assert text.layout.width == "200px"
        assert "styled-input" in text._dom_classes
    
    def test_text_input_with_change_handler(self):
        mock_handler = Mock()
        text = WidgetFactory.text_input(
            value="test",
            on_change=mock_handler
        )
        
        text.value = "new value"
        assert mock_handler.called
    
    def test_password_input(self):
        password = WidgetFactory.password_input(
            value="secret",
            placeholder="Enter password",
            description="Password:"
        )
        
        assert isinstance(password, widgets.Password)
        assert password.value == "secret"
        assert password.placeholder == "Enter password"
        assert "styled-input" in password._dom_classes
    
    def test_textarea_input(self):
        textarea = WidgetFactory.textarea_input(
            value="Multi\nline\ntext",
            placeholder="Enter description",
            width="400px",
            height="150px"
        )
        
        assert isinstance(textarea, widgets.Textarea)
        assert textarea.value == "Multi\nline\ntext"
        assert textarea.layout.width == "400px"
        assert textarea.layout.height == "150px"
        assert "styled-textarea" in textarea._dom_classes
    
    def test_number_input_int(self):
        number = WidgetFactory.number_input(
            value=42,
            min_value=0,
            max_value=100,
            step=1,
            description="Count:"
        )
        assert isinstance(number, widgets.BoundedIntText)
        assert number.value == 42
        assert number.min == 0
        assert number.max == 100
        assert number.step == 1
    
    def test_number_input_float(self):
        number = WidgetFactory.number_input(
            value=3.14,
            min_value=0.0,
            max_value=10.0,
            step=0.01,
            description="Value:"
        )
        
        assert isinstance(number, widgets.BoundedFloatText)
        assert number.value == 3.14
        assert number.min == 0.0
        assert number.max == 10.0
        assert number.step == 0.01
    
    def test_dropdown(self):
        dropdown = WidgetFactory.dropdown(
            options=["Option 1", "Option 2", "Option 3"],
            value="Option 2",
            description="Choose:",
            width="150px"
        )
        
        assert isinstance(dropdown, widgets.Dropdown)
        assert dropdown.value == "Option 2"
        assert dropdown.description == "Choose:"
        assert dropdown.layout.width == "150px"
        assert "styled-dropdown" in dropdown._dom_classes
    
    def test_dropdown_with_tuples(self):
        dropdown = WidgetFactory.dropdown(
            options=[("First", 1), ("Second", 2), ("Third", 3)],
            value=2
        )
        
        assert dropdown.value == 2
        assert dropdown.options == (("First", 1), ("Second", 2), ("Third", 3))
    
    def test_checkbox(self):
        checkbox = WidgetFactory.checkbox(
            value=True,
            description="Enable feature",
            disabled=False,
            indent=True
        )
        
        assert isinstance(checkbox, widgets.Checkbox)
        assert checkbox.value == True
        assert checkbox.description == "Enable feature"
        assert checkbox.indent == True
        assert "styled-checkbox" in checkbox._dom_classes
    
    def test_radio_buttons(self):
        radios = WidgetFactory.radio_buttons(
            options=["Red", "Green", "Blue"],
            i_selected=1
        )
        
        assert len(radios) == 3
        assert all(isinstance(r, widgets.Checkbox) for r in radios)
        assert radios[0].description == "Red"
        assert radios[0].value == False
        assert radios[1].value == True
        assert radios[2].value == False
        
        radios[0].value = True
        assert radios[0].value == True
        assert radios[1].value == False
        assert radios[2].value == False
    
    def test_slider_int(self):
        slider = WidgetFactory.slider(
            value=50,
            min_value=0,
            max_value=100,
            step=5,
            description="Volume:"
        )
        
        assert isinstance(slider, widgets.IntSlider)
        assert slider.value == 50
        assert slider.min == 0
        assert slider.max == 100
        assert slider.step == 5
        assert "styled-slider" in slider._dom_classes
    
    def test_slider_float(self):
        slider = WidgetFactory.slider(
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            orientation="vertical"
        )
        
        assert isinstance(slider, widgets.FloatSlider)
        assert slider.value == 0.5
        assert slider.orientation == "vertical"
    
    def test_date_picker(self):
        from datetime import date
        today = date.today()
        
        picker = WidgetFactory.date_picker(
            value=today,
            description="Date:",
            width="180px"
        )
        
        assert isinstance(picker, widgets.DatePicker)
        assert picker.value == today
        assert picker.description == "Date:"
        assert "styled-date-picker" in picker._dom_classes
    
    def test_progress_bar_int(self):
        progress = WidgetFactory.progress_bar(
            value=75,
            min_value=0,
            max_value=100,
            description="Progress:"
        )
        
        assert isinstance(progress, widgets.IntProgress)
        assert progress.value == 75
        assert progress.min == 0
        assert progress.max == 100
        assert "styled-progress" in progress._dom_classes
    
    def test_progress_bar_float(self):
        progress = WidgetFactory.progress_bar(
            value=0.75,
            min_value=0.0,
            max_value=1.0
        )
        
        assert isinstance(progress, widgets.FloatProgress)
        assert progress.value == 0.75
    
    def test_tab(self):
        child1 = widgets.Label("Content 1")
        child2 = widgets.Label("Content 2")
        
        tab = WidgetFactory.tab(
            children=[child1, child2],
            titles=["Tab 1", "Tab 2"],
            width="500px",
            height="300px"
        )
        
        assert isinstance(tab, widgets.Tab)
        assert len(tab.children) == 2
        assert tab.get_title(0) == "Tab 1"
        assert tab.get_title(1) == "Tab 2"
        assert "styled-tab" in tab._dom_classes
    
    def test_accordion(self):
        child1 = widgets.Label("Section 1")
        child2 = widgets.Label("Section 2")
        
        accordion = WidgetFactory.accordion(
            children=[child1, child2],
            titles=["First", "Second"]
        )
        
        assert isinstance(accordion, widgets.Accordion)
        assert len(accordion.children) == 2
        assert accordion.get_title(0) == "First"
        assert accordion.get_title(1) == "Second"
        assert "styled-accordion" in accordion._dom_classes
    
    def test_output_widget(self):
        output = WidgetFactory.output_widget(
            width="400px",
            height="250px"
        )
        
        assert isinstance(output, widgets.Output)
        assert output.layout.width == "400px"
        assert output.layout.height == "250px"
        assert "styled-output" in output._dom_classes
    
    def test_label(self):
        label = WidgetFactory.label(
            value="Important:",
            emphasis=True
        )
        
        assert isinstance(label, widgets.HTML)
        assert label.value == "Important:"
        assert "styled-label" in label._dom_classes
        assert "label-emphasis" in label._dom_classes
    
    def test_html_widget(self):
        html = WidgetFactory.html_widget(
            value="<h1>Title</h1><p>Content</p>",
            width="100%",
            height="auto"
        )
        
        assert isinstance(html, widgets.HTML)
        assert html.value == "<h1>Title</h1><p>Content</p>"
        assert "styled-html" in html._dom_classes
    
    # CONTAINER TESTS
    
    def test_hbox(self):
        child1 = widgets.Label("Child 1")
        child2 = widgets.Label("Child 2")
        
        hbox = WidgetFactory.hbox(
            children=[child1, child2],
            width="100%",
            gap="10px",
            align_items="center"
        )
        
        assert isinstance(hbox, widgets.HBox)
        assert len(hbox.children) == 2
        assert hbox.layout.width == "100%"
        assert hbox.layout.align_items == "center"
        assert "styled-hbox" in hbox._dom_classes
    
    def test_vbox(self):
        child1 = widgets.Label("Child 1")
        child2 = widgets.Label("Child 2")
        
        vbox = WidgetFactory.vbox(
            children=[child1, child2],
            height="500px",
            gap="5px",
            justify_content="space-between"
        )
        
        assert isinstance(vbox, widgets.VBox)
        assert len(vbox.children) == 2
        assert vbox.layout.height == "500px"
        assert vbox.layout.justify_content == "space-between"
        assert "styled-vbox" in vbox._dom_classes
    
    def test_grid_container(self):
        children = [widgets.Label(f"Item {i}") for i in range(6)]
        
        grid = WidgetFactory.grid_container(
            children=children,
            padding="10px",
            width="600px"
        )
        
        assert isinstance(grid, widgets.HBox)
        assert len(grid.children) == 6
        assert grid.layout.display == "flex"
        assert grid.layout.flex_flow == "row wrap"
        assert "styled-grid-container" in grid._dom_classes
    
    def test_info_field_default(self):
        content = widgets.Label("Info message")
        
        field = WidgetFactory.info_field_default(
            children=[content],
            width="300px"
        )
        
        assert isinstance(field, widgets.VBox)
        assert len(field.children) == 1
        assert "info-field-default" in field._dom_classes
    
    def test_info_field_success(self):
        field = WidgetFactory.info_field_success()
        assert "info-field-success" in field._dom_classes
    
    def test_info_field_warning(self):
        field = WidgetFactory.info_field_warning()
        assert "info-field-warning" in field._dom_classes
    
    def test_info_field_error(self):
        field = WidgetFactory.info_field_error()
        assert "info-field-error" in field._dom_classes
    
    def test_hbox_overflow_classes(self):
        hbox = WidgetFactory.hbox(
            children=[],
            overflow="hidden",
            overflow_x="hidden",
            overflow_y="hidden"
        )
        
        assert "styled-overflow-hidden" in hbox._dom_classes
        assert "styled-overflow-x-hidden" in hbox._dom_classes
        assert "styled-overflow-y-hidden" in hbox._dom_classes
    
    def test_vbox_overflow_classes(self):
        vbox = WidgetFactory.vbox(
            children=[],
            overflow="hidden",
            overflow_x="hidden",
            overflow_y="hidden"
        )
        assert "styled-overflow-hidden" in vbox._dom_classes
        assert "styled-overflow-x-hidden" in vbox._dom_classes
        assert "styled-overflow-y-hidden" in vbox._dom_classes