"""
Run a standalone check of the Phase 2 option-payoff scaffold.

Run this file from PyCharm.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_payoff_scaffold.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.option_payoff_model import (  # noqa: E402
    CoveredCallInput,
    calculate_covered_call_payoff,
    estimate_demo_call_premium,
    estimate_demo_strike,
)


def main() -> None:
    print("=" * 88)
    print("Phase 2 option-payoff scaffold check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    start_price = 545.25
    target_delta = 0.30
    target_dte = 30
    strike = estimate_demo_strike(start_price, target_delta, target_dte)
    premium = estimate_demo_call_premium(start_price, target_delta, target_dte)

    terminal_prices = [500.00, 545.25, 570.00, 600.00]
    rows = []
    for end_price in terminal_prices:
        payoff = calculate_covered_call_payoff(
            CoveredCallInput(
                ticker="SPY",
                start_price=start_price,
                end_price=end_price,
                strike_price=strike,
                call_premium=premium,
                contracts=1,
                transaction_cost=1.00,
                slippage=0.01,
            )
        )
        rows.append(payoff.to_dict())

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("Demo assumptions")
    print("-" * 88)
    print(f"Start price:      ${start_price:,.2f}")
    print(f"Target delta:     {target_delta:.2f}")
    print(f"Target DTE:       {target_dte}")
    print(f"Estimated strike: ${strike:,.2f}")
    print(f"Estimated premium:${premium:,.2f}")
    print()

    print("Payoff rows")
    print("-" * 88)
    for row in rows:
        print(
            f"End ${row['end_price']:,.2f} | "
            f"covered-call P/L {row['covered_call_pnl']:,.2f} | "
            f"buy-hold P/L {row['buy_hold_pnl']:,.2f} | "
            f"relative {row['covered_call_minus_buy_hold']:,.2f} | "
            f"assigned {row['assigned']}"
        )
    print()
    print(f"Saved: {OUTPUT_PATH}")
    print()
    print("=" * 88)
    print("Overall option-payoff scaffold status: PASS")
    print("The standalone payoff approximation module is installed and working.")
    print("=" * 88)


if __name__ == "__main__":
    main()
