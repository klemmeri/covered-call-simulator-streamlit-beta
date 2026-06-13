# Phase 5-6 — Main Engine Integration Plan

## Purpose

Phase 5-6 creates a planning artifact for integrating the Phase 5 imported-data work into the real Covered Call Simulator engine.

This checkpoint is intentionally add-only. It does not patch the simulator engine, does not change the dashboard, and does not change the public customer workflow.

## Why this checkpoint exists

The prior Phase 5 checkpoints created controlled artifacts for historical paths and option-chain premiums. Before patching core simulator files, the project needs a clear map of where the integration should occur and what regression guards are required.

## Outputs

This checkpoint writes:

- `outputs/tables/paid_simulator/phase5_6_engine_file_status.csv`
- `outputs/tables/paid_simulator/phase5_6_prior_artifact_status.csv`
- `outputs/tables/paid_simulator/phase5_6_engine_integration_touchpoints.csv`
- `outputs/tables/paid_simulator/phase5_6_recommended_patch_order.csv`
- `outputs/tables/paid_simulator/phase5_6_main_engine_integration_plan_summary.csv`
- `outputs/reports/paid_simulator/phase5_6_main_engine_integration_plan.json`
- `outputs/reports/paid_simulator/phase5_6_main_engine_integration_plan_report.txt`

## Design rules

- Synthetic mode remains the default.
- Historical-import mode must remain explicit only.
- No dashboard change occurs in this checkpoint.
- No engine patch occurs in this checkpoint.
- Future regime or market-data inputs should be treated as scenario guidance, not market oracles.

## Recommended next checkpoint

Phase 5-7 should add a synthetic-default regression guard before patching the actual simulator engine. This reduces the chance that imported-data integration changes the existing simulator behavior.
