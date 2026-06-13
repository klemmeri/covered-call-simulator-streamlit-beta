"""
premium_model_validation.py

Phase 2C premium-model validation scaffold for the Covered Call Strategy Stress Test.

This module checks whether the Phase 2B option-premium outputs look internally
reasonable before those values are treated as customer-facing modeling results.
It is intentionally conservative and standalone.

Inputs, when available:
    outputs/tables/paid_simulator/option_premium_scaffold.csv
    outputs/tables/paid_simulator/premium_aware_payoff_scaffold.csv
    config/premium_model_validation_config.json

Outputs:
    outputs/tables/paid_simulator/premium_model_validation_scaffold.csv
    outputs/reports/paid_simulator/premium_model_validation_scaffold.html
    outputs/reports/paid_simulator/premium_model_validation_summary.txt
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json
import math

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"

OPTION_PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"
PREMIUM_AWARE_PAYOFF_CSV = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
VALIDATION_CONFIG_PATH = CONFIG_DIR / "premium_model_validation_config.json"
VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
VALIDATION_HTML = REPORT_DIR / "premium_model_validation_scaffold.html"
VALIDATION_SUMMARY_TXT = REPORT_DIR / "premium_model_validation_summary.txt"


DEFAULT_VALIDATION_CONFIG: dict[str, Any] = {
    "version": "Phase 2C scaffold v0.1",
    "description": "Validation bands for the option-premium model scaffold. These are reasonableness checks, not live-market quote rules.",
    "premium_percent_min": 0.10,
    "premium_percent_max": 6.00,
    "iv_min": 0.06,
    "iv_max": 0.75,
    "target_delta_default": 0.30,
    "delta_tolerance": 0.06,
    "minimum_otm_moneyness_percent": 0.00,
    "maximum_otm_moneyness_percent": 12.00,
    "warning_premium_percent_low": 0.25,
    "warning_premium_percent_high": 4.00,
    "require_positive_premium": True,
    "require_otm_call": True,
    "relationship_checks": {
        "volatile_whipsaw_should_have_higher_iv_than_strong_rally": True,
        "downtrend_should_have_higher_iv_than_sideways_choppy": True,
        "sideways_choppy_should_not_have_lower_premium_than_strong_rally_by_more_than_percent": 35.0
    }
}


COLUMN_CANDIDATES = {
    "scenario_name": ["scenario_name", "scenario", "Scenario", "market_path", "path", "name"],
    "display_name": ["display_name", "scenario_display_name", "Scenario", "scenario"],
    "underlying_price": ["underlying_price", "current_price", "starting_price", "stock_price", "price"],
    "target_delta": ["target_delta", "desired_delta", "call_target_delta"],
    "estimated_strike": ["estimated_strike", "call_strike", "strike", "selected_strike", "short_call_strike"],
    "days_to_expiration": ["days_to_expiration", "dte", "target_dte"],
    "implied_volatility": ["implied_volatility", "iv", "estimated_iv", "scenario_iv"],
    "estimated_call_premium": ["estimated_call_premium", "call_premium", "premium", "short_call_premium"],
    "estimated_call_delta": ["estimated_call_delta", "call_delta", "delta", "selected_delta"],
    "moneyness_percent": ["moneyness_percent", "moneyness", "otm_percent"],
}


@dataclass(frozen=True)
class PremiumValidationResult:
    """Summary of a premium-model validation run."""

    csv_path: Path
    html_path: Path
    summary_path: Path
    row_count: int
    pass_count: int
    review_count: int
    fail_count: int
    overall_status: str


def normalize_column_name(name: Any) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def normalize_scenario_name(name: Any) -> str:
    return normalize_column_name(name)


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        norm = normalize_column_name(col)
        for candidate in candidates:
            if normalize_column_name(candidate) in norm:
                return col
    return None


def currency(value: Any) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)


def percent_from_decimal(value: Any) -> str:
    try:
        return f"{float(value) * 100.0:.1f}%"
    except Exception:
        return str(value)


def percent_value(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return str(value)


def ensure_validation_config(config_path: Path = VALIDATION_CONFIG_PATH) -> dict[str, Any]:
    """Load validation config, creating the default file if needed."""

    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        config_path.write_text(json.dumps(DEFAULT_VALIDATION_CONFIG, indent=2), encoding="utf-8")
        return dict(DEFAULT_VALIDATION_CONFIG)

    try:
        with config_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
    except Exception:
        loaded = {}

    merged = dict(DEFAULT_VALIDATION_CONFIG)
    if isinstance(loaded, dict):
        for key, value in loaded.items():
            if key == "relationship_checks" and isinstance(value, dict):
                checks = dict(DEFAULT_VALIDATION_CONFIG["relationship_checks"])
                checks.update(value)
                merged[key] = checks
            else:
                merged[key] = value
    return merged


def _try_generate_upstream_outputs() -> None:
    """Best-effort upstream generation for missing Phase 2B outputs."""

    if not OPTION_PREMIUM_CSV.exists():
        try:
            from app.paid_simulator.option_premium_model import export_option_premium_results

            export_option_premium_results(OPTION_PREMIUM_CSV)
        except Exception:
            pass

    if not PREMIUM_AWARE_PAYOFF_CSV.exists():
        try:
            from app.paid_simulator.premium_aware_payoff_runner import run_premium_aware_payoff

            run_premium_aware_payoff()
        except Exception:
            pass


def load_option_premium_table(path: Path = OPTION_PREMIUM_CSV) -> pd.DataFrame:
    _try_generate_upstream_outputs()
    if not path.exists():
        raise FileNotFoundError(f"Missing option-premium scaffold output: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Option-premium scaffold output is empty: {path}")
    return df


def prepare_premium_frame(df: pd.DataFrame) -> pd.DataFrame:
    detected: dict[str, str] = {}
    missing: list[str] = []
    for canonical, candidates in COLUMN_CANDIDATES.items():
        col = find_column(df, candidates)
        if col is None and canonical in {
            "scenario_name",
            "underlying_price",
            "estimated_strike",
            "implied_volatility",
            "estimated_call_premium",
            "estimated_call_delta",
        }:
            missing.append(canonical)
        elif col is not None:
            detected[canonical] = col

    if missing:
        raise ValueError("Could not detect required option-premium columns: " + ", ".join(missing))

    work = pd.DataFrame()
    work["scenario_name"] = df[detected["scenario_name"]].astype(str)
    display_col = detected.get("display_name", detected["scenario_name"])
    work["display_name"] = df[display_col].astype(str)
    work["scenario_key"] = work["scenario_name"].map(normalize_scenario_name)
    work["underlying_price"] = pd.to_numeric(df[detected["underlying_price"]], errors="coerce")
    work["estimated_strike"] = pd.to_numeric(df[detected["estimated_strike"]], errors="coerce")
    work["implied_volatility"] = pd.to_numeric(df[detected["implied_volatility"]], errors="coerce")
    work["estimated_call_premium"] = pd.to_numeric(df[detected["estimated_call_premium"]], errors="coerce")
    work["estimated_call_delta"] = pd.to_numeric(df[detected["estimated_call_delta"]], errors="coerce")

    target_delta_col = detected.get("target_delta")
    if target_delta_col:
        work["target_delta"] = pd.to_numeric(df[target_delta_col], errors="coerce")
    else:
        work["target_delta"] = float(DEFAULT_VALIDATION_CONFIG["target_delta_default"])

    dte_col = detected.get("days_to_expiration")
    if dte_col:
        work["days_to_expiration"] = pd.to_numeric(df[dte_col], errors="coerce")
    else:
        work["days_to_expiration"] = 30

    moneyness_col = detected.get("moneyness_percent")
    if moneyness_col:
        work["moneyness_percent"] = pd.to_numeric(df[moneyness_col], errors="coerce")
    else:
        work["moneyness_percent"] = (work["estimated_strike"] / work["underlying_price"] - 1.0) * 100.0

    work["premium_percent_of_underlying"] = (
        work["estimated_call_premium"] / work["underlying_price"] * 100.0
    )
    work["strike_distance_dollars"] = work["estimated_strike"] - work["underlying_price"]
    return work


def classify_row(row: pd.Series, config: dict[str, Any]) -> tuple[str, str, str]:
    """Return status, issue, and suggested adjustment for a premium row."""

    issues: list[str] = []
    warnings: list[str] = []
    adjustments: list[str] = []

    premium = row.get("estimated_call_premium")
    premium_pct = row.get("premium_percent_of_underlying")
    iv = row.get("implied_volatility")
    delta = row.get("estimated_call_delta")
    target_delta = row.get("target_delta")
    moneyness = row.get("moneyness_percent")
    strike = row.get("estimated_strike")
    underlying = row.get("underlying_price")

    def bad_number(value: Any) -> bool:
        try:
            return pd.isna(value) or not math.isfinite(float(value))
        except Exception:
            return True

    if config.get("require_positive_premium", True) and (bad_number(premium) or float(premium) <= 0):
        issues.append("Premium is missing or non-positive")
        adjustments.append("Check Black-Scholes inputs and scenario IV mapping")

    if not bad_number(premium_pct):
        if float(premium_pct) < float(config.get("premium_percent_min", 0.10)):
            issues.append("Premium is below minimum validation band")
            adjustments.append("Raise IV, shorten strike distance, or review target delta")
        elif float(premium_pct) > float(config.get("premium_percent_max", 6.00)):
            issues.append("Premium is above maximum validation band")
            adjustments.append("Lower IV, widen strike distance, or review DTE")
        elif float(premium_pct) < float(config.get("warning_premium_percent_low", 0.25)):
            warnings.append("Premium is very low")
            adjustments.append("Review whether this setup has enough income to justify capped upside")
        elif float(premium_pct) > float(config.get("warning_premium_percent_high", 4.00)):
            warnings.append("Premium is unusually high")
            adjustments.append("Review whether volatility or path-risk assumptions are too aggressive")
    else:
        issues.append("Premium percent cannot be calculated")

    if bad_number(iv) or float(iv) < float(config.get("iv_min", 0.06)) or float(iv) > float(config.get("iv_max", 0.75)):
        issues.append("Implied volatility is outside validation band")
        adjustments.append("Review scenario-level realized-volatility and IV-bias mapping")

    if bad_number(delta) or bad_number(target_delta):
        issues.append("Estimated delta or target delta is missing")
    else:
        delta_error = abs(float(delta) - float(target_delta))
        if delta_error > float(config.get("delta_tolerance", 0.06)):
            issues.append("Estimated delta is too far from target delta")
            adjustments.append("Review strike solver, rounding, and delta tolerance")

    if config.get("require_otm_call", True):
        if bad_number(strike) or bad_number(underlying) or float(strike) <= float(underlying):
            issues.append("Estimated strike is not above the underlying price")
            adjustments.append("Review target delta, DTE, IV, and strike rounding")

    if not bad_number(moneyness):
        if float(moneyness) < float(config.get("minimum_otm_moneyness_percent", 0.0)):
            issues.append("Moneyness is below minimum OTM band")
        elif float(moneyness) > float(config.get("maximum_otm_moneyness_percent", 12.0)):
            warnings.append("Strike is far OTM for the current scaffold")
            adjustments.append("Check whether target delta or IV assumptions create too-wide strikes")
    else:
        warnings.append("Moneyness cannot be calculated")

    if issues:
        status = "REVIEW"
        issue_text = "; ".join(dict.fromkeys(issues + warnings))
    elif warnings:
        status = "WATCH"
        issue_text = "; ".join(dict.fromkeys(warnings))
    else:
        status = "PASS"
        issue_text = "Within current validation bands"

    if not adjustments:
        adjustment_text = "No immediate adjustment suggested"
    else:
        adjustment_text = "; ".join(dict.fromkeys(adjustments))

    return status, issue_text, adjustment_text


def build_relationship_checks(work: pd.DataFrame, config: dict[str, Any]) -> list[dict[str, Any]]:
    """Run scenario-to-scenario consistency checks."""

    checks: list[dict[str, Any]] = []
    relationship_config = config.get("relationship_checks", {}) or {}
    by_key = {row["scenario_key"]: row for _, row in work.iterrows()}

    def get_metric(key: str, metric: str) -> float | None:
        row = by_key.get(key)
        if row is None:
            return None
        try:
            value = float(row.get(metric))
        except Exception:
            return None
        if math.isfinite(value):
            return value
        return None

    if relationship_config.get("volatile_whipsaw_should_have_higher_iv_than_strong_rally", True):
        a = get_metric("volatile_whipsaw", "implied_volatility")
        b = get_metric("strong_rally", "implied_volatility")
        if a is not None and b is not None:
            checks.append(
                {
                    "check_name": "volatile_whipsaw_iv_gt_strong_rally_iv",
                    "status": "PASS" if a > b else "REVIEW",
                    "detail": f"Volatile Whipsaw IV {a:.3f} vs Strong Rally IV {b:.3f}",
                }
            )

    if relationship_config.get("downtrend_should_have_higher_iv_than_sideways_choppy", True):
        a = get_metric("downtrend", "implied_volatility")
        b = get_metric("sideways_choppy", "implied_volatility")
        if a is not None and b is not None:
            checks.append(
                {
                    "check_name": "downtrend_iv_gt_sideways_choppy_iv",
                    "status": "PASS" if a > b else "REVIEW",
                    "detail": f"Downtrend IV {a:.3f} vs Sideways Choppy IV {b:.3f}",
                }
            )

    threshold = relationship_config.get(
        "sideways_choppy_should_not_have_lower_premium_than_strong_rally_by_more_than_percent",
        35.0,
    )
    try:
        threshold_float = float(threshold)
    except Exception:
        threshold_float = 35.0

    sideways = get_metric("sideways_choppy", "estimated_call_premium")
    rally = get_metric("strong_rally", "estimated_call_premium")
    if sideways is not None and rally is not None and rally > 0:
        shortfall_pct = max((rally - sideways) / rally * 100.0, 0.0)
        checks.append(
            {
                "check_name": "sideways_premium_not_too_low_vs_strong_rally",
                "status": "PASS" if shortfall_pct <= threshold_float else "WATCH",
                "detail": f"Sideways premium {currency(sideways)} vs Strong Rally premium {currency(rally)}; shortfall {shortfall_pct:.1f}%",
            }
        )

    return checks


def build_validation_frame(config: dict[str, Any] | None = None) -> pd.DataFrame:
    if config is None:
        config = ensure_validation_config()

    premium_df = load_option_premium_table()
    work = prepare_premium_frame(premium_df)

    statuses: list[str] = []
    issues: list[str] = []
    adjustments: list[str] = []
    for _, row in work.iterrows():
        status, issue, adjustment = classify_row(row, config)
        statuses.append(status)
        issues.append(issue)
        adjustments.append(adjustment)

    work["validation_status"] = statuses
    work["validation_issue"] = issues
    work["suggested_adjustment"] = adjustments

    ordered = [
        "scenario_name",
        "display_name",
        "validation_status",
        "underlying_price",
        "estimated_strike",
        "strike_distance_dollars",
        "moneyness_percent",
        "target_delta",
        "estimated_call_delta",
        "days_to_expiration",
        "implied_volatility",
        "estimated_call_premium",
        "premium_percent_of_underlying",
        "validation_issue",
        "suggested_adjustment",
    ]
    return work[[col for col in ordered if col in work.columns]].copy()


def build_html_report(validation_df: pd.DataFrame, relationship_checks: list[dict[str, Any]], result: PremiumValidationResult | None = None) -> str:
    status_counts = validation_df["validation_status"].value_counts().to_dict() if not validation_df.empty else {}
    overall = "PASS"
    if any(value in status_counts for value in ["REVIEW"]):
        overall = "REVIEW"
    elif any(value in status_counts for value in ["WATCH"]):
        overall = "WATCH"
    if any(check.get("status") == "REVIEW" for check in relationship_checks):
        overall = "REVIEW"
    elif overall == "PASS" and any(check.get("status") == "WATCH" for check in relationship_checks):
        overall = "WATCH"

    html = [
        "<!doctype html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Phase 2C Premium Model Validation</title>",
        "<style>",
        "body{font-family:Arial,Helvetica,sans-serif;margin:28px;line-height:1.45;color:#222;}",
        "h1,h2{color:#1f2937;}",
        "table{border-collapse:collapse;width:100%;margin:12px 0 24px 0;font-size:14px;}",
        "th,td{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top;}",
        "th{background:#f3f4f6;}",
        ".status{font-weight:bold;padding:8px 10px;border-radius:6px;display:inline-block;}",
        ".pass{background:#ecfdf5;color:#065f46;}",
        ".watch{background:#fffbeb;color:#92400e;}",
        ".review{background:#fef2f2;color:#991b1b;}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Phase 2C Premium Model Validation</h1>",
        f"<p class='status {overall.lower()}'>{overall}</p>",
        "<p>This report checks whether the current premium-model scaffold is internally reasonable. It is not a live option quote and should not be presented as final production pricing.</p>",
        "<h2>Scenario-level validation</h2>",
        validation_df.to_html(index=False, escape=False),
        "<h2>Relationship checks</h2>",
    ]

    if relationship_checks:
        html.append(pd.DataFrame(relationship_checks).to_html(index=False, escape=False))
    else:
        html.append("<p>No relationship checks were available.</p>")

    html.extend(
        [
            "<h2>Interpretation</h2>",
            "<p>PASS means the row is within the current reasonableness bands. WATCH means the row is plausible but worth monitoring. REVIEW means one or more assumptions should be inspected before moving the premium model closer to a customer-facing workflow.</p>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(html)


def build_summary_text(validation_df: pd.DataFrame, relationship_checks: list[dict[str, Any]], config: dict[str, Any]) -> str:
    counts = validation_df["validation_status"].value_counts().to_dict() if not validation_df.empty else {}
    review_count = int(counts.get("REVIEW", 0))
    watch_count = int(counts.get("WATCH", 0))
    pass_count = int(counts.get("PASS", 0))
    rel_review_count = sum(1 for check in relationship_checks if check.get("status") == "REVIEW")
    rel_watch_count = sum(1 for check in relationship_checks if check.get("status") == "WATCH")

    if review_count or rel_review_count:
        overall = "REVIEW"
    elif watch_count or rel_watch_count:
        overall = "WATCH"
    else:
        overall = "PASS"

    lines = [
        "Phase 2C premium-model validation summary",
        "=" * 72,
        f"Overall status: {overall}",
        f"Scenario rows: {len(validation_df)}",
        f"PASS rows: {pass_count}",
        f"WATCH rows: {watch_count}",
        f"REVIEW rows: {review_count}",
        f"Relationship checks: {len(relationship_checks)}",
        f"Relationship WATCH/REVIEW: {rel_watch_count}/{rel_review_count}",
        "",
        "Validation bands",
        "-" * 72,
        f"Premium percent band: {config.get('premium_percent_min')}% to {config.get('premium_percent_max')}% of underlying",
        f"IV band: {percent_from_decimal(config.get('iv_min'))} to {percent_from_decimal(config.get('iv_max'))}",
        f"Delta tolerance: +/- {config.get('delta_tolerance')}",
        f"OTM moneyness band: {config.get('minimum_otm_moneyness_percent')}% to {config.get('maximum_otm_moneyness_percent')}%",
        "",
        "Files written",
        "-" * 72,
        str(VALIDATION_CSV),
        str(VALIDATION_HTML),
        str(VALIDATION_SUMMARY_TXT),
    ]
    return "\n".join(lines) + "\n"


def run_premium_model_validation(
    output_csv: Path = VALIDATION_CSV,
    output_html: Path = VALIDATION_HTML,
    summary_txt: Path = VALIDATION_SUMMARY_TXT,
    config_path: Path = VALIDATION_CONFIG_PATH,
) -> PremiumValidationResult:
    config = ensure_validation_config(config_path)
    validation_df = build_validation_frame(config)
    premium_work = prepare_premium_frame(load_option_premium_table())
    relationship_checks = build_relationship_checks(premium_work, config)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    summary_txt.parent.mkdir(parents=True, exist_ok=True)

    validation_df.to_csv(output_csv, index=False)

    counts = validation_df["validation_status"].value_counts().to_dict() if not validation_df.empty else {}
    fail_count = int(counts.get("REVIEW", 0))
    review_count = int(counts.get("WATCH", 0))
    pass_count = int(counts.get("PASS", 0))
    relationship_review = sum(1 for check in relationship_checks if check.get("status") == "REVIEW")
    relationship_watch = sum(1 for check in relationship_checks if check.get("status") == "WATCH")

    if fail_count or relationship_review:
        overall = "REVIEW"
    elif review_count or relationship_watch:
        overall = "WATCH"
    else:
        overall = "PASS"

    result = PremiumValidationResult(
        csv_path=output_csv,
        html_path=output_html,
        summary_path=summary_txt,
        row_count=len(validation_df),
        pass_count=pass_count,
        review_count=review_count,
        fail_count=fail_count,
        overall_status=overall,
    )

    output_html.write_text(build_html_report(validation_df, relationship_checks, result), encoding="utf-8")
    summary_txt.write_text(build_summary_text(validation_df, relationship_checks, config), encoding="utf-8")
    return result


if __name__ == "__main__":
    run_premium_model_validation()
