"""
run_paid_simulator_phase2g_model_promotion_viewer.py

Launch the standalone Phase 2G model-promotion viewer.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
VIEWER_APP = PROJECT_ROOT / "app" / "paid_simulator" / "phase2g_model_promotion_viewer.py"


def main() -> None:
    if not VIEWER_APP.exists():
        raise FileNotFoundError(f"Missing viewer app: {VIEWER_APP}")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(VIEWER_APP), "--server.headless=false"],
        cwd=str(PROJECT_ROOT),
        check=False,
    )


if __name__ == "__main__":
    main()
