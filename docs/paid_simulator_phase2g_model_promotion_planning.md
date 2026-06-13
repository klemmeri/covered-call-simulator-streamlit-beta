# Phase 2G — Controlled Model-Promotion Planning

This package adds the first Phase 2G planning layer for the paid simulator.

It does **not** promote a model into the customer-facing workflow. It creates a
controlled internal promotion plan from the Phase 2F model-decision summary.

## Added files

```text
app\paid_simulator\model_promotion_planning.py
app\run_paid_simulator_model_promotion_planning_check.py
docs\paid_simulator_phase2g_model_promotion_planning.md
```

## Inputs

```text
outputs\tables\paid_simulator\model_decision_summary.csv
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
```

Only `model_decision_summary.csv` is required. The other files are used as
supporting evidence when available.

## Outputs

```text
outputs\tables\paid_simulator\model_promotion_plan.csv
outputs\reports\paid_simulator\model_promotion_plan.html
outputs\reports\paid_simulator\model_promotion_plan.txt
outputs\reports\paid_simulator\phase2g_model_promotion_planning_check_report.txt
```

## Promotion labels

The plan uses internal development labels:

```text
PROMOTION CANDIDATE - INTERNAL ONLY
KEEP AS RESEARCH MODEL
REVIEW BEFORE PROMOTION
DO NOT PROMOTE
UNCLASSIFIED - REVIEW
```

All scenarios remain `Developer view only` at this stage.

## Test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_model_promotion_planning_check.py
```

Expected:

```text
Overall Phase 2G model-promotion planning status: PASS
```

## Next step

After this passes, add a standalone Phase 2G model-promotion viewer.
