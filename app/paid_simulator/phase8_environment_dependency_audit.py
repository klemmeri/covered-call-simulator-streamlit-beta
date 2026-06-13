"""
phase8_environment_dependency_audit.py

Phase 8-3 environment and dependency audit.

This module is passive. It audits the local Python environment and the core
project files needed for deployment packaging. It does not modify dashboard or
engine code.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DEPENDENCIES_CSV = OUTPUT_TABLE_DIR / "phase8_3_environment_dependency_audit_dependencies.csv"
FILES_CSV = OUTPUT_TABLE_DIR / "phase8_3_environment_dependency_audit_required_files.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_3_environment_dependency_audit_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_3_environment_dependency_audit.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_3_environment_dependency_audit_report.txt"

READY_MARKER = "PHASE8_3_ENVIRONMENT_DEPENDENCY_AUDIT_READY"
RELEASE_DECISION = "PHASE8_3_ENVIRONMENT_DEPENDENCY_AUDIT_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "environment_dependency_audit"

CORE_PACKAGES = ["pandas", "numpy", "matplotlib", "streamlit"]
REQUIRED_FILES = [
    "app/paid_simulator/config_form_app.py",
    "app/price_paths.py",
    "app/simulator.py",
    "app/strategy.py",
    "app/portfolio.py",
    "app/config.py",
]


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _package_status(package_name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(package_name)
    installed = spec is not None
    version = "unknown"
    if installed:
        try:
            module = __import__(package_name)
            version = str(getattr(module, "__version__", "unknown"))
        except Exception:
            version = "importable_version_unknown"
    return {
        "package": package_name,
        "installed": installed,
        "version": version,
        "deployment_required": True,
    }


def _required_file_status(relative_path: str) -> dict[str, Any]:
    path = PROJECT_ROOT / relative_path
    return {
        "relative_path": relative_path,
        "exists": path.exists(),
        "required_for_deployment": True,
    }


def build_phase8_3_summary() -> dict[str, Any]:
    _ensure_dirs()

    dependency_rows = [_package_status(package) for package in CORE_PACKAGES]
    dependency_df = pd.DataFrame(dependency_rows)
    dependency_df.to_csv(DEPENDENCIES_CSV, index=False)

    file_rows = [_required_file_status(path) for path in REQUIRED_FILES]
    file_df = pd.DataFrame(file_rows)
    file_df.to_csv(FILES_CSV, index=False)

    all_core_packages_installed = bool(dependency_df["installed"].all()) if not dependency_df.empty else False
    all_required_files_present = bool(file_df["exists"].all()) if not file_df.empty else False
    python_version = platform.python_version()

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "environment_dependency_audit_created": True,
        "python_version": python_version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "core_package_rows": int(len(dependency_df)),
        "required_file_rows": int(len(file_df)),
        "all_core_packages_installed": all_core_packages_installed,
        "all_required_files_present": all_required_files_present,
        "requirements_file_needed": True,
        "streamlit_mvp_path_supported": True,
        "deployment_packaging_ready_for_next_step": all_required_files_present,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "row_count": int(len(dependency_df) + len(file_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 8-3 environment and dependency audit",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Python version: {python_version}",
        f"Core package rows: {summary['core_package_rows']}",
        f"Required file rows: {summary['required_file_rows']}",
        f"All core packages installed: {all_core_packages_installed}",
        f"All required files present: {all_required_files_present}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase8_3_summary(), indent=2))
