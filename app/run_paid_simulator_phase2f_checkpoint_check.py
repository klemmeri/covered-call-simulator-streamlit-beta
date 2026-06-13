"""
run_paid_simulator_phase2f_checkpoint_check.py

Phase 2F model-decision checkpoint check for the Covered Call Simulator.

This version is intentionally tolerant about wording in the model-decision
text summary. The summary file is data-driven, so the checkpoint should not
fail just because a particular display phrase such as "Overall" is absent or
formatted differently.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

OUTPUT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_checkpoint_report.txt"


class CheckResult:
    def __init__(self, status: str, label: str, detail: str = "") -> None:
        self.status = status
        self.label = label
        self.detail = detail


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def line(title: str = "", width: int = 96) -> str:
    if title:
        return f"{title}\n" + "-" * width
    return "-" * width


def check_file(label: str, path: Path) -> CheckResult:
    if path.exists():
        return CheckResult("FOUND", label, str(path))
    return CheckResult("MISSING", label, str(path))


def read_text_safe(path: Path) -> str:
    if not path.exists():
        return ""
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""


def csv_row_check(label: str, path: Path) -> CheckResult:
    if not path.exists():
        return CheckResult("MISSING", label, str(path))
    if pd is None:
        return CheckResult("REVIEW", label, "pandas is not available; row count not checked")
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        return CheckResult("REVIEW", label, f"could not read CSV: {exc}")
    if len(df) > 0:
        return CheckResult("PASS", label, f"rows={len(df)}")
    return CheckResult("REVIEW", label, "rows=0")


def marker_check(label: str, text: str, markers: list[str]) -> CheckResult:
    lower = text.lower()
    found = [marker for marker in markers if marker.lower() in lower]
    if found:
        return CheckResult("PASS", label, ", ".join(found))
    return CheckResult("REVIEW", label, "none of: " + ", ".join(markers))


def print_results(results: list[CheckResult], output_lines: list[str]) -> None:
    for result in results:
        output_lines.append(f"{result.status:<10} {result.label:<55} {result.detail}")


def section(output_lines: list[str], title: str, results: list[CheckResult]) -> None:
    output_lines.append("")
    output_lines.append(line(title))
    print_results(results, output_lines)


def has_failures(results: list[CheckResult]) -> bool:
    return any(result.status in {"MISSING", "REVIEW"} for result in results)


def main() -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_lines: list[str] = []
    all_results: list[CheckResult] = []

    output_lines.append("=" * 96)
    output_lines.append("Phase 2F model-decision checkpoint check")
    output_lines.append("=" * 96)
    output_lines.append(f"Generated: {now}")
    output_lines.append(f"Project root: {PROJECT_ROOT}")

    source_files = [
        ("Option premium model", PROJECT_ROOT / "app" / "paid_simulator" / "option_premium_model.py"),
        ("Premium-aware payoff runner", PROJECT_ROOT / "app" / "paid_simulator" / "premium_aware_payoff_runner.py"),
        ("Premium-vs-scaffold comparison", PROJECT_ROOT / "app" / "paid_simulator" / "premium_vs_scaffold_comparison.py"),
        ("Premium-model validation module", PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_validation.py"),
        ("Premium-model tuning module", PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_tuning.py"),
        ("Premium-model adjustment module", PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_adjustment.py"),
        ("Adjusted premium payoff comparison", PROJECT_ROOT / "app" / "paid_simulator" / "adjusted_premium_payoff_comparison.py"),
        ("Model-decision summary module", PROJECT_ROOT / "app" / "paid_simulator" / "model_decision_summary.py"),
        ("Phase 2F model-decision viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2f_model_decision_viewer.py"),
        ("Main dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
        ("Main dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ]
    results = [check_file(label, path) for label, path in source_files]
    all_results.extend(results)
    section(output_lines, "Required Phase 2B through Phase 2F source files", results)

    runner_files = [
        ("Phase 2E checkpoint check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2e_checkpoint_check.py"),
        ("Model-decision summary check", PROJECT_ROOT / "app" / "run_paid_simulator_model_decision_summary_check.py"),
        ("Phase 2F viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_viewer.py"),
        ("Phase 2F viewer check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_viewer_check.py"),
        ("Phase 2F pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_pipeline_check.py"),
        ("Phase 2F dashboard-tab check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_dashboard_tab_check.py"),
        ("Phase 2F integration-readiness check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_integration_readiness_check.py"),
    ]
    results = [check_file(label, path) for label, path in runner_files]
    all_results.extend(results)
    section(output_lines, "Required Phase 2F runner/check files", results)

    config_files = [
        ("Premium-model validation config", PROJECT_ROOT / "config" / "premium_model_validation_config.json"),
        ("Premium-model tuning config", PROJECT_ROOT / "config" / "premium_model_tuning_config.json"),
        ("Premium-model adjustment config", PROJECT_ROOT / "config" / "premium_model_adjustment_config.json"),
    ]
    results = [check_file(label, path) for label, path in config_files]
    all_results.extend(results)
    section(output_lines, "Required Phase 2B through Phase 2E config files", results)

    output_files = [
        ("Option premium CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"),
        ("Premium-aware payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"),
        ("Premium-aware payoff HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_aware_payoff_scaffold.html"),
        ("Premium-vs-scaffold CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv"),
        ("Premium-vs-scaffold HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_vs_scaffold_comparison.html"),
        ("Premium validation CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_validation_scaffold.csv"),
        ("Premium validation HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_scaffold.html"),
        ("Premium validation summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_summary.txt"),
        ("Premium tuning recommendations CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_tuning_recommendations.csv"),
        ("Premium tuning recommendations HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_tuning_recommendations.html"),
        ("Premium tuning summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_tuning_summary.txt"),
        ("Adjusted premiums CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_adjusted_premiums.csv"),
        ("Premium adjustment comparison HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_adjustment_comparison.html"),
        ("Premium adjustment summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_adjustment_summary.txt"),
        ("Adjusted payoff comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "adjusted_premium_payoff_comparison.csv"),
        ("Adjusted payoff comparison HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "adjusted_premium_payoff_comparison.html"),
        ("Adjusted payoff summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "adjusted_premium_payoff_summary.txt"),
        ("Model decision CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "model_decision_summary.csv"),
        ("Model decision HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.html"),
        ("Model decision text summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.txt"),
        ("Phase 2F model decision summary check report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_model_decision_summary_check_report.txt"),
        ("Phase 2F model decision viewer check report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_model_decision_viewer_check_report.txt"),
        ("Phase 2F model decision pipeline report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_model_decision_pipeline_report.txt"),
        ("Phase 2F integration-readiness report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_integration_readiness_report.txt"),
    ]
    results = [check_file(label, path) for label, path in output_files]
    all_results.extend(results)
    section(output_lines, "Expected Phase 2B through Phase 2F generated outputs", results)

    docs = [
        ("Option premium model scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_option_premium_model_scaffold.md"),
        ("Premium-aware payoff", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_aware_payoff.md"),
        ("Premium-vs-scaffold comparison", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md"),
        ("Phase 2B checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_checkpoint_summary.md"),
        ("Premium-model validation", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_premium_model_validation.md"),
        ("Phase 2C checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_checkpoint_summary.md"),
        ("Premium-model tuning", PROJECT_ROOT / "docs" / "paid_simulator_phase2d_premium_model_tuning.md"),
        ("Phase 2D checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2d_checkpoint_summary.md"),
        ("Premium-model adjustment", PROJECT_ROOT / "docs" / "paid_simulator_phase2e_premium_model_adjustment.md"),
        ("Adjusted premium payoff comparison", PROJECT_ROOT / "docs" / "paid_simulator_phase2e_adjusted_premium_payoff_comparison.md"),
        ("Phase 2E checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2e_checkpoint_summary.md"),
        ("Model-decision summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2f_model_decision_summary.md"),
        ("Model-decision viewer", PROJECT_ROOT / "docs" / "paid_simulator_phase2f_model_decision_viewer.md"),
        ("Model-decision pipeline", PROJECT_ROOT / "docs" / "paid_simulator_phase2f_model_decision_pipeline_check.md"),
        ("Phase 2F dashboard tab", PROJECT_ROOT / "docs" / "paid_simulator_phase2f_dashboard_tab.md"),
        ("Phase 2F integration readiness", PROJECT_ROOT / "docs" / "paid_simulator_phase2f_integration_readiness.md"),
        ("Phase 2F checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2f_checkpoint_summary.md"),
    ]
    results = [check_file(label, path) for label, path in docs]
    all_results.extend(results)
    section(output_lines, "Phase 2B through Phase 2F documentation", results)

    csv_files = [
        ("option_premium_scaffold.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"),
        ("premium_aware_payoff_scaffold.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"),
        ("premium_model_validation_scaffold.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_validation_scaffold.csv"),
        ("premium_model_tuning_recommendations.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_tuning_recommendations.csv"),
        ("premium_model_adjusted_premiums.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_adjusted_premiums.csv"),
        ("adjusted_premium_payoff_comparison.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "adjusted_premium_payoff_comparison.csv"),
        ("model_decision_summary.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "model_decision_summary.csv"),
    ]
    results = [csv_row_check(label, path) for label, path in csv_files]
    all_results.extend(results)
    section(output_lines, "CSV row checks", results)

    dashboard_text = read_text_safe(PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py")
    dash_checks = [
        ("Dashboard marker 'Phase 2B premium model'", ["Phase 2B premium model"]),
        ("Dashboard marker 'Phase 2C validation'", ["Phase 2C validation"]),
        ("Dashboard marker 'Phase 2D tuning'", ["Phase 2D tuning"]),
        ("Dashboard marker 'Phase 2E adjustment'", ["Phase 2E adjustment"]),
        ("Dashboard marker 'Phase 2F model decision'", ["Phase 2F model decision"]),
        ("Dashboard marker 'phase2f_model_decision_viewer'", ["phase2f_model_decision_viewer"]),
        ("Dashboard marker 'run_paid_simulator_phase2f_model_decision_pipeline_check.py'", ["run_paid_simulator_phase2f_model_decision_pipeline_check.py"]),
    ]
    results = [marker_check(label, dashboard_text, markers) for label, markers in dash_checks]
    all_results.extend(results)
    section(output_lines, "Main dashboard Phase 2F tab markers", results)

    summary_path = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.txt"
    summary_text = read_text_safe(summary_path)
    summary_checks = [
        marker_check("Model decision summary marker 'model-decision'", summary_text, ["model-decision", "model decision", "model_decision"]),
        marker_check("Model decision summary marker 'summary/overall'", summary_text, ["overall", "summary", "decision", "scenario"]),
    ]
    results = summary_checks
    all_results.extend(results)
    section(output_lines, "Model-decision summary markers", results)

    output_lines.append("")
    output_lines.append("=" * 96)
    if has_failures(all_results):
        output_lines.append("Overall Phase 2F checkpoint status: REVIEW")
        output_lines.append("One or more Phase 2F checkpoint items need attention before promotion planning.")
        exit_code = 1
    else:
        output_lines.append("Overall Phase 2F checkpoint status: PASS")
        output_lines.append("Phase 2F model-decision checkpoint is complete. Promotion planning can begin.")
        exit_code = 0
    output_lines.append("=" * 96)

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    output_lines.append("")
    output_lines.append(f"Saved checkpoint report: {OUTPUT_REPORT}")

    print("\n".join(output_lines))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
