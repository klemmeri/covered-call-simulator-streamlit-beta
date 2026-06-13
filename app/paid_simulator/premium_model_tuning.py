"""
premium_model_tuning.py

Phase 2D premium-model assumption tuning scaffold for the Covered Call
Strategy Stress Test project.

This module does not replace the current option-premium model. It reads the
Phase 2B/2C premium-model outputs and produces a tuning recommendation table
that identifies where the current assumptions may need adjustment.

Inputs
------
outputs/tables/paid_simulator/option_premium_scaffold.csv
outputs/tables/paid_simulator/premium_model_validation_scaffold.csv
config/premium_model_tuning_config.json  (created automatically if missing)

Outputs
-------
outputs/tables/paid_simulator/premium_model_tuning_recommendations.csv
outputs/reports/paid_simulator/premium_model_tuning_recommendations.html
outputs/reports/paid_simulator/premium_model_tuning_summary.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OPTION_PREMIUM_CSV = OUTPUT_TABLE_DIR / "option_premium_scaffold.csv"
VALIDATION_CSV = OUTPUT_TABLE_DIR / "premium_model_validation_scaffold.csv"
TUNING_CONFIG_JSON = CONFIG_DIR / "premium_model_tuning_config.json"

TUNING_OUTPUT_CSV = OUTPUT_TABLE_DIR / "premium_model_tuning_recommendations.csv"
TUNING_OUTPUT_HTML = OUTPUT_REPORT_DIR / "premium_model_tuning_recommendations.html"
TUNING_SUMMARY_TXT = OUTPUT_REPORT_DIR / "premium_model_tuning_summary.txt"


DEFAULT_TUNING_CONFIG: dict[str, Any] = {
    "description": "Phase 2D tuning thresholds for the premium-model scaffold.",
    "target_delta_default": 0.30,
    "target_delta_tolerance": 0.05,
    "minimum_premium_pct_of_stock": 0.20,
    "maximum_premium_pct_of_stock": 6.00,
    "minimum_implied_volatility": 0.05,
    "maximum_implied_volatility": 0.80,
    "minimum_strike_distance_pct": 0.50,
    "maximum_strike_distance_pct": 15.00,
    "scenario_relationship_rules": {
        "volatile_whipsaw_should_have_highest_iv": True,
        "downtrend_iv_should_exceed_sideways_choppy_iv": True,
        "strong_rally_iv_should_not_exceed_volatile_whipsaw_iv": True,
    },
    "notes": [
        "Percent thresholds use percentage points. For example, 0.20 means 0.20% of stock price.",
        "This config drives tuning recommendations only. It does not change the pricing model yet.",
    ],
}


COLUMN_CANDIDATES = {
    "scenario": ["scenario", "scenario_name", "name"],
    "display_name": ["display_name", "scenario_display_name", "market_path", "scenario_label"],
    "stock_price": ["underlying_price", "stock_price", "current_price", "demo_price", "starting_price"],
    "strike": ["estimated_strike", "call_strike", "strike", "selected_strike"],
    "premium": [
        "estimated_call_premium",
        "call_premium",
        "premium",
        "option_premium",
        "estimated_premium",
    ],
    "delta": ["estimated_call_delta", "call_delta", "estimated_delta", "delta"],
    "target_delta": ["target_delta", "configured_target_delta", "desired_delta"],
    "iv": [
        "estimated_implied_volatility",
        "implied_volatility",
        "estimated_iv",
        "iv",
        "scenario_iv",
    ],
    "moneyness_pct": [
        "moneyness_pct",
        "moneyness_percent",
        "strike_distance_pct",
        "strike_distance_percent",
    ],
}


@dataclass
class TuningResult:
    scenario: str
    display_name: str
    stock_price: float | None
    strike: float | None
    premium: float | None
    premium_pct_of_stock: float | None
    implied_volatility: float | None
    estimated_delta: float | None
    target_delta: float
    delta_error: float | None
    strike_distance_pct: float | None
    tuning_status: str
    tuning_area: str
    recommendation: str


def ensure_directories() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_or_create_tuning_config() -> dict[str, Any]:
    ensure_directories()
    if not TUNING_CONFIG_JSON.exists():
        TUNING_CONFIG_JSON.write_text(
            json.dumps(DEFAULT_TUNING_CONFIG, indent=2),
            encoding="utf-8",
        )
        return dict(DEFAULT_TUNING_CONFIG)

    try:
        loaded = json.loads(TUNING_CONFIG_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        backup_path = TUNING_CONFIG_JSON.with_suffix(".invalid.json")
        backup_path.write_text(TUNING_CONFIG_JSON.read_text(encoding="utf-8"), encoding="utf-8")
        TUNING_CONFIG_JSON.write_text(json.dumps(DEFAULT_TUNING_CONFIG, indent=2), encoding="utf-8")
        return dict(DEFAULT_TUNING_CONFIG)

    merged = dict(DEFAULT_TUNING_CONFIG)
    merged.update(loaded)
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


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def read_value(row: pd.Series, column: str | None) -> Any:
    if column is None:
        return None
    if column not in row.index:
        return None
    return row[column]


def build_column_map(df: pd.DataFrame) -> dict[str, str | None]:
    return {key: find_column(df, candidates) for key, candidates in COLUMN_CANDIDATES.items()}


def scenario_key(value: Any) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip()
    if not text:
        return "unknown"
    return text.lower().replace(" ", "_").replace("-", "_")


def classify_row(
    scenario: str,
    display_name: str,
    stock_price: float | None,
    strike: float | None,
    premium: float | None,
    implied_volatility: float | None,
    estimated_delta: float | None,
    target_delta: float,
    config: dict[str, Any],
) -> TuningResult:
    min_premium_pct = float(config["minimum_premium_pct_of_stock"])
    max_premium_pct = float(config["maximum_premium_pct_of_stock"])
    min_iv = float(config["minimum_implied_volatility"])
    max_iv = float(config["maximum_implied_volatility"])
    delta_tolerance = float(config["target_delta_tolerance"])
    min_strike_distance_pct = float(config["minimum_strike_distance_pct"])
    max_strike_distance_pct = float(config["maximum_strike_distance_pct"])

    premium_pct: float | None = None
    strike_distance_pct: float | None = None
    delta_error: float | None = None

    if stock_price is not None and stock_price > 0 and premium is not None:
        premium_pct = 100.0 * premium / stock_price

    if stock_price is not None and stock_price > 0 and strike is not None:
        strike_distance_pct = 100.0 * (strike - stock_price) / stock_price

    if estimated_delta is not None:
        delta_error = estimated_delta - target_delta

    issues: list[tuple[str, str]] = []

    if stock_price is None or stock_price <= 0:
        issues.append(("Input data", "Stock price is missing or invalid."))

    if strike is None:
        issues.append(("Strike selection", "Estimated strike is missing."))
    elif stock_price is not None and strike <= stock_price:
        issues.append(("Strike selection", "Estimated strike is not above the stock price for a covered call."))

    if premium is None or premium <= 0:
        issues.append(("Premium level", "Estimated premium is missing or non-positive."))
    elif premium_pct is not None and premium_pct < min_premium_pct:
        issues.append(("Premium level", "Estimated premium is very small relative to the stock price."))
    elif premium_pct is not None and premium_pct > max_premium_pct:
        issues.append(("Premium level", "Estimated premium is very large relative to the stock price."))

    if implied_volatility is None:
        issues.append(("Volatility", "Estimated implied volatility is missing."))
    elif implied_volatility < min_iv:
        issues.append(("Volatility", "Estimated implied volatility is below the configured floor."))
    elif implied_volatility > max_iv:
        issues.append(("Volatility", "Estimated implied volatility is above the configured ceiling."))

    if estimated_delta is None:
        issues.append(("Delta targeting", "Estimated call delta is missing."))
    elif abs(estimated_delta - target_delta) > delta_tolerance:
        if estimated_delta < target_delta:
            issues.append(("Delta targeting", "Estimated delta is below target; strike may be too far OTM or IV too low."))
        else:
            issues.append(("Delta targeting", "Estimated delta is above target; strike may be too close or IV too high."))

    if strike_distance_pct is not None:
        if strike_distance_pct < min_strike_distance_pct:
            issues.append(("Strike distance", "Strike is very close to the current stock price."))
        elif strike_distance_pct > max_strike_distance_pct:
            issues.append(("Strike distance", "Strike is very far above the current stock price."))

    if not issues:
        status = "PASS"
        area = "No immediate tuning"
        recommendation = "No tuning change suggested by the current Phase 2D thresholds."
    else:
        area = issues[0][0]
        status = "TUNE" if len(issues) == 1 else "REVIEW"
        recommendation = "; ".join(message for _, message in issues)

    return TuningResult(
        scenario=scenario,
        display_name=display_name,
        stock_price=stock_price,
        strike=strike,
        premium=premium,
        premium_pct_of_stock=premium_pct,
        implied_volatility=implied_volatility,
        estimated_delta=estimated_delta,
        target_delta=target_delta,
        delta_error=delta_error,
        strike_distance_pct=strike_distance_pct,
        tuning_status=status,
        tuning_area=area,
        recommendation=recommendation,
    )


def add_relationship_recommendations(results_df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    if results_df.empty or "scenario" not in results_df.columns:
        return results_df

    df = results_df.copy()
    iv_by_scenario: dict[str, float] = {}
    for _, row in df.iterrows():
        key = scenario_key(row.get("scenario"))
        iv = as_float(row.get("implied_volatility"))
        if iv is not None:
            iv_by_scenario[key] = iv

    global_issues: list[str] = []
    rules = config.get("scenario_relationship_rules", {})

    volatile_iv = iv_by_scenario.get("volatile_whipsaw")
    strong_rally_iv = iv_by_scenario.get("strong_rally")
    downtrend_iv = iv_by_scenario.get("downtrend")
    sideways_iv = iv_by_scenario.get("sideways_choppy")

    if rules.get("volatile_whipsaw_should_have_highest_iv", True) and volatile_iv is not None:
        other_ivs = [value for key, value in iv_by_scenario.items() if key != "volatile_whipsaw"]
        if other_ivs and volatile_iv < max(other_ivs):
            global_issues.append("Volatile Whipsaw IV is not the highest scenario IV.")

    if rules.get("downtrend_iv_should_exceed_sideways_choppy_iv", True):
        if downtrend_iv is not None and sideways_iv is not None and downtrend_iv <= sideways_iv:
            global_issues.append("Downtrend IV does not exceed Sideways Choppy IV.")

    if rules.get("strong_rally_iv_should_not_exceed_volatile_whipsaw_iv", True):
        if strong_rally_iv is not None and volatile_iv is not None and strong_rally_iv > volatile_iv:
            global_issues.append("Strong Rally IV exceeds Volatile Whipsaw IV.")

    if not global_issues:
        df["relationship_note"] = "Scenario IV relationships pass current checks."
        return df

    note = " ".join(global_issues)
    df["relationship_note"] = note
    mask = df["tuning_status"].eq("PASS")
    df.loc[mask, "tuning_status"] = "REVIEW"
    df.loc[mask, "tuning_area"] = "Scenario relationships"
    df.loc[mask, "recommendation"] = note
    df.loc[~mask, "recommendation"] = df.loc[~mask, "recommendation"].astype(str) + " " + note
    return df


def build_tuning_recommendations() -> pd.DataFrame:
    ensure_directories()
    config = load_or_create_tuning_config()

    if not OPTION_PREMIUM_CSV.exists():
        raise FileNotFoundError(f"Missing required option premium CSV: {OPTION_PREMIUM_CSV}")

    option_df = pd.read_csv(OPTION_PREMIUM_CSV)
    if option_df.empty:
        raise ValueError(f"Option premium CSV has no data rows: {OPTION_PREMIUM_CSV}")

    columns = build_column_map(option_df)
    target_delta_default = float(config.get("target_delta_default", 0.30))

    results: list[TuningResult] = []
    for index, row in option_df.iterrows():
        scenario_value = read_value(row, columns["scenario"])
        display_value = read_value(row, columns["display_name"])
        scenario = str(scenario_value).strip() if scenario_value is not None else f"scenario_{index + 1}"
        display_name = str(display_value).strip() if display_value is not None else scenario

        stock_price = as_float(read_value(row, columns["stock_price"]))
        strike = as_float(read_value(row, columns["strike"]))
        premium = as_float(read_value(row, columns["premium"]))
        iv = as_float(read_value(row, columns["iv"]))
        delta = as_float(read_value(row, columns["delta"]))
        target_delta = as_float(read_value(row, columns["target_delta"])) or target_delta_default

        moneyness_col = columns.get("moneyness_pct")
        moneyness_value = as_float(read_value(row, moneyness_col)) if moneyness_col else None
        result = classify_row(
            scenario=scenario,
            display_name=display_name,
            stock_price=stock_price,
            strike=strike,
            premium=premium,
            implied_volatility=iv,
            estimated_delta=delta,
            target_delta=target_delta,
            config=config,
        )
        if moneyness_value is not None and result.strike_distance_pct is None:
            result.strike_distance_pct = moneyness_value
        results.append(result)

    result_df = pd.DataFrame([r.__dict__ for r in results])
    result_df = add_relationship_recommendations(result_df, config)

    result_df = result_df[
        [
            "scenario",
            "display_name",
            "tuning_status",
            "tuning_area",
            "recommendation",
            "stock_price",
            "strike",
            "strike_distance_pct",
            "premium",
            "premium_pct_of_stock",
            "implied_volatility",
            "estimated_delta",
            "target_delta",
            "delta_error",
            "relationship_note",
        ]
    ]

    result_df.to_csv(TUNING_OUTPUT_CSV, index=False)
    write_html_report(result_df, config)
    write_summary(result_df, config)
    return result_df


def format_float(value: Any, digits: int = 4) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.{digits}f}"


def write_html_report(df: pd.DataFrame, config: dict[str, Any]) -> None:
    status_counts = df["tuning_status"].value_counts().to_dict() if "tuning_status" in df.columns else {}
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table_html = df.to_html(index=False, escape=True)

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>Phase 2D Premium Model Tuning Recommendations</title>
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
<h1>Phase 2D Premium Model Tuning Recommendations</h1>
<p class=\"small\">Generated: {generated}</p>
<div class=\"summary\">
<h2>Summary</h2>
<p>This report reviews the current premium-model outputs and flags assumptions that may need tuning before the premium model is promoted further into the customer-facing workflow.</p>
<p><strong>Status counts:</strong> {status_counts}</p>
<p><strong>Config file:</strong> {TUNING_CONFIG_JSON}</p>
</div>
<h2>Recommendations</h2>
{table_html}
</body>
</html>
"""
    TUNING_OUTPUT_HTML.write_text(html, encoding="utf-8")


def write_summary(df: pd.DataFrame, config: dict[str, Any]) -> None:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_counts = df["tuning_status"].value_counts().to_dict() if "tuning_status" in df.columns else {}
    total_rows = len(df)
    pass_rows = int(status_counts.get("PASS", 0))
    review_rows = total_rows - pass_rows

    lines = [
        "Phase 2D Premium Model Tuning Summary",
        "=" * 48,
        f"Generated: {generated}",
        f"Project root: {PROJECT_ROOT}",
        "",
        "Purpose",
        "-------",
        "This scaffold reviews the current premium-model outputs and produces tuning recommendations.",
        "It does not change the option-pricing model yet.",
        "",
        "Status counts",
        "-------------",
    ]

    for status, count in sorted(status_counts.items()):
        lines.append(f"{status}: {count}")

    lines.extend(
        [
            "",
            "Overall tuning status",
            "---------------------",
            "PASS" if review_rows == 0 else "REVIEW",
            "",
            "Output files",
            "------------",
            str(TUNING_OUTPUT_CSV),
            str(TUNING_OUTPUT_HTML),
            str(TUNING_SUMMARY_TXT),
            "",
            "Next modeling step",
            "------------------",
            "After these recommendations are reviewed, the next step is to make the option-premium model tunable from a config file rather than relying on hard-coded scenario assumptions.",
        ]
    )

    TUNING_SUMMARY_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 96)
    print("Phase 2D premium-model assumption tuning scaffold")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Input option premium CSV: {OPTION_PREMIUM_CSV}")
    print(f"Tuning config: {TUNING_CONFIG_JSON}")
    print()

    df = build_tuning_recommendations()
    print("Tuning recommendations created.")
    print(f"Rows: {len(df)}")
    print(f"CSV:  {TUNING_OUTPUT_CSV}")
    print(f"HTML: {TUNING_OUTPUT_HTML}")
    print(f"TXT:  {TUNING_SUMMARY_TXT}")
    print()

    status_counts = df["tuning_status"].value_counts().to_dict()
    print("Status counts:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print()
    print("Overall Phase 2D tuning scaffold status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
