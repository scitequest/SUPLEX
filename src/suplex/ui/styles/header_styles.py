"""
Header styling utilities
"""

import logging
from typing import Any

import ipywidgets as widgets

from .color_utils import get_emphasized_hex_color, hex_to_rgba

logger = logging.getLogger(__name__)


def get_header_styles(scheme: Any) -> widgets.HTML:
    """
    Generate CSS styles for the SUPLEX application header.

    Creates styling for header layout, logo, title, version display, social icons,
    and the color wheel theme dropdown. Includes responsive design and hover effects.

    Args:
        scheme: Color scheme object containing layout colors and text styling

    Returns:
        HTML widget containing header CSS styles with zero dimensions
    """
    logger.debug("Generating header styles for scheme: %s", getattr(scheme, "NAME", "Unknown"))

    try:
        css_content = f"""
        <style>
        /* Header Container */
        .suplex-header-container {{
            background: linear-gradient(90deg, {scheme.LAYOUT_COLOR.HEADER}, {scheme.LAYOUT_COLOR.HEADER_GRADIENT}) !important;
            transition: all 0.3s ease !important;
            overflow: hidden !important;
        }}
        
        /* Header Layout Sections */
        .header-left-section {{
            flex-shrink: 0 !important;
        }}
        
        .header-right-section {{
            flex-shrink: 0 !important;
        }}
        
        .header-right-bottom-section {{
            flex-shrink: 0 !important;
        }}
        
        /* Logo */
        .header-logo {{
            border-radius: 8px !important;
            overflow: hidden !important;
            transition: transform 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            flex-shrink: 0 !important;
        }}
        
        /* Title */
        .header-title {{
            font-size: {scheme.TEXT.SIZE.MAIN_TITLE} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
            color: {scheme.TEXT.COLOR.MAIN_TITLE} !important;
            font-family: {scheme.TEXT.FONT.MAIN_TITLE} !important;
            letter-spacing: 0.5px !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }}
        
        /* Version */
        .header-version {{
            font-size: {scheme.TEXT.SIZE.LABEL} !important;
            opacity: {scheme.OPACITY.MEDIUM} !important;
            color: {scheme.LAYOUT_COLOR.CONTRAST} !important;
            font-family: {scheme.TEXT.FONT.LABEL} !important;
            transition: opacity 0.2s ease !important;
            text-align: right !important;
            white-space: nowrap !important;
        }}
        
        .header-version:hover {{
            opacity: {scheme.OPACITY.FULL} !important;
        }}
        
        /* Social Icons */
        .header-social-icons {{
            display: flex !important;
            gap: 10px !important; /* Have to force gap here instead of regular code */
            align-items: center !important;
            flex-shrink: 0 !important;
        }}
        
        /* Text color affects vector graphics */
        .social-icon {{
            color: {scheme.LAYOUT_COLOR.CONTRAST} !important;
            opacity: {scheme.OPACITY.MEDIUM} !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-decoration: none !important;
            flex-shrink: 0 !important;
        }}
        
        .social-icon:hover {{
            opacity: {scheme.OPACITY.FULL} !important;
            transform: translateY(-1px) !important;
            color: {scheme.LAYOUT_COLOR.CONTRAST} !important;
        }}
        
        /* Theme Dropdown */
        .header-theme-dropdown-widget {{
            position: relative !important;
            margin: 0 !important;
            flex-shrink: 0 !important;
            overflow: visible !important;
        }}
        
        .header-theme-dropdown-widget .widget-dropdown {{
            width: 22px !important;
            height: 22px !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            position: relative !important;
        }}
        
        .header-theme-dropdown-widget select {{
            width: 22px !important;
            height: 22px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 2px solid {scheme.LAYOUT_COLOR.CONTRAST} !important;
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.BODY, scheme.OPACITY.STRONG)} !important;
            color: transparent !important;
            font-size: 0 !important;
            cursor: pointer !important;
            appearance: none !important;
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            overflow: visible !important;
            position: relative !important;
            
            background: conic-gradient(
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} 0deg 90deg,
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} 90deg 180deg,
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER} 180deg 270deg,
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} 270deg 360deg
            ) !important;
            border: 2px solid {scheme.LAYOUT_COLOR.CONTRAST} !important;
            border-radius: 50% !important;
            box-shadow: 
                inset 0 0 0 1px rgba(0,0,0,0.15),
                0 2px 4px rgba(0,0,0,0.3) !important;
            background-size: cover !important;
        }}
        
        .header-theme-dropdown-widget select:hover {{
            border-color: {scheme.LAYOUT_COLOR.CONTRAST} !important;
            background-color: transparent !important;
            transform: scale(1.05) !important;
            transition: all 0.2s ease !important;
            
            background: conic-gradient(
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} 0deg 90deg,
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} 90deg 180deg,
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DANGER} 180deg 270deg,
                {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} 270deg 360deg
            ) !important;
            border: 2px solid {scheme.LAYOUT_COLOR.CONTRAST} !important;
            border-radius: 0 !important;
            box-shadow: 
                inset 0 0 0 1px rgba(0,0,0,0.2),
                0 3px 6px rgba(0,0,0,0.4) !important;
        }}
        
        .header-theme-dropdown-widget select:focus {{
            outline: none !important;
            border-color: {scheme.LAYOUT_COLOR.CONTRAST} !important;
            border-radius: 0 !important;
            box-shadow: 
                inset 0 0 0 1px rgba(0,0,0,0.2),
                0 3px 6px rgba(0,0,0,0.4) !important;
        }}
        
        /* Dropdown Menu Options */
        .header-theme-dropdown-widget select option {{
            color: {scheme.TEXT.COLOR.DEFAULT} !important;
            background: {scheme.LAYOUT_COLOR.BODY} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
        }}
        
        /* Orient Dropdown menu to the right */
        .header-theme-dropdown-widget:focus-within select,
        .header-theme-dropdown-widget select:focus {{
            transform-origin: top right !important;
        }}
        
        /* Container: Icon Box */
        .widget-hbox.icon-box {{
            flex-shrink: 0 !important;
            overflow: hidden !important;
        }}
        
        /* Container: Version Box */
        .widget-hbox.version-box {{
            flex-shrink: 0 !important;
            overflow: hidden !important;
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .header-right-bottom-section {{
                gap: 8px !important;
            }}
            
            .header-social-icons {{
                gap: 8px !important;
            }}
            
            .header-left-section {{
                gap: 10px !important;
            }}
        }}
        
        /* Prevent any overflow issues */
        .suplex-header-container *,
        .suplex-header-container *::before,
        .suplex-header-container *::after {{
            box-sizing: border-box !important;
        }}
        
        /* Try to prevent any scrollbars in the header */
        .widget-html-content {{
            overflow: visible !important;
        }}
        
        .widget-hbox {{
            overflow-x: hidden !important;
        }}
        
        .widget-vbox {{
            overflow-x: hidden !important;
        }}
        </style>
        """

        style_widget = widgets.HTML(
            value=css_content, layout=widgets.Layout(width="0px", height="0px")
        )

        logger.debug("Successfully generated header styles")
        return style_widget

    except Exception as e:
        logger.error("Failed to generate header styles: %s", e, exc_info=True)
        return widgets.HTML(
            value="<style>/* Error loading header styles */</style>",
            layout=widgets.Layout(width="0px", height="0px"),
        )
