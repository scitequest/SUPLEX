"""
Popup logger styling utilities.
"""

import logging
from typing import Any

import ipywidgets as widgets

from .color_utils import get_emphasized_hex_color, hex_to_rgba

logger = logging.getLogger(__name__)


def get_popup_logger_styles(scheme: Any) -> widgets.HTML:
    """
    Generate CSS styles for the SUPLEX popup logger component.

    Creates comprehensive styling for the popup logger including panel animations,
    log entry styling by level (debug, info, warning, error, critical),
    control buttons, scrollbars, and the toggle button states.

    Args:
        scheme: Color scheme object containing layout colors and text styling

    Returns:
        HTML widget containing popup logger CSS styles with zero dimensions
    """
    logger.debug(
        "Generating popup logger styles for scheme: %s",
        getattr(scheme, "NAME", "Unknown"),
    )

    try:
        css_content = f"""
        <style>
        /* Panel Animation */
        .popup-panel-override {{
            animation: popupFadeIn 0.2s ease-out !important;
            transform-origin: top right !important;
        }}
        
        @keyframes popupFadeIn {{
            from {{
                opacity: {scheme.OPACITY.HIDDEN};
                transform: scale(0.95) translateY(-10px);
            }}
            to {{
                opacity: {scheme.OPACITY.FULL};
                transform: scale(1) translateY(0);
            }}
        }}
        
        /* General Container */
        .popup-panel-override {{
            background-color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.BACKGROUND} !important;
            border: 1px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.BORDER} !important;
            border-radius: 12px !important;
            box-shadow: 0 5px 10px {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.SHADOW, scheme.OPACITY.MODERATE)}, 0 0 0 1px {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.GLOW, scheme.OPACITY.BARELY)} !important;
        }}
        .popup-header-override {{
            background-color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.BACKGROUND} !important;
            border-bottom: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LAYOUT_LINE, scheme.OPACITY.SUBTLE)} !important;
        }}
        .popup-log-container-override {{
            background-color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.PANEL} !important;
        }}
        .popup-footer-override {{
            background-color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.BACKGROUND} !important;
            border-top: 1px solid {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LAYOUT_LINE, scheme.OPACITY.SUBTLE)} !important;
        }}
        .popup-panel-override .widget-html-content {{
            background-color: transparent !important;
        }}
        .popup-panel-override .widget-box {{
            background-color: inherit !important;
        }}
        .popup-panel-override .widget-vbox {{
            background-color: inherit !important;
        }}
        .popup-panel-override .widget-hbox {{
            background-color: inherit !important;
        }}

        
        /* Header Title */
        .popup-header-title {{
            color: {scheme.TEXT.COLOR.LOGGER_TITLE} !important;
            font-size: {scheme.TEXT.SIZE.SUB_HEADER} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
            letter-spacing: 0.5px !important;
            font-family: {scheme.TEXT.FONT.SUB_HEADER} !important;
        }}
        
        /* Close Button */
        .popup-close-button {{
            background: none !important;
            border: none !important;
            outline: none !important;
            color: {scheme.TEXT.COLOR.LOGGER_CLOSE_BUTTON} !important;
            cursor: pointer !important;
            transition: color 0.2s ease, opacity 0.2s ease !important;
            font-size: {scheme.TEXT.SIZE.POPUP_LOGGER_CLOSE_ICON} !important;
            line-height: 1 !important;
        }}
        
        .popup-close-button:hover {{
            color: {scheme.TEXT.COLOR.LOGGER_CLOSE_BUTTON} !important;
            opacity: 0.7 !important;
        }}
        .popup-close-button:focus {{
            outline: none !important;
            box-shadow: none !important;
        }}
        
        /* Log Display */
        .popup-log-display {{
            font-family: {scheme.TEXT.FONT.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            line-height: 1.5 !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            word-break: break-all !important;
            overflow-wrap: anywhere !important;
            box-sizing: border-box !important;
            color: {scheme.TEXT.COLOR.LOGGER_LOG_TEXT} !important;
        }}
        
        /* Empty Log State */
        .popup-log-empty {{
            color: {hex_to_rgba(scheme.TEXT.COLOR.LOGGER_LOG_TEXT, scheme.OPACITY.MODERATE)} !important;
            font-style: {scheme.TEXT.STYLE.ITALIC} !important;
            text-align: center !important;
        }}
        
        /* Scrollbar styling - fits the entire logger but is only used for the log container*/
        .popup-log-container-override::-webkit-scrollbar {{
            width: 8px !important;
        }}
        .popup-log-container-override::-webkit-scrollbar-track {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.PANEL, scheme.OPACITY.SUBTLE)} !important;
            border-radius: 4px !important;
        }}
        .popup-log-container-override::-webkit-scrollbar-thumb {{
            background: {hex_to_rgba(scheme.TEXT.COLOR.SUBTLE, scheme.OPACITY.MODERATE)} !important;
            border-radius: 4px !important;
        }}
        .popup-log-container-override::-webkit-scrollbar-thumb:hover {{
            background: {hex_to_rgba(scheme.TEXT.COLOR.SUBTLE, scheme.OPACITY.MEDIUM)} !important;
        }}
        
        /* Individual log entries */
        .popup-log-entry {{
            margin-bottom: 10px !important;
            padding: 10px 10px !important;
            border-radius: 4px !important;
            word-wrap: break-word !important;
            word-break: break-all !important;
            overflow-wrap: anywhere !important;
            transition: all 0.2s ease !important;
        }}
        
        /* Header of log entries - i.e. icon level and timestamp */
        .popup-log-entry-header {{
            display: flex !important;
            align-items: center !important;
            margin-bottom: 2px !important;
        }}
        
        /* Log Level Icon */
        .popup-log-level-icon {{
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
            font-size: {scheme.TEXT.SIZE.LABEL} !important;
        }}
        
        /* Log Timestamp */
        .popup-log-timestamp {{
            color: {scheme.TEXT.COLOR.LOGGER_LOG_TEXT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            margin-left: 5px !important;
            font-family: monospace !important;
        }}
        
        /* Log Message */
        .popup-log-message {{
            color: {scheme.TEXT.COLOR.LOGGER_LOG_TEXT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            line-height: 1.3 !important;
            word-wrap: break-word !important;
            word-break: break-all !important;
            overflow-wrap: anywhere !important;
            margin: 0 !important;
        }}
        
        /* Log colors by level */
        .popup-log-debug {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEBUG, scheme.OPACITY.FAINT)} !important;
            border-left: 3px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEBUG} !important;
        }}
        .popup-log-debug .popup-log-level-icon {{
            color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEBUG} !important;
        }}
        
        .popup-log-info {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.INFO, scheme.OPACITY.FAINT)} !important;
            border-left: 3px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.INFO} !important;
        }}
        .popup-log-info .popup-log-level-icon {{
            color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.INFO} !important;
        }}
        
        .popup-log-warning {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.WARNING, scheme.OPACITY.FAINT)} !important;
            border-left: 3px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.WARNING} !important;
        }}
        .popup-log-warning .popup-log-level-icon {{
            color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.WARNING} !important;
        }}
        
        .popup-log-error {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.ERROR, scheme.OPACITY.FAINT)} !important;
            border-left: 3px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.ERROR} !important;
        }}
        .popup-log-error .popup-log-level-icon {{
            color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.ERROR} !important;
        }}
        
        .popup-log-critical {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.CRITICAL, scheme.OPACITY.SUBTLE)} !important;
            border-left: 3px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.CRITICAL} !important;
        }}
        .popup-log-critical .popup-log-level-icon {{
            color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.CRITICAL} !important;
        }}
        
        .popup-log-default {{
            background: {hex_to_rgba(scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEFAULT, scheme.OPACITY.FAINT)} !important;
            border-left: 3px solid {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEFAULT} !important;
        }}
        .popup-log-default .popup-log-level-icon {{
            color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.LOG_LEVEL.DEFAULT} !important;
        }}
        
        /* Log Entry Hover Effects */
        .popup-log-entry:hover {{
            background: {hex_to_rgba(scheme.TEXT.COLOR.SUBTLE, scheme.OPACITY.BARELY)} !important;
            transform: translateX(2px) !important;
            transition: all 0.2s ease !important;
        }}
        
        /* Footer */
        
        /* Dropdown Styling */
        .popup-panel-override .widget-dropdown select {{
            height: 100% !important;
            background-color: {scheme.LAYOUT_COLOR.POPUP_LOGGER.PANEL} !important;
            border: 1px solid {hex_to_rgba(scheme.TEXT.COLOR.SUBTLE, scheme.OPACITY.SUBTLE)} !important;
            border-radius: 3px !important;
            color: {scheme.TEXT.COLOR.LOGGER_LOG_TEXT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            transition: border-color 0.2s ease !important;
        }}
        
        .popup-panel-override .widget-dropdown select:hover {{
            border-color: {hex_to_rgba(scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS, scheme.OPACITY.MODERATE)} !important;
        }}
        
        /* Control buttons at bottom of footer */
        .popup-button-clear {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} !important;
            border: 1px solid {scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING} !important;
            border-radius: 8px !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.WARNING} !important;
            transition: background-color 0.2s ease !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
        }}
        .popup-button-clear:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.WARNING)} !important;
        }}
        
        .popup-button-copy {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            border: 1px solid {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            border-radius: 8px !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            transition: background-color 0.2s ease !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
        }}
        .popup-button-copy:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS)} !important;
        }}
        
        .popup-button-save {{
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} !important;
            border: 1px solid {scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS} !important;
            border-radius: 8px !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.SUCCESS} !important;
            transition: background-color 0.2s ease !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
        }}
        .popup-button-save:hover {{
            background-color: {get_emphasized_hex_color(scheme.LAYOUT_COLOR.WIDGET.BUTTON.SUCCESS)} !important;
        }}

        /* Message Counter */
        .popup-message-counter {{
            color: {scheme.TEXT.COLOR.SUBTLE} !important;
            font-size: {scheme.TEXT.SIZE.LABEL} !important;
            font-weight: {scheme.TEXT.WEIGHT.MEDIUM} !important;
            margin: 0 !important;
            font-family: {scheme.TEXT.FONT.LABEL} !important;
            opacity: {scheme.OPACITY.MEDIUM} !important;
            transition: opacity 0.2s ease !important;
        }}
        .popup-message-counter:hover {{
            opacity: {scheme.OPACITY.FULL} !important;
        }}
        
        /* Activate logger button */
        
        /* Normal state */
        .popup-toggle-button-normal {{
            border: 1px solid {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.DEFAULT} !important;
            border-radius: 8px !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.DEFAULT} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            overflow-y: hidden !important;
        }}
        /* Unread state */
        .popup-toggle-button-unread {{
            border: 1px solid {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            background-color: {scheme.LAYOUT_COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            border-radius: 8px !important;
            color: {scheme.TEXT.COLOR.WIDGET.BUTTON.EMPHASIS} !important;
            font-size: {scheme.TEXT.SIZE.DEFAULT} !important;
            overflow-y: hidden !important;
            overflow-x: hidden !important;
        }}


        /* This prevents unnecessary scrollbars */
        .popup-panel-override *,
        .popup-panel-override *::before,
        .popup-panel-override *::after,
        .popup-toggle-button-normal,
        .popup-toggle-button-unread,
        .popup-toggle-button-normal::before,
        .popup-toggle-button-normal::after,
        .popup-toggle-button-unread::before,
        .popup-toggle-button-unread::after {{
            box-sizing: border-box !important;
        }}
        </style>
        """

        style_widget = widgets.HTML(
            value=css_content, layout=widgets.Layout(width="0px", height="0px")
        )

        logger.debug("Successfully generated popup logger styles")
        return style_widget

    except Exception as e:
        logger.error("Failed to generate popup logger styles: %s", e, exc_info=True)
        return widgets.HTML(
            value="<style>/* Error loading popup logger styles */</style>",
            layout=widgets.Layout(width="0px", height="0px"),
        )
