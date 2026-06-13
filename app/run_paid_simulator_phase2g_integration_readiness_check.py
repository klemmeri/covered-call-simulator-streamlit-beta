"""
run_paid_simulator_phase2g_integration_readiness_check.py

Phase 2G integration-readiness checker for the Covered Call Strategy Stress Test.

This script verifies that the Phase 2G controlled model-promotion planning layer
is installed, that its standalone viewer and pipeline checker exist, that the
expected generated outputs are present, and that the Developer-view-only Phase 2G
main-dashboard tab markers are present.

It is intentionally read-only except for writing a plain-text readiness report.
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
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

REPORT_PATH = OUTPUT_REPORTS_DIR / "phase2g_integration_readiness_report.txt"


class CheckLogger:
    """Collects and prints check lines in a consistent format."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures = 0
        self.reviews = 0

    def write(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def section(self, title: str) -> None:
        self.write("")
        self.write(title)
        self.write("-" * 96)

    def result(self, status: str, label: str, detail: str = "") -> None:
        if status == "MISSING" or status == "FAIL":
            self.failures += 1
        elif status == "REVIEW":
            self.reviews += 1
        detail_text = f" {detail}" if detail else ""
        self.write(f"{status:<10} {label:<48} {detail_text}")

    def save(self) -> None:
        OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def file_exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def check_files(logger: CheckLogger, title: str, items: Iterable[tuple[str, Path]]) -> None:
    logger.section(title)
    for label, path in items:
        if file_exists(path):
            logger.result("FOUND", label, str(path))
        else:
            logger.result("MISSING", label, str(path))


def count_csv_rows(path: Path) -> int | None:
    if not file_exists(path):
        return None
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return sum(1 for _ in reader)
    except Exception:
        return None


def read_text(path: Path) -> str:
    if not file_exists(path):
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    text_lower = text.lower()
    return any(phrase.lower() in text_lower for phrase in phrases)


def main() -> int:
    logger = CheckLogger()

    logger.write("=" * 96)
    logger.write("Phase 2G model-promotion integration-readiness check")
    logger.write("=" * 96)
    logger.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.write(f"Project root: {PROJECT_ROOT}")

    source_files = [
        ("Model-promotion planning module", PAID_SIMULATOR_DIR / "model_promotion_planning.py"),
        ("Phase 2G model-promotion viewer", PAID_SIMULATOR_DIR / "phase2g_model_promotion_viewer.py"),
        ("Model-decision summary module", PAID_SIMULATOR_DIR / "model_decision_summary.py"),
        ("Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py"),
        ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
    ]
    check_files(logger, "Required Phase 2G source files", source_files)

    runner_files = [
        ("Model-promotion planning check", APP_DIR / "run_paid_simulator_model_promotion_planning_check.py"),
        ("Phase 2G viewer launcher", APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer.py"),
        ("Phase 2G viewer check", APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer_check.py"),
        ("Phase 2G pipeline check", APP_DIR / "run_paid_simulator_phase2g_model_promotion_pipeline_check.py"),
        ("Phase 2G dashboard-tab check", APP_DIR / "run_paid_simulator_phase2g_dashboard_tab_check.py"),
        ("Phase 2F checkpoint check", APP_DIR / "run_paid_simulator_phase2f_checkpoint_check.py"),
    ]
    check_files(logger, "Required Phase 2G runner/check files", runner_files)

    output_files = [
        ("Model-promotion plan CSV", OUTPUT_TABLES_DIR / "model_promotion_plan.csv"),
        ("Model-promotion plan HTML", OUTPUT_REPORTS_DIR / "model_promotion_plan.html"),
        ("Model-promotion plan text", OUTPUT_REPORTS_DIR / "model_promotion_plan.txt"),
        ("Model-promotion planning check report", OUTPUT_REPORTS_DIR / "phase2g_model_promotion_planning_check_report.txt"),
        ("Model-promotion viewer check report", OUTPUT_REPORTS_DIR / "phase2g_model_promotion_viewer_check_report.txt"),
        ("Model-promotion pipeline report", OUTPUT_REPORTS_DIR / "phase2g_model_promotion_pipeline_report.txt"),
    ]
    check_files(logger, "Expected Phase 2G generated outputs", output_files)

    context_outputs = [
        ("Model-decision summary CSV", OUTPUT_TABLES_DIR / "model_decision_summary.csv"),
        ("Adjusted payoff comparison CSV", OUTPUT_TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
        ("Premium tuning recommendations CSV", OUTPUT_TABLES_DIR / "premium_model_tuning_recommendations.csv"),
        ("Premium validation CSV", OUTPUT_TABLES_DIR / "premium_model_validation_scaffold.csv"),
        ("Option premium CSV", OUTPUT_TABLES_DIR / "option_premium_scaffold.csv"),
    ]
    check_files(logger, "Required Phase 2F and earlier context outputs", context_outputs)

    documentation_files = [
        ("Model-promotion planning", DOCS_DIR / "paid_simulator_phase2g_model_promotion_planning.md"),
        ("Model-promotion viewer", DOCS_DIR / "paid_simulator_phase2g_model_promotion_viewer.md"),
        ("Model-promotion pipeline", DOCS_DIR / "paid_simulator_phase2g_model_promotion_pipeline_check.md"),
        ("Phase 2G dashboard tab", DOCS_DIR / "paid_simulator_phase2g_dashboard_tab.md"),
        ("Phase 2G integration readiness", DOCS_DIR / "paid_simulator_phase2g_integration_readiness.md"),
    ]
    check_files(logger, "Phase 2G documentation", documentation_files)

    logger.section("CSV row checks")
    csv_checks = [
        ("model_promotion_plan.csv", OUTPUT_TABLES_DIR / "model_promotion_plan.csv"),
        ("model_decision_summary.csv", OUTPUT_TABLES_DIR / "model_decision_summary.csv"),
        ("adjusted_premium_payoff_comparison.csv", OUTPUT_TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
    ]
    for label, path in csv_checks:
        rows = count_csv_rows(path)
        if rows is None:
            logger.result("REVIEW", label, "could not read CSV")
        elif rows > 0:
            logger.result("PASS", label, f"rows={rows}")
        else:
            logger.result("FAIL", label, "rows=0")

    logger.section("Main dashboard Phase 2G tab markers")
    dashboard_text = read_text(PAID_SIMULATOR_DIR / "config_form_app.py")
    dashboard_markers = [
        "Phase 2B premium model",
        "Phase 2C validation",
        "Phase 2D tuning",
        "Phase 2E adjustment",
        "Phase 2F model decision",
        "Phase 2G model promotion",
        "phase2g_model_promotion_viewer",
        "run_paid_simulator_phase2g_model_promotion_pipeline_check.py",
    ]
    for marker in dashboard_markers:
        if marker in dashboard_text:
            logger.result("PASS", f"Dashboard marker '{marker}'", marker)
        else:
            logger.result("REVIEW", f"Dashboard marker '{marker}'", "not found")

    logger.section("Model-promotion plan summary markers")
    summary_text = read_text(OUTPUT_REPORTS_DIR / "model_promotion_plan.txt")
    flexible_markers = [
        ("model promotion", ["model promotion", "model-promotion", "promotion plan"]),
        ("internal only", ["internal only", "developer view", "research model", "promotion candidate"]),
    ]
    for label, alternatives in flexible_markers:
        if contains_any(summary_text, alternatives):
            logger.result("PASS", f"Model-promotion summary marker '{label}'", label)
        else:
            logger.result("REVIEW", f"Model-promotion summary marker '{label}'", "not found")

    logger.write("")
    logger.write("=" * 96)
    if logger.failures == 0 and logger.reviews == 0:
        logger.write("Overall Phase 2G integration-readiness status: PASS")
        exit_code = 0
    elif logger.failures == 0:
        logger.write("Overall Phase 2G integration-readiness status: REVIEW")
        logger.write("No required files are missing, but one or more marker checks should be reviewed.")
        exit_code = 1
    else:
        logger.write("Overall Phase 2G integration-readiness status: FAIL")
        logger.write("One or more required Phase 2G integration items are missing or invalid.")
        exit_code = 1
    logger.write("=" * 96)

    logger.save()
    logger.write(f"\nSaved integration-readiness report: {REPORT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
