"""Build a self-installing SUPLEX executable with PyApp (https://ofek.dev/pyapp/).

The resulting binary embeds the SUPLEX wheel and, on first start, installs a private
CPython and the locked dependencies into the user's application data directory using
uv. Later starts reuse that installation. Run from the repository root:

    uv build --wheel
    uv run python packaging/pyapp/build.py

Requires a Rust toolchain (cargo). The binary is written to dist/pyapp/.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYAPP_VERSION = "0.30.0"
PYTHON_VERSION = "3.14"


def project_metadata() -> tuple[str, str]:
    with open(REPO_ROOT / "pyproject.toml", "rb") as pyproject:
        project = tomllib.load(pyproject)["project"]
    return project["name"], project["version"]


def built_wheel(name: str, version: str) -> Path:
    # uv normalizes hyphens to underscores in wheel filenames
    normalized = name.replace("-", "_")
    wheel = REPO_ROOT / "dist" / f"{normalized}-{version}-py3-none-any.whl"
    if not wheel.is_file():
        sys.exit(f"{wheel} not found; run `uv build --wheel` first")
    return wheel


def pyapp_environment(name: str, version: str, wheel: Path) -> dict[str, str]:
    """PyApp is configured entirely through environment variables at compile time."""
    settings = {
        "PYAPP_PROJECT_NAME": name,
        "PYAPP_PROJECT_VERSION": version,
        "PYAPP_PROJECT_PATH": str(wheel),
        "PYAPP_EXEC_SPEC": "suplex.cli:main",
        "PYAPP_PYTHON_VERSION": PYTHON_VERSION,
        "PYAPP_UV_ENABLED": "1",
        "PYAPP_FULL_ISOLATION": "1",
        "PYAPP_EXPOSE_METADATA": "1",
        "PYAPP_IS_GUI": "1" if platform.system() == "Windows" else "0",
    }
    return {**os.environ, **settings}


def build(name: str, version: str, wheel: Path, output_dir: Path) -> Path:
    with tempfile.TemporaryDirectory() as cargo_root:
        subprocess.run(
            [
                "cargo",
                "install",
                "pyapp",
                "--version",
                PYAPP_VERSION,
                "--force",
                "--root",
                cargo_root,
            ],
            env=pyapp_environment(name, version, wheel),
            check=True,
        )
        suffix = ".exe" if platform.system() == "Windows" else ""
        built = Path(cargo_root) / "bin" / f"pyapp{suffix}"
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"suplex{suffix}"
        shutil.copy2(built, target)
    return target


def main() -> None:
    name, version = project_metadata()
    wheel = built_wheel(name, version)
    target = build(name, version, wheel, REPO_ROOT / "dist" / "pyapp")
    print(f"Built {target}")


if __name__ == "__main__":
    main()
