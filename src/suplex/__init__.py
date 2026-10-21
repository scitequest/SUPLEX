"""SUPLEX - analysis platform for MARTin microarray data."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("scitequest-suplex")
except PackageNotFoundError:  # running from a plain checkout without installation
    __version__ = "0.0.0+unknown"
