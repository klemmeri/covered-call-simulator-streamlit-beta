"""
run_paid_simulator_phase2c_premium_validation_viewer.py

Launcher for the standalone Phase 2C Premium Validation Viewer.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
VIEWER_APP = APP_DIR / "paid_simulator" / "phase2c_premium_validation_viewer.py"


def main() -> None:
    if not VIEWER_APP.exists():
        raise FileNotFoundError(f"Viewer app not found: {VIEWER_APP}")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(VIEWER_APP),
        "--server.headless=false",
    ]

    subprocess.run(command, cwd=PROJECT_ROOT, check=False)


if __name__ == "__main__":
    main()
