"""
Check script for the Phase 3 interactive covered-call payoff viewer.

This is intentionally a lightweight static/runtime check. It verifies that the
new files are present, the viewer source contains the required markers, and the
pure payoff calculation functions work for a default covered-call setup.
"""

from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

VIEWER_FILE = PAID_SIMULATOR_DIR / "phase3_interactive_payoff_viewer.py"
LAUNCHER_FILE = APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer.py"
CHECK_FILE = APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py"
DOC_FILE = DOCS_DIR / "paid_simulator_phase3_interactive_payoff_viewer.md"
REPORT_FILE = REPORT_DIR / "phase3_interactive_payoff_viewer_check_report.txt"


def status_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<55} {detail}"


def load_viewer_module():
    spec = importlib.util.spec_from_file_location("phase3_interactive_payoff_viewer", VIEWER_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create import specification for viewer module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules["phase3_interactive_payoff_viewer"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    lines: list[str] = []
    failures = 0

    lines.append("=" * 96)
    lines.append("Phase 3 interactive covered-call payoff viewer check")
    lines.append("=" * 96)
    lines.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    required_files = [
        ("Phase 3 viewer app", VIEWER_FILE),
        ("Phase 3 viewer launcher", LAUNCHER_FILE),
        ("Phase 3 viewer check", CHECK_FILE),
        ("Phase 3 viewer documentation", DOC_FILE),
    ]

    lines.append("Required files")
    lines.append("-" * 96)
    for label, path in required_files:
        if path.exists():
            lines.append(status_line("FOUND", label, str(path)))
        else:
            lines.append(status_line("MISSING", label, str(path)))
            failures += 1
    lines.append("")

    if VIEWER_FILE.exists():
        source = VIEWER_FILE.read_text(encoding="utf-8", errors="replace")
        markers = [
            "Phase 3: Interactive Covered-Call Payoff Viewer",
            "CoveredCallInputs",
            "covered_call_payoff",
            "build_payoff_table",
            "Break-even",
            "Assignment zone",
            "phase3_interactive_payoff_snapshot.csv",
        ]
        lines.append("Viewer source markers")
        lines.append("-" * 96)
        for marker in markers:
            if marker in source:
                lines.append(status_line("PASS", f"Viewer marker '{marker}'"))
            else:
                lines.append(status_line("REVIEW", f"Viewer marker '{marker}'"))
                failures += 1
        lines.append("")

    if failures == 0:
        try:
            module = load_viewer_module()
            inputs = module.CoveredCallInputs(
                ticker="SPY",
                current_price=545.25,
                shares=100,
                strike_price=555.00,
                premium_per_share=4.20,
                dte=30,
                call_delta=0.30,
                contracts=1,
            )
            payoff_df = module.build_payoff_table(inputs)
            scenario_df = module.build_scenario_table(inputs)
            row = module.covered_call_payoff(inputs, 555.00)

            lines.append("Runtime calculation checks")
            lines.append("-" * 96)
            if len(payoff_df) >= 50:
                lines.append(status_line("PASS", "Payoff grid row count", f"rows={len(payoff_df)}"))
            else:
                lines.append(status_line("REVIEW", "Payoff grid row count", f"rows={len(payoff_df)}"))
                failures += 1

            if len(scenario_df) == 7:
                lines.append(status_line("PASS", "Scenario table row count", f"rows={len(scenario_df)}"))
            else:
                lines.append(status_line("REVIEW", "Scenario table row count", f"rows={len(scenario_df)}"))
                failures += 1

            if row["covered_call_pl"] >= row["buy_hold_pl"]:
                lines.append(status_line("PASS", "At strike, covered-call P/L includes premium", str(row)))
            else:
                lines.append(status_line("REVIEW", "At strike, covered-call P/L check", str(row)))
                failures += 1
            lines.append("")
        except Exception as exc:  # pragma: no cover - check script report
            lines.append("Runtime calculation checks")
            lines.append("-" * 96)
            lines.append(status_line("FAILED", "Runtime calculation import/test", repr(exc)))
            lines.append("")
            failures += 1

    lines.append("=" * 96)
    if failures == 0:
        lines.append("Overall Phase 3 interactive payoff viewer status: PASS")
    else:
        lines.append("Overall Phase 3 interactive payoff viewer status: REVIEW")
        lines.append("One or more Phase 3 viewer items need attention before dashboard integration.")
    lines.append("=" * 96)

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSaved check report: {REPORT_FILE}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
