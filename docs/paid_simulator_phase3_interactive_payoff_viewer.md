# Phase 3 Interactive Covered-Call Payoff Viewer

## Purpose

This package starts Phase 3 of the Covered Call Strategy Stress Test project.

It adds a standalone Streamlit prototype where a user can enter their own covered-call setup and immediately see a graphical payoff comparison.

This is the first step toward the Pro-version visual interface.

## Files added

```text
app\paid_simulator\phase3_interactive_payoff_viewer.py
app\run_paid_simulator_phase3_interactive_payoff_viewer.py
app\run_paid_simulator_phase3_interactive_payoff_viewer_check.py
docs\paid_simulator_phase3_interactive_payoff_viewer.md
```

## What the viewer includes

The viewer lets the user enter:

```text
Ticker
Current stock price
Shares owned
Short call contracts
Short call strike
Call premium per share
Days to expiration
Approximate call delta
```

It displays:

```text
Buy-and-hold payoff line
Covered-call payoff line
Current price marker
Strike / assignment marker
Break-even marker
Total premium
Maximum profit estimate
Downside cushion
Scenario payoff table
Full payoff grid
```

## Outputs written

Every time the viewer runs, it writes a local snapshot:

```text
outputs\tables\paid_simulator\phase3_interactive_payoff_snapshot.csv
outputs\reports\paid_simulator\phase3_interactive_payoff_snapshot.html
```

## Important limitation

This is not yet a live ticker.

The current version uses manually entered price and option values. A future phase can add live or imported price/option-chain data.

## Test script

Run:

```text
app\run_paid_simulator_phase3_interactive_payoff_viewer_check.py
```

Expected result:

```text
Overall Phase 3 interactive payoff viewer status: PASS
```

## Launch script

Run:

```text
app\run_paid_simulator_phase3_interactive_payoff_viewer.py
```

This opens the standalone viewer in the browser.

## Design note

This is intentionally standalone and add-only. It does not replace the main paid simulator dashboard. Integration into the Developer view should happen only after the standalone viewer passes.
