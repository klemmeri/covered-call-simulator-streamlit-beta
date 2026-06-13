"""
Check installation of the Phase 3C richer graphical payoff viewer.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3c_rich_payoff_viewer_check_report.txt"

REQUIRED_FILES = [
    ("Phase 3C viewer app", PAID_DIR / "phase3c_rich_payoff_viewer.py"),
    ("Phase 3C viewer launcher", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer.py"),
    ("Phase 3C viewer check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"),
    ("Phase 3C documentation", DOCS_DIR / "paid_simulator_phase3c_rich_payoff_viewer.md"),
]

OPTIONAL_OUTPUTS = [
    ("Phase 3C snapshot CSV", TABLE_DIR / "phase3c_rich_payoff_snapshot.csv"),
    ("Phase 3C snapshot HTML", REPORT_DIR / "phase3c_rich_payoff_snapshot.html"),
]

SOURCE_MARKERS = [
    "Phase 3C richer graphical covered-call payoff viewer",
    "Payoff graph",
    "Scenario overlay",
    "Save Phase 3C payoff snapshot",
    "phase3c_rich_payoff_snapshot.csv",
]


def line(label: str = "", char: str = "-") -> str:
    if label:
        return f"{label}\n" + char * 96
    return char * 96


def status_row(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<45} {detail}"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output: list[str] = []
    failures = 0
    optional_missing = 0

    output.append(line("Phase 3C richer graphical payoff viewer check", "="))
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Project root: {PROJECT_ROOT}")
    output.append("")

    output.append(line("Required files"))
    for label, path in REQUIRED_FILES:
        if path.exists():
            output.append(status_row("FOUND", label, str(path)))
        else:
            failures += 1
            output.append(status_row("MISSING", label, str(path)))
    output.append("")

    viewer_path = PAID_DIR / "phase3c_rich_payoff_viewer.py"
    output.append(line("Viewer source markers"))
    if viewer_path.exists():
        source = viewer_path.read_text(encoding="utf-8", errors="ignore")
        for marker in SOURCE_MARKERS:
            if marker in source:
                output.append(status_row("PASS", f"Viewer marker '{marker}'", marker))
            else:
                failures += 1
                output.append(status_row("REVIEW", f"Viewer marker '{marker}'", marker))
    else:
        failures += 1
        output.append(status_row("REVIEW", "Viewer source not readable", str(viewer_path)))
    output.append("")

    output.append(line("Optional snapshot outputs"))
    for label, path in OPTIONAL_OUTPUTS:
        if path.exists():
            output.append(status_row("FOUND", label, str(path)))
        else:
            optional_missing += 1
            output.append(status_row("OPTIONAL", label, f"Not found yet: {path}"))
    output.append("")

    output.append(line("Phase 3C viewer result", "="))
    if failures == 0 and optional_missing == 0:
        final_status = "PASS"
        exit_code = 0
    elif failures == 0:
        final_status = "PASS WITH OPTIONAL SNAPSHOT REVIEW"
        exit_code = 0
    else:
        final_status = "REVIEW"
        exit_code = 1

    output.append(f"Overall Phase 3C rich payoff viewer status: {final_status}")
    if final_status == "PASS WITH OPTIONAL SNAPSHOT REVIEW":
        output.append("Only optional snapshot files are missing. This is acceptable before saving a setup from the viewer.")
    elif final_status == "REVIEW":
        output.append("One or more required Phase 3C viewer items need attention.")
    output.append("=" * 96)
    output.append("")
    output.append(f"Saved check report: {REPORT_PATH}")

    text = "\n".join(output)
    print(text)
    REPORT_PATH.write_text(text, encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
