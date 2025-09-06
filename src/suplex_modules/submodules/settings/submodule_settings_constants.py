from enum import Enum
from typing import Optional

OPTION_WIDGETS_MAX_WIDTH = "500px"

class OPTION_INSET:
    BASELINE = "0px 0px 0px 0px"
    PRIMARY = "0px 0px 0px 10px"
    SECONDARY = "0px 0px 0px 20px"
    TERTIARY = "0px 0px 0px 30px"
    QUATERNARY = "0px 0px 0px 40px"

class SCALE_TYPE(Enum):
    """Available scale types"""
    LINEAR = "linear"
    LOG = "log"
    SYMLOG = "symlog"

class INTERPOLATION_TYPE(Enum):
    """Available interpolation types"""
    NEAREST = "nearest"
    BILINEAR = "bilinear"
    BICUBIC = "bicubic"
    SPLINE16 = "spline16"
    SPLINE36 = "spline36"

class GRID_STYLE(Enum):
    """Available grid styles"""
    DARKGRID = "darkgrid"
    WHITEGRID = "whitegrid"
    TICKS = "ticks"

class LEGEND_POSITION(Enum):
    """Available legend positions"""
    BEST = "best"
    UPPER_RIGHT = "upper right"
    UPPER_LEFT = "upper left"
    LOWER_RIGHT = "lower right"
    LOWER_LEFT = "lower left"
    RIGHT = "right"
    LEFT = "left"
    CENTER_LEFT = "center left"
    CENTER_RIGHT = "center right"
    LOWER_CENTER = "lower center"
    UPPER_CENTER = "upper center"
    CENTER = "center"

class ASPECT_RATIO(Enum):
    """Available aspect ratios"""
    AUTO = "auto"
    EQUAL = "equal"
    FOUR_THREE = "4:3"
    SIXTEEN_NINE = "16:9"
    GOLDEN = "1.618:1"
    SILVER = "2.414:1"
    BRONZE = "3.303:1"
    THREE_TWO = "3:2"
    TWO_THREE = "2:3"
    SIXTEEN_TEN = "16:10"
    NINE_SIXTEEN = "9:16"

def get_aspect_ratio_value(ar: ASPECT_RATIO) -> Optional[float]:
    """
    Translates the aspect ratio enum into a valid fraction
    """
    if ar == ASPECT_RATIO.AUTO:
        return None
    elif ar == ASPECT_RATIO.EQUAL:
        return 1.0
    else:
        try:
            parts = ar.value.split(":")
            if len(parts) != 2:
                raise ValueError
            width_str = parts[0].strip()
            height_str = parts[1].strip()
            # Eval also allows formulas
            width = eval(width_str, {"sqrt": math.sqrt}) if "sqrt" in width_str else float(width_str)
            height = float(height_str)
            return width / height
        except Exception:
            return None

class SEQUENTIAL_COLOR_SCHEME(Enum):
    """Available sequential color schemes"""
    # Original schemes
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"
    BLUES = "Blues"
    GREENS = "Greens"
    GREYS = "Greys"
    ORANGES = "Oranges"
    PURPLES = "Purples"
    REDS = "Reds"
    BUGN = "BuGn"
    BUPU = "BuPu"
    GNBU = "GnBu"
    ORRD = "OrRd"
    PUBU = "PuBu"
    PUBUGN = "PuBuGn"
    PURD = "PuRd"
    YLGN = "YlGn"
    YLGNBU = "YlGnBu"
    YLORBR = "YlOrBr"
    YLORRD = "YlOrRd"
    ROCKET = "rocket"
    MAKO = "mako"
    FLARE = "flare"
    CREST = "crest"
    RAINBOW = "rainbow"
    JET = "jet"
    TURBO = "turbo"

    VIRIDIS_R = "viridis_r"
    PLASMA_R = "plasma_r"
    INFERNO_R = "inferno_r"
    MAGMA_R = "magma_r"
    CIVIDIS_R = "cividis_r"
    BLUES_R = "Blues_r"
    GREENS_R = "Greens_r"
    GREYS_R = "Greys_r"
    ORANGES_R = "Oranges_r"
    PURPLES_R = "Purples_r"
    REDS_R = "Reds_r"
    BUGN_R = "BuGn_r"
    BUPU_R = "BuPu_r"
    GNBU_R = "GnBu_r"
    ORRD_R = "OrRd_r"
    PUBU_R = "PuBu_r"
    PUBUGN_R = "PuBuGn_r"
    PURD_R = "PuRd_r"
    YLGN_R = "YlGn_r"
    YLGNBU_R = "YlGnBu_r"
    YLORBR_R = "YlOrBr_r"
    YLORRD_R = "YlOrRd_r"
    ROCKET_R = "rocket_r"
    MAKO_R = "mako_r"
    FLARE_R = "flare_r"
    CREST_R = "crest_r"
    RAINBOW_R = "rainbow_r"
    JET_R = "jet_r"
    TURBO_R = "turbo_r"

class DIVERGENT_COLOR_SCHEME(Enum):
    """Available divergent color schemes"""
    COOLWARM = "coolwarm"
    SEISMIC = "seismic"
    RDBU = "RdBu"
    BRBG = "BrBG"
    PIYG = "PiYG"
    PRGN = "PRGn"
    PUOR = "PuOr"
    RDGY = "RdGy"
    RDYLBU = "RdYlBu"
    RDYLGN = "RdYlGn"
    SPECTRAL = "Spectral"
    VLAG = "vlag"
    ICEFIRE = "icefire"
    FLARE = "flare"
    CREST = "crest"

    RDBU_R = "RdBu_r"
    BRBG_R = "BrBG_r"
    PIYG_R = "PiYG_r"
    PRGN_R = "PRGn_r"
    PUOR_R = "PuOr_r"
    RDGY_R = "RdGy_r"
    RDYLBU_R = "RdYlBu_r"
    RDYLGN_R = "RdYlGn_r"
    SPECTRAL_R = "Spectral_r"
    VLAG_R = "vlag_r"
    ICEFIRE_R = "icefire_r"
    FLARE_R = "flare_r"
    CREST_R = "crest_r"
    
class WHISKER_MODE(Enum):
    NONE = "None"
    IQR = "IQR"
    PERCENTILES = "Percentiles"
    MIN_MAX = "Min-Max"
    
class JITTER_TYPE(Enum):
    UNIFORM = "uniform"
    GAUSSIAN = "gaussian"

class ANNOTATION_COLOR(Enum):
    AUTO = "auto"
    BLACK = "black"
    WHITE = "white"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    GRAY = "gray" 

class LINE_COLOR(Enum):
    WHITE = "white"
    BLACK = "black"
    GRAY = "gray"
    NONE = "none"

class CBAR_ORIENTATION(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    HIDE = "hide colorbar"