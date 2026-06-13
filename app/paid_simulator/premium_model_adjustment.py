"""
premium_model_adjustment.py

Phase 2E controlled premium-model tuning adjustment scaffold for the
Covered Call Strategy Stress Test project.

This module applies one conservative, reversible adjustment layer to the
Phase 2B option-premium scaffold. It does not replace the original premium
model and it does not modify any existing CSV files. Instead, it writes a
separate adjusted-premium comparison so the adjustment can be inspected before
being promoted into the main modeling workflow.

Inputs
------
outputs/tables/paid_simulator/option_premium_scaffold.csv
outputs/tables/paid_simulator/premium_model_tuning_recommendations.csv
config/premium_model_adjustment_config.json  (created automatically if missing)

Outputs
-------
outputs/tables/paid_simulator/premium_model_adjusted_premiums.csv
outputs/reports/paid_simulator/premium_model_adjustment_comparison.html
outputs/reports/paid_simulator/premium_model_adjustment_summary.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from math import erf, exp, log, sqrt
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OPTION_PREMIUM_CSV = OUTPUT_TABLE_DIR / "option_premium_scaffold.csv"
TUNING_RECOMMENDATIONS_CSV = OUTPUT_TABLE_DIR / "premium_model_tuning_recommendations.csv"
ADJUSTMENT_CONFIG_JSON = CONFIG_DIR / "premium_model_adjustment_config.json"

ADJUSTED_PREMIUM_CSV = OUTPUT_TABLE_DIR / "premium_model_adjusted_premiums.csv"
ADJUSTMENT_HTML = OUTPUT_REPORT_DIR / "premium_model_adjustment_comparison.html"
ADJUSTMENT_SUMMARY_TXT = OUTPUT_REPORT_DIR / "premium_model_adjustment_summary.txt"


DEFAULT_ADJUSTMENT_CONFIG: dict[str, Any] = {
    "description": "Phase 2E controlled premium-model adjustment settings.",
    "apply_adjustments": True,
    "adjustment_scope": "iv_only_fixed_strike",
    "max_abs_iv_adjustment_per_run": 0.020,
    "minimum_adjusted_iv": 0.060,
    "maximum_adjusted_iv": 0.750,
    "premium_low_iv_bump": 0.010,
    "premium_high_iv_cut": -0.010,
    "delta_low_iv_bump": 0.005,
    "delta_high_iv_cut": -0.005,
    "volatility_low_iv_bump": 0.010,
    "volatility_high_iv_cut": -0.010,
    "relationship_min_iv_gap": 0.005,
    "scenario_relationship_adjustments": {
        "ensure_volatile_whipsaw_has_highest_iv": True,
        "ensure_downtrend_iv_exceeds_sideways_choppy_iv": True,
    },
    "notes": [
        "This is a controlled experiment. It writes adjusted outputs only and does not overwrite option_premium_scaffold.csv.",
        "The first controlled adjustment changes implied volatility only while keeping strike fixed, so the effect can be isolated.",
        "Volatility values are decimals. For example, 0.020 means two volatility points."
    ],
}


COLUMN_CANDIDATES = {
    "scenario": ["scenario_name", "scenario", "name"],
    "display_name": ["display_name", "scenario_display_name", "market_path", "scenario_label"],
    "underlying_price": ["underlying_price", "stock_price", "current_price", "demo_price", "starting_price"],
    "target_delta": ["target_delta", "configured_target_delta", "desired_delta"],
    "strike": ["estimated_strike", "call_strike", "strike", "selected_strike", "strike_price"],
    "dte": ["days_to_expiration", "dte", "target_dte"],
    "iv": ["implied_volatility", "estimated_implied_volatility", "estimated_iv", "iv", "scenario_iv"],
    "risk_free_rate": ["risk_free_rate", "r"],
    "dividend_yield": ["dividend_yield", "q"],
    "premium": ["estimated_call_premium", "call_premium", "premium", "option_premium", "estimated_premium"],
    "delta": ["estimated_call_delta", "call_delta", "estimated_delta", "delta"],
    "moneyness_percent": ["moneyness_percent", "moneyness_pct", "strike_distance_pct", "strike_distance_percent"],
}

TUNING_COLUMN_CANDIDATES = {
    "scenario": ["scenario", "scenario_name", "name"],
    "status": ["tuning_status", "status", "validation_status"],
    "area": ["tuning_area", "area", "check_area"],
    "recommendation": ["recommendation", "message", "note"],
}


@dataclass
class AdjustedPremiumResult:
    scenario_name: str
    display_name: str
    adjustment_status: str
    adjustment_reason: str
    underlying_price: float
    target_delta: float
    estimated_strike: float
    days_to_expiration: int
    original_implied_volatility: float
    iv_adjustment: float
    adjusted_implied_volatility: float
    risk_free_rate: float
    dividend_yield: float
    original_call_premium: float
    adjusted_call_premium: float
    premium_change: float
    premium_change_pct: float | None
    original_call_delta: float
    adjusted_call_delta: float
    delta_change: float
    moneyness_percent: float
    tuning_status: str
    tuning_area: str
    tuning_recommendation: str


def ensure_directories() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_or_create_adjustment_config() -> dict[str, Any]:
    ensure_directories()
    if not ADJUSTMENT_CONFIG_JSON.exists():
        ADJUSTMENT_CONFIG_JSON.write_text(
            json.dumps(DEFAULT_ADJUSTMENT_CONFIG, indent=2),
            encoding="utf-8",
        )
        return dict(DEFAULT_ADJUSTMENT_CONFIG)

    try:
        loaded = json.loads(ADJUSTMENT_CONFIG_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        backup_path = ADJUSTMENT_CONFIG_JSON.with_suffix(".invalid.json")
        backup_path.write_text(ADJUSTMENT_CONFIG_JSON.read_text(encoding="utf-8"), encoding="utf-8")
        ADJUSTMENT_CONFIG_JSON.write_text(json.dumps(DEFAULT_ADJUSTMENT_CONFIG, indent=2), encoding="utf-8")
        return dict(DEFAULT_ADJUSTMENT_CONFIG)

    merged = dict(DEFAULT_ADJUSTMENT_CONFIG)
    merged.update(loaded)
    if isinstance(DEFAULT_ADJUSTMENT_CONFIG.get("scenario_relationship_adjustments"), dict):
        nested = dict(DEFAULT_ADJUSTMENT_CONFIG["scenario_relationship_adjustments"])
        nested.update(loaded.get("scenario_relationship_adjustments", {}))
        merged["scenario_relationship_adjustments"] = nested
    return merged


def normalize_column_name(value: str) -> str:
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def as_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 30) -> int:
    number = as_float(value)
    if number is None:
        return default
    return int(round(number))


def scenario_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text.replace(" ", "_").replace("-", "_") or "unknown"


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _time_to_expiration_years(days_to_expiration: int) -> float:
    return max(float(days_to_expiration), 1.0) / 365.0


def black_scholes_call_price(
    underlying_price: float,
    strike_price: float,
    days_to_expiration: int,
    implied_volatility: float,
    risk_free_rate: float = 0.045,
    dividend_yield: float = 0.0,
) -> float:
    s = float(underlying_price)
    k = float(strike_price)
    t = _time_to_expiration_years(days_to_expiration)
    sigma = max(float(implied_volatility), 0.0001)
    r = float(risk_free_rate)
    q = float(dividend_yield)

    if s <= 0 or k <= 0:
        return 0.0

    d1 = (log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt(t))
    d2 = d1 - sigma * sqrt(t)
    call = s * exp(-q * t) * normal_cdf(d1) - k * exp(-r * t) * normal_cdf(d2)
    return max(call, 0.0)


def black_scholes_call_delta(
    underlying_price: float,
    strike_price: float,
    days_to_expiration: int,
    implied_volatility: float,
    risk_free_rate: float = 0.045,
    dividend_yield: float = 0.0,
) -> float:
    s = float(underlying_price)
    k = float(strike_price)
    t = _time_to_expiration_years(days_to_expiration)
    sigma = max(float(implied_volatility), 0.0001)
    r = float(risk_free_rate)
    q = float(dividend_yield)

    if s <= 0 or k <= 0:
        return 0.0

    d1 = (log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt(t))
    return exp(-q * t) * normal_cdf(d1)


def clamp(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)


def build_option_column_map(df: pd.DataFrame) -> dict[str, str | None]:
    return {key: find_column(df, candidates) for key, candidates in COLUMN_CANDIDATES.items()}


def build_tuning_column_map(df: pd.DataFrame) -> dict[str, str | None]:
    return {key: find_column(df, candidates) for key, candidates in TUNING_COLUMN_CANDIDATES.items()}


def load_tuning_lookup() -> dict[str, dict[str, str]]:
    if not TUNING_RECOMMENDATIONS_CSV.exists():
        return {}

    tuning_df = pd.read_csv(TUNING_RECOMMENDATIONS_CSV)
    if tuning_df.empty:
        return {}

    columns = build_tuning_column_map(tuning_df)
    scenario_col = columns.get("scenario")
    if scenario_col is None:
        return {}

    lookup: dict[str, dict[str, str]] = {}
    for _, row in tuning_df.iterrows():
        key = scenario_key(row.get(scenario_col))
        lookup[key] = {
            "status": str(row.get(columns.get("status") or "", "PASS")),
            "area": str(row.get(columns.get("area") or "", "No immediate tuning")),
            "recommendation": str(row.get(columns.get("recommendation") or "", "")),
        }
    return lookup


def determine_base_iv_adjustment(
    tuning_status: str,
    tuning_area: str,
    tuning_recommendation: str,
    config: dict[str, Any],
) -> tuple[float, str]:
    if not bool(config.get("apply_adjustments", True)):
        return 0.0, "Adjustments disabled by config."

    status = str(tuning_status or "PASS").upper()
    area = str(tuning_area or "").lower()
    rec = str(tuning_recommendation or "").lower()

    if status == "PASS":
        return 0.0, "No tuning issue detected."

    adjustment = 0.0
    reasons: list[str] = []

    if "premium" in area or "premium" in rec:
        if "small" in rec or "low" in rec or "non-positive" in rec:
            adjustment += float(config.get("premium_low_iv_bump", 0.010))
            reasons.append("Raised IV slightly because premium appeared low.")
        elif "large" in rec or "high" in rec:
            adjustment += float(config.get("premium_high_iv_cut", -0.010))
            reasons.append("Reduced IV slightly because premium appeared high.")

    if "volatility" in area or "volatility" in rec or " iv " in f" {rec} ":
        if "below" in rec or "low" in rec:
            adjustment += float(config.get("volatility_low_iv_bump", 0.010))
            reasons.append("Raised IV slightly because validation flagged low volatility.")
        elif "above" in rec or "high" in rec or "ceiling" in rec:
            adjustment += float(config.get("volatility_high_iv_cut", -0.010))
            reasons.append("Reduced IV slightly because validation flagged high volatility.")

    if "delta" in area or "delta" in rec:
        if "below target" in rec or "too far" in rec:
            adjustment += float(config.get("delta_low_iv_bump", 0.005))
            reasons.append("Raised IV slightly because estimated delta was below target.")
        elif "above target" in rec or "too close" in rec:
            adjustment += float(config.get("delta_high_iv_cut", -0.005))
            reasons.append("Reduced IV slightly because estimated delta was above target.")

    if not reasons and status in {"TUNE", "REVIEW"}:
        reasons.append("Recommendation logged; no automatic IV-only adjustment was appropriate.")

    max_abs = abs(float(config.get("max_abs_iv_adjustment_per_run", 0.020)))
    adjustment = clamp(adjustment, -max_abs, max_abs)
    return adjustment, " ".join(reasons)


def apply_relationship_adjustments(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    relationship_config = config.get("scenario_relationship_adjustments", {})
    min_gap = float(config.get("relationship_min_iv_gap", 0.005))
    max_abs = abs(float(config.get("max_abs_iv_adjustment_per_run", 0.020)))
    min_iv = float(config.get("minimum_adjusted_iv", 0.060))
    max_iv = float(config.get("maximum_adjusted_iv", 0.750))

    by_key = {scenario_key(row["scenario_name"]): row for row in rows}

    if relationship_config.get("ensure_volatile_whipsaw_has_highest_iv", True):
        volatile = by_key.get("volatile_whipsaw")
        if volatile is not None and rows:
            other_adjusted_ivs = [float(row["adjusted_implied_volatility"]) for row in rows if row is not volatile]
            if other_adjusted_ivs:
                required = max(other_adjusted_ivs) + min_gap
                current = float(volatile["adjusted_implied_volatility"])
                if current < required:
                    allowed = float(volatile["original_implied_volatility"]) + max_abs
                    new_iv = clamp(min(required, allowed), min_iv, max_iv)
                    extra = new_iv - current
                    volatile["adjusted_implied_volatility"] = new_iv
                    volatile["iv_adjustment"] = float(volatile["iv_adjustment"]) + extra
                    volatile["adjustment_reason"] += " Relationship rule raised Volatile Whipsaw IV toward the highest scenario IV."

    if relationship_config.get("ensure_downtrend_iv_exceeds_sideways_choppy_iv", True):
        downtrend = by_key.get("downtrend")
        sideways = by_key.get("sideways_choppy")
        if downtrend is not None and sideways is not None:
            required = float(sideways["adjusted_implied_volatility"]) + min_gap
            current = float(downtrend["adjusted_implied_volatility"])
            if current < required:
                allowed = float(downtrend["original_implied_volatility"]) + max_abs
                new_iv = clamp(min(required, allowed), min_iv, max_iv)
                extra = new_iv - current
                downtrend["adjusted_implied_volatility"] = new_iv
                downtrend["iv_adjustment"] = float(downtrend["iv_adjustment"]) + extra
                downtrend["adjustment_reason"] += " Relationship rule raised Downtrend IV above Sideways Choppy IV."


def recalculate_outputs(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        adjusted_iv = float(row["adjusted_implied_volatility"])
        underlying = float(row["underlying_price"])
        strike = float(row["estimated_strike"])
        dte = int(row["days_to_expiration"])
        risk_free_rate = float(row["risk_free_rate"])
        dividend_yield = float(row["dividend_yield"])
        original_premium = float(row["original_call_premium"])
        original_delta = float(row["original_call_delta"])

        adjusted_premium = black_scholes_call_price(
            underlying_price=underlying,
            strike_price=strike,
            days_to_expiration=dte,
            implied_volatility=adjusted_iv,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
        )
        adjusted_delta = black_scholes_call_delta(
            underlying_price=underlying,
            strike_price=strike,
            days_to_expiration=dte,
            implied_volatility=adjusted_iv,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
        )
        premium_change = adjusted_premium - original_premium
        premium_change_pct = None
        if original_premium != 0:
            premium_change_pct = 100.0 * premium_change / original_premium

        row["adjusted_call_premium"] = round(adjusted_premium, 4)
        row["premium_change"] = round(premium_change, 4)
        row["premium_change_pct"] = round(premium_change_pct, 4) if premium_change_pct is not None else None
        row["adjusted_call_delta"] = round(adjusted_delta, 4)
        row["delta_change"] = round(adjusted_delta - original_delta, 4)
        row["adjusted_implied_volatility"] = round(adjusted_iv, 6)
        row["iv_adjustment"] = round(float(row["iv_adjustment"]), 6)
        if abs(float(row["iv_adjustment"])) < 0.000001:
            row["adjustment_status"] = "UNCHANGED"
        else:
            row["adjustment_status"] = "ADJUSTED"


def build_adjusted_premiums() -> pd.DataFrame:
    ensure_directories()
    config = load_or_create_adjustment_config()

    if not OPTION_PREMIUM_CSV.exists():
        raise FileNotFoundError(f"Missing required option premium CSV: {OPTION_PREMIUM_CSV}")

    option_df = pd.read_csv(OPTION_PREMIUM_CSV)
    if option_df.empty:
        raise ValueError(f"Option premium CSV has no data rows: {OPTION_PREMIUM_CSV}")

    tuning_lookup = load_tuning_lookup()
    columns = build_option_column_map(option_df)

    min_iv = float(config.get("minimum_adjusted_iv", 0.060))
    max_iv = float(config.get("maximum_adjusted_iv", 0.750))

    rows: list[dict[str, Any]] = []
    for index, source_row in option_df.iterrows():
        scenario_name = str(source_row.get(columns.get("scenario") or "", f"scenario_{index + 1}")).strip()
        display_name = str(source_row.get(columns.get("display_name") or "", scenario_name)).strip()
        key = scenario_key(scenario_name)
        tuning = tuning_lookup.get(key, {"status": "PASS", "area": "No immediate tuning", "recommendation": "No tuning recommendation found."})

        underlying = as_float(source_row.get(columns.get("underlying_price") or ""), 545.25) or 545.25
        target_delta = as_float(source_row.get(columns.get("target_delta") or ""), 0.30) or 0.30
        strike = as_float(source_row.get(columns.get("strike") or ""), underlying * 1.03) or underlying * 1.03
        dte = as_int(source_row.get(columns.get("dte") or ""), 30)
        original_iv = as_float(source_row.get(columns.get("iv") or ""), 0.20) or 0.20
        risk_free_rate = as_float(source_row.get(columns.get("risk_free_rate") or ""), 0.045) or 0.045
        dividend_yield = as_float(source_row.get(columns.get("dividend_yield") or ""), 0.0) or 0.0
        original_premium = as_float(source_row.get(columns.get("premium") or ""), 0.0) or 0.0
        original_delta = as_float(source_row.get(columns.get("delta") or ""), 0.0) or 0.0
        moneyness = as_float(source_row.get(columns.get("moneyness_percent") or ""), ((strike / underlying) - 1.0) * 100.0)
        if moneyness is None:
            moneyness = ((strike / underlying) - 1.0) * 100.0

        iv_adjustment, reason = determine_base_iv_adjustment(
            tuning_status=tuning["status"],
            tuning_area=tuning["area"],
            tuning_recommendation=tuning["recommendation"],
            config=config,
        )
        adjusted_iv = clamp(original_iv + iv_adjustment, min_iv, max_iv)
        iv_adjustment = adjusted_iv - original_iv

        rows.append(
            {
                "scenario_name": scenario_name,
                "display_name": display_name,
                "adjustment_status": "UNCHANGED",
                "adjustment_reason": reason,
                "underlying_price": round(float(underlying), 4),
                "target_delta": round(float(target_delta), 4),
                "estimated_strike": round(float(strike), 4),
                "days_to_expiration": int(dte),
                "original_implied_volatility": round(float(original_iv), 6),
                "iv_adjustment": round(float(iv_adjustment), 6),
                "adjusted_implied_volatility": round(float(adjusted_iv), 6),
                "risk_free_rate": round(float(risk_free_rate), 6),
                "dividend_yield": round(float(dividend_yield), 6),
                "original_call_premium": round(float(original_premium), 4),
                "adjusted_call_premium": 0.0,
                "premium_change": 0.0,
                "premium_change_pct": None,
                "original_call_delta": round(float(original_delta), 4),
                "adjusted_call_delta": 0.0,
                "delta_change": 0.0,
                "moneyness_percent": round(float(moneyness), 4),
                "tuning_status": tuning["status"],
                "tuning_area": tuning["area"],
                "tuning_recommendation": tuning["recommendation"],
            }
        )

    apply_relationship_adjustments(rows, config)
    recalculate_outputs(rows)

    output_columns = [field.name for field in AdjustedPremiumResult.__dataclass_fields__.values()]
    result_df = pd.DataFrame(rows)
    result_df = result_df[output_columns]
    result_df.to_csv(ADJUSTED_PREMIUM_CSV, index=False)
    write_html_report(result_df, config)
    write_summary(result_df, config)
    return result_df


def write_html_report(df: pd.DataFrame, config: dict[str, Any]) -> None:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed_rows = int((df["adjustment_status"] == "ADJUSTED").sum()) if "adjustment_status" in df.columns else 0
    total_change = float(df["premium_change"].sum()) if "premium_change" in df.columns else 0.0
    average_change = float(df["premium_change"].mean()) if "premium_change" in df.columns and not df.empty else 0.0
    table_html = df.to_html(index=False, escape=True)

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>Phase 2E Controlled Premium Model Adjustment</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
h1, h2 {{ color: #111827; }}
.summary {{ background: #f3f4f6; padding: 16px; border-radius: 10px; margin: 16px 0; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
th {{ background: #e5e7eb; }}
.small {{ color: #6b7280; font-size: 12px; }}
</style>
</head>
<body>
<h1>Phase 2E Controlled Premium Model Adjustment</h1>
<p class=\"small\">Generated: {generated}</p>
<div class=\"summary\">
<h2>Summary</h2>
<p>This report applies a conservative IV-only adjustment layer to the Phase 2B premium model. Original premium outputs are not overwritten.</p>
<p><strong>Adjusted rows:</strong> {changed_rows} of {len(df)}</p>
<p><strong>Total premium change across scenarios:</strong> {total_change:.4f}</p>
<p><strong>Average premium change:</strong> {average_change:.4f}</p>
<p><strong>Adjustment config:</strong> {ADJUSTMENT_CONFIG_JSON}</p>
</div>
<h2>Adjusted premium comparison</h2>
{table_html}
</body>
</html>
"""
    ADJUSTMENT_HTML.write_text(html, encoding="utf-8")


def write_summary(df: pd.DataFrame, config: dict[str, Any]) -> None:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed_rows = int((df["adjustment_status"] == "ADJUSTED").sum()) if "adjustment_status" in df.columns else 0
    total_change = float(df["premium_change"].sum()) if "premium_change" in df.columns else 0.0
    average_change = float(df["premium_change"].mean()) if "premium_change" in df.columns and not df.empty else 0.0
    max_abs_change = float(df["premium_change"].abs().max()) if "premium_change" in df.columns and not df.empty else 0.0

    lines = [
        "Phase 2E Controlled Premium Model Adjustment Summary",
        "=" * 58,
        f"Generated: {generated}",
        f"Project root: {PROJECT_ROOT}",
        "",
        "Purpose",
        "-------",
        "This scaffold applies one conservative premium-model tuning adjustment layer.",
        "It does not overwrite the original option premium scaffold output.",
        "",
        "Adjustment method",
        "-----------------",
        str(config.get("adjustment_scope", "iv_only_fixed_strike")),
        "",
        "Summary metrics",
        "---------------",
        f"Rows reviewed: {len(df)}",
        f"Rows adjusted: {changed_rows}",
        f"Total premium change across scenarios: {total_change:.4f}",
        f"Average premium change: {average_change:.4f}",
        f"Maximum absolute premium change: {max_abs_change:.4f}",
        "",
        "Output files",
        "------------",
        str(ADJUSTED_PREMIUM_CSV),
        str(ADJUSTMENT_HTML),
        str(ADJUSTMENT_SUMMARY_TXT),
        "",
        "Next modeling step",
        "------------------",
        "After reviewing this controlled adjustment, compare adjusted premiums against premium-aware payoff results before replacing any customer-facing assumptions.",
    ]
    ADJUSTMENT_SUMMARY_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 96)
    print("Phase 2E controlled premium-model tuning adjustment scaffold")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Input option premium CSV: {OPTION_PREMIUM_CSV}")
    print(f"Input tuning recommendations CSV: {TUNING_RECOMMENDATIONS_CSV}")
    print(f"Adjustment config: {ADJUSTMENT_CONFIG_JSON}")
    print()

    df = build_adjusted_premiums()
    changed_rows = int((df["adjustment_status"] == "ADJUSTED").sum()) if "adjustment_status" in df.columns else 0
    print("Controlled premium-model adjustment output created.")
    print(f"Rows: {len(df)}")
    print(f"Adjusted rows: {changed_rows}")
    print(f"CSV:  {ADJUSTED_PREMIUM_CSV}")
    print(f"HTML: {ADJUSTMENT_HTML}")
    print(f"TXT:  {ADJUSTMENT_SUMMARY_TXT}")
    print()
    print("Overall Phase 2E controlled premium adjustment status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
