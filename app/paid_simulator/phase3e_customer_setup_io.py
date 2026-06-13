"""
phase3e_customer_setup_io.py

Phase 3E-2 customer setup save/reload utilities for the Covered Call Simulator.

This module provides a small, customer-facing input/output layer for saving,
exporting, listing, and reloading covered-call payoff setups. It is intentionally
standalone so it can be checked before being wired into the Streamlit dashboard.

Design goals
------------
1. Save setups in a predictable project-local location.
2. Keep the saved JSON readable and stable.
3. Include customer-facing labels and derived payoff metrics.
4. Validate required fields before writing or loading.
5. Avoid developer/test language in customer-facing output.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import math
import re
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETUP_DIR = PROJECT_ROOT / "outputs" / "saved_setups" / "paid_simulator"


@dataclass(frozen=True)
class CoveredCallSetup:
    """
    Customer-facing covered-call setup.

    All price and premium values are per share. Share count is the number of
    shares controlled by the covered-call position, normally 100 shares per
    short call contract.
    """

    ticker: str
    current_price: float
    strike_price: float
    option_premium: float
    share_count: int = 100
    expiration_date: str = ""
    setup_name: str = "Customer covered-call setup"
    notes: str = ""


@dataclass(frozen=True)
class PayoffMetrics:
    """
    Derived customer-facing metrics for a covered-call setup.
    """

    breakeven_price: float
    max_profit_dollars: float
    max_profit_percent: float
    downside_cushion_dollars: float
    downside_cushion_percent: float
    assignment_zone_starts_at: float
    premium_income_dollars: float
    stock_value_dollars: float


REQUIRED_SETUP_FIELDS = {
    "ticker",
    "current_price",
    "strike_price",
    "option_premium",
    "share_count",
}


CUSTOMER_SECTION_LABELS = {
    "setup_summary": "Setup summary",
    "payoff_metrics": "Payoff metrics",
    "risk_warnings": "Risk warnings",
    "saved_setup": "Saved setup",
}


def _round_money(value: float) -> float:
    """Round a money value to cents."""

    return round(float(value), 2)


def _round_percent(value: float) -> float:
    """Round a percentage value to two decimals."""

    return round(float(value), 2)


def _clean_ticker(ticker: str) -> str:
    """Return a simple uppercase ticker symbol for display and file names."""

    cleaned = re.sub(r"[^A-Za-z0-9._-]", "", str(ticker).strip().upper())
    return cleaned or "COVERED_CALL"


def _safe_slug(text: str) -> str:
    """Create a filesystem-safe slug."""

    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(text).strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "covered_call_setup"


def validate_setup(setup: CoveredCallSetup | dict[str, Any]) -> list[str]:
    """
    Validate a setup and return a list of customer-readable error messages.

    The function does not raise for normal validation failures because it is
    intended for use in a dashboard warning box.
    """

    data = asdict(setup) if isinstance(setup, CoveredCallSetup) else dict(setup)
    errors: list[str] = []

    missing = sorted(field for field in REQUIRED_SETUP_FIELDS if field not in data)
    for field in missing:
        errors.append(f"Missing required setup field: {field}.")

    ticker = str(data.get("ticker", "")).strip()
    if not ticker:
        errors.append("Ticker is required.")

    numeric_fields = ["current_price", "strike_price", "option_premium"]
    for field in numeric_fields:
        value = data.get(field)
        try:
            number = float(value)
        except (TypeError, ValueError):
            errors.append(f"{field} must be a number.")
            continue
        if not math.isfinite(number):
            errors.append(f"{field} must be finite.")
        elif number <= 0:
            errors.append(f"{field} must be greater than zero.")

    try:
        share_count = int(data.get("share_count", 0))
    except (TypeError, ValueError):
        errors.append("share_count must be a whole number.")
    else:
        if share_count <= 0:
            errors.append("share_count must be greater than zero.")
        if share_count % 100 != 0:
            errors.append("share_count should normally be a multiple of 100 for listed equity options.")

    return errors


def calculate_payoff_metrics(setup: CoveredCallSetup) -> PayoffMetrics:
    """
    Calculate customer-facing payoff metrics for a covered call.

    Formulas are per standard covered-call payoff logic:
    - Breakeven = current stock price - premium received
    - Maximum profit = strike - current price + premium, times shares
    - Downside cushion = premium received
    """

    errors = validate_setup(setup)
    if errors:
        raise ValueError("Setup is not valid: " + " ".join(errors))

    breakeven = setup.current_price - setup.option_premium
    premium_income = setup.option_premium * setup.share_count
    max_profit_per_share = setup.strike_price - setup.current_price + setup.option_premium
    max_profit = max_profit_per_share * setup.share_count
    stock_value = setup.current_price * setup.share_count

    max_profit_percent = 0.0
    if stock_value > 0:
        max_profit_percent = (max_profit / stock_value) * 100.0

    downside_cushion_percent = 0.0
    if setup.current_price > 0:
        downside_cushion_percent = (setup.option_premium / setup.current_price) * 100.0

    return PayoffMetrics(
        breakeven_price=_round_money(breakeven),
        max_profit_dollars=_round_money(max_profit),
        max_profit_percent=_round_percent(max_profit_percent),
        downside_cushion_dollars=_round_money(setup.option_premium),
        downside_cushion_percent=_round_percent(downside_cushion_percent),
        assignment_zone_starts_at=_round_money(setup.strike_price),
        premium_income_dollars=_round_money(premium_income),
        stock_value_dollars=_round_money(stock_value),
    )


def build_warning_messages(setup: CoveredCallSetup) -> list[str]:
    """
    Return customer-facing warning messages for potentially risky setups.
    """

    errors = validate_setup(setup)
    if errors:
        return errors

    messages: list[str] = []
    moneyness_percent = ((setup.strike_price - setup.current_price) / setup.current_price) * 100.0
    cushion_percent = (setup.option_premium / setup.current_price) * 100.0

    if setup.strike_price < setup.current_price:
        messages.append(
            "The strike is below the current stock price. This setup is already in the assignment zone."
        )
    elif moneyness_percent < 1.0:
        messages.append(
            "The strike is very close to the current stock price. Assignment risk may be high."
        )

    if cushion_percent < 0.5:
        messages.append(
            "The premium provides a small downside cushion relative to the stock price."
        )

    if setup.option_premium > setup.current_price * 0.15:
        messages.append(
            "The premium is unusually large relative to the stock price. Check the option quote before relying on this setup."
        )

    if setup.share_count > 1000:
        messages.append(
            "This setup controls a large share position. Confirm the dollar risk before entering the trade."
        )

    return messages


def build_customer_payload(setup: CoveredCallSetup) -> dict[str, Any]:
    """
    Build a stable JSON-serializable customer setup payload.
    """

    metrics = calculate_payoff_metrics(setup)
    warnings = build_warning_messages(setup)
    created_at = datetime.now().replace(microsecond=0).isoformat()

    return {
        "version": "phase3e-2",
        "created_at": created_at,
        "section_labels": CUSTOMER_SECTION_LABELS,
        "setup": {
            "setup_name": setup.setup_name,
            "ticker": _clean_ticker(setup.ticker),
            "current_price": _round_money(setup.current_price),
            "strike_price": _round_money(setup.strike_price),
            "option_premium": _round_money(setup.option_premium),
            "share_count": int(setup.share_count),
            "expiration_date": setup.expiration_date,
            "notes": setup.notes,
        },
        "payoff_metrics": asdict(metrics),
        "risk_warnings": warnings,
    }


def save_customer_setup(
    setup: CoveredCallSetup,
    output_dir: Path | str = DEFAULT_SETUP_DIR,
    filename: str | None = None,
) -> Path:
    """
    Save a customer setup as JSON and return the saved path.
    """

    errors = validate_setup(setup)
    if errors:
        raise ValueError("Setup is not valid: " + " ".join(errors))

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if filename is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticker = _clean_ticker(setup.ticker)
        name = _safe_slug(setup.setup_name)
        filename = f"{stamp}_{ticker}_{name}.json"

    if not filename.lower().endswith(".json"):
        filename += ".json"

    destination = output_path / _safe_slug(filename.replace(".json", ""))
    destination = destination.with_suffix(".json")

    payload = build_customer_payload(setup)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def load_customer_setup(path: Path | str) -> dict[str, Any]:
    """
    Load a saved customer setup JSON file and validate its core fields.
    """

    setup_path = Path(path)
    if not setup_path.exists():
        raise FileNotFoundError(f"Saved setup file was not found: {setup_path}")

    payload = json.loads(setup_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Saved setup file is not a JSON object.")

    setup_data = payload.get("setup")
    if not isinstance(setup_data, dict):
        raise ValueError("Saved setup file does not contain a setup section.")

    errors = validate_setup(setup_data)
    if errors:
        raise ValueError("Saved setup is not valid: " + " ".join(errors))

    return payload


def list_saved_customer_setups(output_dir: Path | str = DEFAULT_SETUP_DIR) -> list[Path]:
    """
    Return saved customer setup JSON files, newest first by modified time.
    """

    setup_dir = Path(output_dir)
    if not setup_dir.exists():
        return []

    files = [path for path in setup_dir.glob("*.json") if path.is_file()]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def export_setup_summary_text(payload: dict[str, Any]) -> str:
    """
    Create a plain-English summary suitable for a customer export/download.
    """

    setup = payload["setup"]
    metrics = payload["payoff_metrics"]
    warnings = payload.get("risk_warnings", [])

    lines = [
        "Covered Call Setup Summary",
        "==========================",
        f"Setup name: {setup.get('setup_name', '')}",
        f"Ticker: {setup['ticker']}",
        f"Current price: ${setup['current_price']:,.2f}",
        f"Strike price: ${setup['strike_price']:,.2f}",
        f"Premium: ${setup['option_premium']:,.2f} per share",
        f"Share count: {setup['share_count']:,}",
        f"Expiration date: {setup.get('expiration_date', '')}",
        "",
        "Payoff Metrics",
        "--------------",
        f"Breakeven price: ${metrics['breakeven_price']:,.2f}",
        f"Maximum profit: ${metrics['max_profit_dollars']:,.2f}",
        f"Maximum profit percent: {metrics['max_profit_percent']:,.2f}%",
        f"Downside cushion: ${metrics['downside_cushion_dollars']:,.2f} per share",
        f"Downside cushion percent: {metrics['downside_cushion_percent']:,.2f}%",
        f"Assignment zone starts at: ${metrics['assignment_zone_starts_at']:,.2f}",
        f"Premium income: ${metrics['premium_income_dollars']:,.2f}",
        "",
        "Risk Warnings",
        "-------------",
    ]

    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No setup warnings were triggered by the current rules.")

    notes = setup.get("notes", "")
    if notes:
        lines.extend(["", "Notes", "-----", notes])

    return "\n".join(lines) + "\n"


def save_setup_summary_text(
    payload: dict[str, Any],
    output_dir: Path | str = DEFAULT_SETUP_DIR,
    filename: str | None = None,
) -> Path:
    """
    Save a plain-text customer summary for a previously built setup payload.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    setup = payload.get("setup", {})
    if filename is None:
        ticker = _clean_ticker(setup.get("ticker", "COVERED_CALL"))
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stamp}_{ticker}_customer_summary.txt"

    if not filename.lower().endswith(".txt"):
        filename += ".txt"

    destination = output_path / _safe_slug(filename.replace(".txt", ""))
    destination = destination.with_suffix(".txt")
    destination.write_text(export_setup_summary_text(payload), encoding="utf-8")
    return destination


def build_demo_setup() -> CoveredCallSetup:
    """
    Return a deterministic demo setup for checks and examples.
    """

    return CoveredCallSetup(
        setup_name="SPY balanced covered call",
        ticker="SPY",
        current_price=545.25,
        strike_price=555.00,
        option_premium=4.20,
        share_count=100,
        expiration_date="Demo expiration",
        notes="Demo setup for Phase 3E customer save and reload workflow.",
    )
