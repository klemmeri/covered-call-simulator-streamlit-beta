"""
phase4_market_data_input_scaffold.py

Phase 4-2 market-data input scaffold for the Covered Call Simulator.

This module does not fetch live data. It defines a clean local input contract for
future real ticker/price/option-chain ingestion while keeping the current paid
simulator dashboard untouched.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any
import csv
import json


PHASE4_2_READY_MARKER = "PHASE4_2_MARKET_DATA_INPUT_SCAFFOLD_READY"
PHASE4_2_RELEASE_DECISION = "PHASE4_2_MARKET_DATA_INPUT_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE"


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
SAMPLE_INPUT_DIR = PROJECT_ROOT / "inputs" / "market_data"


@dataclass(frozen=True)
class MarketDataColumnSpec:
    column_name: str
    required: bool
    data_type: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketDataInputScaffold:
    ready_marker: str
    release_decision: str
    dashboard_changed: bool
    ticker_price_columns: list[MarketDataColumnSpec]
    option_chain_columns: list[MarketDataColumnSpec]
    validation_rules: list[str]
    next_phase_recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready_marker": self.ready_marker,
            "release_decision": self.release_decision,
            "dashboard_changed": self.dashboard_changed,
            "ticker_price_columns": [item.to_dict() for item in self.ticker_price_columns],
            "option_chain_columns": [item.to_dict() for item in self.option_chain_columns],
            "validation_rules": list(self.validation_rules),
            "next_phase_recommendations": list(self.next_phase_recommendations),
        }


def build_market_data_input_scaffold() -> MarketDataInputScaffold:
    ticker_price_columns = [
        MarketDataColumnSpec("date", True, "date", "Trading date for the underlying price observation."),
        MarketDataColumnSpec("ticker", True, "string", "Underlying symbol such as SPY, QQQ, AAPL, or SOXL."),
        MarketDataColumnSpec("open", True, "float", "Opening price for the trading session."),
        MarketDataColumnSpec("high", True, "float", "High price for the trading session."),
        MarketDataColumnSpec("low", True, "float", "Low price for the trading session."),
        MarketDataColumnSpec("close", True, "float", "Closing price for the trading session."),
        MarketDataColumnSpec("volume", False, "float", "Share volume, optional for current modeling."),
    ]

    option_chain_columns = [
        MarketDataColumnSpec("as_of_date", True, "date", "Date the option-chain quote was observed."),
        MarketDataColumnSpec("ticker", True, "string", "Underlying symbol."),
        MarketDataColumnSpec("expiration", True, "date", "Option expiration date."),
        MarketDataColumnSpec("option_type", True, "string", "call or put."),
        MarketDataColumnSpec("strike", True, "float", "Option strike price."),
        MarketDataColumnSpec("bid", True, "float", "Option bid price."),
        MarketDataColumnSpec("ask", True, "float", "Option ask price."),
        MarketDataColumnSpec("mid", False, "float", "Optional midpoint; can be calculated from bid and ask."),
        MarketDataColumnSpec("delta", False, "float", "Optional option delta for strategy selection."),
        MarketDataColumnSpec("iv", False, "float", "Optional implied volatility."),
        MarketDataColumnSpec("open_interest", False, "float", "Optional open interest for liquidity filtering."),
        MarketDataColumnSpec("volume", False, "float", "Optional contract volume for liquidity filtering."),
    ]

    validation_rules = [
        "Required columns must be present before importing a dataset.",
        "Dates must parse as calendar dates and expirations must be on or after as_of_date.",
        "Prices, strikes, bid, ask, and close values must be non-negative.",
        "Ask must be greater than or equal to bid when both are present.",
        "Option type must normalize to call or put.",
        "Ticker symbols must be non-empty strings.",
        "Delta and IV are optional in Phase 4-2 but should be preserved when available.",
    ]

    next_phase_recommendations = [
        "Add a CSV validator that reads user-supplied price and option-chain files.",
        "Create sample input CSV templates under inputs/market_data.",
        "Add a model bridge that maps validated market data into simulator configuration fields.",
        "Keep live API ingestion separate from the first local-file ingestion step.",
    ]

    return MarketDataInputScaffold(
        ready_marker=PHASE4_2_READY_MARKER,
        release_decision=PHASE4_2_RELEASE_DECISION,
        dashboard_changed=False,
        ticker_price_columns=ticker_price_columns,
        option_chain_columns=option_chain_columns,
        validation_rules=validation_rules,
        next_phase_recommendations=next_phase_recommendations,
    )


def write_sample_templates(project_root: Path | None = None) -> dict[str, str]:
    root = project_root or PROJECT_ROOT
    sample_dir = root / "inputs" / "market_data"
    sample_dir.mkdir(parents=True, exist_ok=True)

    price_path = sample_dir / "sample_underlying_prices.csv"
    option_path = sample_dir / "sample_option_chain.csv"

    with price_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "ticker", "open", "high", "low", "close", "volume"])
        writer.writerow([date.today().isoformat(), "SPY", 545.00, 548.25, 543.75, 546.50, 1000000])

    with option_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["as_of_date", "ticker", "expiration", "option_type", "strike", "bid", "ask", "mid", "delta", "iv", "open_interest", "volume"])
        writer.writerow([date.today().isoformat(), "SPY", date.today().isoformat(), "call", 550.0, 2.10, 2.25, 2.175, 0.30, 0.18, 2500, 350])

    return {
        "price_template": str(price_path),
        "option_chain_template": str(option_path),
    }


def write_scaffold_outputs(project_root: Path | None = None) -> dict[str, str]:
    root = project_root or PROJECT_ROOT
    output_dir = root / "outputs" / "tables" / "paid_simulator"
    report_dir = root / "outputs" / "reports" / "paid_simulator"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    scaffold = build_market_data_input_scaffold()
    templates = write_sample_templates(root)

    json_path = report_dir / "phase4_2_market_data_input_scaffold.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(scaffold.to_dict(), f, indent=2)

    price_schema_path = output_dir / "phase4_2_underlying_price_schema.csv"
    with price_schema_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["column_name", "required", "data_type", "description"])
        writer.writeheader()
        for item in scaffold.ticker_price_columns:
            writer.writerow(item.to_dict())

    option_schema_path = output_dir / "phase4_2_option_chain_schema.csv"
    with option_schema_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["column_name", "required", "data_type", "description"])
        writer.writeheader()
        for item in scaffold.option_chain_columns:
            writer.writerow(item.to_dict())

    report_path = report_dir / "phase4_2_market_data_input_scaffold_report.txt"
    lines = [
        "Phase 4-2 market-data input scaffold",
        "=" * 60,
        f"Ready marker: {scaffold.ready_marker}",
        f"Release decision: {scaffold.release_decision}",
        f"Dashboard changed: {scaffold.dashboard_changed}",
        "",
        "Generated templates:",
        f"- {templates['price_template']}",
        f"- {templates['option_chain_template']}",
        "",
        "Validation rules:",
    ]
    lines.extend(f"- {rule}" for rule in scaffold.validation_rules)
    lines.extend(["", "Next recommendations:"])
    lines.extend(f"- {item}" for item in scaffold.next_phase_recommendations)
    report_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "json": str(json_path),
        "price_schema": str(price_schema_path),
        "option_chain_schema": str(option_schema_path),
        "report": str(report_path),
        **templates,
    }


def render_market_data_input_scaffold() -> dict[str, Any]:
    return build_market_data_input_scaffold().to_dict()
