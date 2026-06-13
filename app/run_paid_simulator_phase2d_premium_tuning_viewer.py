"""
run_paid_simulator_phase2d_premium_tuning_viewer.py

Launch the standalone Phase 2D Premium-Model Tuning Viewer.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
VIEWER_APP = APP_DIR / "paid_simulator" / "phase2d_premium_tuning_viewer.py"


def main() -> int:
    if not VIEWER_APP.exists():
        print(f"ERROR: Viewer app not found: {VIEWER_APP}")
        return 1

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(VIEWER_APP),
        "--server.headless=false",
    ]

    print("Launching Phase 2D Premium-Model Tuning Viewer")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Viewer app:   {VIEWER_APP}")
    print(" ".join(command))

    return subprocess.call(command, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
