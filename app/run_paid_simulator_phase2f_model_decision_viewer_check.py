"""
run_paid_simulator_phase2f_model_decision_viewer_check.py

Phase 2F model-decision viewer check.

This checker verifies that the standalone Phase 2F model-decision viewer is
installed and that the expected Phase 2F model-decision outputs are present.

Marker-fix note:
The prior version required the exact phrase "CANDIDATE FOR CONTROLLED PROMOTION"
to appear in the viewer source code. That was too strict because the viewer is
allowed to display decision labels from data rather than hard-code every possible
label. This version checks the structural viewer markers and treats the exact
promotion-label string as optional/data-driven.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

VIEWER_APP = PROJECT_ROOT / "app" / "paid_simulator" / "phase2f_model_decision_viewer.py"
VIEWER_LAUNCHER = PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_viewer.py"
VIEWER_CHECK = PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_viewer_check.py"
VIEWER_DOC = PROJECT_ROOT / "docs" / "paid_simulator_phase2f_model_decision_viewer.md"

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = REPORT_DIR / "phase2f_model_decision_viewer_check_report.txt"

MODEL_DECISION_CSV = TABLE_DIR / "model_decision_summary.csv"
MODEL_DECISION_HTML = REPORT_DIR / "model_decision_summary.html"
MODEL_DECISION_TEXT = REPORT_DIR / "model_decision_summary.txt"
MODEL_DECISION_CHECK_REPORT = REPORT_DIR / "phase2f_model_decision_summary_check_report.txt"

CONTEXT_OUTPUTS = [
    ("Option premium CSV", TABLE_DIR / "option_premium_scaffold.csv"),
    ("Premium-aware payoff CSV", TABLE_DIR / "premium_aware_payoff_scaffold.csv"),
    ("Premium validation CSV", TABLE_DIR / "premium_model_validation_scaffold.csv"),
    ("Premium tuning recommendations CSV", TABLE_DIR / "premium_model_tuning_recommendations.csv"),
    ("Adjusted premiums CSV", TABLE_DIR / "premium_model_adjusted_premiums.csv"),
    ("Adjusted payoff comparison CSV", TABLE_DIR / "adjusted_premium_payoff_comparison.csv"),
]


def line(char: str = "=", width: int = 96) -> str:
    return char * width


def status_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<48} {detail}"


def file_status(label: str, path: Path) -> tuple[bool, str]:
    if path.exists():
        return True, status_line("FOUND", label, str(path))
    return False, status_line("MISSING", label, str(path))


def csv_row_count(path: Path) -> tuple[bool, str, int]:
    if not path.exists():
        return False, status_line("MISSING", path.name, str(path)), 0
    if pd is None:
        return False, status_line("REVIEW", path.name, "pandas is not installed"), 0
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover
        return False, status_line("REVIEW", path.name, f"could not read CSV: {exc}"), 0
    rows = len(df)
    if rows > 0:
        return True, status_line("PASS", path.name, f"rows={rows}"), rows
    return False, status_line("REVIEW", path.name, "rows=0"), rows


def source_contains(path: Path, marker: str) -> bool:
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    return marker in text


def csv_contains_value(path: Path, target: str) -> bool:
    if not path.exists() or pd is None:
        return False
    try:
        df = pd.read_csv(path).astype(str)
    except Exception:
        return False
    target_upper = target.upper()
    for column in df.columns:
        if df[column].str.upper().str.contains(target_upper, regex=False, na=False).any():
            return True
    return False


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    ok = True

    lines.append(line())
    lines.append("Phase 2F model-decision viewer check")
    lines.append(line())
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    lines.append("Required viewer files")
    lines.append(line("-"))
    required_files = [
        ("Phase 2F viewer app", VIEWER_APP),
        ("Phase 2F viewer launcher", VIEWER_LAUNCHER),
        ("Phase 2F viewer check", VIEWER_CHECK),
        ("Phase 2F viewer documentation", VIEWER_DOC),
    ]
    for label, path in required_files:
        passed, msg = file_status(label, path)
        ok = ok and passed
        lines.append(msg)
    lines.append("")

    lines.append("Expected Phase 2F outputs")
    lines.append(line("-"))
    phase2f_outputs = [
        ("Model decision CSV", MODEL_DECISION_CSV),
        ("Model decision HTML", MODEL_DECISION_HTML),
        ("Model decision text summary", MODEL_DECISION_TEXT),
        ("Model decision check report", MODEL_DECISION_CHECK_REPORT),
    ]
    for label, path in phase2f_outputs:
        passed, msg = file_status(label, path)
        ok = ok and passed
        lines.append(msg)
    lines.append("")

    lines.append("Phase 2F context outputs")
    lines.append(line("-"))
    for label, path in CONTEXT_OUTPUTS:
        passed, msg = file_status(label, path)
        ok = ok and passed
        lines.append(msg)
    lines.append("")

    lines.append("CSV row checks")
    lines.append(line("-"))
    rows_ok, rows_msg, _ = csv_row_count(MODEL_DECISION_CSV)
    ok = ok and rows_ok
    lines.append(rows_msg)
    lines.append("")

    lines.append("Viewer source markers")
    lines.append(line("-"))
    required_markers = [
        "Phase 2F model-decision viewer",
        "Model decisions",
        "Promotion candidates",
        "model_decision_summary.csv",
    ]
    for marker in required_markers:
        if source_contains(VIEWER_APP, marker):
            lines.append(status_line("PASS", f"Viewer marker '{marker}'"))
        else:
            ok = False
            lines.append(status_line("REVIEW", f"Viewer marker '{marker}'"))

    optional_marker = "CANDIDATE FOR CONTROLLED PROMOTION"
    if source_contains(VIEWER_APP, optional_marker):
        lines.append(status_line("PASS", f"Optional label marker '{optional_marker}'", "found in viewer source"))
    elif csv_contains_value(MODEL_DECISION_CSV, optional_marker):
        lines.append(status_line("PASS", f"Optional label marker '{optional_marker}'", "found in model-decision data"))
    else:
        lines.append(status_line("PASS", f"Optional label marker '{optional_marker}'", "not required; decision labels are data-driven"))
    lines.append("")

    lines.append(line())
    if ok:
        lines.append("Overall Phase 2F model-decision viewer status: PASS")
        lines.append("Phase 2F model-decision viewer is installed and has the required outputs.")
        exit_code = 0
    else:
        lines.append("Overall Phase 2F model-decision viewer status: REVIEW")
        lines.append("One or more Phase 2F model-decision viewer items need attention.")
        exit_code = 1
    lines.append(line())
    lines.append("")
    lines.append(f"Saved check report: {CHECK_REPORT}")

    output = "\n".join(lines)
    print(output)
    CHECK_REPORT.write_text(output, encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
