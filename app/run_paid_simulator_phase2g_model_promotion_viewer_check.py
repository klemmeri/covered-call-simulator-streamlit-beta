"""
run_paid_simulator_phase2g_model_promotion_viewer_check.py

Installation/readiness check for the standalone Phase 2G model-promotion viewer.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHECK_REPORT = REPORT_DIR / "phase2g_model_promotion_viewer_check_report.txt"

REQUIRED_FILES = [
    ("Phase 2G viewer app", PAID_DIR / "phase2g_model_promotion_viewer.py"),
    ("Phase 2G viewer launcher", APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer.py"),
    ("Phase 2G viewer check", APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer_check.py"),
    ("Phase 2G viewer documentation", DOCS_DIR / "paid_simulator_phase2g_model_promotion_viewer.md"),
]

EXPECTED_OUTPUTS = [
    ("Model promotion plan CSV", TABLE_DIR / "model_promotion_plan.csv"),
    ("Model promotion plan HTML", REPORT_DIR / "model_promotion_plan.html"),
    ("Model promotion plan text", REPORT_DIR / "model_promotion_plan.txt"),
    ("Phase 2G planning check report", REPORT_DIR / "phase2g_model_promotion_planning_check_report.txt"),
    ("Model decision CSV", TABLE_DIR / "model_decision_summary.csv"),
]

VIEWER_MARKERS = [
    "Phase 2G model-promotion viewer",
    "Promotion plan",
    "Promotion candidates",
    "model_promotion_plan.csv",
    "Phase 2G planning check",
]


def line(title: str = "", char: str = "=") -> str:
    if title:
        return f"{title}\n" + char * 96
    return char * 96


def status_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<48} {detail}"


def check_file(label: str, path: Path) -> tuple[bool, str]:
    if path.exists():
        return True, status_line("FOUND", label, str(path))
    return False, status_line("MISSING", label, str(path))


def check_csv_rows(label: str, path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, status_line("MISSING", label, str(path))
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        return False, status_line("REVIEW", label, f"Could not read CSV: {exc}")
    if len(df) <= 0:
        return False, status_line("REVIEW", label, "rows=0")
    return True, status_line("PASS", label, f"rows={len(df)}")


def main() -> int:
    rows: list[str] = []
    ok = True

    rows.append(line("Phase 2G model-promotion viewer check"))
    rows.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rows.append(f"Project root: {PROJECT_ROOT}")
    rows.append("")

    rows.append(line("Required viewer files", "-"))
    for label, path in REQUIRED_FILES:
        passed, text = check_file(label, path)
        ok = ok and passed
        rows.append(text)
    rows.append("")

    rows.append(line("Expected Phase 2G outputs", "-"))
    for label, path in EXPECTED_OUTPUTS:
        passed, text = check_file(label, path)
        ok = ok and passed
        rows.append(text)
    rows.append("")

    rows.append(line("CSV row checks", "-"))
    passed, text = check_csv_rows("model_promotion_plan.csv", TABLE_DIR / "model_promotion_plan.csv")
    ok = ok and passed
    rows.append(text)
    rows.append("")

    rows.append(line("Viewer source markers", "-"))
    viewer_path = PAID_DIR / "phase2g_model_promotion_viewer.py"
    if viewer_path.exists():
        source = viewer_path.read_text(encoding="utf-8", errors="replace")
        for marker in VIEWER_MARKERS:
            if marker in source:
                rows.append(status_line("PASS", f"Viewer marker '{marker}'"))
            else:
                ok = False
                rows.append(status_line("REVIEW", f"Viewer marker '{marker}'"))
    else:
        ok = False
        rows.append(status_line("MISSING", "Viewer source", str(viewer_path)))
    rows.append("")

    rows.append(line())
    if ok:
        rows.append("Overall Phase 2G model-promotion viewer status: PASS")
    else:
        rows.append("Overall Phase 2G model-promotion viewer status: REVIEW")
        rows.append("One or more Phase 2G model-promotion viewer items need attention.")
    rows.append(line())
    rows.append("")
    rows.append(f"Saved check report: {CHECK_REPORT}")

    output = "\n".join(rows)
    CHECK_REPORT.write_text(output, encoding="utf-8")
    print(output)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
