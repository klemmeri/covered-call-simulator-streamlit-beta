# Phase 5-3 — Controlled Historical Path Engine Hook

## Purpose

Phase 5-3 creates a controlled hook contract for using imported historical price paths inside the simulator engine.

This checkpoint does **not** replace the engine and does **not** change the dashboard. It creates an explicit contract showing how a future engine integration should select between:

- the current synthetic-path mode, and
- imported historical-path mode.

## Design rule

Synthetic simulation remains the default until historical mode is explicitly selected.

This prevents accidental changes to existing simulator behavior while still moving the project toward real-data integration.

## Files added

```text
app\paid_simulator\phase5_controlled_historical_path_engine_hook.py
app\run_paid_simulator_phase5_3_controlled_engine_hook_check.py
docs\phase5_3_controlled_historical_path_engine_hook.md
```

## Inputs

The module reads the Phase 5-2 engine-ready path when available:

```text
outputs\tables\paid_simulator\phase5_2_engine_ready_historical_path.csv
```

## Outputs

```text
outputs\tables\paid_simulator\phase5_3_historical_path_engine_hook_contract.csv
outputs\tables\paid_simulator\phase5_3_historical_path_engine_hook_preview.csv
outputs\tables\paid_simulator\phase5_3_historical_path_engine_hook_summary.csv
outputs\reports\paid_simulator\phase5_3_historical_path_engine_hook.json
outputs\reports\paid_simulator\phase5_3_historical_path_engine_hook_report.txt
```

## Release decision

```text
PHASE5_3_ENGINE_HOOK_CONTRACT_CREATED_NO_DASHBOARD_CHANGE
```

## Next checkpoint

Phase 5-4 should patch the engine in a controlled way so it can call the historical-path hook while preserving synthetic-path behavior as the default.
