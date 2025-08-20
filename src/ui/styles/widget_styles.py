"""
Widget styling utilities.
"""

import logging
from typing import Any

import ipywidgets as widgets

from ui.styles.color_utils import get_emphasized_hex_color, hex_to_rgba

logger = logging.getLogger(__name__)


def get_widget_styles(scheme: Any) -> widgets.HTML:
    """
    Generate comprehensive CSS styles for all SUPLEX widget components.

    Args:
        scheme: Color scheme object containing layout colors and text styling

    Returns:
        HTML widget containing widget CSS styles with zero dimensions
    """
    logger.debug("Generating widget styles for scheme: %s", scheme.NAME)

    try:
        css_content = f"""
        <style>
        /* Base widget container properties - only for styled widgets */
        .styled-widget {{
            box-sizing: border-box !important;
        }}
        
        /* BUTTON STYLES */
        
        /* Base Button Styling - Target only styled widgets */
        .styled-widget.styled-button,
        .styled-widget .styled-button {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            box-shadow: 0px 0px 0px {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.SHADOW, scheme.OPACITY.SUBTLE)} !important;
            border: 1px solid !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            box-sizing: border-box !important;
            text-align: center !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: hidden !important;
        }}
        
        /* Button Types */
        .styled-widget.styled-button.button-default,
        .styled-widget .styled-button.button-default {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.DEFAULT} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-default button,
        .styled-widget .styled-button.button-default button {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.DEFAULT} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-default:hover,
        .styled-widget .styled-button.button-default:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT} !important;
        }}
        
        .styled-widget.styled-button.button-default button:hover,
        .styled-widget .styled-button.button-default button:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT} !important;
        }}
        
        .styled-widget.styled-button.button-emphasis,
        .styled-widget .styled-button.button-emphasis {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-emphasis button,
        .styled-widget .styled-button.button-emphasis button {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-emphasis:hover,
        .styled-widget .styled-button.button-emphasis:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
        }}
        
        .styled-widget.styled-button.button-emphasis button:hover,
        .styled-widget .styled-button.button-emphasis button:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
        }}
        
        .styled-widget.styled-button.button-success,
        .styled-widget .styled-button.button-success {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.SUCCESS} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-success button,
        .styled-widget .styled-button.button-success button {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.SUCCESS} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-success:hover,
        .styled-widget .styled-button.button-success:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} !important;
        }}
        
        .styled-widget.styled-button.button-success button:hover,
        .styled-widget .styled-button.button-success button:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} !important;
        }}
        
        .styled-widget.styled-button.button-danger,
        .styled-widget .styled-button.button-danger {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.DANGER} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-danger button,
        .styled-widget .styled-button.button-danger button {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.DANGER} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-danger:hover,
        .styled-widget .styled-button.button-danger:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER} !important;
        }}
        
        .styled-widget.styled-button.button-danger button:hover,
        .styled-widget .styled-button.button-danger button:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER} !important;
        }}
        
        .styled-widget.styled-button.button-warning,
        .styled-widget .styled-button.button-warning {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.WARNING} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-warning button,
        .styled-widget .styled-button.button-warning button {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.WARNING} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING, 0.8)} !important;
        }}
        
        .styled-widget.styled-button.button-warning:hover,
        .styled-widget .styled-button.button-warning:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} !important;
        }}
        
        .styled-widget.styled-button.button-warning button:hover,
        .styled-widget .styled-button.button-warning button:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING, 0.1)} !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} !important;
        }}
        
        .styled-widget.styled-button.button-inactive,
        .styled-widget .styled-button.button-inactive {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.INACTIVE} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.INACTIVE} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.INACTIVE, 0.8)} !important;
            cursor: not-allowed !important;
            opacity: 0.6 !important;
        }}
        
        .styled-widget.styled-button.button-inactive button,
        .styled-widget .styled-button.button-inactive button {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.INACTIVE} !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.INACTIVE} !important;
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.INACTIVE, 0.8)} !important;
            cursor: not-allowed !important;
            opacity: 0.6 !important;
        }}
        
        /* INPUT FIELD STYLES */
        
        /* Base Input Styling */
        .styled-widget.styled-input,
        .styled-widget .styled-input {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DEFAULT} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DEFAULT} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.DEFAULT, 0.8)} !important;
            border-radius: 6px !important;
            box-sizing: border-box !important;
            transition: all 0.2s ease !important;
        }}
        
        /* Hide/transparent inner input elements */
        .styled-widget.styled-input input,
        .styled-widget .styled-input input {{
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            font-family: inherit !important;
            font-size: inherit !important;
            color: inherit !important;
            width: 100% !important;
            height: 100% !important;
            padding: 0 5px !important;
            margin: 0 !important;
        }}
        
        /* Focus states */
        .styled-widget.styled-input:focus-within,
        .styled-widget .styled-input:focus-within {{
            outline: none !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS} !important;
            box-shadow: 0 0 0 2px {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS, 0.2)} !important;
        }}
        
        /* Disabled states */
        .styled-widget.styled-input:has(input:disabled),
        .styled-widget .styled-input:has(input:disabled) {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DISABLED} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DISABLED} !important;
            cursor: not-allowed !important;
            opacity: 0.6 !important;
        }}
        
        /* Textarea */
        .styled-widget.styled-textarea,
        .styled-widget .styled-textarea {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DEFAULT} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DEFAULT} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.DEFAULT, 0.8)} !important;
            border-radius: 6px !important;
            box-sizing: border-box !important;
            transition: all 0.2s ease !important;
        }}
        
        .styled-widget.styled-textarea textarea,
        .styled-widget .styled-textarea textarea {{
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            font-family: inherit !important;
            font-size: inherit !important;
            color: inherit !important;
            width: 100% !important;
            height: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            resize: vertical !important;
        }}
        
        .styled-widget.styled-textarea:focus-within,
        .styled-widget .styled-textarea:focus-within {{
            outline: none !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS} !important;
            box-shadow: 0 0 0 2px {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS, 0.2)} !important;
        }}
        
        .styled-widget.styled-textarea:has(textarea:disabled),
        .styled-widget .styled-textarea:has(textarea:disabled) {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DISABLED} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DISABLED} !important;
            cursor: not-allowed !important;
            opacity: 0.6 !important;
        }}
        
        /* DROPDOWN STYLES */
        
        .styled-widget.styled-dropdown,
        .styled-widget .styled-dropdown {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            position: relative !important;
        }}
        
        .styled-widget.styled-dropdown select,
        .styled-widget .styled-dropdown select {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.DROPDOWN} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BACKGROUND} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BORDER, 0.8)} !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}
        
        .styled-widget.styled-dropdown select:focus,
        .styled-widget .styled-dropdown select:focus {{
            outline: none !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BORDER} !important;
            box-shadow: 0 0 0 2px {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BORDER, 0.2)} !important;
        }}
        
        .styled-widget.styled-dropdown select:hover,
        .styled-widget .styled-dropdown select:hover {{
            border-color: {scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BORDER} !important;
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BACKGROUND, 0.05)} !important;
        }}
        
        .styled-widget.styled-dropdown select:disabled,
        .styled-widget .styled-dropdown select:disabled {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DISABLED} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DISABLED} !important;
            cursor: not-allowed !important;
            opacity: 0.6 !important;
        }}
        
        .styled-widget.styled-dropdown select option,
        .styled-widget .styled-dropdown select option {{
            color: {scheme.TEXT.COLOR.WIDGET.DROPDOWN} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.DROPDOWN.BACKGROUND} !important;
            padding: 5px 10px !important;
        }}
        
        /* CHECKBOX STYLES */
        .styled-widget.styled-checkbox input[type="checkbox"],
        .styled-widget .styled-checkbox input[type="checkbox"] {{
            /* Forces Voila to use our CSS */
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
            
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.BORDER, 0.8)} !important;
            border-radius: 3px !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.BACKGROUND} !important;
            width: 16px !important;
            height: 16px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            position: relative !important;

            vertical-align: middle !important;
            margin: 0px 5px 0px 0px !important;
        }}
        
        .styled-widget.styled-checkbox input[type="checkbox"]:checked::before,
        .styled-widget .styled-checkbox input[type="checkbox"]:checked::before {{
            content: "✓" !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            color: {scheme.LAYOUT_COLOR.WIDGET.CHECKBOX.CHECKED} !important;
            font-size: 12px !important;
        }}

        .styled-widget.styled-checkbox label,
        .styled-widget .styled-checkbox label{{
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            cursor: pointer !important;
     
            vertical-align: middle !important;
        }}
        
        
        /* SLIDER STYLES*/

        .styled-widget.styled-slider,
        .styled-widget .styled-slider {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            display: block !important;
            visibility: visible !important;
            justify-content: center;
            padding: 10px !important;
        }}

        .styled-widget.styled-slider .widget-label:empty {{
            display: none !important;
            margin: 0 !important;
        }}
        
        .styled-widget.styled-slider .widget-hslider,
        .styled-widget .styled-slider .widget-hslider,
        .styled-widget.styled-slider .widget-vslider,
        .styled-widget .styled-slider .widget-vslider {{
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }}
        
        /* Track */
        .styled-widget.styled-slider .noUi-target,
        .styled-widget .styled-slider .noUi-target {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.CONTRAST, 0.3)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.CONTRAST, 0.8)} !important;
            border-radius: 4px !important;
            height: 8px !important;
            box-shadow: none !important;
        }}
        
        /* Thumb */
        .styled-widget.styled-slider .noUi-handle,
        .styled-widget .styled-slider .noUi-handle {{
            background: {scheme.LAYOUT_COLOR.WIDGET.SLIDER.HANDLE} !important;
            border: 2px solid {scheme.LAYOUT_COLOR.BACKGROUND} !important;
            border-radius: 50% !important;
            width: 20px !important;
            height: 20px !important;
            cursor: pointer !important;
            outline: none !important;
            top: -7px !important;
            right: -10px !important;
            box-shadow: none !important;
        }}
        
        .styled-widget.styled-slider .noUi-handle:hover,
        .styled-widget .styled-slider .noUi-handle:hover,
        .styled-widget.styled-slider .noUi-handle:focus,
        .styled-widget .styled-slider .noUi-handle:focus {{
            background: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.SLIDER.HANDLE, 0.1)} !important;
            box-shadow: 0 0 0 3px {hex_to_rgba(scheme.LAYOUT_COLOR.HEADER, 0.2)} !important;
        }}
        
        
        .styled-widget.styled-slider .noUi-connect,
        .styled-widget .styled-slider .noUi-connect {{
            background: {scheme.LAYOUT_COLOR.WIDGET.SLIDER.RANGE} !important;
            border-radius: 4px !important;
        }}
        
        /* Slider Readout */
        .styled-widget.styled-slider .widget-readout,
        .styled-widget .styled-slider .widget-readout {{
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DEFAULT} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.DEFAULT, 0.8)} !important;
            border-radius: 4px !important;
            padding: 2px 8px !important;
            /* Using margins in combination with width I tricked the css into positioning the readout correctly, this might not be the best solution.*/
            margin-top: 5px !important;
            margin-left: 10% !important;
            min-width: 80% !important;
            max-width: 80% !important;
            text-align: center !important;
            white-space: nowrap !important;
        }}
        
        .styled-widget.styled-slider .threshold-values {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 10px !important;
            margin-top: 5px !important;
        }}
        
        /* Disabled State */
        .styled-widget.styled-slider[disabled] .noUi-target,
        .styled-widget .styled-slider[disabled] .noUi-target {{
            opacity: 0.5 !important;
            pointer-events: none !important;
        }}
        

        
        /* DATE PICKER STYLES */
        
        .styled-widget.styled-date-picker,
        .styled-widget .styled-date-picker {{
            position: relative !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DEFAULT} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DEFAULT} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.DEFAULT, 0.8)} !important;
            border-radius: 6px !important;
            box-sizing: border-box !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }}
        
        .styled-widget.styled-date-picker input[type="date"] {{
            position: relative !important;
        }}
        
        .styled-widget.styled-date-picker input[type="date"]::-webkit-calendar-picker-indicator {{
            opacity: 0 !important;
            position: absolute !important;
            right: 0 !important;
            width: 20px !important;
            height: 20px !important;
            cursor: pointer !important;
        }}
        
        .styled-widget.styled-date-picker::after {{
            content: "{scheme.ICON.CALENDAR}" !important;
            position: absolute !important;
            right: 5px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            pointer-events: none !important;
            font-size: 16px !important;
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
        }}
        
        .styled-widget.styled-date-picker input,
        .styled-widget .styled-date-picker input {{
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            font-family: inherit !important;
            font-size: inherit !important;
            color: inherit !important;
            width: 100% !important;
            height: 100% !important;
            padding: 0 5px !important;
            margin: 0 !important;
            cursor: pointer !important;
        }}
        
        .styled-widget.styled-date-picker:focus-within,
        .styled-widget .styled-date-picker:focus-within {{
            outline: none !important;
            border-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS} !important;
            box-shadow: 0 0 0 2px {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.INPUT.BORDER.FOCUS, 0.2)} !important;
        }}
        
        .styled-widget.styled-date-picker:has(input:disabled),
        .styled-widget .styled-date-picker:has(input:disabled) {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.INPUT.BACKGROUND.DISABLED} !important;
            color: {scheme.TEXT.COLOR.WIDGET.INPUT.DISABLED} !important;
            cursor: not-allowed !important;
            opacity: 0.6 !important;
        }}
            
        /* PROGRESS BAR STYLES */
        
        .styled-widget.styled-progress,
        .styled-widget .styled-progress {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            overflow: hidden !important;
        }}
        
        .styled-widget.styled-progress .progress,
        .styled-widget .styled-progress .progress {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.PROGRESS.BACKGROUND, 0.8)} !important;
            border-radius: 6px !important;
            overflow: hidden !important;
        }}
        
        .styled-widget.styled-progress .progress-bar,
        .styled-widget .styled-progress .progress-bar {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.PROGRESS.BAR} !important;
            transition: width 0.3s ease !important;
            border-radius: 0 !important;
        }}
        
        /* Bouncing Animation Keyframes */
        @keyframes bouncing-loader {{
            0% {{
                opacity: 1 !important;
                transform: translate3d(0, 0, 0) !important;
            }}
            100% {{
                opacity: 0.1 !important;
                transform: translate3d(0, -20px, 0) !important;
            }}
        }}

        /* TAB STYLES - Optimized for ipywidgets */
        
        .styled-widget.styled-tab,
        .styled-widget .styled-tab {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
        }}
        
        /* Tab Bar Container */
        .styled-widget.styled-tab > .widget-tab,
        .styled-tab > .widget-tab {{
            height: 100% !important;
        }}
        
        /* Tab navigation bar */
        .styled-widget.styled-tab .widget-tab-bar,
        .styled-tab .widget-tab-bar {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.TAB.BACKGROUND} !important;
            border-bottom: 2px solid {hex_to_rgba(scheme.TEXT.COLOR.SUBTLE, 0.3)} !important;
            display: flex !important;
            align-items: stretch !important;
        }}
        
        /* Individual tab buttons */
        .styled-widget.styled-tab .widget-tab-tab,
        .styled-tab .widget-tab-tab {{
            background-color: transparent !important;
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            padding: 10px 20px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            margin: 0 !important;
            outline: none !important;
        }}
        
        /* Tab hover state */
        .styled-widget.styled-tab .widget-tab-tab:hover,
        .styled-tab .widget-tab-tab:hover {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.TAB.HOVER, 0.5)} !important;
            color: {scheme.TEXT.COLOR.EMPHASIZE} !important;
        }}
        
        /* Active/selected tab - multiple selectors for compatibility */
        .styled-widget.styled-tab .widget-tab-tab.mod-active,
        .styled-tab .widget-tab-tab.mod-active,
        .styled-widget.styled-tab .widget-tab-tab[aria-selected="true"],
        .styled-tab .widget-tab-tab[aria-selected="true"],
        .styled-widget.styled-tab .widget-tab-tab.p-mod-current,
        .styled-tab .widget-tab-tab.p-mod-current {{
            color: {scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE} !important;
            border-bottom-color: {scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE} !important;
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE, 0.1)} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
        }}
        
        /* Tab content area */
        .styled-widget.styled-tab .widget-tab-contents,
        .styled-tab .widget-tab-contents {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.TAB.PANEL} !important;
            padding: 0 !important;
            height: calc(100% - 45px) !important; /* Subtract tab bar height */
        }}
        
        /* Ensure proper height for tab children */
        .styled-widget.styled-tab .widget-tab-child,
        .styled-tab .widget-tab-child {{
            height: 100% !important;
            overflow: auto !important;
        }}
        
        /* Additional compatibility for Jupyter Lab */
        .styled-widget.styled-tab .jp-widgets-tab,
        .styled-tab .jp-widgets-tab {{
            height: 100% !important;
        }}
        
        .styled-widget.styled-tab .lm-TabBar-tab,
        .styled-tab .lm-TabBar-tab {{
            background-color: transparent !important;
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            border: none !important;
            padding: 8px 16px !important;
            cursor: pointer !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
        }}
        
        .styled-widget.styled-tab .lm-TabBar-tab:hover,
        .styled-tab .lm-TabBar-tab:hover {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.TAB.HOVER, 0.5)} !important;
        }}
        
        .styled-widget.styled-tab .lm-TabBar-tab.lm-mod-current,
        .styled-tab .lm-TabBar-tab.lm-mod-current {{
            color: {scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE} !important;
            border-bottom: 3px solid {scheme.LAYOUT_COLOR.WIDGET.TAB.ACTIVE} !important;
        }}
        
        /* ACCORDION STYLES */
        /* We use basic HTML structure since it works in any Jupyter application */
        
        .styled-widget.styled-accordion > div > div,
        .styled-widget .styled-accordion > div > div {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.ACCORDION.PANEL} !important;
            color: {scheme.TEXT.COLOR.WIDGET.ACCORDION} !important;
        }}
        
        /* OUTPUT WIDGET STYLES */
        
        .styled-widget.styled-output,
        .styled-widget .styled-output {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.WIDGET.OUTPUT} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.OUTPUT.BACKGROUND} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.OUTPUT.BORDER, 0.8)} !important;
            border-radius: 6px !important;
            overflow: auto !important;
        }}
        
        /* LABEL STYLES */
        
        .styled-widget.styled-label,
        .styled-widget .styled-label {{
            font-family: {scheme.TEXT.FONT.LABEL} !important;
            font-size: {scheme.TEXT.SIZE.LABEL} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.LABEL} !important;
            display: block !important;
            padding: 0px !important;
            margin: 0px !important;
            line-height: 1.0 !important;
        }}
        
        .styled-widget.styled-label.label-emphasis,
        .styled-widget .styled-label.label-emphasis {{
            color: {scheme.TEXT.COLOR.EMPHASIZE} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
        }}
        
        /* HTML WIDGET STYLES */
        
        .styled-widget.styled-html,
        .styled-widget .styled-html {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            line-height: 1.5 !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            hyphens: auto !important;
        }}
        
        .styled-widget.styled-html h1,
        .styled-widget .styled-html h1 {{
            font-family: {scheme.TEXT.FONT.HEADER} !important;
            font-size: {scheme.TEXT.SIZE.HEADER} !important;
            color: {scheme.TEXT.COLOR.HEADER} !important;
            font-weight: {scheme.TEXT.WEIGHT.BOLD} !important;
        }}
        
        .styled-widget.styled-html h2,
        .styled-widget .styled-html h2 {{
            font-family: {scheme.TEXT.FONT.SUB_HEADER} !important;
            font-size: {scheme.TEXT.SIZE.SUB_HEADER} !important;
            color: {scheme.TEXT.COLOR.SUB_HEADER} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
        }}
        
        .styled-widget.styled-html h3,
        .styled-widget .styled-html h3 {{
            font-family: {scheme.TEXT.FONT.SUB_SUB_HEADER} !important;
            font-size: {scheme.TEXT.SIZE.SUB_SUB_HEADER} !important;
            color: {scheme.TEXT.COLOR.SUB_SUB_HEADER} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
        }}
        
        /* Hyperlinks */
        .styled-widget.styled-html a,
        .styled-widget .styled-html a {{
            color: {scheme.TEXT.COLOR.HYPERLINK} !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }}
        
        .styled-widget.styled-html a:hover,
        .styled-widget .styled-html a:hover {{
            text-decoration: underline !important;
            color: {get_emphasized_hex_color(scheme.TEXT.COLOR.HYPERLINK, 0.1)} !important;
        }}
        
        /* CONTAINER STYLES - currently mostly placeholders*/
        
        .styled-widget.styled-box,
        .styled-widget .styled-box {{
            box-sizing: border-box !important;
        }}
        
        .styled-widget.styled-hbox,
        .styled-widget .styled-hbox {{
            box-sizing: border-box !important;
        }}

        .styled-widget.styled-vbox,
        .styled-widget .styled-vbox {{
            box-sizing: border-box !important;
        }}

        /* CSS hidden attributes force the disapperance of the scrollbar */
        .styled-widget.styled-overflow-y-hidden,
        .styled-widget .styled-overflow-y-hidden {{
            overflow-y: hidden !important;
        }}
        
        .styled-widget.styled-overflow-x-hidden,
        .styled-widget .styled-overflow-x-hidden {{
            overflow-x: hidden !important;
        }}
        
        .styled-widget.styled-overflow-hidden,
        .styled-widget .styled-overflow-hidden {{
            overflow: hidden !important;
        }}
        
        /* INFO FIELD STYLES */
        
        .styled-widget.styled-vbox.info-field-default,
        .styled-widget .styled-vbox.info-field-default {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}
        
        .styled-widget.styled-vbox.info-field-info,
        .styled-widget .styled-vbox.info-field-info {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}
        
        .styled-widget.styled-vbox.info-field-success,
        .styled-widget .styled-vbox.info-field-success {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}
        
        .styled-widget.styled-vbox.info-field-warning,
        .styled-widget .styled-vbox.info-field-warning {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.WARNING, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.WARNING, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}
        
        .styled-widget.styled-vbox.info-field-error,
        .styled-widget .styled-vbox.info-field-error {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.ERROR, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.ERROR, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}
        
        .styled-widget.styled-vbox.info-field-critical,
        .styled-widget .styled-vbox.info-field-critical {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}    
        
        .styled-widget.styled-vbox.info-field-debug,
        .styled-widget .styled-vbox.info-field-debug {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG, scheme.OPACITY.FULL)} !important;
            border-radius: 6px !important;
        }}
        </style>
        """

        style_widget = widgets.HTML(
            value=css_content,
            layout=widgets.Layout(width="0px", height="0px", margin="0px"),
        )

        logger.debug("Successfully generated widget styles")
        return style_widget

    except Exception as e:
        logger.error("Failed to generate widget styles: %s", e, exc_info=True)
        return widgets.HTML(
            value="<style>/* Error loading widget styles */</style>",
            layout=widgets.Layout(width="0px", height="0px", margin="0px"),
        )
