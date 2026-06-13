"""
Launcher for the Phase 3 interactive covered-call payoff viewer.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
VIEWER_APP = APP_DIR / "paid_simulator" / "phase3_interactive_payoff_viewer.py"


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
    print("Launching Phase 3 interactive covered-call payoff viewer...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Viewer app:   {VIEWER_APP}")
    return subprocess.call(command, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
