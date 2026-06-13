"""
phase3c_rich_payoff_viewer.py

Standalone Streamlit prototype for the Phase 3C richer graphical
covered-call payoff interface.

This file is intentionally isolated from the main paid simulator dashboard.
It lets us test a more useful visual payoff panel before promoting the
feature into the main application.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # pragma: no cover - viewer still loads without charts
    alt = None


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
SNAPSHOT_CSV = OUTPUT_TABLE_DIR / "phase3c_rich_payoff_snapshot.csv"
SNAPSHOT_HTML = OUTPUT_REPORT_DIR / "phase3c_rich_payoff_snapshot.html"


@dataclass
class CoveredCallSetup:
    ticker: str
    current_price: float
    shares: int
    contracts: int
    strike: float
    premium: float
    dte: int
    delta: float
    lower_move_pct: float
    upper_move_pct: float
    grid_points: int

    @property
    def covered_shares(self) -> int:
        return int(max(0, self.contracts) * 100)

    @property
    def effective_shares(self) -> int:
        return int(min(max(0, self.shares), self.covered_shares))

    @property
    def uncovered_shares(self) -> int:
        return int(max(0, self.shares - self.effective_shares))

    @property
    def premium_income(self) -> float:
        return float(self.premium * self.effective_shares)

    @property
    def breakeven_price(self) -> float:
        if self.shares <= 0:
            return self.current_price
        return self.current_price - (self.premium_income / self.shares)

    @property
    def max_profit_at_or_above_strike(self) -> float:
        covered_gain = (self.strike - self.current_price) * self.effective_shares
        uncovered_gain = (self.strike - self.current_price) * self.uncovered_shares
        return covered_gain + uncovered_gain + self.premium_income


def currency(value: float) -> str:
    return f"${value:,.2f}"


def signed_currency(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.2f}"


def pct(value: float) -> str:
    return f"{value:.2f}%"


def ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def payoff_at_price(setup: CoveredCallSetup, final_price: float) -> Dict[str, float | str | bool]:
    stock_pnl = (final_price - setup.current_price) * setup.shares
    intrinsic_loss = max(0.0, final_price - setup.strike) * setup.effective_shares
    covered_call_pnl = stock_pnl + setup.premium_income - intrinsic_loss
    relative = covered_call_pnl - stock_pnl
    assignment = final_price >= setup.strike
    downside_cushion = setup.premium_income / max(1, setup.shares)

    if final_price < setup.breakeven_price:
        zone = "Below breakeven"
    elif final_price < setup.strike:
        zone = "Profit zone below strike"
    else:
        zone = "Assignment / capped-upside zone"

    return {
        "ticker": setup.ticker.upper(),
        "final_price": round(final_price, 4),
        "price_change_pct": round(((final_price / setup.current_price) - 1.0) * 100.0, 4),
        "buy_hold_pnl": round(stock_pnl, 2),
        "covered_call_pnl": round(covered_call_pnl, 2),
        "covered_call_minus_buy_hold": round(relative, 2),
        "premium_income": round(setup.premium_income, 2),
        "intrinsic_call_loss": round(intrinsic_loss, 2),
        "assignment_flag": bool(assignment),
        "zone": zone,
        "breakeven_price": round(setup.breakeven_price, 4),
        "strike": round(setup.strike, 4),
        "current_price": round(setup.current_price, 4),
        "downside_cushion_per_share": round(downside_cushion, 4),
    }


def build_payoff_grid(setup: CoveredCallSetup) -> pd.DataFrame:
    lower = setup.current_price * (1.0 + setup.lower_move_pct / 100.0)
    upper = setup.current_price * (1.0 + setup.upper_move_pct / 100.0)
    if lower <= 0:
        lower = max(0.01, setup.current_price * 0.5)
    if upper <= lower:
        upper = lower + max(1.0, setup.current_price * 0.2)

    grid_points = int(max(21, min(301, setup.grid_points)))
    prices = [lower + (upper - lower) * i / (grid_points - 1) for i in range(grid_points)]
    rows = [payoff_at_price(setup, p) for p in prices]
    return pd.DataFrame(rows)


def build_scenario_table(setup: CoveredCallSetup) -> pd.DataFrame:
    scenario_specs = [
        ("Sharp pullback", -12.0),
        ("Moderate pullback", -6.0),
        ("Flat / pin", 0.0),
        ("Mild rally", 4.0),
        ("Strike test", ((setup.strike / setup.current_price) - 1.0) * 100.0),
        ("Strong rally", 12.0),
    ]
    rows: List[Dict[str, float | str | bool]] = []
    for label, move in scenario_specs:
        final_price = setup.current_price * (1.0 + move / 100.0)
        row = payoff_at_price(setup, final_price)
        row["scenario"] = label
        rows.append(row)
    return pd.DataFrame(rows)


def create_payoff_chart(payoff_df: pd.DataFrame, setup: CoveredCallSetup):
    if alt is None:
        return None

    line_df = payoff_df.melt(
        id_vars=["final_price", "zone"],
        value_vars=["buy_hold_pnl", "covered_call_pnl"],
        var_name="strategy",
        value_name="pnl",
    )
    line_df["strategy"] = line_df["strategy"].map(
        {
            "buy_hold_pnl": "Buy and hold",
            "covered_call_pnl": "Covered call",
        }
    )

    x_scale = alt.Scale(domain=[float(payoff_df["final_price"].min()), float(payoff_df["final_price"].max())])

    lines = (
        alt.Chart(line_df)
        .mark_line(point=False)
        .encode(
            x=alt.X("final_price:Q", title="Final stock price", scale=x_scale),
            y=alt.Y("pnl:Q", title="Profit / loss"),
            color=alt.Color("strategy:N", title="Strategy"),
            tooltip=[
                alt.Tooltip("strategy:N", title="Strategy"),
                alt.Tooltip("final_price:Q", title="Final price", format="$.2f"),
                alt.Tooltip("pnl:Q", title="P/L", format="$,.2f"),
            ],
        )
    )

    marker_df = pd.DataFrame(
        [
            {"label": "Current", "price": setup.current_price},
            {"label": "Strike", "price": setup.strike},
            {"label": "Breakeven", "price": setup.breakeven_price},
        ]
    )
    markers = (
        alt.Chart(marker_df)
        .mark_rule(strokeDash=[5, 5])
        .encode(
            x=alt.X("price:Q", scale=x_scale),
            tooltip=[
                alt.Tooltip("label:N", title="Marker"),
                alt.Tooltip("price:Q", title="Price", format="$.2f"),
            ],
        )
    )

    labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=4, dy=-6)
        .encode(
            x=alt.X("price:Q", scale=x_scale),
            y=alt.value(8),
            text="label:N",
        )
    )

    return (lines + markers + labels).properties(height=420)


def create_relative_chart(scenario_df: pd.DataFrame):
    if alt is None:
        return None
    return (
        alt.Chart(scenario_df)
        .mark_bar()
        .encode(
            x=alt.X("covered_call_minus_buy_hold:Q", title="Covered call minus buy and hold"),
            y=alt.Y("scenario:N", title="Scenario", sort=None),
            tooltip=[
                alt.Tooltip("scenario:N", title="Scenario"),
                alt.Tooltip("final_price:Q", title="Final price", format="$.2f"),
                alt.Tooltip("covered_call_pnl:Q", title="Covered-call P/L", format="$,.2f"),
                alt.Tooltip("covered_call_minus_buy_hold:Q", title="Relative P/L", format="$,.2f"),
                alt.Tooltip("assignment_flag:N", title="Assigned"),
            ],
        )
        .properties(height=280)
    )


def write_html_report(setup: CoveredCallSetup, payoff_df: pd.DataFrame, scenario_df: pd.DataFrame) -> None:
    ensure_output_dirs()
    rows = []
    rows.append("<html><head><title>Phase 3C Rich Payoff Snapshot</title></head><body>")
    rows.append("<h1>Phase 3C Rich Payoff Snapshot</h1>")
    rows.append(f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    rows.append("<h2>Setup</h2>")
    rows.append("<ul>")
    rows.append(f"<li>Ticker: {setup.ticker.upper()}</li>")
    rows.append(f"<li>Current price: {currency(setup.current_price)}</li>")
    rows.append(f"<li>Shares: {setup.shares}</li>")
    rows.append(f"<li>Contracts: {setup.contracts}</li>")
    rows.append(f"<li>Strike: {currency(setup.strike)}</li>")
    rows.append(f"<li>Premium per share: {currency(setup.premium)}</li>")
    rows.append(f"<li>Total premium: {currency(setup.premium_income)}</li>")
    rows.append(f"<li>Breakeven: {currency(setup.breakeven_price)}</li>")
    rows.append("</ul>")
    rows.append("<h2>Scenario Table</h2>")
    rows.append(scenario_df.to_html(index=False))
    rows.append("<h2>Payoff Grid</h2>")
    rows.append(payoff_df.to_html(index=False))
    rows.append("</body></html>")
    SNAPSHOT_HTML.write_text("\n".join(rows), encoding="utf-8")


def save_snapshot(setup: CoveredCallSetup, payoff_df: pd.DataFrame, scenario_df: pd.DataFrame) -> None:
    ensure_output_dirs()
    output_df = payoff_df.copy()
    output_df.insert(0, "snapshot_type", "payoff_grid")
    scenario_output = scenario_df.copy()
    scenario_output.insert(0, "snapshot_type", "scenario")
    combined = pd.concat([output_df, scenario_output], ignore_index=True, sort=False)
    for key, value in {
        "setup_ticker": setup.ticker.upper(),
        "setup_current_price": setup.current_price,
        "setup_shares": setup.shares,
        "setup_contracts": setup.contracts,
        "setup_strike": setup.strike,
        "setup_premium": setup.premium,
        "setup_dte": setup.dte,
        "setup_delta": setup.delta,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }.items():
        combined[key] = value
    combined.to_csv(SNAPSHOT_CSV, index=False)
    write_html_report(setup, payoff_df, scenario_df)


def setup_sidebar() -> CoveredCallSetup:
    st.sidebar.header("Covered-call setup")
    ticker = st.sidebar.text_input("Ticker", value="SPY").strip().upper() or "SPY"
    current_price = st.sidebar.number_input("Current stock price", min_value=0.01, value=545.25, step=1.0)
    shares = st.sidebar.number_input("Shares owned", min_value=0, value=100, step=100)
    contracts = st.sidebar.number_input("Short call contracts", min_value=0, value=1, step=1)
    strike = st.sidebar.number_input("Short call strike", min_value=0.01, value=555.00, step=1.0)
    premium = st.sidebar.number_input("Call premium per share", min_value=0.0, value=4.20, step=0.10)
    dte = st.sidebar.number_input("Days to expiration", min_value=0, value=30, step=1)
    delta = st.sidebar.number_input("Approximate call delta", min_value=0.0, max_value=1.0, value=0.30, step=0.01)

    st.sidebar.header("Graph range")
    lower_move_pct = st.sidebar.slider("Lower price move %", min_value=-50.0, max_value=-1.0, value=-20.0, step=1.0)
    upper_move_pct = st.sidebar.slider("Upper price move %", min_value=1.0, max_value=80.0, value=25.0, step=1.0)
    grid_points = st.sidebar.slider("Grid points", min_value=41, max_value=301, value=121, step=20)

    return CoveredCallSetup(
        ticker=ticker,
        current_price=float(current_price),
        shares=int(shares),
        contracts=int(contracts),
        strike=float(strike),
        premium=float(premium),
        dte=int(dte),
        delta=float(delta),
        lower_move_pct=float(lower_move_pct),
        upper_move_pct=float(upper_move_pct),
        grid_points=int(grid_points),
    )


def show_metric_row(setup: CoveredCallSetup) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total premium", currency(setup.premium_income))
    c2.metric("Breakeven", currency(setup.breakeven_price))
    c3.metric("Max profit near strike", signed_currency(setup.max_profit_at_or_above_strike))
    c4.metric("Downside cushion/share", currency(setup.premium_income / max(1, setup.shares)))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Covered shares", f"{setup.effective_shares:,}")
    c6.metric("Uncovered shares", f"{setup.uncovered_shares:,}")
    c7.metric("Strike distance", pct(((setup.strike / setup.current_price) - 1.0) * 100.0))
    c8.metric("Approx. delta", f"{setup.delta:.2f}")


def main() -> None:
    st.set_page_config(page_title="Phase 3C Rich Payoff Viewer", layout="wide")
    st.title("Phase 3C richer graphical covered-call payoff viewer")
    st.caption("Standalone prototype. Manual inputs only. No live market data yet.")

    setup = setup_sidebar()
    payoff_df = build_payoff_grid(setup)
    scenario_df = build_scenario_table(setup)

    show_metric_row(setup)

    if setup.contracts * 100 < setup.shares:
        st.warning("The selected contracts cover fewer shares than the share count. The model treats excess shares as uncovered stock.")
    if setup.strike <= setup.current_price:
        st.warning("The strike is at or below the current price. This is an in-the-money or at-the-money call setup.")

    tabs = st.tabs(["Payoff graph", "Scenario overlay", "Payoff grid", "Snapshot export", "Notes"])

    with tabs[0]:
        st.subheader("Covered-call payoff versus buy-and-hold")
        chart = create_payoff_chart(payoff_df, setup)
        if chart is not None:
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Altair is not available. Showing payoff table instead.")
            st.dataframe(payoff_df, use_container_width=True)

    with tabs[1]:
        st.subheader("Scenario overlay")
        chart = create_relative_chart(scenario_df)
        if chart is not None:
            st.altair_chart(chart, use_container_width=True)
        display_cols = [
            "scenario",
            "final_price",
            "price_change_pct",
            "buy_hold_pnl",
            "covered_call_pnl",
            "covered_call_minus_buy_hold",
            "premium_income",
            "intrinsic_call_loss",
            "assignment_flag",
            "zone",
        ]
        st.dataframe(scenario_df[display_cols], use_container_width=True)

    with tabs[2]:
        st.subheader("Full payoff grid")
        st.dataframe(payoff_df, use_container_width=True)

    with tabs[3]:
        st.subheader("Save current setup")
        st.write("Saving creates a CSV snapshot and a simple HTML report for later dashboard integration.")
        if st.button("Save Phase 3C payoff snapshot"):
            save_snapshot(setup, payoff_df, scenario_df)
            st.success(f"Saved snapshot: {SNAPSHOT_CSV}")
            st.success(f"Saved report: {SNAPSHOT_HTML}")
        st.write("Expected snapshot files:")
        st.code(str(SNAPSHOT_CSV))
        st.code(str(SNAPSHOT_HTML))

    with tabs[4]:
        st.subheader("Prototype notes")
        st.markdown(
            """
            This Phase 3C viewer improves the graphical payoff interface but remains a controlled prototype.

            It does not yet use live prices, option-chain imports, dividends, taxes, or assignment-probability modeling.
            The goal is to refine the user-facing payoff graph, markers, scenario overlay, and export workflow before
            integrating this interface into the customer-facing paid dashboard.
            """
        )


if __name__ == "__main__":
    main()
