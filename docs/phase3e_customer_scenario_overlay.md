# Phase 3E-4 — Customer Scenario-Overlay Workflow

## Purpose

Phase 3E-4 adds a standalone customer-facing scenario-overlay workflow for the paid Covered Call Simulator.

This checkpoint keeps the workflow outside the main Streamlit dashboard until the logic passes cleanly. The goal is to support a later customer interface where a user can adjust a covered-call setup and refresh the payoff scenario summary with one click.

## Added files

```text
app\paid_simulator\phase3e_customer_scenario_overlay.py
app\run_paid_simulator_phase3e_customer_scenario_overlay_check.py
docs\phase3e_customer_scenario_overlay.md
```

## Customer-facing concepts included

The workflow calculates and labels:

- current price
- strike
- premium
- breakeven
- maximum profit if assigned
- downside cushion
- assignment zone
- stock-only profit
- covered-call profit
- option effect
- plain-English customer zone
- plain-English explanation for each scenario row

## Scenario zones

Each scenario row is assigned one of three customer-readable zones:

```text
Below breakeven
Profitable stock zone
Assignment zone
```

## Warning-box logic

The module includes warning logic for setups such as:

- strike below the current stock price
- strike too close to the current stock price
- premium providing a very small downside cushion
- breakeven above the current price
- unusually large premium relative to the stock price

These are warning hooks for the future customer dashboard. They are intentionally plain-English rather than developer-oriented.

## One-click overlay update hook

The function below is intended for future dashboard buttons or input widgets:

```text
update_customer_scenario_overlay(...)
```

It can update:

- current price
- strike
- premium
- cost basis
- scenario prices

If scenario prices are not supplied, the module builds a simple default scenario range around the current price and strike.

## Output files created by the check script

The check script creates:

```text
outputs\tables\paid_simulator\phase3e_customer_scenario_overlay.csv
outputs\tables\paid_simulator\phase3e_customer_scenario_overlay_updated.csv
outputs\saved_setups\paid_simulator\phase3e_customer_scenario_setup.json
outputs\reports\paid_simulator\phase3e_customer_scenario_overlay_checkpoint_report.txt
```

## How to run the check

After extracting the package into the project root, run this file in PyCharm:

```text
app\run_paid_simulator_phase3e_customer_scenario_overlay_check.py
```

Expected final line:

```text
Overall Phase 3E-4 checkpoint status: PASS
```

## Notes

This checkpoint does not modify the main dashboard. It prepares the customer scenario-overlay logic for later integration after the standalone workflow is verified.
