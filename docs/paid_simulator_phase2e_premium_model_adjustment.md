# Phase 2E Controlled Premium-Model Adjustment Scaffold

## Purpose

Phase 2E applies the first controlled premium-model tuning adjustment.

The goal is not to replace the premium model yet. The goal is to create a safe, reversible comparison layer that shows what happens if we apply a conservative adjustment to the implied-volatility assumption.

## Added files

```text
app\paid_simulator\premium_model_adjustment.py
app\run_paid_simulator_premium_model_adjustment_check.py
docs\paid_simulator_phase2e_premium_model_adjustment.md
```

The first run also creates:

```text
config\premium_model_adjustment_config.json
```

## Inputs

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
```

## Outputs

```text
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\reports\paid_simulator\premium_model_adjustment_comparison.html
outputs\reports\paid_simulator\premium_model_adjustment_summary.txt
outputs\reports\paid_simulator\phase2e_premium_model_adjustment_check_report.txt
```

## What the adjustment does

This first adjustment is intentionally narrow:

```text
Adjustment scope: IV-only, fixed strike
```

That means the model keeps the original estimated strike and changes only the implied-volatility assumption by a small, capped amount. Then it recalculates:

```text
Adjusted call premium
Adjusted call delta
Premium change
Delta change
```

This is deliberately conservative. It isolates the effect of volatility tuning before we allow the model to change strike selection or payoff logic.

## Why this is safer

The original Phase 2B file remains unchanged:

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
```

The adjusted output is written separately:

```text
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
```

So we can compare the adjusted model against the old model before promoting any changes into the main dashboard.

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_premium_model_adjustment_check.py
```

Expected final line:

```text
Overall Phase 2E controlled premium adjustment status: PASS
```

## Meaning of PASS

A PASS means the controlled adjustment layer is installed, it reads the Phase 2B/2D inputs, and it writes the adjusted premium comparison files.

A PASS does not mean the model is fully calibrated to live option chains.

## Recommended next step

After this passes, the next step is to compare the adjusted premium output against the existing premium-aware payoff layer. That comparison should be done before replacing or promoting any customer-facing model assumptions.
