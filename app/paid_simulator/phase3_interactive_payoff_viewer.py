"""
phase3_interactive_payoff_viewer.py

Standalone Phase 3 prototype for the Covered Call Strategy Stress Test project.

Purpose
-------
Provide an interactive graphical covered-call payoff viewer where a user can
enter their own ticker/setup assumptions and immediately see:

- Buy-and-hold payoff line
- Covered-call payoff line
- Current price marker
- Strike/assignment marker
- Break-even marker
- Maximum profit estimate
- Downside cushion estimate
- Scenario payoff table

This file is intentionally standalone. It does not replace the existing paid
simulator dashboard and it does not require live market data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import math

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # pragma: no cover - dashboard fallback
    alt = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

PAYOFF_OUTPUT_CSV = OUTPUT_DIR / "phase3_interactive_payoff_snapshot.csv"
PAYOFF_OUTPUT_HTML = REPORT_DIR / "phase3_interactive_payoff_snapshot.html"


@dataclass(frozen=True)
class CoveredCallInputs:
    """User-defined covered-call setup."""

    ticker: str
    current_price: float
    shares: int
    strike_price: float
    premium_per_share: float
    dte: int
    call_delta: float
    contracts: int

    @property
    def contract_shares(self) -> int:
        return self.contracts * 100

    @property
    def covered_shares(self) -> int:
        return min(self.shares, self.contract_shares)

    @property
    def uncovered_shares(self) -> int:
        return max(0, self.shares - self.covered_shares)

    @property
    def premium_total(self) -> float:
        return self.premium_per_share * self.covered_shares

    @property
    def stock_cost(self) -> float:
        return self.current_price * self.shares

    @property
    def break_even_price(self) -> float:
        if self.shares <= 0:
            return self.current_price
        return self.current_price - (self.premium_total / self.shares)

    @property
    def downside_cushion_pct(self) -> float:
        if self.current_price <= 0:
            return 0.0
        return (self.premium_total / self.shares) / self.current_price * 100.0

    @property
    def max_profit(self) -> float:
        assigned_gain = max(0.0, self.strike_price - self.current_price) * self.covered_shares
        uncovered_gain_at_strike = max(0.0, self.strike_price - self.current_price) * self.uncovered_shares
        return assigned_gain + uncovered_gain_at_strike + self.premium_total


def covered_call_payoff(inputs: CoveredCallInputs, terminal_price: float) -> Dict[str, float | str]:
    """Calculate buy-and-hold and covered-call payoff at a terminal stock price."""

    stock_pl = (terminal_price - inputs.current_price) * inputs.shares
    covered_stock_pl = (terminal_price - inputs.current_price) * inputs.covered_shares
    uncovered_stock_pl = (terminal_price - inputs.current_price) * inputs.uncovered_shares
    call_intrinsic_loss = max(0.0, terminal_price - inputs.strike_price) * inputs.covered_shares
    covered_call_pl = covered_stock_pl + uncovered_stock_pl + inputs.premium_total - call_intrinsic_loss
    relative_pl = covered_call_pl - stock_pl

    if terminal_price >= inputs.strike_price:
        zone = "Assignment zone"
    elif terminal_price <= inputs.break_even_price:
        zone = "Below break-even"
    else:
        zone = "Profit zone below strike"

    return {
        "ticker": inputs.ticker.upper().strip(),
        "terminal_price": round(float(terminal_price), 2),
        "buy_hold_pl": round(float(stock_pl), 2),
        "covered_call_pl": round(float(covered_call_pl), 2),
        "covered_call_minus_buy_hold": round(float(relative_pl), 2),
        "premium_income": round(float(inputs.premium_total), 2),
        "call_intrinsic_loss": round(float(call_intrinsic_loss), 2),
        "assignment_flag": bool(terminal_price >= inputs.strike_price),
        "zone": zone,
    }


def build_payoff_table(inputs: CoveredCallInputs, points: int = 81) -> pd.DataFrame:
    """Build a payoff table across a terminal-price range."""

    low = max(0.01, inputs.current_price * 0.70)
    high = max(inputs.current_price * 1.30, inputs.strike_price * 1.12)
    if math.isclose(low, high):
        high = low + 1.0

    step = (high - low) / max(1, points - 1)
    prices = [low + i * step for i in range(points)]

    anchor_prices = [
        inputs.break_even_price,
        inputs.current_price,
        inputs.strike_price,
        inputs.current_price * 0.90,
        inputs.current_price * 1.10,
    ]
    prices.extend(p for p in anchor_prices if p > 0)
    prices = sorted(set(round(p, 2) for p in prices))

    rows = [covered_call_payoff(inputs, p) for p in prices]
    return pd.DataFrame(rows)


def build_scenario_table(inputs: CoveredCallInputs) -> pd.DataFrame:
    """Build a compact scenario table for common percentage moves."""

    moves = [-20, -10, -5, 0, 5, 10, 20]
    rows = []
    for move in moves:
        price = inputs.current_price * (1.0 + move / 100.0)
        row = covered_call_payoff(inputs, price)
        row["price_move_pct"] = move
        rows.append(row)
    return pd.DataFrame(rows)[
        [
            "price_move_pct",
            "terminal_price",
            "buy_hold_pl",
            "covered_call_pl",
            "covered_call_minus_buy_hold",
            "premium_income",
            "call_intrinsic_loss",
            "assignment_flag",
            "zone",
        ]
    ]


def validate_inputs(inputs: CoveredCallInputs) -> list[str]:
    """Return blocking validation messages for impossible inputs."""

    errors: list[str] = []
    if inputs.current_price <= 0:
        errors.append("Current price must be greater than zero.")
    if inputs.shares <= 0:
        errors.append("Shares must be greater than zero.")
    if inputs.contracts <= 0:
        errors.append("Contracts must be at least 1.")
    if inputs.contract_shares > inputs.shares:
        errors.append("Contracts cover more shares than entered. Reduce contracts or increase shares.")
    if inputs.strike_price <= 0:
        errors.append("Strike price must be greater than zero.")
    if inputs.premium_per_share < 0:
        errors.append("Premium cannot be negative.")
    if inputs.dte < 0:
        errors.append("DTE cannot be negative.")
    if not (0 <= inputs.call_delta <= 1):
        errors.append("Call delta should be between 0 and 1.")
    return errors


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_signed_currency(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.2f}"


def save_snapshot(inputs: CoveredCallInputs, payoff_df: pd.DataFrame, scenario_df: pd.DataFrame) -> None:
    """Save current interactive snapshot to CSV and HTML."""

    payoff_df.to_csv(PAYOFF_OUTPUT_CSV, index=False)

    metrics = {
        "Ticker": inputs.ticker.upper().strip(),
        "Current price": format_currency(inputs.current_price),
        "Shares": f"{inputs.shares:,}",
        "Contracts": f"{inputs.contracts:,}",
        "Strike": format_currency(inputs.strike_price),
        "Premium per share": format_currency(inputs.premium_per_share),
        "Total premium": format_currency(inputs.premium_total),
        "Break-even": format_currency(inputs.break_even_price),
        "Max profit estimate": format_currency(inputs.max_profit),
        "Downside cushion": f"{inputs.downside_cushion_pct:.2f}%",
    }

    html = [
        "<html><head><title>Phase 3 Interactive Payoff Snapshot</title>",
        "<style>body{font-family:Arial,sans-serif;margin:32px;} table{border-collapse:collapse;width:100%;margin-bottom:24px;} th,td{border:1px solid #ddd;padding:8px;text-align:right;} th{text-align:left;background:#f4f4f4;} h1,h2{color:#222;} .note{color:#555;}</style>",
        "</head><body>",
        "<h1>Phase 3 Interactive Covered-Call Payoff Snapshot</h1>",
        "<p class='note'>This is a local prototype snapshot, not a trade recommendation.</p>",
        "<h2>Setup</h2>",
        "<table><tr><th>Field</th><th>Value</th></tr>",
    ]
    for key, value in metrics.items():
        html.append(f"<tr><td style='text-align:left'>{key}</td><td>{value}</td></tr>")
    html.append("</table>")
    html.append("<h2>Scenario Table</h2>")
    html.append(scenario_df.to_html(index=False, escape=False))
    html.append("<h2>Payoff Grid</h2>")
    html.append(payoff_df.to_html(index=False, escape=False))
    html.append("</body></html>")
    PAYOFF_OUTPUT_HTML.write_text("\n".join(html), encoding="utf-8")


def render_payoff_chart(payoff_df: pd.DataFrame, inputs: CoveredCallInputs) -> None:
    """Render the payoff chart using Altair if available, otherwise Streamlit line_chart."""

    chart_df = payoff_df[["terminal_price", "buy_hold_pl", "covered_call_pl"]].melt(
        id_vars="terminal_price",
        value_vars=["buy_hold_pl", "covered_call_pl"],
        var_name="strategy",
        value_name="profit_loss",
    )
    chart_df["strategy"] = chart_df["strategy"].map(
        {
            "buy_hold_pl": "Buy-and-hold",
            "covered_call_pl": "Covered call",
        }
    )

    marker_df = pd.DataFrame(
        [
            {"price": inputs.current_price, "label": "Current price"},
            {"price": inputs.strike_price, "label": "Strike / assignment"},
            {"price": inputs.break_even_price, "label": "Break-even"},
        ]
    )

    if alt is not None:
        base = alt.Chart(chart_df).mark_line(size=3).encode(
            x=alt.X("terminal_price:Q", title="Terminal stock price"),
            y=alt.Y("profit_loss:Q", title="Profit / loss ($)"),
            color=alt.Color("strategy:N", title="Strategy"),
            tooltip=["strategy:N", "terminal_price:Q", "profit_loss:Q"],
        )

        zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(strokeDash=[4, 4]).encode(y="y:Q")

        markers = alt.Chart(marker_df).mark_rule(strokeDash=[6, 4]).encode(
            x="price:Q",
            tooltip=["label:N", "price:Q"],
        )

        labels = alt.Chart(marker_df).mark_text(angle=270, align="left", dx=4, dy=-120).encode(
            x="price:Q",
            y=alt.value(20),
            text="label:N",
        )

        st.altair_chart((base + zero_line + markers + labels).properties(height=420), use_container_width=True)
    else:
        fallback = payoff_df.set_index("terminal_price")[["buy_hold_pl", "covered_call_pl"]]
        st.line_chart(fallback)


def main() -> None:
    st.set_page_config(page_title="Phase 3 Interactive Covered-Call Payoff", layout="wide")

    st.title("Phase 3: Interactive Covered-Call Payoff Viewer")
    st.caption("Standalone local prototype. No live market data yet. Not a trade recommendation.")

    with st.sidebar:
        st.header("Covered-call setup")
        ticker = st.text_input("Ticker", value="SPY").upper().strip() or "SPY"
        current_price = st.number_input("Current stock price", min_value=0.01, value=545.25, step=1.0)
        shares = st.number_input("Shares owned", min_value=1, value=100, step=100)
        contracts = st.number_input("Short call contracts", min_value=1, value=1, step=1)
        strike_price = st.number_input("Short call strike", min_value=0.01, value=555.00, step=1.0)
        premium_per_share = st.number_input("Call premium per share", min_value=0.0, value=4.20, step=0.10)
        dte = st.number_input("Days to expiration", min_value=0, value=30, step=1)
        call_delta = st.slider("Approximate call delta", min_value=0.0, max_value=1.0, value=0.30, step=0.01)

        st.divider()
        st.caption("This prototype uses manually entered values. Live ticker/option-chain import comes later.")

    inputs = CoveredCallInputs(
        ticker=ticker,
        current_price=float(current_price),
        shares=int(shares),
        strike_price=float(strike_price),
        premium_per_share=float(premium_per_share),
        dte=int(dte),
        call_delta=float(call_delta),
        contracts=int(contracts),
    )

    errors = validate_inputs(inputs)
    if errors:
        st.error("Fix these inputs before using the chart:")
        for error in errors:
            st.write(f"- {error}")
        return

    payoff_df = build_payoff_table(inputs)
    scenario_df = build_scenario_table(inputs)
    save_snapshot(inputs, payoff_df, scenario_df)

    st.subheader("Setup summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ticker", inputs.ticker.upper())
    col2.metric("Total premium", format_currency(inputs.premium_total))
    col3.metric("Break-even", format_currency(inputs.break_even_price))
    col4.metric("Downside cushion", f"{inputs.downside_cushion_pct:.2f}%")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Max profit estimate", format_currency(inputs.max_profit))
    col6.metric("Strike", format_currency(inputs.strike_price))
    col7.metric("DTE", f"{inputs.dte}")
    col8.metric("Call delta", f"{inputs.call_delta:.2f}")

    st.subheader("Interactive payoff chart")
    render_payoff_chart(payoff_df, inputs)

    st.subheader("Interpretation")
    if inputs.strike_price <= inputs.current_price:
        st.warning("The short call strike is at or below the current stock price. This is already in or near the assignment zone.")
    else:
        upside_to_strike = (inputs.strike_price / inputs.current_price - 1.0) * 100.0
        st.info(
            f"The short call strike is {upside_to_strike:.2f}% above the current price. "
            f"The covered call receives {format_currency(inputs.premium_total)} in premium and has a break-even near {format_currency(inputs.break_even_price)}."
        )

    tab1, tab2, tab3 = st.tabs(["Scenario table", "Full payoff grid", "Saved files"])
    with tab1:
        st.dataframe(scenario_df, use_container_width=True)
    with tab2:
        st.dataframe(payoff_df, use_container_width=True)
    with tab3:
        st.write("The current snapshot is saved locally each time the app reruns:")
        st.code(str(PAYOFF_OUTPUT_CSV))
        st.code(str(PAYOFF_OUTPUT_HTML))


if __name__ == "__main__":
    main()
