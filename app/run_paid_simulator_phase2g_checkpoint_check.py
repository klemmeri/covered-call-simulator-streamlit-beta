"""
run_paid_simulator_phase2g_checkpoint_check.py

Checkpoint checker for Phase 2G of the Covered Call Strategy Stress Test.

Phase 2G is the controlled model-promotion planning layer. This script checks
that the model-promotion planner, viewer, pipeline, dashboard tab, reports, and
supporting Phase 2B through Phase 2F artifacts are present.

This checker is intentionally conservative about source/output existence and
CSV row counts, but intentionally flexible about text markers. Promotion labels
are data-driven and should not be required to appear as hard-coded source text.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT_PATH = REPORTS_DIR / "phase2g_checkpoint_report.txt"


class CheckRecorder:
    """Collects checkpoint lines and tracks hard failures."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def line(self, text: str = "") -> None:
        self.lines.append(text)
        print(text)

    def section(self, title: str) -> None:
        self.line("")
        self.line(title)
        self.line("-" * 96)

    def status(self, status: str, label: str, detail: str = "", hard_fail: bool = True) -> None:
        if detail:
            rendered = f"{status:<10} {label:<55} {detail}"
        else:
            rendered = f"{status:<10} {label}"
        self.line(rendered)
        if status in {"MISSING", "FAIL"} and hard_fail:
            self.failures.append(label)
        elif status in {"REVIEW", "WARNING"}:
            self.warnings.append(label)


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        if not rows:
            return 0
        return max(0, len(rows) - 1)
    except Exception:
        return 0


def check_files(rec: CheckRecorder, title: str, items: Iterable[tuple[str, Path]]) -> None:
    rec.section(title)
    for label, path in items:
        if path.exists():
            rec.status("FOUND", label, str(path))
        else:
            rec.status("MISSING", label, str(path))


def check_csv_rows(rec: CheckRecorder, items: Iterable[tuple[str, Path]]) -> None:
    rec.section("CSV row checks")
    for label, path in items:
        if not path.exists():
            rec.status("MISSING", label, str(path))
            continue
        rows = csv_row_count(path)
        if rows > 0:
            rec.status("PASS", label, f"rows={rows}")
        else:
            rec.status("FAIL", label, "rows=0")


def check_text_markers(
    rec: CheckRecorder,
    title: str,
    path: Path,
    markers: Iterable[str],
    hard_fail: bool = False,
) -> None:
    rec.section(title)
    if not path.exists():
        rec.status("MISSING", f"Marker source {path.name}", str(path), hard_fail=hard_fail)
        return
    text = read_text_safe(path).lower()
    for marker in markers:
        if marker.lower() in text:
            rec.status("PASS", f"Marker '{marker}'", marker, hard_fail=hard_fail)
        else:
            status = "REVIEW" if not hard_fail else "FAIL"
            rec.status(status, f"Marker '{marker}'", marker, hard_fail=hard_fail)


def main() -> int:
    rec = CheckRecorder()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rec.line("=" * 96)
    rec.line("Phase 2G controlled model-promotion checkpoint check")
    rec.line("=" * 96)
    rec.line(f"Generated: {generated}")
    rec.line(f"Project root: {PROJECT_ROOT}")

    check_files(
        rec,
        "Required Phase 2B through Phase 2G source files",
        [
            ("Option premium model", PAID_SIMULATOR_DIR / "option_premium_model.py"),
            ("Premium-aware payoff runner", PAID_SIMULATOR_DIR / "premium_aware_payoff_runner.py"),
            ("Premium-vs-scaffold comparison", PAID_SIMULATOR_DIR / "premium_vs_scaffold_comparison.py"),
            ("Premium-model validation module", PAID_SIMULATOR_DIR / "premium_model_validation.py"),
            ("Premium-model tuning module", PAID_SIMULATOR_DIR / "premium_model_tuning.py"),
            ("Premium-model adjustment module", PAID_SIMULATOR_DIR / "premium_model_adjustment.py"),
            ("Adjusted premium payoff comparison", PAID_SIMULATOR_DIR / "adjusted_premium_payoff_comparison.py"),
            ("Model-decision summary module", PAID_SIMULATOR_DIR / "model_decision_summary.py"),
            ("Model-promotion planning module", PAID_SIMULATOR_DIR / "model_promotion_planning.py"),
            ("Phase 2G model-promotion viewer", PAID_SIMULATOR_DIR / "phase2g_model_promotion_viewer.py"),
            ("Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py"),
            ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
        ],
    )

    check_files(
        rec,
        "Required Phase 2G runner/check files",
        [
            ("Phase 2F checkpoint check", APP_DIR / "run_paid_simulator_phase2f_checkpoint_check.py"),
            ("Model-promotion planning check", APP_DIR / "run_paid_simulator_model_promotion_planning_check.py"),
            ("Phase 2G viewer launcher", APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer.py"),
            ("Phase 2G viewer check", APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer_check.py"),
            ("Phase 2G pipeline check", APP_DIR / "run_paid_simulator_phase2g_model_promotion_pipeline_check.py"),
            ("Phase 2G dashboard-tab check", APP_DIR / "run_paid_simulator_phase2g_dashboard_tab_check.py"),
            ("Phase 2G integration-readiness check", APP_DIR / "run_paid_simulator_phase2g_integration_readiness_check.py"),
        ],
    )

    check_files(
        rec,
        "Required Phase 2B through Phase 2E config files",
        [
            ("Premium-model validation config", CONFIG_DIR / "premium_model_validation_config.json"),
            ("Premium-model tuning config", CONFIG_DIR / "premium_model_tuning_config.json"),
            ("Premium-model adjustment config", CONFIG_DIR / "premium_model_adjustment_config.json"),
        ],
    )

    check_files(
        rec,
        "Expected Phase 2B through Phase 2G generated outputs",
        [
            ("Option premium CSV", TABLES_DIR / "option_premium_scaffold.csv"),
            ("Premium-aware payoff CSV", TABLES_DIR / "premium_aware_payoff_scaffold.csv"),
            ("Premium-aware payoff HTML", REPORTS_DIR / "premium_aware_payoff_scaffold.html"),
            ("Premium-vs-scaffold CSV", TABLES_DIR / "premium_vs_scaffold_comparison.csv"),
            ("Premium-vs-scaffold HTML", REPORTS_DIR / "premium_vs_scaffold_comparison.html"),
            ("Premium validation CSV", TABLES_DIR / "premium_model_validation_scaffold.csv"),
            ("Premium validation HTML", REPORTS_DIR / "premium_model_validation_scaffold.html"),
            ("Premium validation summary", REPORTS_DIR / "premium_model_validation_summary.txt"),
            ("Premium tuning recommendations CSV", TABLES_DIR / "premium_model_tuning_recommendations.csv"),
            ("Premium tuning recommendations HTML", REPORTS_DIR / "premium_model_tuning_recommendations.html"),
            ("Premium tuning summary", REPORTS_DIR / "premium_model_tuning_summary.txt"),
            ("Adjusted premiums CSV", TABLES_DIR / "premium_model_adjusted_premiums.csv"),
            ("Premium adjustment comparison HTML", REPORTS_DIR / "premium_model_adjustment_comparison.html"),
            ("Premium adjustment summary", REPORTS_DIR / "premium_model_adjustment_summary.txt"),
            ("Adjusted payoff comparison CSV", TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
            ("Adjusted payoff comparison HTML", REPORTS_DIR / "adjusted_premium_payoff_comparison.html"),
            ("Adjusted payoff summary", REPORTS_DIR / "adjusted_premium_payoff_summary.txt"),
            ("Model decision CSV", TABLES_DIR / "model_decision_summary.csv"),
            ("Model decision HTML", REPORTS_DIR / "model_decision_summary.html"),
            ("Model decision text summary", REPORTS_DIR / "model_decision_summary.txt"),
            ("Model promotion plan CSV", TABLES_DIR / "model_promotion_plan.csv"),
            ("Model promotion plan HTML", REPORTS_DIR / "model_promotion_plan.html"),
            ("Model promotion plan text summary", REPORTS_DIR / "model_promotion_plan.txt"),
            ("Phase 2G planning check report", REPORTS_DIR / "phase2g_model_promotion_planning_check_report.txt"),
            ("Phase 2G viewer check report", REPORTS_DIR / "phase2g_model_promotion_viewer_check_report.txt"),
            ("Phase 2G pipeline report", REPORTS_DIR / "phase2g_model_promotion_pipeline_report.txt"),
            ("Phase 2G integration-readiness report", REPORTS_DIR / "phase2g_integration_readiness_report.txt"),
        ],
    )

    check_files(
        rec,
        "Phase 2B through Phase 2G documentation",
        [
            ("Option premium model scaffold", DOCS_DIR / "paid_simulator_phase2_option_premium_model_scaffold.md"),
            ("Premium-aware payoff", DOCS_DIR / "paid_simulator_phase2b_premium_aware_payoff.md"),
            ("Premium-vs-scaffold comparison", DOCS_DIR / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md"),
            ("Phase 2B checkpoint summary", DOCS_DIR / "paid_simulator_phase2b_checkpoint_summary.md"),
            ("Premium-model validation", DOCS_DIR / "paid_simulator_phase2c_premium_model_validation.md"),
            ("Phase 2C checkpoint summary", DOCS_DIR / "paid_simulator_phase2c_checkpoint_summary.md"),
            ("Premium-model tuning", DOCS_DIR / "paid_simulator_phase2d_premium_model_tuning.md"),
            ("Phase 2D checkpoint summary", DOCS_DIR / "paid_simulator_phase2d_checkpoint_summary.md"),
            ("Premium-model adjustment", DOCS_DIR / "paid_simulator_phase2e_premium_model_adjustment.md"),
            ("Adjusted premium payoff comparison", DOCS_DIR / "paid_simulator_phase2e_adjusted_premium_payoff_comparison.md"),
            ("Phase 2E checkpoint summary", DOCS_DIR / "paid_simulator_phase2e_checkpoint_summary.md"),
            ("Model-decision summary", DOCS_DIR / "paid_simulator_phase2f_model_decision_summary.md"),
            ("Phase 2F checkpoint summary", DOCS_DIR / "paid_simulator_phase2f_checkpoint_summary.md"),
            ("Model-promotion planning", DOCS_DIR / "paid_simulator_phase2g_model_promotion_planning.md"),
            ("Model-promotion viewer", DOCS_DIR / "paid_simulator_phase2g_model_promotion_viewer.md"),
            ("Model-promotion pipeline", DOCS_DIR / "paid_simulator_phase2g_model_promotion_pipeline_check.md"),
            ("Phase 2G dashboard tab", DOCS_DIR / "paid_simulator_phase2g_dashboard_tab.md"),
            ("Phase 2G integration readiness", DOCS_DIR / "paid_simulator_phase2g_integration_readiness.md"),
            ("Phase 2G checkpoint summary", DOCS_DIR / "paid_simulator_phase2g_checkpoint_summary.md"),
        ],
    )

    check_csv_rows(
        rec,
        [
            ("option_premium_scaffold.csv", TABLES_DIR / "option_premium_scaffold.csv"),
            ("premium_aware_payoff_scaffold.csv", TABLES_DIR / "premium_aware_payoff_scaffold.csv"),
            ("premium_model_validation_scaffold.csv", TABLES_DIR / "premium_model_validation_scaffold.csv"),
            ("premium_model_tuning_recommendations.csv", TABLES_DIR / "premium_model_tuning_recommendations.csv"),
            ("premium_model_adjusted_premiums.csv", TABLES_DIR / "premium_model_adjusted_premiums.csv"),
            ("adjusted_premium_payoff_comparison.csv", TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
            ("model_decision_summary.csv", TABLES_DIR / "model_decision_summary.csv"),
            ("model_promotion_plan.csv", TABLES_DIR / "model_promotion_plan.csv"),
        ],
    )

    check_text_markers(
        rec,
        "Main dashboard Phase 2G tab markers",
        PAID_SIMULATOR_DIR / "config_form_app.py",
        [
            "Phase 2B premium model",
            "Phase 2C validation",
            "Phase 2D tuning",
            "Phase 2E adjustment",
            "Phase 2F model decision",
            "Phase 2G model promotion",
            "phase2g_model_promotion_viewer",
            "run_paid_simulator_phase2g_model_promotion_pipeline_check.py",
        ],
        hard_fail=False,
    )

    check_text_markers(
        rec,
        "Model-promotion plan summary markers",
        REPORTS_DIR / "model_promotion_plan.txt",
        [
            "promotion",
            "model",
        ],
        hard_fail=False,
    )

    rec.line("")
    rec.line("=" * 96)
    if rec.failures:
        rec.line("Overall Phase 2G checkpoint status: REVIEW")
        rec.line("One or more Phase 2G checkpoint items need attention before Phase 3 planning.")
        exit_code = 1
    else:
        rec.line("Overall Phase 2G checkpoint status: PASS")
        if rec.warnings:
            rec.line("Non-blocking review markers were noted, but all hard checkpoint items passed.")
        else:
            rec.line("All Phase 2G checkpoint items passed.")
        exit_code = 0
    rec.line("=" * 96)

    CHECK_REPORT_PATH.write_text("\n".join(rec.lines) + "\n", encoding="utf-8")
    rec.line(f"\nSaved checkpoint report: {CHECK_REPORT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
