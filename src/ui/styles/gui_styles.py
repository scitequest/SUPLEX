"""
GUI styling utilities for SUPLEX application.
"""

import logging
from typing import Any

import ipywidgets as widgets

from .color_utils import get_emphasized_hex_color, hex_to_rgba

logger = logging.getLogger(__name__)


def get_gui_styles(scheme: Any) -> widgets.HTML:
    """
    Generate comprehensive CSS styles for the SUPLEX GUI based on a color scheme.

    Creates a complete CSS stylesheet that styles all major UI components including
    layout containers, info fields, scrollbars, and interactive elements. The CSS
    uses the provided color scheme to ensure consistent theming throughout the
    application.

    Args:
        scheme: Color scheme object containing layout colors, text styling,
                and opacity values for theming

    Returns:
        HTML widget containing the complete CSS stylesheet with zero dimensions
        (invisible but applies global styles)

    """
    logger.debug("Generating GUI styles for scheme: %s", getattr(scheme, "NAME", "Unknown"))

    try:
        # Generate complete CSS content for the SUPLEX interface
        css_content = f"""
        <style> 
        /* Content Container - Root Grid Layout */
        .gui-content-container {{
            display: grid !important;
            grid-template-rows: 1fr !important;
            grid-template-columns: 1fr !important;
            padding: 5px !important;
            height: 95vh !important;
            width: 95vw !important;
            min-height: 560px !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            overflow_y: hidden !important;
            overflow_x: hidden !important;
        }}
        
        /* Main Layout Container - Card Style */
        .gui-main-layout {{
            background: {scheme.LAYOUT_COLOR.BACKGROUND} !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            box-sizing: border-box !important;
            border-radius: 16px !important;
            box-shadow: 2px 2px 3px {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.SHADOW, scheme.OPACITY.SUBTLE)}, 
                        1px 1px 1px {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.SHADOW, scheme.OPACITY.FAINT)} !important;
            overflow: hidden !important;
        }}
        
        /* Content Area */
        .gui-content-area {{
            background-color: {scheme.LAYOUT_COLOR.BODY} !important;
            min-height: 0 !important;
            flex: 1 1 0 !important;
            padding: 5px 5px 5px 5px !important;
            margin: 5px 5px 0 5px !important;
            overflow: hidden !important;
            border-radius: 6px !important;
            width: calc(100% - 10px) !important;
        }}
        
        /* Info Field Container */
        .gui-info-container {{
            margin: 0 !important;
            padding: 10px !important;
            gap: 3px !important;
            overflow_y: hidden !important;
            overflow_x: hidden !important;
            background: {scheme.LAYOUT_COLOR.BACKGROUND} !important;
        }}
        
        /* Info Field Base Styling */
        .gui-info-field {{
            border: 1px solid {scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT} !important;
            border-radius: 6px !important;
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.MODERATE)} !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT} !important;
            display: flex !important;
            align-items: center !important;
            transition: all 0.2s ease !important;
            box-sizing: border-box !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;

            /* Ensure proper positioning and scrolling */
            overflow-x: hidden !important;
            overflow-y: auto !important;
            overflow-wrap: break-word !important;
            word-break: break-word !important;
            hyphens: auto !important;
            padding: 6px 10px !important;
        }}
        
        /* Info Field States - Different visual states for different message types */
        .gui-info-field-default {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.DEFAULT} !important;
        }}
        
        .gui-info-field-info {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.INFO} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.INFO} !important;
        }}
        
        .gui-info-field-success {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.SUCCESS} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.SUCCESS} !important;
        }}
        
        .gui-info-field-warning {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.WARNING, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.WARNING} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.WARNING} !important;
        }}
        
        .gui-info-field-error {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.ERROR, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.ERROR} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.ERROR} !important;
        }}
        
        .gui-info-field-critical {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.CRITICAL} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.CRITICAL} !important;
        }}
        
        .gui-info-field-debug {{
            background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG, scheme.OPACITY.MODERATE)} !important;
            border-color: {scheme.LAYOUT_COLOR.INFO_FIELD.DEBUG} !important;
            color: {scheme.TEXT.COLOR.INFO_FIELD.DEBUG} !important;
        }}

        /* Content Holder - Scrollable content area */
        .gui-content-holder {{
            background-color: {scheme.LAYOUT_COLOR.BODY} !important;
            overflow-y: auto !important;
            overflow-x: auto !important;
            min-height: 0 !important;
            max-height: 100% !important;
            flex: 1 1 0 !important;
            display: flex !important;
            border-radius: 6px !important;
            padding: 5px !important;
        }}

        /* Scrollbar Styling - Custom themed scrollbars */
        .gui-main-layout *::-webkit-scrollbar {{
            width: 8px !important;
        }}
        
        .gui-main-layout *::-webkit-scrollbar-track {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.HEADER, scheme.OPACITY.SUBTLE)} !important;
            border-radius: 4px !important;
        }}
        
        .gui-main-layout *::-webkit-scrollbar-thumb {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.HEADER, scheme.OPACITY.MODERATE)} !important;
            border-radius: 4px !important;
        }}
        
        .gui-main-layout *::-webkit-scrollbar-thumb:hover {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.HEADER, scheme.OPACITY.MEDIUM)} !important;
        }}
        
        /* Global Box Sizing - Makes element sizes predictable */
        .gui-main-layout * {{
            box-sizing: border-box !important;
        }}
        </style>
        """

        # Create invisible HTML widget that applies the styles globally
        style_widget = widgets.HTML(
            value=css_content,
            layout=widgets.Layout(width="0px", height="0px", margin="0px"),
        )

        logger.debug("Successfully generated GUI styles")
        return style_widget

    except Exception as e:
        logger.error("Failed to generate GUI styles: %s", e, exc_info=True)
        # Return empty style widget as fallback
        return widgets.HTML(
            value="<style>/* Error loading styles */</style>",
            layout=widgets.Layout(width="0px", height="0px", margin="0px"),
        )
