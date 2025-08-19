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
    
class WHISKER_MODE(Enum):
    NONE = "None"
    IQR = "IQR"
    PERCENTILES = "Percentiles"
    MIN_MAX = "Min-Max"
    
class JITTER_TYPE(Enum):
    UNIFORM = "uniform"
    GAUSSIAN = "gaussian"