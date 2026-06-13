# Phase 3E-5 — Customer Payoff Workbench

## Purpose

Phase 3E-5 combines the earlier Phase 3E customer-facing pieces into one standalone workflow module. It is still separate from the main Streamlit dashboard so it can be checked safely before any dashboard integration.

The workbench is intended to become the customer-ready payoff workflow for the future Pro dashboard.

## Files added

```text
app\paid_simulator\phase3e_customer_payoff_workbench.py
app\run_paid_simulator_phase3e_customer_workbench_check.py
docs\phase3e_customer_payoff_workbench.md
```

## What the module does

The module provides one customer-facing workflow that can:

1. Validate a covered-call setup.
2. Calculate key payoff metrics.
3. Build customer-facing metric cards.
4. Build risk-warning boxes.
5. Build a scenario overlay.
6. Save a setup to JSON.
7. Reload a saved setup.
8. Export scenario rows to CSV.
9. Write a plain-text customer summary report.
10. Refresh the scenario overlay using a one-call update hook.

## Customer-facing labels included

The checkpoint verifies language for:

- current stock price
- call strike price
- premium received
- breakeven price
- maximum profit if assigned
- downside cushion from premium
- distance to assignment zone
- scenario overlay
- risk warnings

## Outputs created by the check script

```text
outputs\saved_setups\paid_simulator\phase3e_customer_workbench_setup.json
outputs\tables\paid_simulator\phase3e_customer_workbench_scenarios.csv
outputs\reports\paid_simulator\phase3e_customer_workbench_summary.txt
```

## How to run the checkpoint

After extracting the zip package into the project root, run:

```text
app\run_paid_simulator_phase3e_customer_workbench_check.py
```

Expected final result:

```text
Overall Phase 3E-5 checkpoint status: PASS
```

## Design note

This checkpoint does not modify the paid dashboard. The next logical phase is to add the customer workbench as a protected Developer-view tab first, verify it in Streamlit, and only later decide how much of it belongs in the true customer-facing dashboard.
