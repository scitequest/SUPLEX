# PyInstaller spec for the Windows build.
#
# Build from the repository root:
#     uv sync --group build
#     uv run pyinstaller packaging/windows/suplex.spec
#
# The result is a one-directory bundle in dist/suplex. The launcher also acts as
# the Jupyter kernel executable (see suplex.cli), so no separate python.exe is
# needed inside the bundle.

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

# Packages whose data files (templates, nbextensions, kernelspecs, grammars) must ship
# with the bundle. The scientific stack is covered by PyInstaller's own hooks.
COLLECTED_PACKAGES = [
    "suplex",
    "voila",
    "jupyter_server",
    "jupyterlab_server",
    "jupyter_client",
    "jupyter_core",
    "nbconvert",
    "nbclient",
    "nbformat",
    "ipykernel",
    "ipywidgets",
    "widgetsnbextension",
    "ipyfilechooser",
    "ipyevents",
    "traitlets",
    "debugpy",
    "jupyter_events",
    "jupyterlab_pygments",
    "pygments",
    "mistune",
    "jinja2",
    "jsonschema",
    "jsonschema_specifications",
    "referencing",
    "rfc3987_syntax",
    "python_json_logger",
]

datas, binaries, hiddenimports = [], [], []
for package in COLLECTED_PACKAGES:
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

# Voila, nbextensions and kernelspecs are installed into <prefix>/share/jupyter; the frozen
# app resolves <prefix> to the bundle directory, so mirror that layout.
share_jupyter = Path(sys.prefix) / "share" / "jupyter"
datas += [(str(share_jupyter), "share/jupyter")]

block_cipher = None

analysis = Analysis(
    ["entry.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter.test", "jupyterlab", "notebook"],
    noarchive=False,
)
pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="suplex",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon="suplex.ico",
)
coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    strip=False,
    upx=False,
    name="suplex",
)
