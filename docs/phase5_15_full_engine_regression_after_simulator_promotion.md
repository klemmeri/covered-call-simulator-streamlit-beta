# Phase 5-15 — Full Engine Regression After Simulator Promotion

## Purpose

Phase 5-15 verifies that the Phase 5-11 `price_paths.py` promotion and Phase 5-14 `simulator.py` promotion have not broken the protected operating contract of the Covered Call Simulator.

This checkpoint is add-only. It does not patch the dashboard and does not replace additional core engine files.

## Regression contract

The checkpoint confirms that:

- synthetic mode remains the default;
- historical-import mode remains explicit only;
- unknown modes remain fallback-safe;
- no dashboard change is required;
- no customer workflow change is required;
- the expected core engine files are present.

## Files added

```text
app\paid_simulator\phase5_full_engine_regression_after_simulator_promotion.py
app\run_paid_simulator_phase5_15_full_engine_regression_check.py
docs\phase5_15_full_engine_regression_after_simulator_promotion.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_15_engine_regression_file_status.csv
outputs\tables\paid_simulator\phase5_15_engine_regression_contract.csv
outputs\tables\paid_simulator\phase5_15_engine_regression_summary.csv
outputs\reports\paid_simulator\phase5_15_engine_regression_after_simulator_promotion.json
outputs\reports\paid_simulator\phase5_15_engine_regression_after_simulator_promotion_report.txt
```

## Next recommended checkpoint

If Phase 5-15 passes, the next recommended checkpoint is Phase 5-16 — Historical import engine-runner candidate.
