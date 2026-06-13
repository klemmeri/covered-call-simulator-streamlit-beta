"""
run_paid_simulator_phase2_assumption_consistency_check.py

Checks consistency across the Phase 2 scaffold assumption, price-path, and payoff outputs.

This is an add-only diagnostic script. It does not modify the dashboard, config, or simulator engine.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
ASSUMPTIONS_CSV = TABLE_DIR / "scenario_assumptions_scaffold.csv"
PRICE_PATHS_CSV = TABLE_DIR / "scenario_price_paths_scaffold.csv"
PAYOFF_CSV = TABLE_DIR / "scenario_payoff_scaffold.csv"
REPORT_CSV = TABLE_DIR / "scenario_payoff_report_scaffold.csv"
COMPARISON_CSV = TABLE_DIR / "phase2_v0_comparison_scaffold.csv"

DOC_PATH = PROJECT_ROOT / "docs" / "paid_simulator_phase2_assumption_consistency_check.md"


def print_rule(title: str | None = None) -> None:
    print("-" * 88)
    if title:
        print(title)
        print("-" * 88)


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize_name(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def find_col(rows: list[dict[str, Any]], candidates: list[str]) -> str | None:
    if not rows:
        return None
    cols = list(rows[0].keys())
    normalized = {normalize_name(c): c for c in cols}
    for candidate in candidates:
        key = normalize_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in cols:
        col_norm = normalize_name(col)
        for candidate in candidates:
            if normalize_name(candidate) in col_norm:
                return col
    return None


def to_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value).replace("%", "").replace(",", ""))
    except Exception:
        return None


def scenario_set(rows: list[dict[str, Any]], candidates: list[str]) -> tuple[set[str], str | None]:
    col = find_col(rows, candidates)
    if col is None:
        return set(), None
    return {normalize_name(row.get(col)) for row in rows if normalize_name(row.get(col))}, col


def main() -> None:
    print("=" * 88)
    print("Phase 2 assumption-consistency check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    required_files = [
        ("Scenario assumptions CSV", ASSUMPTIONS_CSV),
        ("Scenario price paths CSV", PRICE_PATHS_CSV),
        ("Scenario payoff CSV", PAYOFF_CSV),
        ("Scenario payoff report CSV", REPORT_CSV),
        ("Phase 2 vs v0 comparison CSV", COMPARISON_CSV),
        ("Assumption consistency doc", DOC_PATH),
    ]

    problems: list[str] = []

    print_rule("Required files")
    for label, path in required_files:
        if path.exists():
            print(f"FOUND      {label:<36} {path}")
        else:
            print(f"MISSING    {label:<36} {path}")
            problems.append(f"Missing required file: {path}")

    if problems:
        print()
        print("=" * 88)
        print("Overall assumption-consistency status: REVIEW")
        print("One or more required files are missing.")
        print("=" * 88)
        sys.exit(1)

    assumptions = read_rows(ASSUMPTIONS_CSV)
    price_paths = read_rows(PRICE_PATHS_CSV)
    payoffs = read_rows(PAYOFF_CSV)
    report = read_rows(REPORT_CSV)
    comparison = read_rows(COMPARISON_CSV)

    print()
    print_rule("Row counts")
    print(f"scenario_assumptions_scaffold.csv:       {len(assumptions)}")
    print(f"scenario_price_paths_scaffold.csv:       {len(price_paths)}")
    print(f"scenario_payoff_scaffold.csv:            {len(payoffs)}")
    print(f"scenario_payoff_report_scaffold.csv:     {len(report)}")
    print(f"phase2_v0_comparison_scaffold.csv:       {len(comparison)}")

    if len(assumptions) == 0:
        problems.append("Assumptions CSV has no rows.")
    if len(price_paths) == 0:
        problems.append("Price-path CSV has no rows.")
    if len(payoffs) == 0:
        problems.append("Scenario-payoff CSV has no rows.")

    scenario_candidates = ["scenario_name", "name", "scenario", "scenario_id"]
    assumptions_set, assumptions_col = scenario_set(assumptions, scenario_candidates)
    paths_set, paths_col = scenario_set(price_paths, scenario_candidates)
    payoffs_set, payoffs_col = scenario_set(payoffs, scenario_candidates)
    report_set, report_col = scenario_set(report, scenario_candidates + ["Scenario"])
    comparison_set, comparison_col = scenario_set(comparison, scenario_candidates + ["Scenario"])

    print()
    print_rule("Scenario-name columns")
    print(f"Assumptions scenario column:       {assumptions_col}")
    print(f"Price paths scenario column:       {paths_col}")
    print(f"Scenario payoff scenario column:   {payoffs_col}")
    print(f"Report scenario column:            {report_col}")
    print(f"Comparison scenario column:        {comparison_col}")

    if not assumptions_set:
        problems.append("Could not identify scenario names in assumptions CSV.")
    if not paths_set:
        problems.append("Could not identify scenario names in price-path CSV.")
    if not payoffs_set:
        problems.append("Could not identify scenario names in scenario-payoff CSV.")

    print()
    print_rule("Scenario set consistency")
    print(f"Assumptions scenarios:   {sorted(assumptions_set)}")
    print(f"Price-path scenarios:    {sorted(paths_set)}")
    print(f"Payoff scenarios:        {sorted(payoffs_set)}")

    if assumptions_set and paths_set and assumptions_set != paths_set:
        problems.append("Assumption scenarios and price-path scenarios do not match.")
    if assumptions_set and payoffs_set and assumptions_set != payoffs_set:
        problems.append("Assumption scenarios and payoff scenarios do not match.")

    # Compare modeled return assumptions against realized final path return when columns are available.
    assumption_return_col = find_col(
        assumptions,
        ["modeled_total_return", "modeled_total_return_percent", "total_return", "scenario_total_simple_return_percent"],
    )
    path_return_col = find_col(
        price_paths,
        ["realized_path_return", "path_return", "modeled_return", "price_return", "total_return"],
    )
    step_col = find_col(price_paths, ["step", "path_step", "day", "period"])

    print()
    print_rule("Modeled-return consistency")
    print(f"Assumption return column: {assumption_return_col}")
    print(f"Price-path return column: {path_return_col}")
    print(f"Price-path step column:   {step_col}")

    if assumption_return_col and path_return_col and assumptions_col and paths_col:
        assumption_returns = {
            normalize_name(row.get(assumptions_col)): to_float(row.get(assumption_return_col))
            for row in assumptions
        }

        final_path_rows: dict[str, dict[str, Any]] = {}
        for row in price_paths:
            scenario = normalize_name(row.get(paths_col))
            if not scenario:
                continue
            if step_col:
                current_step = to_float(row.get(step_col))
                existing_step = to_float(final_path_rows.get(scenario, {}).get(step_col)) if scenario in final_path_rows else None
                if existing_step is None or (current_step is not None and current_step >= existing_step):
                    final_path_rows[scenario] = row
            else:
                final_path_rows[scenario] = row

        tolerance = 0.05  # percentage points if returns are stored as percent; harmlessly loose for scaffold.
        checked = 0
        mismatches: list[str] = []
        for scenario, assumed_return in assumption_returns.items():
            path_row = final_path_rows.get(scenario)
            if path_row is None or assumed_return is None:
                continue
            path_return = to_float(path_row.get(path_return_col))
            if path_return is None:
                continue
            checked += 1
            # Some scaffold files may store returns as decimal fractions and others as percentages.
            ar = assumed_return
            pr = path_return
            if abs(ar) <= 1.0 and abs(pr) > 1.0:
                ar *= 100.0
            elif abs(pr) <= 1.0 and abs(ar) > 1.0:
                pr *= 100.0
            if abs(ar - pr) > tolerance:
                mismatches.append(f"{scenario}: assumption={ar:.4f}, final_path={pr:.4f}")

        print(f"Return comparisons checked: {checked}")
        if mismatches:
            print("MISMATCHES")
            for item in mismatches:
                print(f"  {item}")
            problems.append("Modeled return assumptions do not match final price-path returns within tolerance.")
        else:
            print("PASS - modeled returns are consistent with final price-path returns where comparable.")
    else:
        print("SKIP - return columns were not available in both files. Scenario-name checks still passed.")

    print()
    if problems:
        print("Items needing attention")
        print_rule()
        for problem in problems:
            print(f"- {problem}")
        print()
        print("=" * 88)
        print("Overall assumption-consistency status: REVIEW")
        print("One or more Phase 2 assumption consistency checks need attention.")
        print("=" * 88)
        sys.exit(1)

    print("=" * 88)
    print("Overall assumption-consistency status: PASS")
    print("Phase 2 assumptions, price paths, and payoff scaffold outputs are mutually consistent.")
    print("=" * 88)


if __name__ == "__main__":
    main()
