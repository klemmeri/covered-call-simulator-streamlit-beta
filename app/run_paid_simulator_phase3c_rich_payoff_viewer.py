"""
Launch the Phase 3C richer graphical covered-call payoff viewer.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
VIEWER_APP = PROJECT_ROOT / "app" / "paid_simulator" / "phase3c_rich_payoff_viewer.py"


def main() -> int:
    if not VIEWER_APP.exists():
        print(f"ERROR: Viewer app not found: {VIEWER_APP}")
        return 1

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(VIEWER_APP),
        "--server.headless=false",
    ]
    return subprocess.call(cmd, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
