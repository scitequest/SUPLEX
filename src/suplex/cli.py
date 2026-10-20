"""Command line entry point: ``suplex`` starts a local Voilà server and opens the browser."""

import argparse
import os
import socket
import sys
import threading
import webbrowser
from importlib.resources import files

from suplex import __version__
from suplex.paths import user_modules_dir, user_schemes_dir

DEFAULT_PORT = 8866
PORT_RANGE = 100
NOTEBOOK_NAME = "Suplex.ipynb"


def _dispatch_kernel() -> bool:
    """Run as a Jupyter kernel when invoked as ``<exe> -m ipykernel_launcher ...``.

    Voilà starts kernels with ``sys.executable -m ipykernel_launcher -f <file>``. In a
    frozen build the executable is this launcher, so it has to behave like Python here.
    """
    if sys.argv[1:3] != ["-m", "ipykernel_launcher"]:
        return False
    sys.argv = [sys.argv[0], *sys.argv[3:]]
    from ipykernel import kernelapp

    kernelapp.launch_new_instance()
    return True


def _acquire_single_instance_lock() -> bool:
    """Return True if no other SUPLEX instance is running (Windows only)."""
    if sys.platform != "win32":
        return True
    import ctypes

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    kernel32.CreateMutexW(None, False, "Global\\SUPLEX_SingleInstance_Mutex")
    error_already_exists = 183
    return kernel32.GetLastError() != error_already_exists


def find_free_port(start: int = DEFAULT_PORT, count: int = PORT_RANGE) -> int:
    for port in range(start, start + count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No free port found in range {start}-{start + count - 1}")


def _wait_for_server(port: int, timeout: float = 60.0) -> bool:
    """Block until the server accepts TCP connections or the timeout elapses."""
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            try:
                sock.connect(("127.0.0.1", port))
            except OSError:
                continue
            return True
    return False


def _open_browser_when_ready(url: str, port: int) -> None:
    def _open() -> None:
        if _wait_for_server(port):
            webbrowser.open(url)
        else:
            print("SUPLEX server did not become ready in time.", file=sys.stderr)

    threading.Thread(target=_open, daemon=True).start()


def notebook_path() -> str:
    return str(files("suplex") / NOTEBOOK_NAME)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="suplex", description="Start the SUPLEX analysis platform in your browser."
    )
    parser.add_argument("--version", action="version", version=f"SUPLEX {__version__}")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"port to listen on (default: first free from {DEFAULT_PORT})",
    )
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    parser.add_argument("--debug", action="store_true", help="show kernel tracebacks in the page")
    parser.add_argument(
        "--demo", action="store_true", help="demo mode: disable saving to disk (sets SUPLEX_DEMO=1)"
    )
    return parser


def run(port: int | None, open_browser: bool, debug: bool, demo: bool) -> int:
    if not _acquire_single_instance_lock():
        print("SUPLEX is already running.", file=sys.stderr)
        return 1
    if demo:
        os.environ["SUPLEX_DEMO"] = "1"

    port = port if port is not None else find_free_port()
    url = f"http://127.0.0.1:{port}/"
    print(f"Starting SUPLEX {__version__} on {url} (Ctrl+C to stop)")
    print(f"Custom modules: {user_modules_dir()}")
    print(f"Custom colour schemes: {user_schemes_dir()}")
    if open_browser:
        _open_browser_when_ready(url, port)

    from voila.app import Voila

    argv = [
        notebook_path(),
        "--Voila.ip=127.0.0.1",
        f"--Voila.port={port}",
        "--Voila.open_browser=False",
        f"--VoilaConfiguration.show_tracebacks={debug}",
    ]
    try:
        Voila.launch_instance(argv=argv)
    except KeyboardInterrupt:
        print("\nShutting down SUPLEX.")
    return 0


def main() -> int:
    if _dispatch_kernel():
        return 0
    args = build_parser().parse_args()
    return run(args.port, not args.no_browser, args.debug, args.demo)


if __name__ == "__main__":
    sys.exit(main())
