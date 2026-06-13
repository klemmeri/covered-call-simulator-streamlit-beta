# Phase 5-17 — Controlled Historical Runner Promotion

## Purpose

Phase 5-17 promotes the Phase 5-16 historical-import engine-runner candidate into a controlled runner contract.

This is still not a dashboard integration step. The customer-facing workflow is unchanged.

## Guardrails

- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- No dashboard change is made.
- No additional live core engine file is replaced in this checkpoint.
- The promoted runner contract is written as an artifact for later regression testing and dashboard integration.

## Files added

```text
app\paid_simulator\phase5_controlled_historical_runner_promotion.py
app\run_paid_simulator_phase5_17_controlled_historical_runner_promotion_check.py
docs\phase5_17_controlled_historical_runner_promotion.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_17_promoted_historical_runner_contract.csv
outputs\tables\paid_simulator\phase5_17_promoted_historical_runner_path_preview.csv
outputs\tables\paid_simulator\phase5_17_controlled_historical_runner_promotion_summary.csv
outputs\reports\paid_simulator\phase5_17_controlled_historical_runner_promotion.json
outputs\reports\paid_simulator\phase5_17_controlled_historical_runner_promotion_report.txt
```

## Check script

Run:

```text
app\run_paid_simulator_phase5_17_controlled_historical_runner_promotion_check.py
```

Expected final line:

```text
Overall Phase 5-17 checkpoint status: PASS
```

## Next checkpoint

Phase 5-18 should perform a historical-mode engine regression test using the promoted controlled runner contract.
