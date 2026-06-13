"""
product_info.py

Product metadata for the Covered Call Simulator paid dashboard.

This module is intentionally small and dependency-free. It provides one
central place for the product name, version label, build label, and short
customer-facing descriptions used by the paid simulator dashboard and
release documentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaidSimulatorProductInfo:
    """Customer-facing product metadata for the paid simulator dashboard."""

    product_name: str
    product_subtitle: str
    version_label: str
    build_label: str
    release_stage: str
    positioning_statement: str
    primary_workflow: tuple[str, ...]
    key_limitations: tuple[str, ...]


def get_product_info() -> PaidSimulatorProductInfo:
    """
    Return the current paid simulator product metadata.

    Keep this function dependency-free so it can be imported safely by
    Streamlit, command-line scripts, health checks, release checks, and docs
    generators.
    """

    return PaidSimulatorProductInfo(
        product_name="Covered Call Strategy Stress Test",
        product_subtitle=(
            "A paid-simulator dashboard for comparing covered-call setups "
            "across modeled market paths."
        ),
        version_label="Paid Simulator Dashboard v0.1",
        build_label="v1.0.0-rc1",
        release_stage="Beta release",
        positioning_statement=(
            "The dashboard is designed to help a user understand the income, "
            "risk, and upside tradeoffs of a covered-call setup before opening "
            "or comparing positions. It is a decision-support tool, not a trade "
            "recommendation engine."
        ),
        primary_workflow=(
            "Choose or edit a covered-call setup.",
            "Validate sizing and assumptions.",
            "Run the simulator across modeled market paths.",
            "Review best, worst, and average relative outcomes versus buy-and-hold.",
            "Inspect scenario details and decision guidance.",
            "Export a Markdown or PDF decision memo.",
            "Compare presets and review run history.",
        ),
        key_limitations=(
            "Market paths are modeled scenarios, not forecasts.",
            "Regime detection, if later added, should be treated as probabilistic guidance, not an oracle.",
            "Covered calls may lag sharply in strong rallies because upside can be capped.",
            "Historical or simulated outcomes do not guarantee future performance.",
            "Transaction costs, slippage, tax treatment, early assignment, dividends, and broker execution details can materially affect real results.",
        ),
    )


def get_status_lines() -> list[str]:
    """Return printable product metadata lines for command-line status output."""

    info = get_product_info()
    lines: list[str] = []
    lines.append(f"Product name:       {info.product_name}")
    lines.append(f"Subtitle:           {info.product_subtitle}")
    lines.append(f"Version:            {info.version_label}")
    lines.append(f"Build:              {info.build_label}")
    lines.append(f"Release stage:      {info.release_stage}")
    lines.append(f"Generated at:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return lines
