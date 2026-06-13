"""
Launch the Phase 3B scenario-overlay Streamlit viewer.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
VIEWER = APP_DIR / "paid_simulator" / "phase3_scenario_overlay_viewer.py"


def main() -> int:
    if not VIEWER.exists():
        print(f"Missing viewer file: {VIEWER}")
        return 1

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(VIEWER),
        "--server.headless=false",
    ]
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
