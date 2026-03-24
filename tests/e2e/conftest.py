"""E2E test fixtures: Streamlit server lifecycle + Playwright browser."""

import os
import signal
import socket
import subprocess
import time

import pytest

_APP_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
_APP_FILE = os.path.join(_APP_DIR, "app.py")


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def app_url():
    """Start Streamlit server for the test session, yield its URL, then stop."""
    port = _free_port()
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    proc = subprocess.Popen(
        ["streamlit", "run", _APP_FILE, "--server.port", str(port)],
        cwd=_APP_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start (max 30s)
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError("Streamlit server failed to start")

    url = f"http://127.0.0.1:{port}"
    yield url

    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=10)
