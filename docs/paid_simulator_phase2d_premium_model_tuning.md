# Phase 2D Premium-Model Assumption Tuning Scaffold

Generated: 2026-06-12

## Purpose

This package adds the first Phase 2D premium-model tuning layer to the Covered Call Strategy Stress Test project.

Phase 2B added a more realistic option-premium scaffold.
Phase 2C added validation checks around that premium model.
Phase 2D begins the process of tuning the premium-model assumptions before those assumptions are promoted further into the customer-facing workflow.

This package does **not** change the working dashboard, the customer view, or the option-pricing model itself. It only reads the current premium-model outputs and produces tuning recommendations.

## Added files

```text
app\paid_simulator\premium_model_tuning.py
app\run_paid_simulator_premium_model_tuning_check.py
docs\paid_simulator_phase2d_premium_model_tuning.md
```

The first run also creates:

```text
config\premium_model_tuning_config.json
```

## Inputs

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
config\premium_model_tuning_config.json
```

## Outputs

```text
outputs\tables\paid_simulator\premium_model_tuning_recommendations.csv
outputs\reports\paid_simulator\premium_model_tuning_recommendations.html
outputs\reports\paid_simulator\premium_model_tuning_summary.txt
outputs\reports\paid_simulator\phase2d_premium_model_tuning_check_report.txt
```

## What the tuning scaffold checks

The scaffold reviews each modeled scenario and checks whether the current premium-model assumptions look reasonable.

It reviews:

```text
Premium as percent of stock price
Estimated implied volatility
Estimated call delta versus target delta
Strike distance above the current stock price
Scenario IV relationships
```

Example relationship checks:

```text
Volatile Whipsaw IV should usually be higher than the other scenario IVs.
Downtrend IV should usually exceed Sideways Choppy IV.
Strong Rally IV should not exceed Volatile Whipsaw IV.
```

## Important limitation

This is a tuning-recommendation scaffold only.

It does **not** yet edit the premium model.
It does **not** yet recalibrate from live option-chain data.
It does **not** yet replace the current Phase 2B premium model.

The next step after this passes is to make the premium model read tunable assumptions from a config file.

## How to test

Run this file in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_premium_model_tuning_check.py
```

Expected final result:

```text
Overall Phase 2D premium-model tuning status: PASS
```

A generated recommendation table may still contain rows marked REVIEW or TUNE. That means the model is giving us useful tuning guidance. It is not necessarily an installation failure.
