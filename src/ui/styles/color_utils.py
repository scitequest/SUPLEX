import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """
    Convert a hexadecimal color string to RGB tuple.

    Supports both 3-character (#RGB) and 6-character (#RRGGBB) hex formats.
    The hash symbol (#) is optional and will be stripped if present.

    Args:
        hex_color: Hexadecimal color string (e.g., "#FF0000", "RGB", "#RRGGBB")

    Returns:
        RGB tuple with values 0-255, or None if conversion fails

    """
    logger.debug("Converting hex color to RGB: %s", hex_color)

    try:
        # Clean and normalize input
        hex_color = hex_color.lstrip("#").upper()

        if len(hex_color) == 3:
            # #RGB → #RRGGBB expansion
            rgb_tuple = tuple(int(hex_color[i] + hex_color[i], 16) for i in range(3))
            logger.debug("Converted 3-char hex %s to RGB: %s", hex_color, rgb_tuple)
            return rgb_tuple

        elif len(hex_color) == 6:
            # Standard RRGGBB format
            rgb_tuple = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            logger.debug("Converted 6-char hex %s to RGB: %s", hex_color, rgb_tuple)
            return rgb_tuple

        else:
            logger.error(
                "Invalid hex color format: '%s'. Must be 3 or 6 characters.", hex_color
            )
            return None

    except ValueError as e:
        logger.error("Failed to parse hex color '%s': %s", hex_color, e, exc_info=True)
        return None
    except Exception as e:
        logger.error(
            "Unexpected error converting hex color '%s': %s",
            hex_color,
            e,
            exc_info=True,
        )
        return None


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hexadecimal color string.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Uppercase hexadecimal color string with # prefix
    """
    logger.debug("Converting RGB(%d, %d, %d) to hex", r, g, b)

    try:
        # Clamp values to valid range
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        logger.debug("Converted RGB(%d, %d, %d) to hex: %s", r, g, b, hex_color)
        return hex_color

    except Exception as e:
        logger.error(
            "Failed to convert RGB(%s, %s, %s) to hex: %s", r, g, b, e, exc_info=True
        )
        return "#000000"  # Return black as fallback


def get_luminance(r: int, g: int, b: int) -> float:
    """
    Calculate the perceived brightness/luminance of a color.

    Uses the ITU-R BT.601-7 standard formula for calculating luminance
    based on human perception of different color components.

    Formula: L = 0.299*R + 0.587*G + 0.114*B

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Luminance value between 0.0 (black) and 1.0 (white)

    References:
        ITU-R Recommendation BT.601-7 "Studio encoding parameters
        of digital television for standard 4:3 and wide-screen 16:9 aspect ratios"
    """
    logger.debug("Calculating luminance for RGB(%d, %d, %d)", r, g, b)

    try:
        # Clamp values to valid range
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        logger.debug(
            "Calculated luminance: %.3f for RGB(%d, %d, %d)", luminance, r, g, b
        )
        return luminance

    except Exception as e:
        logger.error(
            "Failed to calculate luminance for RGB(%s, %s, %s): %s",
            r,
            g,
            b,
            e,
            exc_info=True,
        )
        return 0.5  # Return middle value as fallback


def darken_hex_color(hex_color: str, factor: float = 0.15) -> str:
    """
    Darken a hexadecimal color by a specified factor.

    Reduces the brightness of each RGB component by multiplying with (1 - factor).
    The resulting color will be darker than the original.

    Args:
        hex_color: Hexadecimal color string to darken
        factor: Darkening factor between 0.0 (no change) and 1.0 (black)

    Returns:
        Darkened hexadecimal color string
    """
    logger.debug("Darkening hex color %s by factor %.2f", hex_color, factor)

    try:
        rgb = hex_to_rgb(hex_color)
        if rgb is None:
            logger.warning("Failed to parse hex color for darkening: %s", hex_color)
            return hex_color  # Return original on error

        r, g, b = rgb

        # Apply darkening factor
        factor = max(0.0, min(1.0, factor))  # Clamp factor to valid range
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        darkened_color = rgb_to_hex(r, g, b)
        logger.debug("Darkened %s to %s", hex_color, darkened_color)
        return darkened_color

    except Exception as e:
        logger.error("Failed to darken color %s: %s", hex_color, e, exc_info=True)
        return hex_color  # Return original on error


def lighten_hex_color(hex_color: str, factor: float = 0.15) -> str:
    """
    Lighten a hexadecimal color by a specified factor.

    Increases the brightness of each RGB component by moving it closer to white.
    The resulting color will be lighter than the original.

    Args:
        hex_color: Hexadecimal color string to lighten
        factor: Lightening factor between 0.0 (no change) and 1.0 (white)

    Returns:
        Lightened hexadecimal color string
    """
    logger.debug("Lightening hex color %s by factor %.2f", hex_color, factor)

    try:
        rgb = hex_to_rgb(hex_color)
        if rgb is None:
            logger.warning("Failed to parse hex color for lightening: %s", hex_color)
            return hex_color  # Return original on error

        r, g, b = rgb

        # Apply lightening factor
        factor = max(0.0, min(1.0, factor))  # Clamp factor to valid range
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        lightened_color = rgb_to_hex(r, g, b)
        logger.debug("Lightened %s to %s", hex_color, lightened_color)
        return lightened_color

    except Exception as e:
        logger.error("Failed to lighten color %s: %s", hex_color, e, exc_info=True)
        return hex_color  # Return original on error


def get_emphasized_hex_color(hex_color: str, emphasis_factor: float = 0.15) -> str:
    """
    Create an emphasized version of a color based on its luminance.

    Automatically determines whether to lighten or darken the color based on
    its perceived brightness. Dark colors are lightened, light colors are darkened.
    This creates better contrast and emphasis in UI elements.

    Args:
        hex_color: Hexadecimal color string to emphasize
        emphasis_factor: Emphasis factor between 0.0 (no change) and 1.0 (maximum change)

    Returns:
        Emphasized hexadecimal color string
    """
    logger.debug(
        "Creating emphasized version of color %s with factor %.2f",
        hex_color,
        emphasis_factor,
    )

    try:
        rgb = hex_to_rgb(hex_color)
        if rgb is None:
            logger.warning("Failed to parse hex color for emphasis: %s", hex_color)
            return hex_color  # Return original on error

        r, g, b = rgb
        luminance = get_luminance(r, g, b)

        # Choose emphasis direction based on luminance
        if luminance > 0.5:
            # Light color -> darken for emphasis
            emphasized_color = darken_hex_color(hex_color, emphasis_factor)
            logger.debug(
                "Light color detected (luminance: %.3f), darkening %s to %s",
                luminance,
                hex_color,
                emphasized_color,
            )
        else:
            # Dark color -> lighten for emphasis
            emphasized_color = lighten_hex_color(hex_color, emphasis_factor)
            logger.debug(
                "Dark color detected (luminance: %.3f), lightening %s to %s",
                luminance,
                hex_color,
                emphasized_color,
            )

        return emphasized_color

    except Exception as e:
        logger.error(
            "Failed to create emphasized color for %s: %s", hex_color, e, exc_info=True
        )
        return hex_color  # Return original on error


def hex_to_rgba(hex_color: str, alpha: float = 0.1) -> str:
    """
    Convert a hexadecimal color to RGBA CSS format with specified transparency.

    Args:
        hex_color: Hexadecimal color string to convert
        alpha: Alpha/transparency value between 0.0 (transparent) and 1.0 (opaque)

    Returns:
        RGBA color string in CSS format (e.g., "rgba(255, 0, 0, 0.5)")
    """
    logger.debug("Converting hex color %s to RGBA with alpha %.2f", hex_color, alpha)

    try:
        rgb = hex_to_rgb(hex_color)
        if rgb is None:
            logger.warning(
                "Failed to parse hex color for RGBA conversion: %s", hex_color
            )
            return f"rgba(0, 0, 0, {alpha})"  # Return black with alpha as fallback

        r, g, b = rgb
        alpha = max(0.0, min(1.0, alpha))  # Clamp alpha to valid range

        rgba_string = f"rgba({r}, {g}, {b}, {alpha})"
        logger.debug("Converted %s to RGBA: %s", hex_color, rgba_string)
        return rgba_string

    except Exception as e:
        logger.error("Failed to convert %s to RGBA: %s", hex_color, e, exc_info=True)
        return f"rgba(0, 0, 0, {alpha})"  # Return black with alpha as fallback
