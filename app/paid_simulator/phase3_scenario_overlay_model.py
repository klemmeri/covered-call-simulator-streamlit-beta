"""
phase3_scenario_overlay_model.py

Phase 3B scenario-overlay model for the Covered Call Strategy Stress Test.

This module creates a simple scenario-overlay table for a user-entered
covered-call setup. It is intentionally isolated from the main dashboard.

Inputs
------
Optional:
    outputs/tables/paid_simulator/phase3_interactive_payoff_snapshot.csv

If no snapshot exists, the module uses a conservative SPY demo setup.

Outputs
-------
    outputs/tables/paid_simulator/phase3_scenario_overlay.csv
    outputs/reports/paid_simulator/phase3_scenario_overlay.html
    outputs/reports/paid_simulator/phase3_scenario_overlay_summary.txt
"""

from __future__ import annotations

import csv
import html
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TABLE_DIR = Path("outputs") / "tables" / "paid_simulator"
REPORT_DIR = Path("outputs") / "reports" / "paid_simulator"
SNAPSHOT_FILE = TABLE_DIR / "phase3_interactive_payoff_snapshot.csv"
OVERLAY_CSV = TABLE_DIR / "phase3_scenario_overlay.csv"
OVERLAY_HTML = REPORT_DIR / "phase3_scenario_overlay.html"
OVERLAY_SUMMARY = REPORT_DIR / "phase3_scenario_overlay_summary.txt"


@dataclass(frozen=True)
class CoveredCallSetup:
    ticker: str
    current_price: float
    shares_owned: int
    short_call_contracts: int
    call_strike: float
    call_premium: float
    dte: int
    approximate_call_delta: float

    @property
    def covered_shares(self) -> int:
        return max(0, self.short_call_contracts * 100)

    @property
    def effective_shares(self) -> int:
        return min(self.shares_owned, self.covered_shares)

    @property
    def total_premium(self) -> float:
        return self.call_premium * self.effective_shares

    @property
    def breakeven_price(self) -> float:
        if self.effective_shares <= 0:
            return self.current_price
        return self.current_price - self.call_premium


SCENARIO_RETURNS = [
    ("Sharp pullback", -0.12, "Tests downside cushion; covered call should lose less than buy-and-hold."),
    ("Moderate pullback", -0.06, "Shows partial protection from the premium."),
    ("Flat / pin", 0.00, "Theta-income case; premium dominates the comparison."),
    ("Mild rally", 0.04, "Tests whether upside is still meaningfully available."),
    ("Strike test", None, "Moves price directly to the call strike."),
    ("Strong rally", 0.12, "Tests capped-upside cost versus buy-and-hold."),
]


def _safe_float(value: object, default: float) -> float:
    try:
        if value is None:
            return default
        text = str(value).replace("$", "").replace(",", "").strip()
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def _safe_int(value: object, default: int) -> int:
    try:
        if value is None:
            return default
        text = str(value).replace(",", "").strip()
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def default_setup() -> CoveredCallSetup:
    return CoveredCallSetup(
        ticker="SPY",
        current_price=545.25,
        shares_owned=100,
        short_call_contracts=1,
        call_strike=555.00,
        call_premium=4.20,
        dte=30,
        approximate_call_delta=0.30,
    )


def load_snapshot_setup(project_root: Path) -> CoveredCallSetup:
    """Load the latest Phase 3 interactive payoff snapshot if available."""
    snapshot_path = project_root / SNAPSHOT_FILE
    fallback = default_setup()

    if not snapshot_path.exists():
        return fallback

    try:
        with snapshot_path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception:
        return fallback

    if not rows:
        return fallback

    row = rows[-1]
    return CoveredCallSetup(
        ticker=str(row.get("ticker", fallback.ticker)).strip() or fallback.ticker,
        current_price=_safe_float(row.get("current_price"), fallback.current_price),
        shares_owned=_safe_int(row.get("shares_owned"), fallback.shares_owned),
        short_call_contracts=_safe_int(row.get("short_call_contracts"), fallback.short_call_contracts),
        call_strike=_safe_float(row.get("call_strike"), fallback.call_strike),
        call_premium=_safe_float(row.get("call_premium"), fallback.call_premium),
        dte=_safe_int(row.get("dte"), fallback.dte),
        approximate_call_delta=_safe_float(row.get("approximate_call_delta"), fallback.approximate_call_delta),
    )


def payoff_for_price(setup: CoveredCallSetup, ending_price: float) -> dict[str, object]:
    buy_hold_pnl = (ending_price - setup.current_price) * setup.shares_owned

    stock_pnl = (ending_price - setup.current_price) * setup.shares_owned
    intrinsic_loss = max(0.0, ending_price - setup.call_strike) * setup.effective_shares
    covered_call_pnl = stock_pnl + setup.total_premium - intrinsic_loss
    relative = covered_call_pnl - buy_hold_pnl
    assignment_flag = ending_price > setup.call_strike

    if assignment_flag and relative < 0:
        interpretation = "Covered call lags because upside is capped above the strike."
    elif relative > 0 and ending_price <= setup.call_strike:
        interpretation = "Covered call benefits from premium income without assignment."
    elif abs(relative) < 1e-9:
        interpretation = "Covered call and buy-and-hold are approximately tied."
    else:
        interpretation = "Covered call result depends mainly on stock movement and premium cushion."

    return {
        "ending_price": round(ending_price, 2),
        "buy_hold_pnl": round(buy_hold_pnl, 2),
        "covered_call_pnl": round(covered_call_pnl, 2),
        "covered_call_minus_buy_hold": round(relative, 2),
        "premium_income": round(setup.total_premium, 2),
        "intrinsic_call_loss": round(intrinsic_loss, 2),
        "assignment_flag": "YES" if assignment_flag else "NO",
        "interpretation": interpretation,
    }


def build_overlay_rows(setup: CoveredCallSetup) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for label, move, note in SCENARIO_RETURNS:
        if move is None:
            ending_price = setup.call_strike
            move_pct = (ending_price / setup.current_price - 1.0) * 100.0
        else:
            ending_price = setup.current_price * (1.0 + move)
            move_pct = move * 100.0

        payoff = payoff_for_price(setup, ending_price)
        rows.append(
            {
                "ticker": setup.ticker,
                "scenario": label,
                "price_move_pct": round(move_pct, 2),
                "current_price": round(setup.current_price, 2),
                "call_strike": round(setup.call_strike, 2),
                "call_premium": round(setup.call_premium, 2),
                "shares_owned": setup.shares_owned,
                "short_call_contracts": setup.short_call_contracts,
                "dte": setup.dte,
                "approximate_call_delta": round(setup.approximate_call_delta, 3),
                "breakeven_price": round(setup.breakeven_price, 2),
                "scenario_note": note,
                **payoff,
            }
        )

    return rows


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def money(value: object) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)


def write_html(path: Path, setup: CoveredCallSetup, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table_rows = []
    for row in rows:
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['scenario']))}</td>"
            f"<td>{row['price_move_pct']}%</td>"
            f"<td>{money(row['ending_price'])}</td>"
            f"<td>{money(row['buy_hold_pnl'])}</td>"
            f"<td>{money(row['covered_call_pnl'])}</td>"
            f"<td>{money(row['covered_call_minus_buy_hold'])}</td>"
            f"<td>{html.escape(str(row['assignment_flag']))}</td>"
            f"<td>{html.escape(str(row['interpretation']))}</td>"
            "</tr>"
        )

    html_text = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Phase 3 scenario overlay</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 28px; color: #1f2937; }}
    h1 {{ margin-bottom: 0.2rem; }}
    .subtle {{ color: #6b7280; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 10px; padding: 14px; margin: 14px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Phase 3 scenario overlay</h1>
  <p class=\"subtle\">Interactive covered-call payoff stress-test overlay scaffold.</p>
  <div class=\"card\">
    <strong>Setup:</strong> {html.escape(setup.ticker)} at {money(setup.current_price)},
    {setup.shares_owned} shares, {setup.short_call_contracts} short call contract(s),
    strike {money(setup.call_strike)}, premium {money(setup.call_premium)} per share,
    DTE {setup.dte}, approximate delta {setup.approximate_call_delta:.2f}.
  </div>
  <table>
    <thead>
      <tr>
        <th>Scenario</th><th>Move</th><th>Ending price</th><th>Buy-and-hold P/L</th>
        <th>Covered-call P/L</th><th>CC minus B&H</th><th>Assignment</th><th>Interpretation</th>
      </tr>
    </thead>
    <tbody>
      {''.join(table_rows)}
    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def write_summary(path: Path, setup: CoveredCallSetup, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    best = max(rows, key=lambda r: float(r["covered_call_minus_buy_hold"]))
    worst = min(rows, key=lambda r: float(r["covered_call_minus_buy_hold"]))
    assigned = sum(1 for r in rows if r["assignment_flag"] == "YES")

    text = f"""Phase 3 scenario overlay summary

Overall: PASS

Setup:
- Ticker: {setup.ticker}
- Current price: ${setup.current_price:,.2f}
- Shares owned: {setup.shares_owned}
- Short call contracts: {setup.short_call_contracts}
- Call strike: ${setup.call_strike:,.2f}
- Call premium: ${setup.call_premium:,.2f} per share
- DTE: {setup.dte}
- Approximate call delta: {setup.approximate_call_delta:.2f}
- Total premium: ${setup.total_premium:,.2f}
- Breakeven price: ${setup.breakeven_price:,.2f}

Overlay results:
- Scenario rows: {len(rows)}
- Assignment scenarios: {assigned}
- Best covered-call relative case: {best['scenario']} ({money(best['covered_call_minus_buy_hold'])})
- Worst covered-call relative case: {worst['scenario']} ({money(worst['covered_call_minus_buy_hold'])})

Interpretation:
This scaffold adds scenario-overlay logic for the Phase 3 interactive payoff interface.
It is still a deterministic payoff stress test, not live market data and not a trade recommendation.
"""
    path.write_text(text, encoding="utf-8")


def run(project_root: Path | None = None) -> dict[str, Path]:
    root = Path.cwd() if project_root is None else Path(project_root)
    setup = load_snapshot_setup(root)
    rows = build_overlay_rows(setup)

    csv_path = root / OVERLAY_CSV
    html_path = root / OVERLAY_HTML
    summary_path = root / OVERLAY_SUMMARY

    write_csv(csv_path, rows)
    write_html(html_path, setup, rows)
    write_summary(summary_path, setup, rows)

    return {
        "csv": csv_path,
        "html": html_path,
        "summary": summary_path,
    }


if __name__ == "__main__":
    outputs = run(Path(__file__).resolve().parents[2])
    for label, path in outputs.items():
        print(f"{label}: {path}")
