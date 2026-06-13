"""
dashboard_status.py

Status utilities for the Covered Call Simulator paid simulator dashboard.

This module is intentionally read-only. It checks whether important project
files and generated outputs exist, summarizes their last-modified times, and
returns customer/developer-facing status information for the Streamlit dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
import json
import os


DASHBOARD_BUILD_NAME = "Paid Simulator Browser Dashboard"
DASHBOARD_BUILD_VERSION = "0.9.0-status-panel"
DASHBOARD_BUILD_DATE = "2026-06-11"


@dataclass
class FileStatus:
    label: str
    path: str
    exists: bool
    size_bytes: int | None
    modified_local: str | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DashboardStatus:
    build_name: str
    build_version: str
    build_date: str
    project_root: str
    config_status: FileStatus
    required_files: list[FileStatus]
    output_files: list[FileStatus]
    optional_files: list[FileStatus]
    config_summary: dict
    overall_status: str
    problems: list[str]

    def to_dict(self) -> dict:
        return {
            "build_name": self.build_name,
            "build_version": self.build_version,
            "build_date": self.build_date,
            "project_root": self.project_root,
            "config_status": self.config_status.to_dict(),
            "required_files": [item.to_dict() for item in self.required_files],
            "output_files": [item.to_dict() for item in self.output_files],
            "optional_files": [item.to_dict() for item in self.optional_files],
            "config_summary": self.config_summary,
            "overall_status": self.overall_status,
            "problems": self.problems,
        }


def find_project_root(start_path: Path | None = None) -> Path:
    """Return the Coveredcallsimulator project root."""
    if start_path is None:
        start_path = Path(__file__).resolve()

    for candidate in [start_path, *start_path.parents]:
        if (candidate / "app").exists() and (candidate / "config").exists():
            return candidate

    # dashboard_status.py lives in app/paid_simulator, so parents[2] is normally root.
    return Path(__file__).resolve().parents[2]


def _format_mtime(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def file_status(project_root: Path, relative_path: str, label: str) -> FileStatus:
    path = project_root / relative_path
    exists = path.exists()
    return FileStatus(
        label=label,
        path=str(path),
        exists=exists,
        size_bytes=path.stat().st_size if exists and path.is_file() else None,
        modified_local=_format_mtime(path),
    )


def read_config_summary(config_path: Path) -> dict:
    """Read a short summary from paid_simulator_config.json."""
    if not config_path.exists():
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except Exception as exc:  # noqa: BLE001 - status panel should not crash the app.
        return {"config_read_error": str(exc)}

    fields = [
        "ticker",
        "account_size",
        "risk_tier",
        "position_size_cap",
        "desired_contracts",
        "target_delta",
        "target_dte",
        "management_rule",
        "rolling_rule",
        "re_entry_rule",
        "transaction_cost",
        "slippage_assumption",
        "demo_price",
    ]
    return {field: config.get(field) for field in fields if field in config}


def get_dashboard_status(project_root: Path | None = None) -> DashboardStatus:
    """Return the current status of the paid simulator dashboard."""
    root = project_root or find_project_root()

    config_status = file_status(root, "config/paid_simulator_config.json", "Paid simulator config")

    required_files = [
        file_status(root, "app/run_paid_simulator.py", "Paid simulator runner"),
        file_status(root, "app/run_paid_simulator_health_check.py", "Paid simulator health check"),
        file_status(root, "app/run_paid_simulator_form.py", "Streamlit dashboard launcher"),
        file_status(root, "app/paid_simulator/config_form_app.py", "Streamlit dashboard app"),
    ]

    output_files = [
        file_status(root, "outputs/tables/paid_simulator/scenario_comparison.csv", "Scenario comparison CSV"),
        file_status(root, "outputs/tables/paid_simulator/config_echo.csv", "Config echo CSV"),
        file_status(root, "outputs/reports/paid_simulator/scenario_comparison_report.html", "HTML report"),
    ]

    optional_files = [
        file_status(root, "outputs/tables/paid_simulator/run_history.csv", "Run history CSV"),
        file_status(root, "outputs/tables/paid_simulator/preset_comparison.csv", "Preset comparison CSV"),
        file_status(root, "docs/paid_simulator_browser_dashboard_checkpoint.md", "Dashboard checkpoint doc"),
        file_status(root, "docs/paid_simulator_checkpoint_handoff.md", "Earlier paid simulator checkpoint doc"),
    ]

    problems: list[str] = []
    if not config_status.exists:
        problems.append("Missing paid simulator config file.")

    for item in required_files:
        if not item.exists:
            problems.append(f"Missing required file: {item.label}")

    missing_outputs = [item.label for item in output_files if not item.exists]
    if missing_outputs:
        problems.append("Missing generated output files. Run the paid simulator to regenerate them.")

    config_summary = read_config_summary(root / "config" / "paid_simulator_config.json")
    if "config_read_error" in config_summary:
        problems.append("The paid simulator config file exists but could not be read as valid JSON.")

    overall_status = "PASS" if not problems else "REVIEW"

    return DashboardStatus(
        build_name=DASHBOARD_BUILD_NAME,
        build_version=DASHBOARD_BUILD_VERSION,
        build_date=DASHBOARD_BUILD_DATE,
        project_root=str(root),
        config_status=config_status,
        required_files=required_files,
        output_files=output_files,
        optional_files=optional_files,
        config_summary=config_summary,
        overall_status=overall_status,
        problems=problems,
    )


def status_table_rows(items: Iterable[FileStatus]) -> list[dict]:
    """Return rows suitable for st.dataframe."""
    rows = []
    for item in items:
        rows.append(
            {
                "Status": "FOUND" if item.exists else "MISSING",
                "Item": item.label,
                "Modified": item.modified_local or "",
                "Size bytes": item.size_bytes if item.size_bytes is not None else "",
                "Path": item.path,
            }
        )
    return rows
