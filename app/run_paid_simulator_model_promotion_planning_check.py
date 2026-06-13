"""
run_paid_simulator_model_promotion_planning_check.py

Check runner for the Phase 2G controlled model-promotion planning scaffold.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.model_promotion_planning import (  # noqa: E402
    MODEL_DECISION_CSV,
    PROMOTION_PLAN_CSV,
    PROMOTION_PLAN_HTML,
    PROMOTION_PLAN_TEXT,
    generate_model_promotion_plan,
)

REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2g_model_promotion_planning_check_report.txt"


def status_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<55} {detail}"


def check_file(label: str, path: Path, lines: list[str]) -> bool:
    exists = path.exists()
    lines.append(status_line("FOUND" if exists else "MISSING", label, str(path)))
    return exists


def check_csv_rows(label: str, path: Path, lines: list[str]) -> bool:
    if not path.exists():
        lines.append(status_line("MISSING", label, str(path)))
        return False
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        lines.append(status_line("REVIEW", label, f"Could not read CSV: {exc}"))
        return False
    if len(df) <= 0:
        lines.append(status_line("REVIEW", label, "rows=0"))
        return False
    lines.append(status_line("PASS", label, f"rows={len(df)}"))
    return True


def main() -> int:
    lines: list[str] = []
    lines.append("=" * 96)
    lines.append("Phase 2G controlled model-promotion planning check")
    lines.append("=" * 96)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    all_ok = True

    lines.append("Required source files")
    lines.append("-" * 96)
    all_ok &= check_file(
        "Model-promotion planning module",
        PROJECT_ROOT / "app" / "paid_simulator" / "model_promotion_planning.py",
        lines,
    )
    all_ok &= check_file(
        "Model-promotion planning check",
        CURRENT_FILE,
        lines,
    )
    all_ok &= check_file(
        "Phase 2G documentation",
        PROJECT_ROOT / "docs" / "paid_simulator_phase2g_model_promotion_planning.md",
        lines,
    )
    lines.append("")

    lines.append("Required Phase 2F input")
    lines.append("-" * 96)
    all_ok &= check_file("Model decision CSV", MODEL_DECISION_CSV, lines)
    lines.append("")

    try:
        result = generate_model_promotion_plan()
        lines.append("Generation")
        lines.append("-" * 96)
        lines.append(status_line("PASS", "Generated Phase 2G promotion plan", str(result.csv_path)))
    except Exception as exc:
        all_ok = False
        lines.append("Generation")
        lines.append("-" * 96)
        lines.append(status_line("REVIEW", "Generated Phase 2G promotion plan", str(exc)))
    lines.append("")

    lines.append("Expected Phase 2G outputs")
    lines.append("-" * 96)
    all_ok &= check_file("Model promotion CSV", PROMOTION_PLAN_CSV, lines)
    all_ok &= check_file("Model promotion HTML", PROMOTION_PLAN_HTML, lines)
    all_ok &= check_file("Model promotion text summary", PROMOTION_PLAN_TEXT, lines)
    lines.append("")

    lines.append("CSV row checks")
    lines.append("-" * 96)
    all_ok &= check_csv_rows("model_promotion_plan.csv", PROMOTION_PLAN_CSV, lines)
    lines.append("")

    lines.append("Summary markers")
    lines.append("-" * 96)
    summary_text = PROMOTION_PLAN_TEXT.read_text(encoding="utf-8") if PROMOTION_PLAN_TEXT.exists() else ""
    for marker in ["Phase 2G", "controlled model-promotion", "Developer view only"]:
        found = marker.lower() in summary_text.lower()
        all_ok &= found
        lines.append(status_line("PASS" if found else "REVIEW", f"Summary marker '{marker}'", marker))
    lines.append("")

    lines.append("=" * 96)
    if all_ok:
        lines.append("Overall Phase 2G model-promotion planning status: PASS")
        exit_code = 0
    else:
        lines.append("Overall Phase 2G model-promotion planning status: REVIEW")
        lines.append("One or more Phase 2G planning items need attention before the next step.")
        exit_code = 1
    lines.append("=" * 96)
    lines.append("")
    lines.append(f"Saved check report: {REPORT_PATH}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
