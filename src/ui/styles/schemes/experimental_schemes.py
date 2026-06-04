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


class NATURE_SCHEME:
    NAME = "Nature"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Georgia, 'Times New Roman', serif"
            HEADER = "Georgia, 'Times New Roman', serif"
            SUB_HEADER = "Georgia, 'Times New Roman', serif"
            SUB_SUB_HEADER = "Georgia, 'Times New Roman', serif"
            DEFAULT = "Georgia, 'Times New Roman', serif"
            LABEL = "Georgia, 'Times New Roman', serif"

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
            MAIN_TITLE = "#2d4a22"  # Deep forest green - natural and strong
            HEADER = "#3c5233"  # Medium forest green - readable
            SUB_HEADER = "#4a5a44"  # Sage green - balanced
            SUB_SUB_HEADER = "#5a6855"  # Light sage - for less important text
            DEFAULT = "#3c5233"  # Standard forest green
            LABEL = "#6b7666"  # Muted green-gray

            LOGGER_TITLE = "#f4f1e8"  # Warm cream - good on dark backgrounds
            LOGGER_LOG_TEXT = "#e8e3d3"  # Light beige - comfortable to read
            LOGGER_CLOSE_BUTTON = "#d4c4a8"  # Warm tan - not too bright

            EMPHASIZE = "#8b4513"  # Saddle brown - earthy emphasis
            SUBTLE = "#a0a08a"  # Sage gray
            MUTED = "#c0c0aa"  # Light sage
            HYPERLINK = "#8b6914"  # Dark goldenrod

            LIGHT = "#faf8f0"  # Warm white
            LIGHT_ALT = "#f4f1e8"  # Cream white

            NAVIGATOR_ARROW = "#faf8f0"  # Warm white for arrows
            NAVIGATOR_STEP = "#f4f1e8"  # Cream for step text

            class NAVIGATOR:
                ARROW = "#faf8f0"  # Warm white for arrows
                STEP = "#f4f1e8"  # Cream for step text

            class INFO_FIELD:
                DEFAULT = "#2d4a22"
                INFO = "#3c5233"
                SUCCESS = "#556b2f"
                WARNING = "#8b6914"
                ERROR = "#8b4513"
                CRITICAL = "#a0522d"
                DEBUG = "#6b4423"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#f4f1e8"  # Cream - readable on dark backgrounds
                    DEFAULT = "#2d4a22"  # Dark forest green
                    EMPHASIS = "#faf8f0"  # Cream white on colored background
                    SUCCESS = "#faf8f0"  # Cream white text
                    DANGER = "#faf8f0"  # Cream white text
                    WARNING = "#2d4a22"  # Dark green text on yellow/orange background
                    OPTIONS_LIGHT = "#3c5233"  # Dark for light buttons
                    OPTIONS_DARK = "#faf8f0"  # Light for dark buttons
                    INACTIVE = "#8a9a7a"  # Muted green for inactive buttons

                class INPUT:
                    DEFAULT = "#2d4a22"  # Deep forest green for readability
                    DISABLED = "#8a9a7a"  # Muted green for disabled
                    PLACEHOLDER = "#6b7666"  # Muted green-gray for placeholder

                class TAB:
                    TITLE = "#2d4a22"
                    BODY = "#3c5233"

                ACCORDION = "#2d4a22"
                OUTPUT = "#2d4a22"
                DROPDOWN = "#2d4a22"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#f8f6f0"  # Warm off-white
        HEADER = "#8b6914"  # Dark goldenrod
        HEADER_GRADIENT = "#b8941d"
        BODY = "#faf8f0"  # Warm white
        CONTRAST = "#ffffff"

        class NAVIGATOR:
            BACKGROUND = "#8b6914"  # Dark goldenrod
            PANEL = "#b8941d"  # Lighter goldenrod
            BORDER = "#654321"  # Dark brown border
            SHADOW = "#2d1f0d"  # Very dark brown
            GLOW = "#daa520"  # Goldenrod glow

            class STEP:
                COMPLETED = "#556b2f"  # Dark olive green - growth/success
                ACTIVE = "#daa520"  # Goldenrod - bright/current
                AVAILABLE = "#cd853f"  # Peru orange - warm invitation
                LOCKED = "#8a7a6a"  # Brownish gray - earth/locked

        class POPUP_LOGGER:
            BACKGROUND = "#2d4a22"  # Deep forest green
            PANEL = "#3c5233"  # Medium forest green
            BORDER = "#5a6855"  # Light sage border
            SHADOW = "#1a2e15"  # Very dark green
            GLOW = "#daa520"  # Goldenrod for glow effect

            LAYOUT_LINE = "#5a6855"  # Visible sage lines
            LOG_LINE = "#4a5a44"  # More subtle sage lines

            class LOG_LEVEL:
                DEFAULT = "#8a9a7a"  # Muted green
                INFO = "#87ceeb"  # Sky blue - natural water color
                SUCCESS = "#90ee90"  # Light green - fresh growth
                WARNING = "#daa520"  # Goldenrod - autumn warning
                ERROR = "#cd5c5c"  # Indian red - natural clay
                CRITICAL = "#a0522d"  # Sienna - earth tone
                DEBUG = "#9370db"  # Medium purple - violet flower

        class INFO_FIELD:
            DEFAULT = "#f4f1e8"  # Cream
            INFO = "#e6f3ff"  # Very light blue
            SUCCESS = "#f0fff0"  # Honeydew
            WARNING = "#fff8dc"  # Cornsilk
            ERROR = "#ffe4e1"  # Misty rose
            CRITICAL = "#ffd6cc"  # Light peach
            DEBUG = "#f3e5f5"  # Lavender blush

        class WIDGET:
            class BUTTON:
                DEFAULT = "#d4c4a8"  # Warm tan
                EMPHASIS = "#8b6914"  # Dark goldenrod
                SUCCESS = "#556b2f"  # Dark olive green
                DANGER = "#a0522d"  # Sienna brown
                WARNING = "#cd853f"  # Peru orange
                OPTIONS_LIGHT = "#daa520"  # Goldenrod
                OPTIONS_DARK = "#654321"  # Dark brown
                INACTIVE = "#c0c0aa"  # Light sage for inactive buttons

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#f4f1e8"  # Cream for input backgrounds
                    DISABLED = "#e8e3d3"  # Light beige for disabled
                    FOCUS = "#faf8f0"  # Warm white when focused

                class BORDER:
                    DEFAULT = "#c0c0aa"  # Light sage border
                    FOCUS = "#8b6914"  # Dark goldenrod for focus
                    ERROR = "#a0522d"  # Sienna for errors

            class CHECKBOX:
                BACKGROUND = "#f4f1e8"  # Cream background
                BORDER = "#8a9a7a"  # Muted green border
                CHECKED = "#556b2f"  # Dark olive green when checked
                FOCUS = "#8b6914"  # Dark goldenrod for focus

            class SLIDER:
                TRACK = "#d4c4a8"  # Warm tan track
                HANDLE = "#8b6914"  # Dark goldenrod handle
                RANGE = "#daa520"  # Goldenrod active range

            class PROGRESS:
                BACKGROUND = "#e8e3d3"  # Light beige background
                BAR = "#556b2f"  # Dark olive green progress bar

            class TAB:
                BACKGROUND = "#f4f1e8"  # Cream background for tab bar
                ACTIVE = "#8b6914"  # Dark goldenrod for active tab
                HOVER = "#e8e3d3"  # Light beige for hover
                PANEL = "#faf8f0"  # Warm white for panel

            class ACCORDION:
                PANEL = "#f0fff0"  # Honeydew green panel
                LINES = "#2d4a22"  # Dark forest green lines

            class OUTPUT:
                BACKGROUND = "#faf8f0"  # Warm white for output
                BORDER = "#c0c0aa"  # Light sage border

            class DROPDOWN:
                BACKGROUND = "#f0fff0"  # Honeydew green background
                BORDER = "#8a9a7a"  # Muted green border

        class TABLE:
            HEAD = "#f0fff0"
            LINES = "#2d4a22"

    class ICON:
        DEFAULT = "🌿"
        INFO = "🌊"
        SUCCESS = "🌱"
        WARNING = "🍂"
        ERROR = "🔥"
        CRITICAL = "⛈️"
        DEBUG = "🔍"
        CLEAR = "🧹"
        STORE = "🗃️"
        SAVE = "🌾"
        CLOSE = "✖"
        FORWARD = "🪶"
        BACKWARD = "🏹"
        SEPARATOR = "🌿"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🏔️"
            DATASET_SELECTION = "🌳"
            MODULE_SELECTION = "🍃"
            MODULE = "⚙️"

        class IMAGE_PATH:
            SUPLEX = DEFAULT_MARTIN_ICON_PATH
            MARTIN = DEFAULT_SUPLEX_ICON_PATH

        class SVG:
            GITHUB = X_SVG
            X = GITHUB_SVG

    class OPACITY:
        FULL = 1.0
        STRONG = 0.9
        MEDIUM = 0.7
        MODERATE = 0.5
        SUBTLE = 0.3
        FAINT = 0.1
        BARELY = 0.05
        HIDDEN = 0.0
