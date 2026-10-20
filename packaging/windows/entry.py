"""PyInstaller entry script. Delegates to the regular console entry point."""

import multiprocessing
import sys

from suplex.cli import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main())
