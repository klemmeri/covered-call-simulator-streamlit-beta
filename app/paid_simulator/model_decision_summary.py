"""
model_decision_summary.py

Phase 2F model-decision summary for the Covered Call Strategy Stress Test.

This module consolidates the premium-aware model, adjusted-premium model,
validation checks, and tuning recommendations into one decision report.

It is intentionally conservative. It does not replace any existing model
outputs. It reads existing Phase 2B/2C/2D/2E files and writes separate
Phase 2F summary outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OPTION_PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"
PREMIUM_AWARE_PAYOFF_CSV = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
PREMIUM_VS_SCAFFOLD_CSV = TABLE_DIR / "premium_vs_scaffold_comparison.csv"
PREMIUM_VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
PREMIUM_TUNING_CSV = TABLE_DIR / "premium_model_tuning_recommendations.csv"
ADJUSTED_PREMIUM_CSV = TABLE_DIR / "premium_model_adjusted_premiums.csv"
ADJUSTED_PAYOFF_CSV = TABLE_DIR / "adjusted_premium_payoff_comparison.csv"

SUMMARY_CSV = TABLE_DIR / "model_decision_summary.csv"
SUMMARY_HTML = REPORT_DIR / "model_decision_summary.html"
SUMMARY_TEXT = REPORT_DIR / "model_decision_summary.txt"


@dataclass
class InputStatus:
    label: str
    path: Path
    exists: bool
    rows: int


def _normalize_column_name(name: str) -> str:
    return "".join(ch.lower() for ch in str(name) if ch.isalnum())


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    if df is None or df.empty:
        return None

    normalized = {_normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = _normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]

    for candidate in candidates:
        candidate_key = _normalize_column_name(candidate)
        for normalized_col, original_col in normalized.items():
            if candidate_key in normalized_col or normalized_col in candidate_key:
                return original_col

    return None


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _input_statuses() -> list[InputStatus]:
    paths = [
        ("Option premium estimates", OPTION_PREMIUM_CSV),
        ("Premium-aware payoff", PREMIUM_AWARE_PAYOFF_CSV),
        ("Premium-vs-scaffold comparison", PREMIUM_VS_SCAFFOLD_CSV),
        ("Premium validation", PREMIUM_VALIDATION_CSV),
        ("Premium tuning recommendations", PREMIUM_TUNING_CSV),
        ("Adjusted premium estimates", ADJUSTED_PREMIUM_CSV),
        ("Adjusted payoff comparison", ADJUSTED_PAYOFF_CSV),
    ]

    statuses: list[InputStatus] = []
    for label, path in paths:
        df = _read_csv(path)
        statuses.append(InputStatus(label=label, path=path, exists=path.exists(), rows=len(df)))
    return statuses


def _scenario_key(df: pd.DataFrame) -> str | None:
    return _find_column(
        df,
        [
            "scenario",
            "scenario_name",
            "scenario key",
            "name",
            "display_name",
            "display name",
            "market_path",
            "market path",
        ],
    )


def _numeric_series(df: pd.DataFrame, candidates: list[str]) -> pd.Series | None:
    col = _find_column(df, candidates)
    if col is None:
        return None
    return pd.to_numeric(df[col], errors="coerce")


def _text_series(df: pd.DataFrame, candidates: list[str]) -> pd.Series | None:
    col = _find_column(df, candidates)
    if col is None:
        return None
    return df[col].astype(str)


def _scenario_labels(*dfs: pd.DataFrame) -> list[str]:
    labels: list[str] = []
    for df in dfs:
        if df.empty:
            continue
        key_col = _scenario_key(df)
        if key_col is None:
            continue
        for value in df[key_col].dropna().astype(str).tolist():
            if value not in labels:
                labels.append(value)
    return labels


def _lookup_row(df: pd.DataFrame, scenario: str) -> pd.Series | None:
    if df.empty:
        return None
    key_col = _scenario_key(df)
    if key_col is None:
        return None
    matches = df[df[key_col].astype(str) == str(scenario)]
    if matches.empty:
        return None
    return matches.iloc[0]


def _row_value(row: pd.Series | None, candidates: list[str], default: Any = None) -> Any:
    if row is None:
        return default
    normalized = {_normalize_column_name(col): col for col in row.index}
    for candidate in candidates:
        key = _normalize_column_name(candidate)
        if key in normalized:
            value = row[normalized[key]]
            return default if pd.isna(value) else value
    for candidate in candidates:
        candidate_key = _normalize_column_name(candidate)
        for normalized_col, original_col in normalized.items():
            if candidate_key in normalized_col or normalized_col in candidate_key:
                value = row[original_col]
                return default if pd.isna(value) else value
    return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _status_from_text(value: Any) -> str:
    text = str(value or "").strip().upper()
    if "FAIL" in text or "ERROR" in text or "DO NOT" in text:
        return "FAIL"
    if "TUNE" in text:
        return "TUNE"
    if "REVIEW" in text:
        return "REVIEW"
    if "WATCH" in text:
        return "WATCH"
    if "PASS" in text or "OK" in text:
        return "PASS"
    return "INFO"


def _aggregate_validation_status(validation_df: pd.DataFrame, scenario: str) -> tuple[str, str]:
    if validation_df.empty:
        return "MISSING", "No validation rows found."

    key_col = _scenario_key(validation_df)
    if key_col is None:
        statuses = validation_df.apply(lambda row: _status_from_text(" ".join(row.astype(str).tolist())), axis=1)
        return _combine_statuses(statuses.tolist()), "Validation file exists, but scenario column was not detected."

    rows = validation_df[validation_df[key_col].astype(str) == str(scenario)]
    if rows.empty:
        return "MISSING", "No validation row for this scenario."

    status_col = _find_column(rows, ["status", "check_status", "result", "validation_status", "decision"])
    if status_col is not None:
        statuses = [_status_from_text(value) for value in rows[status_col].tolist()]
    else:
        statuses = rows.apply(lambda row: _status_from_text(" ".join(row.astype(str).tolist())), axis=1).tolist()

    notes_col = _find_column(rows, ["note", "notes", "message", "interpretation", "recommendation"])
    if notes_col is not None:
        notes = "; ".join(str(x) for x in rows[notes_col].dropna().astype(str).tolist()[:3])
    else:
        notes = "Validation row found."

    return _combine_statuses(statuses), notes


def _combine_statuses(statuses: list[str]) -> str:
    severity = {"FAIL": 5, "TUNE": 4, "REVIEW": 3, "WATCH": 2, "INFO": 1, "PASS": 0, "MISSING": 6}
    if not statuses:
        return "INFO"
    return max(statuses, key=lambda item: severity.get(item, 1))


def _model_decision(validation_status: str, tuning_status: str, adjusted_delta: float) -> tuple[str, str]:
    severe_statuses = {"FAIL", "MISSING"}
    medium_statuses = {"TUNE", "REVIEW"}

    if validation_status in severe_statuses:
        return (
            "DO NOT PROMOTE",
            "Validation has missing or failing evidence. Keep this in Developer view and inspect assumptions before promotion.",
        )

    if abs(adjusted_delta) > 250:
        return (
            "REVIEW BEFORE PROMOTION",
            "Adjusted model materially changes scenario payoff. Inspect premium and IV assumptions before promotion.",
        )

    if validation_status in medium_statuses or tuning_status in medium_statuses:
        return (
            "USE AS RESEARCH MODEL",
            "Model is connected and useful for research, but tuning or validation still needs review.",
        )

    return (
        "CANDIDATE FOR CONTROLLED PROMOTION",
        "Model appears internally consistent. Promote only after manual review and customer-facing language cleanup.",
    )


def build_model_decision_summary() -> pd.DataFrame:
    option_df = _read_csv(OPTION_PREMIUM_CSV)
    premium_payoff_df = _read_csv(PREMIUM_AWARE_PAYOFF_CSV)
    comparison_df = _read_csv(PREMIUM_VS_SCAFFOLD_CSV)
    validation_df = _read_csv(PREMIUM_VALIDATION_CSV)
    tuning_df = _read_csv(PREMIUM_TUNING_CSV)
    adjusted_premium_df = _read_csv(ADJUSTED_PREMIUM_CSV)
    adjusted_payoff_df = _read_csv(ADJUSTED_PAYOFF_CSV)

    scenarios = _scenario_labels(
        option_df,
        premium_payoff_df,
        comparison_df,
        validation_df,
        tuning_df,
        adjusted_premium_df,
        adjusted_payoff_df,
    )

    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        option_row = _lookup_row(option_df, scenario)
        premium_payoff_row = _lookup_row(premium_payoff_df, scenario)
        comparison_row = _lookup_row(comparison_df, scenario)
        tuning_row = _lookup_row(tuning_df, scenario)
        adjusted_premium_row = _lookup_row(adjusted_premium_df, scenario)
        adjusted_payoff_row = _lookup_row(adjusted_payoff_df, scenario)

        validation_status, validation_notes = _aggregate_validation_status(validation_df, scenario)

        tuning_status = _status_from_text(
            _row_value(
                tuning_row,
                ["status", "tuning_status", "recommendation_status", "decision", "action"],
                "INFO",
            )
        )

        original_premium = _to_float(
            _row_value(
                option_row,
                ["estimated_call_premium", "call_premium", "premium", "estimated premium", "estimated_premium"],
                0.0,
            )
        )
        adjusted_premium = _to_float(
            _row_value(
                adjusted_premium_row,
                ["adjusted_call_premium", "adjusted_premium", "new_premium", "premium_adjusted"],
                original_premium,
            )
        )
        premium_change = adjusted_premium - original_premium

        original_relative = _to_float(
            _row_value(
                premium_payoff_row,
                [
                    "covered_call_minus_buy_hold",
                    "covered_call_minus_buy_and_hold",
                    "relative_result",
                    "premium_aware_relative_result",
                    "cc_minus_bh",
                ],
                _row_value(
                    comparison_row,
                    ["premium_aware_relative_result", "premium_aware_minus_buy_hold", "phase2b_relative_result"],
                    0.0,
                ),
            )
        )
        adjusted_relative = _to_float(
            _row_value(
                adjusted_payoff_row,
                [
                    "adjusted_covered_call_minus_buy_hold",
                    "adjusted_relative_result",
                    "adjusted_minus_buy_hold",
                    "covered_call_minus_buy_hold_adjusted",
                ],
                original_relative,
            )
        )
        adjusted_minus_original = _to_float(
            _row_value(
                adjusted_payoff_row,
                [
                    "adjusted_minus_original_model_pl",
                    "adjusted_minus_prior_premium_aware_result",
                    "adjusted_minus_original",
                    "model_difference",
                ],
                adjusted_relative - original_relative,
            )
        )

        implied_vol = _to_float(
            _row_value(option_row, ["implied_volatility", "estimated_iv", "iv", "scenario_iv"], 0.0)
        )
        adjusted_iv = _to_float(
            _row_value(adjusted_premium_row, ["adjusted_iv", "new_iv", "implied_volatility_adjusted"], implied_vol)
        )
        estimated_delta = _to_float(
            _row_value(option_row, ["estimated_call_delta", "call_delta", "delta"], 0.0)
        )
        strike = _to_float(
            _row_value(option_row, ["estimated_call_strike", "call_strike", "strike"], 0.0)
        )

        decision, decision_reason = _model_decision(validation_status, tuning_status, adjusted_minus_original)

        rows.append(
            {
                "scenario": scenario,
                "original_premium": round(original_premium, 4),
                "adjusted_premium": round(adjusted_premium, 4),
                "premium_change": round(premium_change, 4),
                "estimated_iv": round(implied_vol, 4),
                "adjusted_iv": round(adjusted_iv, 4),
                "estimated_delta": round(estimated_delta, 4),
                "estimated_strike": round(strike, 4),
                "premium_aware_relative_result": round(original_relative, 2),
                "adjusted_relative_result": round(adjusted_relative, 2),
                "adjusted_minus_original": round(adjusted_minus_original, 2),
                "validation_status": validation_status,
                "tuning_status": tuning_status,
                "model_decision": decision,
                "decision_reason": decision_reason,
                "validation_notes": validation_notes,
            }
        )

    return pd.DataFrame(rows)


def _format_money(value: Any) -> str:
    try:
        number = float(value)
        return f"${number:,.2f}"
    except Exception:
        return str(value)


def _write_html(summary_df: pd.DataFrame, statuses: list[InputStatus]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_rows = "\n".join(
        f"<tr><td>{s.label}</td><td>{'FOUND' if s.exists else 'MISSING'}</td><td>{s.rows}</td><td><code>{s.path}</code></td></tr>"
        for s in statuses
    )

    display_df = summary_df.copy()
    for col in [
        "original_premium",
        "adjusted_premium",
        "premium_change",
        "premium_aware_relative_result",
        "adjusted_relative_result",
        "adjusted_minus_original",
    ]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(_format_money)

    table_html = display_df.to_html(index=False, escape=True)

    decision_counts = (
        summary_df["model_decision"].value_counts().reset_index().rename(columns={"index": "decision", "model_decision": "count"})
        if "model_decision" in summary_df.columns and not summary_df.empty
        else pd.DataFrame(columns=["decision", "count"])
    )
    decision_counts_html = decision_counts.to_html(index=False, escape=True)

    html = f"""<!doctype html>
<html>
<head>
<meta charset=\"utf-8\">
<title>Phase 2F Model Decision Summary</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
h1, h2 {{ color: #1f2937; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
th {{ background: #f3f4f6; }}
code {{ font-size: 12px; }}
.notice {{ background: #f9fafb; border-left: 4px solid #6b7280; padding: 12px; margin: 16px 0; }}
</style>
</head>
<body>
<h1>Phase 2F Model Decision Summary</h1>
<p>Generated: {generated}</p>
<div class=\"notice\">
<p>This report consolidates the premium-aware model, adjusted-premium model, validation checks, and tuning recommendations. It is a decision-support report for internal model development, not a customer-facing trade recommendation.</p>
</div>
<h2>Decision counts</h2>
{decision_counts_html}
<h2>Scenario-level model decision summary</h2>
{table_html}
<h2>Input file status</h2>
<table>
<tr><th>Input</th><th>Status</th><th>Rows</th><th>Path</th></tr>
{status_rows}
</table>
</body>
</html>
"""
    SUMMARY_HTML.write_text(html, encoding="utf-8")


def _write_text(summary_df: pd.DataFrame, statuses: list[InputStatus]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = []
    lines.append("Phase 2F Model Decision Summary")
    lines.append("=" * 80)
    lines.append(f"Generated: {generated}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    lines.append("Input file status")
    lines.append("-" * 80)
    for status in statuses:
        label = "FOUND" if status.exists else "MISSING"
        lines.append(f"{label:<8} rows={status.rows:<4} {status.label}: {status.path}")
    lines.append("")

    if summary_df.empty:
        lines.append("No model-decision rows were generated.")
    else:
        lines.append("Decision counts")
        lines.append("-" * 80)
        for decision, count in summary_df["model_decision"].value_counts().items():
            lines.append(f"{decision}: {count}")
        lines.append("")
        lines.append("Scenario decisions")
        lines.append("-" * 80)
        for _, row in summary_df.iterrows():
            lines.append(f"Scenario: {row.get('scenario', '')}")
            lines.append(f"  Decision: {row.get('model_decision', '')}")
            lines.append(f"  Reason: {row.get('decision_reason', '')}")
            lines.append(f"  Premium change: {_format_money(row.get('premium_change', 0))}")
            lines.append(f"  Adjusted minus original: {_format_money(row.get('adjusted_minus_original', 0))}")
            lines.append(f"  Validation status: {row.get('validation_status', '')}")
            lines.append(f"  Tuning status: {row.get('tuning_status', '')}")
            lines.append("")

    SUMMARY_TEXT.write_text("\n".join(lines), encoding="utf-8")


def run_model_decision_summary() -> pd.DataFrame:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    statuses = _input_statuses()
    summary_df = build_model_decision_summary()
    summary_df.to_csv(SUMMARY_CSV, index=False)
    _write_html(summary_df, statuses)
    _write_text(summary_df, statuses)
    return summary_df


if __name__ == "__main__":
    df = run_model_decision_summary()
    print("Phase 2F model-decision summary complete.")
    print(f"Rows: {len(df)}")
    print(f"CSV:  {SUMMARY_CSV}")
    print(f"HTML: {SUMMARY_HTML}")
    print(f"Text: {SUMMARY_TEXT}")
