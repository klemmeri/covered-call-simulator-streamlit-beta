"""
phase3d_integrated_payoff_overlay_viewer.py

Standalone Phase 3D viewer for the Covered Call Strategy Stress Test.

This viewer combines the richer covered-call payoff interface with the
scenario-overlay stress-test table. It is intentionally separate from the
main dashboard until the workflow is validated.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import os
import subprocess
import sys

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # pragma: no cover - optional visual dependency
    alt = None


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parents[1]
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
PHASE3B_OVERLAY_CSV = OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv"
PHASE3B_OVERLAY_SUMMARY = OUTPUT_REPORT_DIR / "phase3_scenario_overlay_summary.txt"
PHASE3C_SNAPSHOT_CSV = OUTPUT_TABLE_DIR / "phase3c_rich_payoff_snapshot.csv"
PHASE3D_SNAPSHOT_CSV = OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv"
PHASE3D_SNAPSHOT_HTML = OUTPUT_REPORT_DIR / "phase3d_integrated_payoff_overlay_snapshot.html"


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
    range_percent: float

    @property
    def covered_shares(self) -> int:
        return max(0, self.contracts * 100)

    @property
    def effective_shares(self) -> int:
        return max(0, min(self.shares, self.covered_shares))

    @property
    def premium_income(self) -> float:
        return self.premium * self.effective_shares

    @property
    def breakeven(self) -> float:
        if self.shares <= 0:
            return self.current_price
        return self.current_price - (self.premium_income / self.shares)

    @property
    def max_profit_estimate(self) -> float:
        share_profit = (self.strike - self.current_price) * self.effective_shares
        return share_profit + self.premium_income


def currency(value: float) -> str:
    return f"${value:,.2f}"


def signed_currency(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.2f}"


def open_path(path: Path) -> None:
    if not path.exists():
        return
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def load_existing_snapshot() -> dict[str, float | int | str]:
    defaults: dict[str, float | int | str] = {
        "ticker": "SPY",
        "current_price": 545.25,
        "shares": 100,
        "contracts": 1,
        "strike": 555.0,
        "premium": 4.20,
        "dte": 30,
        "delta": 0.30,
        "range_percent": 12.0,
    }

    if not PHASE3C_SNAPSHOT_CSV.exists():
        return defaults

    try:
        df = pd.read_csv(PHASE3C_SNAPSHOT_CSV)
        if df.empty:
            return defaults
        row = df.iloc[0].to_dict()
        mapping = {
            "ticker": ["ticker", "Ticker"],
            "current_price": ["current_price", "Current Price", "stock_price", "Stock Price"],
            "shares": ["shares", "Shares", "shares_owned", "Shares Owned"],
            "contracts": ["contracts", "Contracts", "short_call_contracts", "Short Call Contracts"],
            "strike": ["strike", "Strike", "short_call_strike", "Short Call Strike"],
            "premium": ["premium", "Premium", "premium_per_share", "Premium Per Share"],
            "dte": ["dte", "DTE", "days_to_expiration", "Days To Expiration"],
            "delta": ["delta", "Delta", "call_delta", "Call Delta"],
        }
        for key, candidates in mapping.items():
            for candidate in candidates:
                if candidate in row and pd.notna(row[candidate]):
                    defaults[key] = row[candidate]
                    break
    except Exception:
        return defaults

    return defaults


def compute_payoff_grid(setup: CoveredCallSetup) -> pd.DataFrame:
    low = setup.current_price * (1.0 - setup.range_percent / 100.0)
    high = setup.current_price * (1.0 + setup.range_percent / 100.0)
    if low <= 0:
        low = setup.current_price * 0.5
    if high <= low:
        high = setup.current_price * 1.1

    rows = []
    steps = 81
    for i in range(steps):
        price = low + (high - low) * i / (steps - 1)
        buy_hold_pl = (price - setup.current_price) * setup.shares
        intrinsic_loss = max(0.0, price - setup.strike) * setup.effective_shares
        covered_call_pl = buy_hold_pl + setup.premium_income - intrinsic_loss
        relative = covered_call_pl - buy_hold_pl
        rows.append(
            {
                "ticker": setup.ticker,
                "stock_price_at_expiration": round(price, 2),
                "buy_and_hold_pl": round(buy_hold_pl, 2),
                "covered_call_pl": round(covered_call_pl, 2),
                "covered_call_minus_buy_and_hold": round(relative, 2),
                "intrinsic_call_loss": round(intrinsic_loss, 2),
                "assignment_flag": price >= setup.strike,
                "price_zone": classify_price_zone(price, setup),
            }
        )
    return pd.DataFrame(rows)


def classify_price_zone(price: float, setup: CoveredCallSetup) -> str:
    if price < setup.breakeven:
        return "Below breakeven"
    if price < setup.current_price:
        return "Cushion zone"
    if price < setup.strike:
        return "Upside capture zone"
    return "Assignment / capped upside zone"


def build_scenario_overlay_from_setup(setup: CoveredCallSetup) -> pd.DataFrame:
    scenarios = [
        ("Sharp pullback", -0.10),
        ("Moderate pullback", -0.05),
        ("Flat / pin", 0.00),
        ("Mild rally", 0.04),
        ("Strike test", (setup.strike / setup.current_price) - 1.0),
        ("Strong rally", 0.12),
    ]
    rows = []
    for name, move in scenarios:
        final_price = setup.current_price * (1.0 + move)
        buy_hold_pl = (final_price - setup.current_price) * setup.shares
        intrinsic_loss = max(0.0, final_price - setup.strike) * setup.effective_shares
        covered_call_pl = buy_hold_pl + setup.premium_income - intrinsic_loss
        relative = covered_call_pl - buy_hold_pl
        rows.append(
            {
                "scenario": name,
                "price_move_percent": round(move * 100.0, 2),
                "ending_price": round(final_price, 2),
                "buy_and_hold_pl": round(buy_hold_pl, 2),
                "covered_call_pl": round(covered_call_pl, 2),
                "covered_call_minus_buy_and_hold": round(relative, 2),
                "premium_income": round(setup.premium_income, 2),
                "intrinsic_call_loss": round(intrinsic_loss, 2),
                "assignment_flag": final_price >= setup.strike,
                "interpretation": interpret_scenario(relative, final_price >= setup.strike),
            }
        )
    return pd.DataFrame(rows)


def interpret_scenario(relative: float, assignment: bool) -> str:
    if assignment and relative < 0:
        return "Covered call lags because upside is capped above the strike."
    if relative > 0:
        return "Covered call outperforms buy-and-hold by retaining premium income."
    if relative < 0:
        return "Covered call underperforms buy-and-hold in this scenario."
    return "Covered call and buy-and-hold are approximately tied."


def load_phase3b_overlay() -> pd.DataFrame:
    if not PHASE3B_OVERLAY_CSV.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(PHASE3B_OVERLAY_CSV)
    except Exception:
        return pd.DataFrame()


def normalize_overlay_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    rename_map = {}
    for col in out.columns:
        normalized = col.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized in {"scenario_name", "scenario"}:
            rename_map[col] = "scenario"
        elif normalized in {"ending_price", "final_price", "price_at_expiration"}:
            rename_map[col] = "ending_price"
        elif normalized in {"buy_hold_pl", "buy_and_hold_pl"}:
            rename_map[col] = "buy_and_hold_pl"
        elif normalized in {"covered_call_pl", "covered_call_p_l"}:
            rename_map[col] = "covered_call_pl"
        elif normalized in {"covered_call_minus_buy_hold", "covered_call_minus_buy_and_hold", "relative_result"}:
            rename_map[col] = "covered_call_minus_buy_and_hold"
        elif normalized in {"assignment", "assignment_flag"}:
            rename_map[col] = "assignment_flag"
    return out.rename(columns=rename_map)


def save_snapshot(setup: CoveredCallSetup, payoff_df: pd.DataFrame, overlay_df: pd.DataFrame) -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_rows = []
    setup_data = {
        "ticker": setup.ticker,
        "current_price": setup.current_price,
        "shares": setup.shares,
        "contracts": setup.contracts,
        "strike": setup.strike,
        "premium": setup.premium,
        "dte": setup.dte,
        "delta": setup.delta,
        "range_percent": setup.range_percent,
        "premium_income": setup.premium_income,
        "breakeven": setup.breakeven,
        "max_profit_estimate": setup.max_profit_estimate,
    }
    for key, value in setup_data.items():
        snapshot_rows.append({"field": key, "value": value})

    pd.DataFrame(snapshot_rows).to_csv(PHASE3D_SNAPSHOT_CSV, index=False)

    html = [
        "<html><head><title>Phase 3D Integrated Payoff Overlay Snapshot</title></head><body>",
        "<h1>Phase 3D Integrated Payoff Overlay Snapshot</h1>",
        "<h2>Setup</h2>",
        pd.DataFrame(snapshot_rows).to_html(index=False),
        "<h2>Scenario overlay</h2>",
        overlay_df.to_html(index=False),
        "<h2>Payoff grid</h2>",
        payoff_df.to_html(index=False),
        "</body></html>",
    ]
    PHASE3D_SNAPSHOT_HTML.write_text("\n".join(html), encoding="utf-8")


def chart_payoff(payoff_df: pd.DataFrame, setup: CoveredCallSetup) -> None:
    if alt is None:
        st.line_chart(
            payoff_df.set_index("stock_price_at_expiration")[["buy_and_hold_pl", "covered_call_pl"]]
        )
        return

    long_df = payoff_df.melt(
        id_vars=["stock_price_at_expiration"],
        value_vars=["buy_and_hold_pl", "covered_call_pl"],
        var_name="strategy",
        value_name="profit_loss",
    )
    base = (
        alt.Chart(long_df)
        .mark_line()
        .encode(
            x=alt.X("stock_price_at_expiration:Q", title="Stock price at expiration"),
            y=alt.Y("profit_loss:Q", title="Profit / loss"),
            color=alt.Color("strategy:N", title="Strategy"),
            tooltip=["strategy:N", "stock_price_at_expiration:Q", "profit_loss:Q"],
        )
        .properties(height=420)
    )

    marker_rows = pd.DataFrame(
        [
            {"label": "Current", "x": setup.current_price},
            {"label": "Strike", "x": setup.strike},
            {"label": "Breakeven", "x": setup.breakeven},
        ]
    )
    rules = (
        alt.Chart(marker_rows)
        .mark_rule(strokeDash=[6, 4])
        .encode(x="x:Q", tooltip=["label:N", "x:Q"])
    )
    st.altair_chart(base + rules, use_container_width=True)


def chart_relative_overlay(overlay_df: pd.DataFrame) -> None:
    if overlay_df.empty or "covered_call_minus_buy_and_hold" not in overlay_df.columns:
        st.info("No scenario overlay data available for the relative chart.")
        return
    if alt is None:
        st.bar_chart(overlay_df.set_index("scenario")[["covered_call_minus_buy_and_hold"]])
        return
    chart = (
        alt.Chart(overlay_df)
        .mark_bar()
        .encode(
            x=alt.X("scenario:N", title="Scenario", sort=None),
            y=alt.Y("covered_call_minus_buy_and_hold:Q", title="Covered call minus buy-and-hold"),
            tooltip=["scenario:N", "covered_call_minus_buy_and_hold:Q", "assignment_flag:N"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Phase 3D Integrated Payoff Overlay", layout="wide")

    st.title("Phase 3D integrated payoff and scenario overlay")
    st.caption(
        "Developer prototype: combines the richer payoff graph with scenario-overlay stress tests."
    )

    defaults = load_existing_snapshot()

    with st.sidebar:
        st.header("Covered-call setup")
        ticker = st.text_input("Ticker", value=str(defaults["ticker"]))
        current_price = st.number_input("Current stock price", min_value=0.01, value=float(defaults["current_price"]), step=1.0)
        shares = st.number_input("Shares owned", min_value=0, value=int(float(defaults["shares"])), step=100)
        contracts = st.number_input("Short call contracts", min_value=0, value=int(float(defaults["contracts"])), step=1)
        strike = st.number_input("Short call strike", min_value=0.01, value=float(defaults["strike"]), step=1.0)
        premium = st.number_input("Call premium per share", min_value=0.0, value=float(defaults["premium"]), step=0.10)
        dte = st.number_input("DTE", min_value=0, value=int(float(defaults["dte"])), step=1)
        delta = st.number_input("Approximate call delta", min_value=0.0, max_value=1.0, value=float(defaults["delta"]), step=0.01)
        range_percent = st.slider("Graph range around current price", min_value=5.0, max_value=40.0, value=float(defaults.get("range_percent", 12.0)), step=1.0)
        save_clicked = st.button("Save Phase 3D snapshot")

    setup = CoveredCallSetup(
        ticker=ticker.upper().strip() or "SPY",
        current_price=current_price,
        shares=int(shares),
        contracts=int(contracts),
        strike=strike,
        premium=premium,
        dte=int(dte),
        delta=delta,
        range_percent=range_percent,
    )

    payoff_df = compute_payoff_grid(setup)
    overlay_df = build_scenario_overlay_from_setup(setup)
    phase3b_overlay = normalize_overlay_columns(load_phase3b_overlay())

    if save_clicked:
        save_snapshot(setup, payoff_df, overlay_df)
        st.success(f"Saved snapshot to {PHASE3D_SNAPSHOT_CSV}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Premium income", currency(setup.premium_income))
    col2.metric("Breakeven", currency(setup.breakeven))
    col3.metric("Max profit estimate", signed_currency(setup.max_profit_estimate))
    col4.metric("Covered shares", f"{setup.effective_shares:,}")

    tabs = st.tabs([
        "Integrated payoff",
        "Scenario overlay",
        "Phase 3B context",
        "Payoff grid",
        "Files",
        "Notes",
    ])

    with tabs[0]:
        st.subheader("Integrated payoff graph")
        chart_payoff(payoff_df, setup)
        st.markdown(
            "The chart compares buy-and-hold with the covered-call payoff and marks the current price, strike, and breakeven."
        )

    with tabs[1]:
        st.subheader("Scenario overlay based on current setup")
        chart_relative_overlay(overlay_df)
        st.dataframe(overlay_df, use_container_width=True)

    with tabs[2]:
        st.subheader("Existing Phase 3B scenario-overlay context")
        if phase3b_overlay.empty:
            st.info("No Phase 3B scenario-overlay CSV is available yet.")
        else:
            st.dataframe(phase3b_overlay, use_container_width=True)
        if PHASE3B_OVERLAY_SUMMARY.exists():
            st.text(PHASE3B_OVERLAY_SUMMARY.read_text(encoding="utf-8", errors="replace"))

    with tabs[3]:
        st.subheader("Full payoff grid")
        st.dataframe(payoff_df, use_container_width=True)

    with tabs[4]:
        st.subheader("Files and reports")
        file_rows = [
            {"file": str(PHASE3D_SNAPSHOT_CSV), "exists": PHASE3D_SNAPSHOT_CSV.exists()},
            {"file": str(PHASE3D_SNAPSHOT_HTML), "exists": PHASE3D_SNAPSHOT_HTML.exists()},
            {"file": str(PHASE3B_OVERLAY_CSV), "exists": PHASE3B_OVERLAY_CSV.exists()},
            {"file": str(PHASE3C_SNAPSHOT_CSV), "exists": PHASE3C_SNAPSHOT_CSV.exists()},
        ]
        st.dataframe(pd.DataFrame(file_rows), use_container_width=True)
        if PHASE3D_SNAPSHOT_HTML.exists():
            if st.button("Open Phase 3D snapshot HTML"):
                open_path(PHASE3D_SNAPSHOT_HTML)

    with tabs[5]:
        st.subheader("Notes")
        st.markdown(
            """
This is a Developer-view prototype for Phase 3D.

It is intended to test the combined workflow before promotion into the customer-facing dashboard:

1. Enter a covered-call setup.
2. Inspect the payoff graph.
3. Inspect scenario-overlay outcomes.
4. Save a snapshot.
5. Use the snapshot as a future input to dashboard or report workflows.

This is not live market data and is not a trade recommendation engine.
"""
        )


if __name__ == "__main__":
    main()
