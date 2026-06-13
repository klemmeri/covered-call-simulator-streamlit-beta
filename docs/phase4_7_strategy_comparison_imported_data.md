# Phase 4-7 — Strategy Comparison Using Imported Data

## Purpose

Phase 4-7 connects the Phase 4 imported-data scaffold to a simple strategy comparison layer.

It compares:

1. Buy-and-hold
2. Covered-call scaffold using the best imported option-chain candidate from Phase 4-5

This checkpoint is not intended to be the final production simulator engine. It is a controlled bridge between imported market data and later strategy-comparison modeling.

## Files added

```text
app\paid_simulator\phase4_strategy_comparison_imported_data.py
app\run_paid_simulator_phase4_7_imported_data_strategy_comparison_check.py
docs\phase4_7_strategy_comparison_imported_data.md
```

## Inputs

The module reads these prior Phase 4 artifacts when available:

```text
outputs\tables\paid_simulator\phase4_4_historical_price_path.csv
outputs\tables\paid_simulator\phase4_5_best_covered_call_candidate.csv
```

If either file is missing or empty, the module uses conservative sample fallback values so the scaffold remains testable.

## Outputs

```text
outputs\tables\paid_simulator\phase4_7_imported_data_strategy_comparison_rows.csv
outputs\tables\paid_simulator\phase4_7_imported_data_strategy_comparison_summary.csv
outputs\reports\paid_simulator\phase4_7_imported_data_strategy_comparison.json
outputs\reports\paid_simulator\phase4_7_imported_data_strategy_comparison_report.txt
```

## Design notes

The covered-call calculation is deliberately simple:

- 100 shares are assumed.
- One option contract is assumed.
- Imported option premium is treated as income.
- Covered-call upside is capped at the imported strike.
- Buy-and-hold is calculated from first to last imported historical price.

This is a scaffold for validation and reporting, not yet the final paid production model.

## Dashboard status

No dashboard file is changed by this checkpoint.

## Check script

Run:

```text
app\run_paid_simulator_phase4_7_imported_data_strategy_comparison_check.py
```

Expected final line:

```text
Overall Phase 4-7 checkpoint status: PASS
```
