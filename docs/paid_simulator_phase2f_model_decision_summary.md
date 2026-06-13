# Phase 2F Model-Decision Summary

This package adds a consolidated model-decision report for the Covered Call Strategy Stress Test.

## Purpose

Phase 2F combines the evidence from the premium-aware model, the adjusted-premium model, validation checks, and tuning recommendations into one scenario-level decision report.

It answers a narrow question:

> Is the adjusted premium model ready to remain research-only, move toward controlled promotion, or require more tuning before it becomes central to the dashboard?

## Files added

```text
app\paid_simulator\model_decision_summary.py
app\run_paid_simulator_model_decision_summary_check.py
docs\paid_simulator_phase2f_model_decision_summary.md
```

## Inputs read

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_vs_scaffold_comparison.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
```

## Outputs written

```text
outputs\tables\paid_simulator\model_decision_summary.csv
outputs\reports\paid_simulator\model_decision_summary.html
outputs\reports\paid_simulator\model_decision_summary.txt
outputs\reports\paid_simulator\phase2f_model_decision_summary_check_report.txt
```

## Decision labels

The summary may assign one of these labels by scenario:

```text
CANDIDATE FOR CONTROLLED PROMOTION
USE AS RESEARCH MODEL
REVIEW BEFORE PROMOTION
DO NOT PROMOTE
```

These labels are internal model-development labels. They are not customer-facing trade recommendations.

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_model_decision_summary_check.py
```

Expected result:

```text
Overall Phase 2F model-decision summary status: PASS
```

## Notes

This package is add-only. It does not overwrite the dashboard, customer view, premium model, adjusted premium model, or any earlier Phase 2 output.

The goal is to consolidate evidence before making any model-promotion decision.
