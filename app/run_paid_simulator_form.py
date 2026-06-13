"""
Launcher for the paid simulator Streamlit control panel.

Run this file from PyCharm. It starts Streamlit on the form app located in
app/paid_simulator/config_form_app.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
FORM_APP = APP_DIR / "paid_simulator" / "config_form_app.py"


def main() -> None:
    if not FORM_APP.exists():
        raise FileNotFoundError(f"Could not find Streamlit form app: {FORM_APP}")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(FORM_APP),
        "--server.headless=false",
    ]

    subprocess.run(command, cwd=str(PROJECT_ROOT), check=False)


if __name__ == "__main__":
    main()
