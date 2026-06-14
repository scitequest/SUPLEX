from ui.styles.resources.resources_constants import (
    DEFAULT_SUPLEX_ICON_PATH,
    DEFAULT_MARTIN_ICON_PATH,
    GITHUB_SVG,
    X_SVG,
)


# Just for testing purposes
class NIGHT_SCHEME:
    NAME = "Night Mode"

    class TEXT:
        class FONT:
            MAIN_TITLE = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', monospace"
            HEADER = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', monospace"
            SUB_HEADER = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', monospace"
            SUB_SUB_HEADER = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', monospace"
            DEFAULT = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', monospace"
            LABEL = "JetBrains Mono, 'SF Mono', Monaco, 'Cascadia Code', monospace"

        class SIZE:
            MAIN_TITLE = "20px"
            HEADER = "15px"
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
            MAIN_TITLE = "#f0f6ff"  # Light blue-white - easy on eyes in dark mode
            HEADER = "#c2d9ff"  # Light blue - good contrast on dark
            SUB_HEADER = "#9bb5ff"  # Medium blue - balanced
            SUB_SUB_HEADER = "#7c93ff"  # Lighter blue - for less important text
            DEFAULT = "#e8f0ff"  # Standard light text color
            LABEL = "#8a9cff"  # For small labels

            LOGGER_TITLE = "#1a1a2e"  # Dark blue-black - good on light backgrounds
            LOGGER_LOG_TEXT = "#2d2d50"  # Dark blue-gray - comfortable to read
            LOGGER_CLOSE_BUTTON = "#4a4a70"  # Medium blue-gray - not too bright

            EMPHASIZE = "#6c63ff"  # Electric purple - stands out
            SUBTLE = "#5a5a80"  # Neutral blue-gray
            MUTED = "#3e3e60"  # Dark blue-gray
            HYPERLINK = "#7c73ff"  # Bright purple-blue

            LIGHT = "#0f0f23"  # Very dark blue
            LIGHT_ALT = "#1a1a2e"  # Dark blue-black

            NAVIGATOR_ARROW = "#c2d9ff"  # Light blue for arrows
            NAVIGATOR_STEP = "#e8f0ff"  # Light blue-white for step text

            class NAVIGATOR:
                ARROW = "#c2d9ff"  # Light blue for arrows
                STEP = "#e8f0ff"  # Light blue-white for step text

            class INFO_FIELD:
                DEFAULT = "#e8f0ff"
                INFO = "#c2d9ff"
                SUCCESS = "#9bb5ff"
                WARNING = "#ffd93d"
                ERROR = "#ff6b6b"
                CRITICAL = "#ff4757"
                DEBUG = "#a55eea"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#c2d9ff"  # Light blue - readable on dark backgrounds
                    DEFAULT = "#e8f0ff"  # Light text
                    EMPHASIS = "#1a1a2e"  # Dark text on colored background
                    SUCCESS = "#1a1a2e"  # Dark text
                    DANGER = "#ffffff"  # White text
                    WARNING = "#1a1a2e"  # Dark text on yellow/orange background
                    OPTIONS_LIGHT = "#c2d9ff"  # Light for dark buttons
                    OPTIONS_DARK = "#1a1a2e"  # Dark for light buttons
                    INACTIVE = "#5a5a80"  # Blue-gray for inactive buttons

                class INPUT:
                    DEFAULT = "#e8f0ff"  # Light blue-white for readability
                    DISABLED = "#5a5a80"  # Muted blue-gray for disabled
                    PLACEHOLDER = "#8a9cff"  # Medium blue for placeholder text

                class TAB:
                    TITLE = "#f0f6ff"
                    BODY = "#e8f0ff"

                ACCORDION = "#f0f6ff"
                OUTPUT = "#e8f0ff"
                DROPDOWN = "#e8f0ff"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#0f0f23"  # Very dark blue
        HEADER = "#6c63ff"  # Electric purple
        HEADER_GRADIENT = "#9c8fff"
        BODY = "#1a1a2e"  # Dark blue-black
        CONTRAST = "#ffffff"

        class NAVIGATOR:
            BACKGROUND = "#0a0a1a"  # Very dark blue-black
            PANEL = "#1a1a2e"  # Dark blue-black
            BORDER = "#3e3e60"  # Blue-gray border
            SHADOW = "#000000"  # Black shadow
            GLOW = "#6c63ff"  # Electric purple glow

            class STEP:
                COMPLETED = "#00d4aa"  # Cyan-green - success
                ACTIVE = "#6c63ff"  # Electric purple - current
                AVAILABLE = "#ffd93d"  # Bright yellow - next
                LOCKED = "#3e3e60"  # Dark blue-gray - locked

        class POPUP_LOGGER:
            BACKGROUND = "#0a0a1a"  # Very dark blue-black
            PANEL = "#1a1a2e"  # Slightly lighter dark blue
            BORDER = "#3e3e60"  # Visible blue-gray tone
            SHADOW = "#000000"  # Black for shadows
            GLOW = "#6c63ff"  # Electric purple for glow effect

            LAYOUT_LINE = "#3e3e60"  # Visible separator lines
            LOG_LINE = "#2d2d50"  # More subtle separator lines

            class LOG_LEVEL:
                DEFAULT = "#8a9cff"  # Light blue
                INFO = "#7c73ff"  # Purple-blue
                SUCCESS = "#00d4aa"  # Cyan-green
                WARNING = "#ffd93d"  # Bright yellow
                ERROR = "#ff6b6b"  # Coral red
                CRITICAL = "#ff4757"  # Bright red
                DEBUG = "#a55eea"  # Purple

        class INFO_FIELD:
            DEFAULT = "#1a1a2e"  # Dark blue-black
            INFO = "#2a2a50"  # Dark blue
            SUCCESS = "#1a3d35"  # Dark green
            WARNING = "#3d3d1a"  # Dark yellow
            ERROR = "#3d1a1a"  # Dark red
            CRITICAL = "#501a1a"  # Darker red
            DEBUG = "#2e1a3d"  # Dark purple

        class WIDGET:
            class BUTTON:
                DEFAULT = "#3e3e60"  # Dark blue-gray
                EMPHASIS = "#6c63ff"  # Electric purple
                SUCCESS = "#00d4aa"  # Cyan-green
                DANGER = "#ff6b6b"  # Coral red
                WARNING = "#ffd93d"  # Bright yellow
                OPTIONS_LIGHT = "#7c73ff"  # Light purple
                OPTIONS_DARK = "#3e2aa0"  # Dark purple
                INACTIVE = "#2d2d50"  # Dark blue-gray for inactive buttons

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#2d2d50"  # Dark blue-gray for input fields
                    DISABLED = "#1a1a2e"  # Even darker for disabled
                    FOCUS = "#3e3e60"  # Slightly lighter when focused

                class BORDER:
                    DEFAULT = "#5a5a80"  # Medium blue-gray border
                    FOCUS = "#6c63ff"  # Electric purple for focus
                    ERROR = "#ff6b6b"  # Coral red for errors

            class CHECKBOX:
                BACKGROUND = "#2d2d50"  # Dark blue-gray background
                BORDER = "#5a5a80"  # Medium blue-gray border
                CHECKED = "#6c63ff"  # Electric purple when checked
                FOCUS = "#7c73ff"  # Light purple for focus

            class SLIDER:
                TRACK = "#3e3e60"  # Dark blue-gray track
                HANDLE = "#6c63ff"  # Electric purple handle
                RANGE = "#7c73ff"  # Light purple active range

            class PROGRESS:
                BACKGROUND = "#2d2d50"  # Dark blue-gray background
                BAR = "#6c63ff"  # Electric purple progress bar

            class TAB:
                BACKGROUND = "#1a1a2e"  # Dark background for tab bar
                ACTIVE = "#6c63ff"  # Electric purple for active tab
                HOVER = "#3e3e60"  # Blue-gray for hover
                PANEL = "#2d2d50"  # Slightly lighter for panel

            class ACCORDION:
                PANEL = "#2a2a50"  # Dark blue panel
                LINES = "#f0f6ff"  # Light blue lines

            class OUTPUT:
                BACKGROUND = "#1a1a2e"  # Dark background for output
                BORDER = "#3e3e60"  # Blue-gray border

            class DROPDOWN:
                BACKGROUND = "#2a2a50"  # Dark blue background
                BORDER = "#5a5a80"  # Medium blue-gray border

        class TABLE:
            HEAD = "#2a2a50"
            LINES = "#f0f6ff"

    class ICON:
        DEFAULT = "⚡"
        INFO = "🔮"
        SUCCESS = "🎯"
        WARNING = "⚡"
        ERROR = "💥"
        CRITICAL = "🔴"
        DEBUG = "🔬"
        CLEAR = "🚀"
        STORE = "💻"
        SAVE = "💿"
        CLOSE = "❌"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "⟫"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🔧"
            DATASET_SELECTION = "🔧"
            MODULE_SELECTION = "🔧"
            MODULE = "📁"

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