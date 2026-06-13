"""
refresh_dashboard_outputs.py

PyCharm-friendly dashboard output refresh runner for the Covered Call Simulator.

This script refreshes the data files used by the Streamlit dashboard.

It does not:
    - run app/main.py
    - launch Streamlit
    - modify dashboard/app.py
    - modify app/main.py

It supports two refresh modes:

    quick:
        Runs the dashboard-facing reports.
        By default, quick mode also downloads updated historical prices
        and creates a current-price snapshot.

    full:
        Runs the full historical download, calibration, rolling-regime,
        position-sizing, current-price snapshot, and dashboard-report workflow.

Run from PyCharm with the green Run button, or from terminal with:

    python app/refresh_dashboard_outputs.py
"""

from pathlib import Path
import os
import subprocess
import sys
import time


# =============================================================================
# User settings
# =============================================================================

# Use "quick" for normal daily dashboard use.
# Use "full" when you want to refresh all calibration and rolling-validation files.
REFRESH_MODE = "quick"

# In quick mode, download/update historical price data before rebuilding
# dashboard files.
QUICK_REFRESH_DOWNLOAD_PRICES = True

# In quick mode, build the separate current/near-current price snapshot used
# for dashboard tradability estimates.
QUICK_REFRESH_CURRENT_PRICE_SNAPSHOT = True

STOP_ON_FIRST_ERROR = True

# Suppresses noisy Streamlit "missing ScriptRunContext" messages in child scripts.
# This does not suppress normal Python tracebacks from failed scripts.
SUPPRESS_STREAMLIT_CONTEXT_WARNINGS = True


# =============================================================================
# Refresh step definitions
# =============================================================================

QUICK_REFRESH_STEPS_WITH_PRICE_DOWNLOAD = [
    {
        "label": "Download historical prices",
        "script": "download_historical_prices.py",
        "required": True,
    },
    {
        "label": "Current regime snapshot",
        "script": "current_regime_snapshot.py",
        "required": True,
    },
    {
        "label": "Current price snapshot",
        "script": "current_price_snapshot.py",
        "required": True,
    },
    {
        "label": "Position sizing report",
        "script": "position_sizing_report.py",
        "required": True,
    },
    {
        "label": "Account size sensitivity",
        "script": "account_size_sensitivity.py",
        "required": True,
    },
    {
        "label": "Position size tiers",
        "script": "position_size_tiers.py",
        "required": True,
    },
    {
        "label": "Strategy dashboard report",
        "script": "strategy_dashboard_report.py",
        "required": True,
    },
]


QUICK_REFRESH_STEPS_WITHOUT_PRICE_DOWNLOAD = [
    {
        "label": "Current regime snapshot",
        "script": "current_regime_snapshot.py",
        "required": True,
    },
    {
        "label": "Current price snapshot",
        "script": "current_price_snapshot.py",
        "required": True,
    },
    {
        "label": "Position sizing report",
        "script": "position_sizing_report.py",
        "required": True,
    },
    {
        "label": "Account size sensitivity",
        "script": "account_size_sensitivity.py",
        "required": True,
    },
    {
        "label": "Position size tiers",
        "script": "position_size_tiers.py",
        "required": True,
    },
    {
        "label": "Strategy dashboard report",
        "script": "strategy_dashboard_report.py",
        "required": True,
    },
]


QUICK_REFRESH_STEPS_NO_CURRENT_PRICE = [
    {
        "label": "Current regime snapshot",
        "script": "current_regime_snapshot.py",
        "required": True,
    },
    {
        "label": "Position sizing report",
        "script": "position_sizing_report.py",
        "required": True,
    },
    {
        "label": "Account size sensitivity",
        "script": "account_size_sensitivity.py",
        "required": True,
    },
    {
        "label": "Position size tiers",
        "script": "position_size_tiers.py",
        "required": True,
    },
    {
        "label": "Strategy dashboard report",
        "script": "strategy_dashboard_report.py",
        "required": True,
    },
]


FULL_REFRESH_STEPS = [
    {
        "label": "Download historical prices",
        "script": "download_historical_prices.py",
        "required": True,
    },
    {
        "label": "Historical ticker calibration",
        "script": "historical_ticker_calibration.py",
        "required": True,
    },
    {
        "label": "Historical window calibration",
        "script": "historical_window_calibration.py",
        "required": True,
    },
    {
        "label": "Rolling regime detection",
        "script": "rolling_regime_detection.py",
        "required": True,
    },
    {
        "label": "Current regime snapshot",
        "script": "current_regime_snapshot.py",
        "required": True,
    },
    {
        "label": "Current price snapshot",
        "script": "current_price_snapshot.py",
        "required": True,
    },
    {
        "label": "Rolling strategy calibration",
        "script": "rolling_strategy_calibration.py",
        "required": True,
    },
    {
        "label": "Position sizing report",
        "script": "position_sizing_report.py",
        "required": True,
    },
    {
        "label": "Account size sensitivity",
        "script": "account_size_sensitivity.py",
        "required": True,
    },
    {
        "label": "Position size tiers",
        "script": "position_size_tiers.py",
        "required": True,
    },
    {
        "label": "Strategy dashboard report",
        "script": "strategy_dashboard_report.py",
        "required": True,
    },
]


EXPECTED_OUTPUT_FILES = [
    "outputs/tables/comparison/strategy_dashboard_report.txt",
    "outputs/tables/comparison/current_regime_snapshot.csv",
    "outputs/tables/comparison/current_price_snapshot.csv",
    "outputs/tables/comparison/position_sizing_summary.csv",
    "outputs/tables/comparison/account_size_sensitivity_summary.csv",
    "outputs/tables/comparison/position_size_tiers_summary.csv",
]


# =============================================================================
# Path helpers
# =============================================================================

def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.

    This file is expected to live in:

        Coveredcallsimulator/app/refresh_dashboard_outputs.py

    Therefore, the project root is one level above the app folder.
    """
    current_file = Path(__file__).resolve()
    app_dir = current_file.parent
    project_root = app_dir.parent

    return project_root


def get_app_dir(project_root: Path) -> Path:
    """
    Return the app directory.
    """
    return project_root / "app"


def resolve_script_path(app_dir: Path, script_name: str) -> Path:
    """
    Return the full path to a script inside the app folder.
    """
    return app_dir / script_name


def get_refresh_steps() -> list[dict[str, object]]:
    """
    Return the refresh step list based on REFRESH_MODE and quick-mode settings.
    """
    normalized_mode = REFRESH_MODE.strip().lower()

    if normalized_mode == "quick":
        if QUICK_REFRESH_DOWNLOAD_PRICES and QUICK_REFRESH_CURRENT_PRICE_SNAPSHOT:
            return QUICK_REFRESH_STEPS_WITH_PRICE_DOWNLOAD

        if QUICK_REFRESH_CURRENT_PRICE_SNAPSHOT:
            return QUICK_REFRESH_STEPS_WITHOUT_PRICE_DOWNLOAD

        return QUICK_REFRESH_STEPS_NO_CURRENT_PRICE

    if normalized_mode == "full":
        return FULL_REFRESH_STEPS

    raise ValueError(
        "REFRESH_MODE must be either 'quick' or 'full'. "
        f"Current value: {REFRESH_MODE}"
    )


def get_refresh_description() -> str:
    """
    Return a compact description of the selected refresh behavior.
    """
    normalized_mode = REFRESH_MODE.strip().lower()

    if normalized_mode == "quick":
        if QUICK_REFRESH_DOWNLOAD_PRICES and QUICK_REFRESH_CURRENT_PRICE_SNAPSHOT:
            return "quick refresh with historical price download and current-price snapshot"

        if QUICK_REFRESH_CURRENT_PRICE_SNAPSHOT:
            return "quick refresh with current-price snapshot"

        return "quick refresh without current-price snapshot"

    if normalized_mode == "full":
        return "full recalibration refresh"

    return "unknown refresh mode"


# =============================================================================
# Validation helpers
# =============================================================================

def validate_script_exists(script_path: Path, required: bool) -> bool:
    """
    Check whether a script exists.
    """
    if script_path.exists():
        return True

    if required:
        print()
        print("ERROR: Required script was not found:")
        print(script_path)
        print()
    else:
        print()
        print("WARNING: Optional script was not found and will be skipped:")
        print(script_path)
        print()

    return False


def check_expected_outputs(project_root: Path) -> None:
    """
    Print a simple existence check for the dashboard's expected output files.
    """
    print()
    print("=" * 79)
    print("Checking expected dashboard output files")
    print("=" * 79)

    for relative_path in EXPECTED_OUTPUT_FILES:
        output_path = project_root / relative_path

        if output_path.exists():
            print(f"FOUND:   {relative_path}")
        else:
            print(f"MISSING: {relative_path}")

    print()


# =============================================================================
# Execution helpers
# =============================================================================

def build_child_environment() -> dict[str, str]:
    """
    Build the environment used by child Python scripts.

    The Streamlit environment variables reduce noisy bare-mode warnings
    when helper scripts indirectly import Streamlit.
    """
    child_env = os.environ.copy()

    if SUPPRESS_STREAMLIT_CONTEXT_WARNINGS:
        child_env["STREAMLIT_LOG_LEVEL"] = "error"

        existing_python_warnings = child_env.get("PYTHONWARNINGS", "")

        if existing_python_warnings:
            child_env["PYTHONWARNINGS"] = (
                existing_python_warnings + ",ignore"
            )
        else:
            child_env["PYTHONWARNINGS"] = "ignore"

    return child_env


def run_script(
    project_root: Path,
    script_path: Path,
    step_label: str,
) -> int:
    """
    Run one Python script using the current Python interpreter.
    """
    command = [
        sys.executable,
        str(script_path),
    ]

    print()
    print("=" * 79)
    print(f"Running: {step_label}")
    print("=" * 79)
    print(f"Script: {script_path}")
    print(f"Working directory: {project_root}")
    print()

    start_time = time.time()

    completed_process = subprocess.run(
        command,
        cwd=project_root,
        env=build_child_environment(),
        check=False,
    )

    elapsed_seconds = time.time() - start_time

    print()
    print("-" * 79)

    if completed_process.returncode == 0:
        print(f"SUCCESS: {step_label}")
    else:
        print(f"FAILED:  {step_label}")
        print(f"Return code: {completed_process.returncode}")

    print(f"Elapsed time: {elapsed_seconds:,.1f} seconds")
    print("-" * 79)

    return completed_process.returncode


def refresh_dashboard_outputs() -> None:
    """
    Run dashboard refresh steps in order.
    """
    project_root = get_project_root()
    app_dir = get_app_dir(project_root)
    refresh_steps = get_refresh_steps()
    refresh_description = get_refresh_description()

    print()
    print("=" * 79)
    print("Covered Call Simulator Dashboard Refresh")
    print("=" * 79)
    print(f"Python interpreter:              {sys.executable}")
    print(f"Project root:                    {project_root}")
    print(f"App directory:                   {app_dir}")
    print(f"Refresh mode:                    {REFRESH_MODE}")
    print(f"Refresh description:             {refresh_description}")
    print(f"Quick downloads prices:          {QUICK_REFRESH_DOWNLOAD_PRICES}")
    print(f"Quick current-price snapshot:    {QUICK_REFRESH_CURRENT_PRICE_SNAPSHOT}")
    print()
    print("This refresh does not run app/main.py.")
    print("It only refreshes diagnostic/reporting outputs used by the dashboard.")
    print("=" * 79)

    failed_steps = []

    for step_number, step in enumerate(refresh_steps, start=1):
        label = str(step["label"])
        script_name = str(step["script"])
        required = bool(step["required"])

        script_path = resolve_script_path(app_dir, script_name)

        print()
        print(f"Step {step_number} of {len(refresh_steps)}: {label}")

        script_exists = validate_script_exists(
            script_path=script_path,
            required=required,
        )

        if not script_exists:
            if required:
                failed_steps.append(label)

                if STOP_ON_FIRST_ERROR:
                    print("Stopping because STOP_ON_FIRST_ERROR is True.")
                    break

            continue

        return_code = run_script(
            project_root=project_root,
            script_path=script_path,
            step_label=label,
        )

        if return_code != 0:
            failed_steps.append(label)

            if STOP_ON_FIRST_ERROR:
                print()
                print("Stopping because STOP_ON_FIRST_ERROR is True.")
                break

    check_expected_outputs(project_root)

    print()
    print("=" * 79)
    print("Refresh Summary")
    print("=" * 79)

    if failed_steps:
        print("Status: FAILED")
        print()
        print("Failed steps:")

        for failed_step in failed_steps:
            print(f"  - {failed_step}")

        print()
        print("Fix the first failed step, then rerun this script.")

    else:
        print("Status: SUCCESS")
        print()
        print("Dashboard output files should now be refreshed.")
        print()
        print("Next, launch or rerun the dashboard from PyCharm with:")
        print()
        print("    app/run_dashboard.py")

    print("=" * 79)
    print()


# =============================================================================
# Main entry point
# =============================================================================

if __name__ == "__main__":
    refresh_dashboard_outputs()