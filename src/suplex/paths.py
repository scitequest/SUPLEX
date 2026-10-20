"""Per-user directories for custom modules and colour schemes.

The locations follow the platform conventions implemented by ``platformdirs``
(XDG on Linux, ``~/Library/Application Support`` on macOS, ``%LOCALAPPDATA%`` on
Windows), so they survive upgrades of the installed package.
"""

from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "suplex"
APP_AUTHOR = "scitequest"


def user_data_root() -> Path:
    """Root of the per-user SUPLEX data directory."""
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def user_modules_dir() -> Path:
    """Directory scanned for user-provided SUPLEX modules."""
    return user_data_root() / "modules"


def user_schemes_dir() -> Path:
    """Directory scanned for user-provided colour schemes."""
    return user_data_root() / "schemes"


def ensure_user_dirs() -> tuple[Path, Path]:
    """Create the user module and scheme directories if they do not exist yet."""
    modules = user_modules_dir()
    schemes = user_schemes_dir()
    modules.mkdir(parents=True, exist_ok=True)
    schemes.mkdir(parents=True, exist_ok=True)
    return modules, schemes


def sample_data_dir() -> Path:
    """Directory containing the bundled MARTin sample datasets.

    The package ships the measurement files only. A repository checkout additionally
    holds the microscope images in ``sample_data/`` at the repository root; that copy is
    preferred when present so the image-based modules can be demonstrated too.
    """
    checkout_sample_data = Path(__file__).parents[2] / "sample_data"
    if checkout_sample_data.is_dir():
        return checkout_sample_data
    return Path(__file__).parent / "sample_data"
