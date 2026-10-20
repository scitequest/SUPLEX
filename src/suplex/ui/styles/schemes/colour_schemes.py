from suplex.ui.styles.resources.resources_constants import (
    BG_SUPLEX_ICON_PATH,
    DEFAULT_MARTIN_ICON_PATH,
    DEFAULT_SUPLEX_ICON_PATH,
    DGLG_SUPLEX_ICON_PATH,
    GITHUB_SVG,
    X_SVG,
)


# Emerald Green Theme
class GREEN_SCHEME:
    NAME = "Emerald Green"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_SUB_HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            DEFAULT = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            LABEL = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

        class SIZE:
            MAIN_TITLE = "28px"
            HEADER = "16px"
            SUB_HEADER = "15px"
            SUB_SUB_HEADER = "14px"
            DEFAULT = "13px"
            LABEL = "11px"
            POPUP_LOGGER_CLOSE_ICON = "15px"

        class WEIGHT:
            BOLD = "700"
            MEDIUM = "600"
            DEFAULT = "400"
            LIGHT = "300"

        class STYLE:
            DEFAULT = "normal"
            ITALIC = "italic"
            OBLIQUE = "oblique"

        class COLOR:
            MAIN_TITLE = "#064e3b"  # Dark emerald
            HEADER = "#065f46"  # Deep green
            SUB_HEADER = "#047857"  # Emerald
            SUB_SUB_HEADER = "#059669"  # Medium emerald
            DEFAULT = "#065f46"  # Deep green
            LABEL = "#6b7280"  # Gray

            LOGGER_TITLE = "#f0fdf4"  # Very light green
            LOGGER_LOG_TEXT = "#dcfce7"  # Light green
            LOGGER_CLOSE_BUTTON = "#bbf7d0"  # Medium light green

            EMPHASIZE = "#10b981"  # Bright emerald
            SUBTLE = "#9ca3af"  # Neutral gray
            MUTED = "#d1d5db"  # Light gray
            HYPERLINK = "#059669"  # Medium emerald

            LIGHT = "#ffffff"  # Pure white
            LIGHT_ALT = "#f9fafb"  # Off white

            NAVIGATOR_ARROW = "#ffffff"
            NAVIGATOR_STEP = "#f0fdf4"

            class NAVIGATOR:
                ARROW = "#ffffff"
                STEP = "#f0fdf4"

            class INFO_FIELD:
                DEFAULT = "#065f46"
                INFO = "#065f46"
                SUCCESS = "#064e3b"
                WARNING = "#92400e"
                ERROR = "#991b1b"
                CRITICAL = "#7f1d1d"
                DEBUG = "#581c87"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#ffffff"
                    DEFAULT = "#065f46"
                    EMPHASIS = "#ffffff"
                    SUCCESS = "#ffffff"
                    DANGER = "#ffffff"
                    WARNING = "#451a03"
                    OPTIONS_LIGHT = "#047857"
                    OPTIONS_DARK = "#ffffff"
                    INACTIVE = "#9ca3af"

                class INPUT:
                    DEFAULT = "#065f46"
                    DISABLED = "#9ca3af"
                    PLACEHOLDER = "#6b7280"

                class TAB:
                    TITLE = "#064e3b"
                    BODY = "#065f46"

                ACCORDION = "#064e3b"
                OUTPUT = "#065f46"
                DROPDOWN = "#065f46"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#f0fdf4"  # Very light green
        HEADER = "#10b981"  # Bright emerald
        HEADER_GRADIENT = "#34d399"
        BODY = "#ffffff"  # Pure white
        CONTRAST = "#581c87"

        class NAVIGATOR:
            BACKGROUND = "#581c87"  # Dark purple
            PANEL = "#6b21a8"  # Deep purple
            BORDER = "#7c3aed"  # Purple
            SHADOW = "#2e1065"  # Very dark purple
            GLOW = "#a78bfa"  # Light purple

            class STEP:
                COMPLETED = "#8b5cf6"  # Medium purple
                ACTIVE = "#a78bfa"  # Light purple
                AVAILABLE = "#fbbf24"  # Amber
                LOCKED = "#6b7280"  # Gray

        class POPUP_LOGGER:
            BACKGROUND = "#581c87"  # Dark purple
            PANEL = "#6b21a8"  # Deep purple
            BORDER = "#7c3aed"  # Purple
            SHADOW = "#2e1065"  # Very dark purple
            GLOW = "#a78bfa"  # Light purple

            LAYOUT_LINE = "#7c3aed"
            LOG_LINE = "#8b5cf6"

            class LOG_LEVEL:
                DEFAULT = "#9ca3af"
                INFO = "#3b82f6"
                SUCCESS = "#10b981"
                WARNING = "#f59e0b"
                ERROR = "#ef4444"
                CRITICAL = "#dc2626"
                DEBUG = "#7c3aed"

        class INFO_FIELD:
            DEFAULT = "#f9fafb"
            INFO = "#dbeafe"
            SUCCESS = "#d1fae5"
            WARNING = "#fef3c7"
            ERROR = "#fee2e2"
            CRITICAL = "#fecaca"
            DEBUG = "#ede9fe"

        class WIDGET:
            class BUTTON:
                DEFAULT = "#f3f4f6"
                EMPHASIS = "#7c3aed"
                SUCCESS = "#059669"
                DANGER = "#dc2626"
                WARNING = "#f59e0b"
                OPTIONS_LIGHT = "#a78bfa"
                OPTIONS_DARK = "#6b21a8"
                INACTIVE = "#e5e7eb"

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#ffffff"
                    DISABLED = "#f9fafb"
                    FOCUS = "#ffffff"

                class BORDER:
                    DEFAULT = "#d1d5db"
                    FOCUS = "#7c3aed"
                    ERROR = "#dc2626"

            class CHECKBOX:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"
                CHECKED = "#7c3aed"
                FOCUS = "#7c3aed"

            class SLIDER:
                TRACK = "#e5e7eb"
                HANDLE = "#7c3aed"
                RANGE = "#7c3aed"

            class PROGRESS:
                BACKGROUND = "#e5e7eb"
                BAR = "#7c3aed"

            class TAB:
                BACKGROUND = "#f9fafb"
                ACTIVE = "#7c3aed"
                HOVER = "#f3f4f6"
                PANEL = "#ffffff"

            class ACCORDION:
                PANEL = "#ede9fe"
                LINES = "#581c87"

            class OUTPUT:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"

            class DROPDOWN:
                BACKGROUND = "#ede9fe"
                BORDER = "#d1d5db"

        class TABLE:
            HEAD = "#ede9fe"
            LINES = "#000000"

    class ICON:
        DEFAULT = "🟣"
        INFO = "💜"
        SUCCESS = "✅"
        WARNING = "⚠️"
        ERROR = "❌"
        CRITICAL = "🚨"
        DEBUG = "🔍"
        CLEAR = "🧹"
        STORE = "💾"
        SAVE = "📁"
        CLOSE = "✖"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "▫"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🔮"
            DATASET_SELECTION = "📊"
            MODULE_SELECTION = "⚙"
            MODULE = "🔧"

        class IMAGE_PATH:
            SUPLEX = DGLG_SUPLEX_ICON_PATH
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


# Sunset Orange Theme
class ORANGE_SCHEME:
    NAME = "Sunset Orange"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Lato, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            HEADER = "Lato, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_HEADER = "Lato, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_SUB_HEADER = "Lato, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            DEFAULT = "Lato, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            LABEL = "Lato, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

        class SIZE:
            MAIN_TITLE = "34px"
            HEADER = "16px"
            SUB_HEADER = "15px"
            SUB_SUB_HEADER = "14px"
            DEFAULT = "13px"
            LABEL = "11px"
            POPUP_LOGGER_CLOSE_ICON = "15px"

        class WEIGHT:
            BOLD = "700"
            MEDIUM = "600"
            DEFAULT = "400"
            LIGHT = "300"

        class STYLE:
            DEFAULT = "normal"
            ITALIC = "italic"
            OBLIQUE = "oblique"

        class COLOR:
            MAIN_TITLE = "#9a3412"  # Dark orange
            HEADER = "#c2410c"  # Deep orange
            SUB_HEADER = "#ea580c"  # Orange
            SUB_SUB_HEADER = "#f97316"  # Medium orange
            DEFAULT = "#c2410c"  # Deep orange
            LABEL = "#6b7280"  # Gray

            LOGGER_TITLE = "#fff7ed"  # Very light orange
            LOGGER_LOG_TEXT = "#fed7aa"  # Light orange
            LOGGER_CLOSE_BUTTON = "#fdba74"  # Medium light orange

            EMPHASIZE = "#ea580c"  # Bright orange
            SUBTLE = "#9ca3af"  # Neutral gray
            MUTED = "#d1d5db"  # Light gray
            HYPERLINK = "#f97316"  # Medium orange

            LIGHT = "#ffffff"  # Pure white
            LIGHT_ALT = "#f9fafb"  # Off white

            NAVIGATOR_ARROW = "#ffffff"
            NAVIGATOR_STEP = "#fff7ed"

            class NAVIGATOR:
                ARROW = "#ffffff"
                STEP = "#fff7ed"

            class INFO_FIELD:
                DEFAULT = "#c2410c"
                INFO = "#1e40af"
                SUCCESS = "#065f46"
                WARNING = "#9a3412"
                ERROR = "#991b1b"
                CRITICAL = "#7f1d1d"
                DEBUG = "#581c87"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#ffffff"
                    DEFAULT = "#c2410c"
                    EMPHASIS = "#ffffff"
                    SUCCESS = "#ffffff"
                    DANGER = "#ffffff"
                    WARNING = "#451a03"
                    OPTIONS_LIGHT = "#ea580c"
                    OPTIONS_DARK = "#ffffff"
                    INACTIVE = "#9ca3af"

                class INPUT:
                    DEFAULT = "#c2410c"
                    DISABLED = "#9ca3af"
                    PLACEHOLDER = "#6b7280"

                class TAB:
                    TITLE = "#9a3412"
                    BODY = "#c2410c"

                ACCORDION = "#9a3412"
                OUTPUT = "#c2410c"
                DROPDOWN = "#c2410c"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#fff7ed"  # Very light orange
        HEADER = "#ea580c"  # Bright orange
        HEADER_GRADIENT = "#fb923c"
        BODY = "#ffffff"  # Pure white
        CONTRAST = "#9a3412"

        class NAVIGATOR:
            BACKGROUND = "#9a3412"  # Dark orange
            PANEL = "#c2410c"  # Deep orange
            BORDER = "#ea580c"  # Orange
            SHADOW = "#7c2d12"  # Very dark orange
            GLOW = "#fb923c"  # Light orange

            class STEP:
                COMPLETED = "#f97316"  # Medium orange
                ACTIVE = "#fb923c"  # Light orange
                AVAILABLE = "#fbbf24"  # Amber
                LOCKED = "#6b7280"  # Gray

        class POPUP_LOGGER:
            BACKGROUND = "#9a3412"  # Dark orange
            PANEL = "#c2410c"  # Deep orange
            BORDER = "#ea580c"  # Orange
            SHADOW = "#7c2d12"  # Very dark orange
            GLOW = "#fb923c"  # Light orange

            LAYOUT_LINE = "#ea580c"
            LOG_LINE = "#f97316"

            class LOG_LEVEL:
                DEFAULT = "#9ca3af"
                INFO = "#3b82f6"
                SUCCESS = "#10b981"
                WARNING = "#ea580c"
                ERROR = "#ef4444"
                CRITICAL = "#dc2626"
                DEBUG = "#8b5cf6"

        class INFO_FIELD:
            DEFAULT = "#f9fafb"
            INFO = "#dbeafe"
            SUCCESS = "#d1fae5"
            WARNING = "#fed7aa"
            ERROR = "#fee2e2"
            CRITICAL = "#fecaca"
            DEBUG = "#ede9fe"

        class WIDGET:
            class BUTTON:
                DEFAULT = "#f3f4f6"
                EMPHASIS = "#ea580c"
                SUCCESS = "#059669"
                DANGER = "#dc2626"
                WARNING = "#c2410c"
                OPTIONS_LIGHT = "#fb923c"
                OPTIONS_DARK = "#c2410c"
                INACTIVE = "#e5e7eb"

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#ffffff"
                    DISABLED = "#f9fafb"
                    FOCUS = "#ffffff"

                class BORDER:
                    DEFAULT = "#d1d5db"
                    FOCUS = "#ea580c"
                    ERROR = "#dc2626"

            class CHECKBOX:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"
                CHECKED = "#ea580c"
                FOCUS = "#ea580c"

            class SLIDER:
                TRACK = "#e5e7eb"
                HANDLE = "#ea580c"
                RANGE = "#ea580c"

            class PROGRESS:
                BACKGROUND = "#e5e7eb"
                BAR = "#ea580c"

            class TAB:
                BACKGROUND = "#f9fafb"
                ACTIVE = "#ea580c"
                HOVER = "#f3f4f6"
                PANEL = "#ffffff"

            class ACCORDION:
                PANEL = "#fed7aa"
                LINES = "#9a3412"

            class OUTPUT:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"

            class DROPDOWN:
                BACKGROUND = "#fed7aa"
                BORDER = "#d1d5db"

        class TABLE:
            HEAD = "#fed7aa"
            LINES = "#000000"

    class ICON:
        DEFAULT = "🟠"
        INFO = "🧡"
        SUCCESS = "✅"
        WARNING = "⚠️"
        ERROR = "❌"
        CRITICAL = "🚨"
        DEBUG = "🔍"
        CLEAR = "🧹"
        STORE = "💾"
        SAVE = "📁"
        CLOSE = "✖"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "▫"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🌅"
            DATASET_SELECTION = "📊"
            MODULE_SELECTION = "⚙"
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


# Turquoise Teal Theme
class TEAL_SCHEME:
    NAME = "Turquoise Teal"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Source Sans Pro, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            HEADER = "Source Sans Pro, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_HEADER = "Source Sans Pro, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_SUB_HEADER = "Source Sans Pro, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            DEFAULT = "Source Sans Pro, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            LABEL = "Source Sans Pro, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

        class SIZE:
            MAIN_TITLE = "29px"
            HEADER = "16px"
            SUB_HEADER = "15px"
            SUB_SUB_HEADER = "14px"
            DEFAULT = "13px"
            LABEL = "11px"
            POPUP_LOGGER_CLOSE_ICON = "15px"

        class WEIGHT:
            BOLD = "700"
            MEDIUM = "600"
            DEFAULT = "400"
            LIGHT = "300"

        class STYLE:
            DEFAULT = "normal"
            ITALIC = "italic"
            OBLIQUE = "oblique"

        class COLOR:
            MAIN_TITLE = "#134e4a"  # Dark teal
            HEADER = "#0f766e"  # Deep teal
            SUB_HEADER = "#0d9488"  # Teal
            SUB_SUB_HEADER = "#14b8a6"  # Medium teal
            DEFAULT = "#0f766e"  # Deep teal
            LABEL = "#6b7280"  # Gray

            LOGGER_TITLE = "#f0fdfa"  # Very light teal
            LOGGER_LOG_TEXT = "#ccfbf1"  # Light teal
            LOGGER_CLOSE_BUTTON = "#99f6e4"  # Medium light teal

            EMPHASIZE = "#0d9488"  # Bright teal
            SUBTLE = "#9ca3af"  # Neutral gray
            MUTED = "#d1d5db"  # Light gray
            HYPERLINK = "#14b8a6"  # Medium teal

            LIGHT = "#ffffff"  # Pure white
            LIGHT_ALT = "#f9fafb"  # Off white

            NAVIGATOR_ARROW = "#ffffff"
            NAVIGATOR_STEP = "#f0fdfa"

            class NAVIGATOR:
                ARROW = "#ffffff"
                STEP = "#f0fdfa"

            class INFO_FIELD:
                DEFAULT = "#0f766e"
                INFO = "#1e40af"
                SUCCESS = "#134e4a"
                WARNING = "#92400e"
                ERROR = "#991b1b"
                CRITICAL = "#7f1d1d"
                DEBUG = "#581c87"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#ffffff"
                    DEFAULT = "#0f766e"
                    EMPHASIS = "#ffffff"
                    SUCCESS = "#ffffff"
                    DANGER = "#ffffff"
                    WARNING = "#451a03"
                    OPTIONS_LIGHT = "#0d9488"
                    OPTIONS_DARK = "#ffffff"
                    INACTIVE = "#9ca3af"

                class INPUT:
                    DEFAULT = "#0f766e"
                    DISABLED = "#9ca3af"
                    PLACEHOLDER = "#6b7280"

                class TAB:
                    TITLE = "#134e4a"
                    BODY = "#0f766e"

                ACCORDION = "#134e4a"
                OUTPUT = "#0f766e"
                DROPDOWN = "#0f766e"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#f0fdfa"  # Very light teal
        HEADER = "#0d9488"  # Bright teal
        HEADER_GRADIENT = "#2dd4bf"
        BODY = "#ffffff"  # Pure white
        CONTRAST = "#134e4a"

        class NAVIGATOR:
            BACKGROUND = "#134e4a"  # Dark teal
            PANEL = "#0f766e"  # Deep teal
            BORDER = "#0d9488"  # Teal
            SHADOW = "#042f2e"  # Very dark teal
            GLOW = "#2dd4bf"  # Light teal

            class STEP:
                COMPLETED = "#14b8a6"  # Medium teal
                ACTIVE = "#2dd4bf"  # Light teal
                AVAILABLE = "#fbbf24"  # Amber
                LOCKED = "#6b7280"  # Gray

        class POPUP_LOGGER:
            BACKGROUND = "#134e4a"  # Dark teal
            PANEL = "#0f766e"  # Deep teal
            BORDER = "#0d9488"  # Teal
            SHADOW = "#042f2e"  # Very dark teal
            GLOW = "#2dd4bf"  # Light teal

            LAYOUT_LINE = "#0d9488"
            LOG_LINE = "#14b8a6"

            class LOG_LEVEL:
                DEFAULT = "#9ca3af"
                INFO = "#3b82f6"
                SUCCESS = "#0d9488"
                WARNING = "#f59e0b"
                ERROR = "#ef4444"
                CRITICAL = "#dc2626"
                DEBUG = "#8b5cf6"

        class INFO_FIELD:
            DEFAULT = "#f9fafb"
            INFO = "#dbeafe"
            SUCCESS = "#ccfbf1"
            WARNING = "#fef3c7"
            ERROR = "#fee2e2"
            CRITICAL = "#fecaca"
            DEBUG = "#ede9fe"

        class WIDGET:
            class BUTTON:
                DEFAULT = "#f3f4f6"
                EMPHASIS = "#0d9488"
                SUCCESS = "#14b8a6"
                DANGER = "#dc2626"
                WARNING = "#f59e0b"
                OPTIONS_LIGHT = "#2dd4bf"
                OPTIONS_DARK = "#0f766e"
                INACTIVE = "#e5e7eb"

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#ffffff"
                    DISABLED = "#f9fafb"
                    FOCUS = "#ffffff"

                class BORDER:
                    DEFAULT = "#d1d5db"
                    FOCUS = "#0d9488"
                    ERROR = "#dc2626"

            class CHECKBOX:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"
                CHECKED = "#0d9488"
                FOCUS = "#0d9488"

            class SLIDER:
                TRACK = "#e5e7eb"
                HANDLE = "#0d9488"
                RANGE = "#0d9488"

            class PROGRESS:
                BACKGROUND = "#e5e7eb"
                BAR = "#0d9488"

            class TAB:
                BACKGROUND = "#f9fafb"
                ACTIVE = "#0d9488"
                HOVER = "#f3f4f6"
                PANEL = "#ffffff"

            class ACCORDION:
                PANEL = "#ccfbf1"
                LINES = "#134e4a"

            class OUTPUT:
                BACKGROUND = "#ffffff"
                BORDER = "#d1d5db"

            class DROPDOWN:
                BACKGROUND = "#ccfbf1"
                BORDER = "#d1d5db"

        class TABLE:
            HEAD = "#ccfbf1"
            LINES = "#134e4a"

    class ICON:
        DEFAULT = "🩵"
        INFO = "💎"
        SUCCESS = "✅"
        WARNING = "⚠️"
        ERROR = "❌"
        CRITICAL = "🚨"
        DEBUG = "🔍"
        CLEAR = "🧹"
        STORE = "💾"
        SAVE = "📁"
        CLOSE = "✖"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "▫"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🏝️"
            DATASET_SELECTION = "📊"
            MODULE_SELECTION = "⚙"
            MODULE = "🔧"

        class IMAGE_PATH:
            SUPLEX = BG_SUPLEX_ICON_PATH
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


# High Contrast Accessible Theme (optimized for color vision deficiencies and low vision)
class HIGH_CONTRAST_SCHEME:
    NAME = "High Contrast Accessible"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_SUB_HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            DEFAULT = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            LABEL = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

        class SIZE:
            MAIN_TITLE = "28px"
            HEADER = "16px"
            SUB_HEADER = "15px"
            SUB_SUB_HEADER = "14px"
            DEFAULT = "13px"
            LABEL = "11px"
            POPUP_LOGGER_CLOSE_ICON = "15px"

        class WEIGHT:
            BOLD = "700"
            MEDIUM = "600"
            DEFAULT = "400"
            LIGHT = "300"

        class STYLE:
            DEFAULT = "normal"
            ITALIC = "italic"
            OBLIQUE = "oblique"

        class COLOR:
            MAIN_TITLE = "#111827"  # Near black
            HEADER = "#1f2937"  # Dark slate
            SUB_HEADER = "#374151"  # Slate gray
            SUB_SUB_HEADER = "#4b5563"  # Medium slate
            DEFAULT = "#1f2937"  # Dark slate
            LABEL = "#6b7280"  # Gray

            LOGGER_TITLE = "#f3f4f6"  # Light gray
            LOGGER_LOG_TEXT = "#e5e7eb"  # Lighter gray
            LOGGER_CLOSE_BUTTON = "#9ca3af"  # Muted gray

            EMPHASIZE = "#2563eb"  # Bright blue
            SUBTLE = "#9ca3af"  # Neutral gray
            MUTED = "#d1d5db"  # Light gray
            HYPERLINK = "#1d4ed8"  # Strong blue

            LIGHT = "#ffffff"  # Pure white
            LIGHT_ALT = "#f8fafc"  # Off white

            NAVIGATOR_ARROW = "#ffffff"
            NAVIGATOR_STEP = "#f3f4f6"

            class NAVIGATOR:
                ARROW = "#ffffff"
                STEP = "#f3f4f6"

            class INFO_FIELD:
                DEFAULT = "#1f2937"
                INFO = "#1e40af"
                SUCCESS = "#166534"
                WARNING = "#92400e"
                ERROR = "#991b1b"
                CRITICAL = "#7f1d1d"
                DEBUG = "#581c87"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#ffffff"
                    DEFAULT = "#1f2937"
                    EMPHASIS = "#ffffff"
                    SUCCESS = "#ffffff"
                    DANGER = "#ffffff"
                    WARNING = "#451a03"
                    OPTIONS_LIGHT = "#374151"
                    OPTIONS_DARK = "#ffffff"
                    INACTIVE = "#9ca3af"

                class INPUT:
                    DEFAULT = "#1f2937"
                    DISABLED = "#9ca3af"
                    PLACEHOLDER = "#6b7280"

                class TAB:
                    TITLE = "#111827"
                    BODY = "#1f2937"

                ACCORDION = "#111827"
                OUTPUT = "#1f2937"
                DROPDOWN = "#1f2937"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#f8fafc"  # Very light slate
        HEADER = "#1e40af"  # Indigo blue
        HEADER_GRADIENT = "#3b82f6"
        BODY = "#ffffff"  # Pure white
        CONTRAST = "#111827"

        class NAVIGATOR:
            BACKGROUND = "#1e3a8a"  # Dark blue
            PANEL = "#1e40af"  # Deep blue
            BORDER = "#3b82f6"  # Blue
            SHADOW = "#1e3a8a"
            GLOW = "#60a5fa"  # Light blue

            class STEP:
                COMPLETED = "#3b82f6"
                ACTIVE = "#60a5fa"
                AVAILABLE = "#fbbf24"  # Amber (high visibility)
                LOCKED = "#6b7280"

        class POPUP_LOGGER:
            BACKGROUND = "#1e3a8a"
            PANEL = "#1e40af"
            BORDER = "#3b82f6"
            SHADOW = "#1e3a8a"
            GLOW = "#60a5fa"

            LAYOUT_LINE = "#3b82f6"
            LOG_LINE = "#60a5fa"

            class LOG_LEVEL:
                DEFAULT = "#9ca3af"
                INFO = "#3b82f6"
                SUCCESS = "#10b981"
                WARNING = "#f59e0b"
                ERROR = "#ef4444"
                CRITICAL = "#dc2626"
                DEBUG = "#8b5cf6"

        class INFO_FIELD:
            DEFAULT = "#f1f5f9"
            INFO = "#dbeafe"
            SUCCESS = "#dcfce7"
            WARNING = "#fef3c7"
            ERROR = "#fee2e2"
            CRITICAL = "#fecaca"
            DEBUG = "#ede9fe"

        class WIDGET:
            class BUTTON:
                DEFAULT = "#f1f5f9"
                EMPHASIS = "#1e40af"
                SUCCESS = "#166534"
                DANGER = "#991b1b"
                WARNING = "#b45309"
                OPTIONS_LIGHT = "#60a5fa"
                OPTIONS_DARK = "#1e40af"
                INACTIVE = "#e5e7eb"

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#ffffff"
                    DISABLED = "#f8fafc"
                    FOCUS = "#ffffff"

                class BORDER:
                    DEFAULT = "#cbd5e1"
                    FOCUS = "#3b82f6"
                    ERROR = "#ef4444"

            class CHECKBOX:
                BACKGROUND = "#ffffff"
                BORDER = "#cbd5e1"
                CHECKED = "#1e40af"
                FOCUS = "#1e40af"

            class SLIDER:
                TRACK = "#e2e8f0"
                HANDLE = "#1e40af"
                RANGE = "#1e40af"

            class PROGRESS:
                BACKGROUND = "#e2e8f0"
                BAR = "#1e40af"

            class TAB:
                BACKGROUND = "#f1f5f9"
                ACTIVE = "#1e40af"
                HOVER = "#f1f5f9"
                PANEL = "#ffffff"

            class ACCORDION:
                PANEL = "#e0e7ff"
                LINES = "#1e3a8a"

            class OUTPUT:
                BACKGROUND = "#ffffff"
                BORDER = "#cbd5e1"

            class DROPDOWN:
                BACKGROUND = "#e0e7ff"
                BORDER = "#cbd5e1"

        class TABLE:
            HEAD = "#e0e7ff"
            LINES = "#1e3a8a"

    class ICON:
        DEFAULT = "⬛"
        INFO = "🔷"
        SUCCESS = "✅"
        WARNING = "⚠️"
        ERROR = "❌"
        CRITICAL = "🚨"
        DEBUG = "🔍"
        CLEAR = "🧹"
        STORE = "💾"
        SAVE = "📁"
        CLOSE = "✖"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "▫"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "📂"
            DATASET_SELECTION = "📊"
            MODULE_SELECTION = "⚙"
            MODULE = "🔧"

        class IMAGE_PATH:
            SUPLEX = DGLG_SUPLEX_ICON_PATH
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


# Blue-Orange Colorblind Safe Theme (blue & amber/orange palette)
class BLUE_ORANGE_SCHEME:
    NAME = "Blue-Orange (Colorblind Safe)"

    class TEXT:
        class FONT:
            MAIN_TITLE = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            SUB_SUB_HEADER = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            DEFAULT = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            LABEL = "Poppins, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

        class SIZE:
            MAIN_TITLE = "28px"
            HEADER = "16px"
            SUB_HEADER = "15px"
            SUB_SUB_HEADER = "14px"
            DEFAULT = "13px"
            LABEL = "11px"
            POPUP_LOGGER_CLOSE_ICON = "15px"

        class WEIGHT:
            BOLD = "700"
            MEDIUM = "600"
            DEFAULT = "400"
            LIGHT = "300"

        class STYLE:
            DEFAULT = "normal"
            ITALIC = "italic"
            OBLIQUE = "oblique"

        class COLOR:
            MAIN_TITLE = "#1e3a8a"  # Dark navy blue
            HEADER = "#1e40af"  # Deep blue
            SUB_HEADER = "#2563eb"  # Blue
            SUB_SUB_HEADER = "#3b82f6"  # Medium blue
            DEFAULT = "#1e40af"  # Deep blue
            LABEL = "#64748b"  # Slate gray

            LOGGER_TITLE = "#f0f9ff"  # Very light blue
            LOGGER_LOG_TEXT = "#bae6fd"  # Light sky blue
            LOGGER_CLOSE_BUTTON = "#7dd3fc"  # Medium light blue

            EMPHASIZE = "#2563eb"  # Bright blue
            SUBTLE = "#64748b"  # Neutral gray
            MUTED = "#cbd5e1"  # Light gray
            HYPERLINK = "#3b82f6"  # Medium blue

            LIGHT = "#ffffff"  # Pure white
            LIGHT_ALT = "#f8fafc"  # Off white

            NAVIGATOR_ARROW = "#ffffff"
            NAVIGATOR_STEP = "#f0f9ff"

            class NAVIGATOR:
                ARROW = "#ffffff"
                STEP = "#f0f9ff"

            class INFO_FIELD:
                DEFAULT = "#1e40af"
                INFO = "#1e40af"
                SUCCESS = "#166534"
                WARNING = "#9a3412"
                ERROR = "#991b1b"
                CRITICAL = "#7f1d1d"
                DEBUG = "#581c87"

            class WIDGET:
                class BUTTON:
                    NAVIGATION = "#ffffff"
                    DEFAULT = "#1e40af"
                    EMPHASIS = "#ffffff"
                    SUCCESS = "#ffffff"
                    DANGER = "#ffffff"
                    WARNING = "#451a03"
                    OPTIONS_LIGHT = "#2563eb"
                    OPTIONS_DARK = "#ffffff"
                    INACTIVE = "#64748b"

                class INPUT:
                    DEFAULT = "#1e40af"
                    DISABLED = "#64748b"
                    PLACEHOLDER = "#64748b"

                class TAB:
                    TITLE = "#1e3a8a"
                    BODY = "#1e40af"

                ACCORDION = "#1e3a8a"
                OUTPUT = "#1e40af"
                DROPDOWN = "#1e40af"

            class TABLE:
                HEAD = "#000000"
                BODY = "#000000"
                EMPHASIS = "#000000"

    class LAYOUT_COLOR:
        BACKGROUND = "#f0f9ff"  # Very light blue
        HEADER = "#2563eb"  # Bright blue
        HEADER_GRADIENT = "#60a5fa"
        BODY = "#ffffff"  # Pure white
        CONTRAST = "#1e3a8a"

        class NAVIGATOR:
            BACKGROUND = "#1e3a8a"  # Dark navy
            PANEL = "#1e40af"  # Deep blue
            BORDER = "#2563eb"  # Blue
            SHADOW = "#172554"  # Very dark blue
            GLOW = "#60a5fa"  # Light blue

            class STEP:
                COMPLETED = "#3b82f6"  # Medium blue
                ACTIVE = "#60a5fa"  # Light blue
                AVAILABLE = "#fbbf24"  # Amber (distinct from blue for CVD)
                LOCKED = "#64748b"  # Gray

        class POPUP_LOGGER:
            BACKGROUND = "#1e3a8a"
            PANEL = "#1e40af"
            BORDER = "#2563eb"
            SHADOW = "#172554"
            GLOW = "#60a5fa"

            LAYOUT_LINE = "#2563eb"
            LOG_LINE = "#3b82f6"

            class LOG_LEVEL:
                DEFAULT = "#64748b"
                INFO = "#3b82f6"
                SUCCESS = "#10b981"
                WARNING = "#f59e0b"
                ERROR = "#ef4444"
                CRITICAL = "#dc2626"
                DEBUG = "#8b5cf6"

        class INFO_FIELD:
            DEFAULT = "#f8fafc"
            INFO = "#dbeafe"
            SUCCESS = "#dcfce7"
            WARNING = "#fef3c7"
            ERROR = "#fee2e2"
            CRITICAL = "#fecaca"
            DEBUG = "#ede9fe"

        class WIDGET:
            class BUTTON:
                DEFAULT = "#f1f5f9"
                EMPHASIS = "#2563eb"
                SUCCESS = "#059669"
                DANGER = "#dc2626"
                WARNING = "#d97706"
                OPTIONS_LIGHT = "#60a5fa"
                OPTIONS_DARK = "#1e40af"
                INACTIVE = "#e2e8f0"

            class INPUT:
                class BACKGROUND:
                    DEFAULT = "#ffffff"
                    DISABLED = "#f8fafc"
                    FOCUS = "#ffffff"

                class BORDER:
                    DEFAULT = "#94a3b8"
                    FOCUS = "#2563eb"
                    ERROR = "#ef4444"

            class CHECKBOX:
                BACKGROUND = "#ffffff"
                BORDER = "#94a3b8"
                CHECKED = "#2563eb"
                FOCUS = "#2563eb"

            class SLIDER:
                TRACK = "#e2e8f0"
                HANDLE = "#2563eb"
                RANGE = "#2563eb"

            class PROGRESS:
                BACKGROUND = "#e2e8f0"
                BAR = "#2563eb"

            class TAB:
                BACKGROUND = "#f1f5f9"
                ACTIVE = "#2563eb"
                HOVER = "#f1f5f9"
                PANEL = "#ffffff"

            class ACCORDION:
                PANEL = "#e0f2fe"
                LINES = "#1e3a8a"

            class OUTPUT:
                BACKGROUND = "#ffffff"
                BORDER = "#94a3b8"

            class DROPDOWN:
                BACKGROUND = "#e0f2fe"
                BORDER = "#94a3b8"

        class TABLE:
            HEAD = "#bae6fd"
            LINES = "#1e3a8a"

    class ICON:
        DEFAULT = "🔵"
        INFO = "💙"
        SUCCESS = "✅"
        WARNING = "🟠"
        ERROR = "🔴"
        CRITICAL = "🚨"
        DEBUG = "🔎"
        CLEAR = "🧹"
        STORE = "💾"
        SAVE = "📁"
        CLOSE = "✖"
        FORWARD = "▶"
        BACKWARD = "◀"
        SEPARATOR = "▫"
        CALENDAR = "📅"

        class PAGE:
            DIRECTORY_SELECTION = "🗃️"
            DATASET_SELECTION = "📊"
            MODULE_SELECTION = "⚙️"
            MODULE = "🛠️"

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
