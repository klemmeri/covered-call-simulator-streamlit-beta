"""
run_dashboard.py

PyCharm-friendly launcher for the Covered Call Simulator Streamlit dashboard.

This script lets you start the dashboard from PyCharm's green Run button.

It does not:
    - run simulations
    - modify app/main.py
    - modify dashboard/app.py
    - rewrite output files

It simply runs the equivalent of:

    streamlit run dashboard/app.py

from the project root.
"""

from pathlib import Path
import subprocess
import sys


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.

    This file is expected to live in:

        Coveredcallsimulator/app/run_dashboard.py

    Therefore, the project root is one level above the app folder.
    """
    current_file = Path(__file__).resolve()
    app_dir = current_file.parent
    project_root = app_dir.parent

    return project_root


def get_dashboard_path(project_root: Path) -> Path:
    """
    Return the expected Streamlit dashboard path.
    """
    return project_root / "dashboard" / "app.py"


def validate_dashboard_exists(dashboard_path: Path) -> None:
    """
    Stop with a clear error if the dashboard file is missing.
    """
    if not dashboard_path.exists():
        raise FileNotFoundError(
            f"Dashboard file not found:\n{dashboard_path}"
        )


def launch_streamlit_dashboard() -> None:
    """
    Launch the Streamlit dashboard using the current Python environment.

    Using sys.executable helps PyCharm use the same interpreter configured
    for this project.
    """
    project_root = get_project_root()
    dashboard_path = get_dashboard_path(project_root)

    validate_dashboard_exists(dashboard_path)

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard_path),
    ]

    print("Launching Covered Call Simulator dashboard...")
    print(f"Project root: {project_root}")
    print(f"Dashboard:    {dashboard_path}")
    print()
    print("If the dashboard does not open automatically, go to:")
    print("http://localhost:8501")
    print()

    subprocess.run(
        command,
        cwd=project_root,
        check=False,
    )


if __name__ == "__main__":
    launch_streamlit_dashboard()