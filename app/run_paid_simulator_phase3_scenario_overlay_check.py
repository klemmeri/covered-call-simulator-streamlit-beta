"""
run_paid_simulator_phase3_scenario_overlay_check.py

Checks the Phase 3B scenario-overlay model for the Covered Call Strategy Stress Test.
"""

from __future__ import annotations

import csv
import importlib
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = REPORT_DIR / "phase3_scenario_overlay_check_report.txt"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


REQUIRED_FILES = [
    ("Scenario overlay model", PROJECT_ROOT / "app" / "paid_simulator" / "phase3_scenario_overlay_model.py"),
    ("Scenario overlay check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py"),
    ("Scenario overlay documentation", PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_model.md"),
]

EXPECTED_OUTPUTS = [
    ("Scenario overlay CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3_scenario_overlay.csv"),
    ("Scenario overlay HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_scenario_overlay.html"),
    ("Scenario overlay summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_scenario_overlay_summary.txt"),
]


def line(title: str = "") -> str:
    if title:
        return f"\n{title}\n" + "-" * 96
    return "-" * 96


def check_file(label: str, path: Path) -> tuple[bool, str]:
    ok = path.exists()
    status = "FOUND" if ok else "MISSING"
    return ok, f"{status:<10} {label:<45} {path}"


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return sum(1 for _ in csv.DictReader(f))


def main() -> int:
    messages: list[str] = []
    messages.append("=" * 96)
    messages.append("Phase 3B scenario-overlay check")
    messages.append("=" * 96)
    messages.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    messages.append(f"Project root: {PROJECT_ROOT}")

    all_ok = True

    messages.append(line("Required files"))
    for label, path in REQUIRED_FILES:
        ok, msg = check_file(label, path)
        all_ok = all_ok and ok
        messages.append(msg)

    messages.append(line("Running scenario-overlay model"))
    try:
        module = importlib.import_module("paid_simulator.phase3_scenario_overlay_model")
        outputs = module.run(PROJECT_ROOT)
        messages.append("PASS       Scenario-overlay model ran successfully")
        for key, value in outputs.items():
            messages.append(f"OUTPUT     {key:<40} {value}")
    except Exception as exc:
        all_ok = False
        messages.append(f"FAIL       Scenario-overlay model failed: {exc}")

    messages.append(line("Expected outputs"))
    for label, path in EXPECTED_OUTPUTS:
        ok, msg = check_file(label, path)
        all_ok = all_ok and ok
        messages.append(msg)

    messages.append(line("CSV row checks"))
    overlay_csv = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3_scenario_overlay.csv"
    row_count = count_csv_rows(overlay_csv)
    if row_count >= 5:
        messages.append(f"PASS       phase3_scenario_overlay.csv              rows={row_count}")
    else:
        all_ok = False
        messages.append(f"FAIL       phase3_scenario_overlay.csv              rows={row_count}")

    messages.append(line("Summary markers"))
    summary = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_scenario_overlay_summary.txt"
    summary_text = summary.read_text(encoding="utf-8", errors="replace") if summary.exists() else ""
    for marker in ["Phase 3 scenario overlay", "Overall: PASS", "Breakeven price"]:
        if marker in summary_text:
            messages.append(f"PASS       Summary marker '{marker}'")
        else:
            all_ok = False
            messages.append(f"FAIL       Summary marker '{marker}'")

    messages.append("\n" + "=" * 96)
    if all_ok:
        messages.append("Overall Phase 3B scenario-overlay status: PASS")
        exit_code = 0
    else:
        messages.append("Overall Phase 3B scenario-overlay status: REVIEW")
        exit_code = 1
    messages.append("=" * 96)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CHECK_REPORT.write_text("\n".join(messages) + "\n", encoding="utf-8")
    messages.append(f"\nSaved check report: {CHECK_REPORT}")

    print("\n".join(messages))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
