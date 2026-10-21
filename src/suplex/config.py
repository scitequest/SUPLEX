"""Runtime configuration derived from the environment."""

import os

# Demo mode is used for hosted deployments (e.g. Binder) where the server has no
# desktop: native file dialogs cannot be shown, so saving to disk is disabled.
DEMO: bool = os.environ.get("SUPLEX_DEMO") == "1"
