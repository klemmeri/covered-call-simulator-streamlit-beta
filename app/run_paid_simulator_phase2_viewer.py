"""
Launcher for the Phase 2 scaffold Streamlit viewer.

Run this file from PyCharm. It starts Streamlit on the Phase 2 viewer located in
app/paid_simulator/phase2_scaffold_viewer.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
VIEWER_APP = APP_DIR / "paid_simulator" / "phase2_scaffold_viewer.py"


def main() -> None:
    if not VIEWER_APP.exists():
        raise FileNotFoundError(f"Could not find Phase 2 viewer app: {VIEWER_APP}")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(VIEWER_APP),
        "--server.headless=false",
    ]

    subprocess.run(command, cwd=str(PROJECT_ROOT), check=False)


if __name__ == "__main__":
    main()
