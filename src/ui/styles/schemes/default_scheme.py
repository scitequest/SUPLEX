from ui.styles.resources.resources_constants import (
    DEFAULT_SUPLEX_ICON_PATH,
    DEFAULT_MARTIN_ICON_PATH,
    GITHUB_SVG,
    X_SVG,
)


class DEFAULT_SCHEME:
    NAME = "Default"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            HEADER = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            SUB_HEADER = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            SUB_SUB_HEADER = (
                "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            )
            DEFAULT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            # i.e. smaller info text
            LABEL = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

        class SIZE:
            MAIN_TITLE = "40px"
            HEADER = "30px"
            SUB_HEADER = "14px"
            SUB_SUB_HEADER = "13px"
            DEFAULT = "12px"
            LABEL = "10px"

            POPUP_LOGGER_CLOSE_ICON = "15px"

        class WEIGHT:
            BOLD = "700"
            MEDIUM = "500"
            DEFAULT = "400"
            LIGHT = "300"

        class STYLE:
            DEFAULT = "normal"
            ITALIC = "italic"
            OBLIQUE = "oblique"

        class COLOR:
            MAIN_TITLE = "#1a1a1a"  # Dark but not black - easier on eyes
            HEADER = "#2d3748"  # Dark gray - works on light backgrounds
            SUB_HEADER = "#4a5568"  # Medium gray - balanced
            SUB_SUB_HEADER = "#718096"  # Lighter - for less important text
            DEFAULT = "#2d3748"  # Standard text color
            LABEL = "#718096"  # For small labels

            LOGGER_TITLE = "#f7fafc"  # Near white - good on dark backgrounds
            LOGGER_LOG_TEXT = "#e2e8f0"  # Light gray - comfortable to read
            LOGGER_CLOSE_BUTTON = "#cbd5e0"  # Medium gray - not too bright

            EMPHASIZE = "#3182ce"  # Modern blue - works everywhere
            SUBTLE = "#a0aec0"  # Neutral gray
            MUTED = "#cbd5e0"  # Very light gray
            HYPERLINK = "#3182ce"  # Same as emphasize

            LIGHT = "#ffffff"  # Pure white
            LIGHT_ALT = "#f7fafc"  # Very light gray-white

            # Navigator Text Colors
            NAVIGATOR_ARROW = "#ffffff"  # Arrow text
            NAVIGATOR_STEP = "#ffffff"  # Step text (adjusted per background)

            class NAVIGATOR:
                ARROW = "#ffffff"  # Arrow text
                STEP = "#ffffff"  # Step text (adjusted per background)

            class INFO_FIELD:
                DEFAULT = "#2d3748"
                INFO = "#2d3748"
                SUCCESS = "#2d3748"
                WARNING = "#2d3748"
                ERROR = "#ffffff"
                CRITICAL = "#ffffff"
                DEBUG = "#2d3748"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#ffffff"
                    DEFAULT = "#2d3748"  # Dark text
                    EMPHASIS = "#ffffff"  # White text on colored background

                    SUCCESS = "#ffffff"  # White text
                    DANGER = "#ffffff"  # White text
                    WARNING = "#1a1a1a"  # Dark text on yellow/orange background

                    # Options may be used as a color palette to signify different options from a range
                    OPTIONS_LIGHT = "#4a5568"  # Dark for light buttons
                    OPTIONS_DARK = "#ffffff"  # Light for dark buttons

                    INACTIVE = "#a0aec0"  # Gray for inactive buttons

                class INPUT:
                    DEFAULT = "#2d3748"
                    DISABLED = "#a0aec0"
                    PLACEHOLDER = "#9ca3af"

                class TAB:
                    TITLE = "#000000"
                    BODY = "#000000"

                ACCORDION = "#000000"
                OUTPUT = "#2d3748"
                DROPDOWN = "#000000"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#f8fafc"  # Very light gray-blue
        HEADER = "#4299e1"  # Beautiful, modern blue
        HEADER_GRADIENT = "#42b9e1"
        BODY = "#ffffff"  # Pure white
        CONTRAST = "#ffffff"

        class NAVIGATOR:
            BACKGROUND = "#1a202c"  # Container background
            PANEL = "#2d3748"  # Step container background
            BORDER = "#4a5568"  # Border
            SHADOW = "#000000"  # Shadow
            GLOW = "#63b3ed"  # Glow effects

            class STEP:
                COMPLETED = "#48bb78"  # Green
                ACTIVE = "#ffffff"  # White
                AVAILABLE = "#ed8936"  # Orange
                LOCKED = "#4a5568"  # Gray

        class POPUP_LOGGER:
            BACKGROUND = "#1a202c"  # Dark blue-gray
            PANEL = "#2d3748"  # Slightly lighter for contrast
            BORDER = "#4a5568"  # Visible gray tone
            SHADOW = "#000000"  # Black for shadows
            GLOW = "#63b3ed"  # Light blue for glow effect

            # Line color inbetween logger layout elements
            LAYOUT_LINE = "#4a5568"  # Visible separator lines
            # Line color inbetween log messages
            LOG_LINE = "#374151"  # More subtle separator lines

            class LOG_LEVEL:
                DEFAULT = "#a0aec0"  # Neutral gray
                INFO = "#4299e1"  # Beautiful blue
                SUCCESS = "#48bb78"  # Clear green
                WARNING = "#ed8936"  # Warm orange
                ERROR = "#f56565"  # Clear red
                CRITICAL = "#e53e3e"  # Dark red
                DEBUG = "#9f7aea"  # Purple/violet

        class INFO_FIELD:
            DEFAULT = "#cbccce"  # light gray
            INFO = "#bee3f8"  # Light blue
            SUCCESS = "#c6f6d5"  # Light green
            WARNING = "#fbd38d"  # Light orange
            ERROR = "#fed7d7"  # Light red
            CRITICAL = "#fc8181"  # Medium red
            DEBUG = "#d6bcfa"  # Light purple

        class WIDGET:
            class BUTTON:
                DEFAULT = "#e2e8f0"  # Neutral gray
                EMPHASIS = "#3182ce"  # Primary blue
                SUCCESS = "#38a169"  # Modern green
                DANGER = "#e53e3e"  # Modern red
                WARNING = "#ed8936"  # Warm orange
                # Options may be used as a color palette to signify different options from a range
                OPTIONS_LIGHT = "#63b3ed"  # Light blue
                OPTIONS_DARK = "#2b6cb0"  # Dark blue
                INACTIVE = "#cbd5e0"  # Light gray for inactive buttons

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#ffffff"
                    DISABLED = "#f3f4f6"
                    FOCUS = "#ffffff"

                class BORDER:
                    DEFAULT = "#d1d5db"
                    FOCUS = "#3182ce"
                    ERROR = "#e53e3e"

            class CHECKBOX:
                BACKGROUND = "#ffffff"
                BORDER = "#000000"
                CHECKED = "#000000"
                FOCUS = "#3182ce"

            class SLIDER:
                TRACK = "#e2e8f0"
                HANDLE = "#3182ce"
                RANGE = "#3182ce"

            class PROGRESS:
                BACKGROUND = "#e2e8f0"
                BAR = "#3182ce"

            class TAB:
                BACKGROUND = "#f8fafc"
                ACTIVE = "#3182ce"
                HOVER = "#e2e8f0"
                PANEL = "#ffffff"

            class ACCORDION:
                PANEL = "#bee3f8"
                LINES = "#000000"

            class OUTPUT:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"

            class DROPDOWN:
                BACKGROUND = "#bee3f8"
                BORDER = "#d1d5db"

        class TABLE:
            HEAD = "#ffffff"
            LINES = "#000000"

    class ICON:
        DEFAULT = "💬"
        INFO = "ℹ️"
        SUCCESS = "✅"
        WARNING = "⚠️"
        ERROR = "❌"
        CRITICAL = "🚨"
        DEBUG = "🔍"
        CLEAR = "🗑️"
        STORE = "📋"
        SAVE = "💾"
        CLOSE = "✕"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "›"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🏠"
            DATASET_SELECTION = "📁"
            MODULE_SELECTION = "📁"
            MODULE = "🔧"

        class IMAGE_PATH:
            SUPLEX = DEFAULT_SUPLEX_ICON_PATH
            MARTIN = DEFAULT_MARTIN_ICON_PATH

        class SVG:
            GITHUB = GITHUB_SVG
            X = X_SVG

    class OPACITY:
        FULL = 1.0
        STRONG = 0.9
        MEDIUM = 0.7
        MODERATE = 0.5
        SUBTLE = 0.3
        FAINT = 0.1
        BARELY = 0.05
        HIDDEN = 0.0
