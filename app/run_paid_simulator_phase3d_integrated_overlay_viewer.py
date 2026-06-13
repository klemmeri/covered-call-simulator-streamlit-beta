"""
Launcher for the Phase 3D integrated payoff-overlay viewer.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
VIEWER_APP = PROJECT_ROOT / "app" / "paid_simulator" / "phase3d_integrated_payoff_overlay_viewer.py"


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
