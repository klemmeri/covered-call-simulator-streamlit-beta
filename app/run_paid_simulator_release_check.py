"""
run_paid_simulator_release_check.py

Release-candidate smoke check for the Covered Call Simulator paid dashboard.

This script is intentionally conservative. It does not modify files. It checks
that the paid simulator browser workflow has the expected project structure,
configuration file, generated outputs, and documentation checkpoint.

Run from PyCharm:
    app\run_paid_simulator_release_check.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    ("Config file", PROJECT_ROOT / "config" / "paid_simulator_config.json"),
    ("Paid simulator runner", PROJECT_ROOT / "app" / "run_paid_simulator.py"),
    ("Paid simulator health check", PROJECT_ROOT / "app" / "run_paid_simulator_health_check.py"),
    ("Streamlit dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ("Streamlit dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
    ("App status module", PROJECT_ROOT / "app" / "paid_simulator" / "dashboard_status.py"),
]

GENERATED_OUTPUTS = [
    ("Scenario comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv"),
    ("Config echo CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "config_echo.csv"),
    ("HTML report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_comparison_report.html"),
]

OPTIONAL_OUTPUTS = [
    ("Run history CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "run_history.csv"),
    ("Preset comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "preset_comparison.csv"),
    ("Decision memo folder", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "decision_memos"),
]

CHECKPOINT_DOCS = [
    ("Paid simulator checkpoint handoff", PROJECT_ROOT / "docs" / "paid_simulator_checkpoint_handoff.md"),
    ("Browser dashboard checkpoint", PROJECT_ROOT / "docs" / "paid_simulator_browser_dashboard_checkpoint.md"),
    ("Release readiness checklist", PROJECT_ROOT / "docs" / "paid_simulator_release_readiness_checklist.md"),
]


PASS_TEXT = "PASS"
REVIEW_TEXT = "REVIEW"


def print_header(title: str) -> None:
    print("\n" + title)
    print("-" * 88)


def file_status(items: Iterable[tuple[str, Path]], *, required: bool = True) -> int:
    missing = 0
    for label, path in items:
        exists = path.exists()
        status = "FOUND" if exists else ("MISSING" if required else "OPTIONAL MISSING")
        if required and not exists:
            missing += 1
        print(f"{status:<18} {label:<36} {path}")
    return missing


def check_json_config(path: Path) -> int:
    print_header("Config JSON check")
    if not path.exists():
        print(f"MISSING config file: {path}")
        return 1

    try:
        with path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as exc:  # noqa: BLE001 - diagnostic script
        print(f"INVALID JSON: {exc}")
        return 1

    print("VALID JSON")
    keys_to_show = [
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
    for key in keys_to_show:
        print(f"{key:<24} {config.get(key)}")
    return 0


def check_csv_rows(path: Path, label: str, *, required: bool = True) -> int:
    print_header(f"CSV row check: {label}")
    if not path.exists():
        status = "MISSING" if required else "OPTIONAL MISSING"
        print(f"{status}: {path}")
        return 1 if required else 0

    try:
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as exc:  # noqa: BLE001 - diagnostic script
        print(f"COULD NOT READ CSV: {exc}")
        return 1 if required else 0

    data_rows = max(len(rows) - 1, 0)
    print(f"Rows excluding header: {data_rows}")
    if required and data_rows <= 0:
        print("REVIEW: required CSV has no data rows.")
        return 1
    return 0


def main() -> None:
    print("=" * 88)
    print("Covered Call Simulator - Paid Dashboard Release Check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")

    issues = 0

    print_header("Required files")
    issues += file_status(REQUIRED_FILES, required=True)

    print_header("Generated outputs")
    issues += file_status(GENERATED_OUTPUTS, required=True)

    print_header("Optional dashboard outputs")
    file_status(OPTIONAL_OUTPUTS, required=False)

    print_header("Checkpoint documentation")
    file_status(CHECKPOINT_DOCS, required=False)

    issues += check_json_config(PROJECT_ROOT / "config" / "paid_simulator_config.json")

    issues += check_csv_rows(
        PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv",
        "scenario_comparison.csv",
        required=True,
    )

    check_csv_rows(
        PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "run_history.csv",
        "run_history.csv",
        required=False,
    )

    check_csv_rows(
        PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "preset_comparison.csv",
        "preset_comparison.csv",
        required=False,
    )

    print("\n" + "=" * 88)
    overall = PASS_TEXT if issues == 0 else REVIEW_TEXT
    print(f"Overall release-check status: {overall}")
    if issues:
        print(f"Issues requiring review: {issues}")
    else:
        print("The paid simulator dashboard has the expected files and generated outputs.")
    print("=" * 88)


if __name__ == "__main__":
    main()
