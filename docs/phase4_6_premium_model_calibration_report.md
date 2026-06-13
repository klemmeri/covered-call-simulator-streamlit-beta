# Phase 4-6 — Premium-Model Calibration Report

## Purpose

Phase 4-6 adds a scaffold calibration report that compares imported option-chain observed premiums with a simple model-estimated premium.

This is not a production option-pricing model and does not replace the existing paid simulator premium model. It provides a stable bridge between imported option-chain data and later model-improvement work.

## Files added

```text
app\paid_simulator\phase4_premium_model_calibration_report.py
app\run_paid_simulator_phase4_6_premium_model_calibration_check.py
docs\phase4_6_premium_model_calibration_report.md
```

## Inputs used

The module first attempts to use the best candidate produced by Phase 4-5:

```text
outputs\tables\paid_simulator\phase4_5_best_covered_call_candidate.csv
```

If that file is unavailable or empty, it falls back to:

```text
inputs\market_data\sample_option_chain.csv
```

## Outputs created

```text
outputs\tables\paid_simulator\phase4_6_premium_model_calibration_rows.csv
outputs\tables\paid_simulator\phase4_6_premium_model_calibration_summary.csv
outputs\reports\paid_simulator\phase4_6_premium_model_calibration_report.json
outputs\reports\paid_simulator\phase4_6_premium_model_calibration_report.txt
```

## What is measured

The report creates one or more calibration rows with:

- observed premium
- model-estimated premium
- premium error
- absolute premium error
- percentage premium error
- calibration note

## Design limitation

The scaffold model is deliberately simple. It is intended to verify the data path and calibration-report structure, not to claim that the simulator has been fully calibrated to live option-chain data.

## Dashboard status

No dashboard changes are made in this phase.

## Check script

Run:

```text
app\run_paid_simulator_phase4_6_premium_model_calibration_check.py
```

Expected final line:

```text
Overall Phase 4-6 checkpoint status: PASS
```
