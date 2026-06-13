"""
scenario_payoff_report_adapter.py

Phase 2 scaffold report adapter for the paid covered-call simulator.

This module reads the standalone Phase 2 scenario-payoff scaffold output and
creates a cleaner customer/developer comparison table. It does not modify the
v0.1 paid simulator dashboard or engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
INPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_report_scaffold.csv"
HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_payoff_report_scaffold.html"


@dataclass(frozen=True)
class ReportAdapterResult:
    input_path: Path
    output_path: Path
    html_path: Path
    row_count: int
    relative_column: str | None
    scenario_column: str | None
    best_scenario: str | None
    worst_scenario: str | None
    average_relative_result: float | None


def _normalize_column_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {_normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = _normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        norm = _normalize_column_name(col)
        for candidate in candidates:
            if _normalize_column_name(candidate) in norm:
                return col
    return None


def _signed_currency(value: Any) -> str:
    try:
        number = float(value)
    except Exception:
        return str(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}${abs(number):,.2f}"


def _currency(value: Any) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)


def _percent(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except Exception:
        return str(value)


def load_scenario_payoff(path: Path = INPUT_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Scenario-payoff scaffold CSV not found: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Scenario-payoff scaffold CSV is empty: {path}")
    return df


def build_report_table(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    scenario_col = _find_column(
        df,
        [
            "scenario_display_name",
            "scenario_name",
            "scenario",
            "market_path",
            "path",
            "name",
        ],
    )
    final_price_col = _find_column(df, ["final_modeled_price", "final_price", "ending_price", "end_price"])
    start_price_col = _find_column(df, ["start_price", "initial_price", "demo_price"])
    path_return_col = _find_column(df, ["realized_path_return", "scenario_return", "total_return", "path_return"])
    buy_hold_col = _find_column(df, ["buy_hold_p_l", "buy_and_hold_p_l", "buy_hold_pl", "buy_hold"])
    covered_call_col = _find_column(df, ["covered_call_p_l", "covered_call_pl", "covered_call"])
    relative_col = _find_column(
        df,
        [
            "covered_call_minus_buy_hold",
            "covered_call_minus_buy_and_hold",
            "relative_result",
            "relative_p_l",
            "relative_pl",
            "relative_pnl",
            "outperformance",
        ],
    )
    assigned_col = _find_column(df, ["assignment_flag", "assigned", "is_assigned"])

    rows: list[dict[str, Any]] = []
    for i, row in df.iterrows():
        scenario = str(row[scenario_col]) if scenario_col else f"Scenario {i + 1}"
        relative_value = row[relative_col] if relative_col else None
        try:
            rel_float = float(relative_value) if relative_value is not None else None
        except Exception:
            rel_float = None

        if rel_float is None:
            interpretation = "Relative performance was not available for this scenario."
        elif rel_float >= 0:
            interpretation = "Covered call helped versus buy-and-hold in this modeled path."
        else:
            interpretation = "Covered call lagged buy-and-hold in this modeled path."

        rows.append(
            {
                "Scenario": scenario,
                "Start price": _currency(row[start_price_col]) if start_price_col else "",
                "Final price": _currency(row[final_price_col]) if final_price_col else "",
                "Modeled return": _percent(row[path_return_col]) if path_return_col else "",
                "Buy-and-hold P/L": _currency(row[buy_hold_col]) if buy_hold_col else "",
                "Covered-call P/L": _currency(row[covered_call_col]) if covered_call_col else "",
                "Relative result": _signed_currency(relative_value) if relative_col else "",
                "Assigned": str(row[assigned_col]) if assigned_col else "",
                "Interpretation": interpretation,
            }
        )

    report_df = pd.DataFrame(rows)
    metadata: dict[str, Any] = {
        "scenario_col": scenario_col,
        "relative_col": relative_col,
        "row_count": len(report_df),
        "best_scenario": None,
        "worst_scenario": None,
        "average_relative_result": None,
    }

    if relative_col:
        values = pd.to_numeric(df[relative_col], errors="coerce")
        valid = df.loc[values.notna()].copy()
        valid["_relative_value"] = values.loc[values.notna()]
        if not valid.empty:
            best_idx = valid["_relative_value"].idxmax()
            worst_idx = valid["_relative_value"].idxmin()
            metadata["average_relative_result"] = float(valid["_relative_value"].mean())
            metadata["best_scenario"] = str(valid.loc[best_idx, scenario_col]) if scenario_col else f"Scenario {best_idx + 1}"
            metadata["worst_scenario"] = str(valid.loc[worst_idx, scenario_col]) if scenario_col else f"Scenario {worst_idx + 1}"

    return report_df, metadata


def write_html_report(report_df: pd.DataFrame, metadata: dict[str, Any], html_path: Path = HTML_PATH) -> Path:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    average = metadata.get("average_relative_result")
    avg_text = _signed_currency(average) if average is not None else "Not available"
    best = metadata.get("best_scenario") or "Not available"
    worst = metadata.get("worst_scenario") or "Not available"

    table_html = report_df.to_html(index=False, escape=True)
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Phase 2 Scenario Payoff Report Scaffold</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .subtitle {{ color: #4b5563; margin-bottom: 1.5rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 18px 0; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px; background: #f9fafb; }}
    .label {{ color: #6b7280; font-size: 0.85rem; }}
    .value {{ font-size: 1.1rem; font-weight: 700; margin-top: 4px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .note {{ margin-top: 1.5rem; color: #4b5563; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Phase 2 Scenario Payoff Report Scaffold</h1>
  <div class=\"subtitle\">Standalone comparison table generated from scenario_payoff_scaffold.csv.</div>

  <div class=\"cards\">
    <div class=\"card\"><div class=\"label\">Rows</div><div class=\"value\">{len(report_df)}</div></div>
    <div class=\"card\"><div class=\"label\">Best scenario</div><div class=\"value\">{best}</div></div>
    <div class=\"card\"><div class=\"label\">Worst scenario</div><div class=\"value\">{worst}</div></div>
  </div>
  <div class=\"cards\">
    <div class=\"card\"><div class=\"label\">Average relative result</div><div class=\"value\">{avg_text}</div></div>
    <div class=\"card\"><div class=\"label\">Relative column</div><div class=\"value\">{metadata.get('relative_col') or 'Not detected'}</div></div>
    <div class=\"card\"><div class=\"label\">Scenario column</div><div class=\"value\">{metadata.get('scenario_col') or 'Not detected'}</div></div>
  </div>

  {table_html}

  <p class=\"note\">This is a Phase 2 scaffold report. It is intended for development validation, not final investment analysis.</p>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
    return html_path


def run_report_adapter(
    input_path: Path = INPUT_PATH,
    output_path: Path = OUTPUT_PATH,
    html_path: Path = HTML_PATH,
) -> ReportAdapterResult:
    df = load_scenario_payoff(input_path)
    report_df, metadata = build_report_table(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(output_path, index=False)
    write_html_report(report_df, metadata, html_path)

    return ReportAdapterResult(
        input_path=input_path,
        output_path=output_path,
        html_path=html_path,
        row_count=len(report_df),
        relative_column=metadata.get("relative_col"),
        scenario_column=metadata.get("scenario_col"),
        best_scenario=metadata.get("best_scenario"),
        worst_scenario=metadata.get("worst_scenario"),
        average_relative_result=metadata.get("average_relative_result"),
    )
