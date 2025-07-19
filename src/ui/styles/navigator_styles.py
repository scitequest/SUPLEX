"""
Navigator styling utilities.
"""

import logging
from typing import Any

import ipywidgets as widgets

from .color_utils import get_emphasized_hex_color, hex_to_rgba

logger = logging.getLogger(__name__)


def get_navigator_styles(scheme: Any) -> widgets.HTML:
    """
    Generate CSS styles for the SUPLEX navigation breadcrumb component.

    Creates styling for navigation steps, arrow buttons, and different states
    (completed, active, available, locked) with animations and hover effects.

    Args:
        scheme: Color scheme object containing layout colors and text styling

    Returns:
        HTML widget containing navigator CSS styles with zero dimensions
    """
    logger.debug(
        "Generating navigator styles for scheme: %s", getattr(scheme, "NAME", "Unknown")
    )

    try:
        css_content = f"""
        <style>
        /* Container Styling */
        .slim-breadcrumb-container {{
            background: linear-gradient(135deg, {scheme.LAYOUT_COLOR.NAVIGATOR.BACKGROUND} 0%, {scheme.LAYOUT_COLOR.NAVIGATOR.PANEL} 100%) !important;
            border-radius: 6px !important;
            padding: 4px 20px !important;
            margin: 0px 10px !important;
            height: 45px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 8px !important;
            color: {scheme.TEXT.COLOR.NAVIGATOR.STEP} !important;
            border: 1px solid {scheme.LAYOUT_COLOR.NAVIGATOR.BORDER} !important;
            box-shadow: 0 2px 3px {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.SHADOW, scheme.OPACITY.MODERATE)}!important;
            overflow_y: hidden !important;
            overflow_x: hidden !important;
        }}
        
        /* Navigation Arrow Buttons */
        .nav-arrow {{
            border-radius: 50% !important;
            border: 1px solid {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.SUBTLE)} !important;
            background: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.FAINT)} !important;
            color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.MEDIUM)} !important;
            font-weight: {scheme.TEXT.WEIGHT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            transition: all 0.2s ease !important;
            padding: 0 !important;
            margin: 0 !important;
            flex-shrink: 0 !important;
        }}
        
        .nav-arrow:hover {{
            background: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.SUBTLE)} !important;
            color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.STRONG)} !important;
            border-color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.MODERATE)} !important;
            transform: scale(1.05) !important;
        }}
        
        .nav-arrow:disabled {{
            background: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.BARELY)} !important;
            border-color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.FAINT)} !important;
            color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.SUBTLE)} !important;
            cursor: not-allowed !important;
            opacity: {scheme.OPACITY.MODERATE} !important;
        }}
        
        .nav-arrow:disabled:hover {{
            transform: none !important;
            background: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.BARELY)} !important;
            color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.SUBTLE)} !important;
            border-color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.ARROW, scheme.OPACITY.FAINT)} !important;
        }}
        
        .nav-back {{
            margin-right: 5px !important;
        }}
        
        .nav-forward {{
            margin-left: 5px !important;
        }}
        
        /* Breadcrumb Steps Container */
        .step-breadcrumb-container {{
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            flex: 1 !important;
            justify-content: center !important;
            padding: 0 15px !important;
            overflow: hidden !important;
        }}
        
        /* Individual Steps - Button Styling */
        .step-item {{
            border: none !important;
            border-radius: 4px !important;
            font-size: {scheme.TEXT.SIZE.SUB_HEADER} !important;
            font-family: {scheme.TEXT.FONT.SUB_HEADER} !important;
            transition: all 0.2s !important;
            white-space: nowrap !important;
            cursor: default !important;
            padding: 0px 5px !important;
            margin: 0 !important;
            outline: none !important;
            justify-content: center !important;
            vertical-align: middle !important;
        }}
        
        .step-item:focus {{
            outline: none !important;
            box-shadow: none !important;
        }}
        
        .step-completed {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.COMPLETED, scheme.OPACITY.STRONG)} !important;
            color: {scheme.TEXT.COLOR.NAVIGATOR.STEP} !important;
            cursor: pointer !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.COMPLETED, scheme.OPACITY.STRONG)} !important;
        }}
        
        .step-completed:hover {{
            background: {scheme.LAYOUT_COLOR.NAVIGATOR.STEP.COMPLETED} !important;
            transform: translateY(-1px) !important;
            border: 1px solid {scheme.LAYOUT_COLOR.NAVIGATOR.STEP.COMPLETED} !important;
        }}
        
        .step-active {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.ACTIVE, scheme.OPACITY.STRONG)} !important;
            color: {scheme.LAYOUT_COLOR.NAVIGATOR.BACKGROUND} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
            box-shadow: 0 0 10px {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.ACTIVE, scheme.OPACITY.MODERATE)} !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.ACTIVE, scheme.OPACITY.STRONG)} !important;
        }}
        
        .step-available {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.AVAILABLE, scheme.OPACITY.STRONG)} !important;
            color: {scheme.LAYOUT_COLOR.NAVIGATOR.BACKGROUND} !important;
            cursor: pointer !important;
            animation: pulse-available 2s infinite !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.AVAILABLE, scheme.OPACITY.STRONG)} !important;
        }}
        
        .step-available:hover {{
            background: {scheme.LAYOUT_COLOR.NAVIGATOR.STEP.AVAILABLE} !important;
            transform: translateY(-1px) !important;
            border: 1px solid {scheme.LAYOUT_COLOR.NAVIGATOR.STEP.AVAILABLE} !important;
        }}
        
        .step-locked {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.LOCKED, scheme.OPACITY.FAINT)} !important;
            color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.STEP, scheme.OPACITY.MODERATE)} !important;
            cursor: not-allowed !important;
            border: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.LOCKED, scheme.OPACITY.FAINT)} !important;
        }}
        
        .step-locked:hover {{
            transform: none !important;
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.NAVIGATOR.STEP.LOCKED, scheme.OPACITY.FAINT)} !important;
        }}
        
        /* Step Separators */
        .step-separator {{
            color: {hex_to_rgba(scheme.TEXT.COLOR.NAVIGATOR.STEP, scheme.OPACITY.MEDIUM)} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            margin: 0 2px !important;
        }}
        
        /* Animations */
        @keyframes pulse-available {{
            0%, 100% {{ opacity: {scheme.OPACITY.FULL}; }}
            50% {{ opacity: {scheme.OPACITY.STRONG}; }}
        }}
        </style>
        """

        style_widget = widgets.HTML(
            value=css_content, layout=widgets.Layout(width="0px", height="0px")
        )

        logger.debug("Successfully generated navigator styles")
        return style_widget

    except Exception as e:
        logger.error("Failed to generate navigator styles: %s", e, exc_info=True)
        return widgets.HTML(
            value="<style>/* Error loading navigator styles */</style>",
            layout=widgets.Layout(width="0px", height="0px"),
        )
