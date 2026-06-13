"""
run_paid_simulator_phase2f_model_decision_viewer.py

Launcher for the standalone Phase 2F model-decision viewer.
"""

from pathlib import Path
import subprocess
import sys


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
VIEWER_APP = APP_DIR / "paid_simulator" / "phase2f_model_decision_viewer.py"


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

    print("=" * 96)
    print("Launching Phase 2F model-decision viewer")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Viewer app:   {VIEWER_APP}")
    print()

    completed = subprocess.run(command, cwd=PROJECT_ROOT)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
