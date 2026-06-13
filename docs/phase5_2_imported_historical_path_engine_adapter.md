# Phase 5-2 — Imported Historical Path Engine Adapter

## Purpose

Phase 5-2 creates an adapter between the imported historical path artifacts from Phase 4 and the paid simulator engine. It does not patch the main simulator engine yet. The goal is to create a clean, engine-ready table that later Phase 5 checkpoints can pass into the actual simulation flow.

## Files added

```text
app\paid_simulator\phase5_imported_historical_path_engine_adapter.py
app\run_paid_simulator_phase5_2_imported_historical_path_engine_adapter_check.py
docs\phase5_2_imported_historical_path_engine_adapter.md
```

## Inputs

The adapter uses the best available source in this order:

1. `outputs\tables\paid_simulator\phase4_4_historical_price_path.csv`
2. `inputs\market_data\sample_underlying_prices.csv`
3. Built-in one-row fallback for checkpoint stability

## Outputs

```text
outputs\tables\paid_simulator\phase5_2_engine_ready_historical_path.csv
outputs\tables\paid_simulator\phase5_2_engine_ready_historical_path_summary.csv
outputs\reports\paid_simulator\phase5_2_imported_historical_path_engine_adapter.json
outputs\reports\paid_simulator\phase5_2_imported_historical_path_engine_adapter_report.txt
```

## Engine-ready table columns

```text
path_id
engine_step
source_date
underlying_price
simple_return
source_mode
engine_adapter_mode
usable_by_engine
```

## Important design constraint

Synthetic simulation mode remains preserved. This checkpoint prepares imported historical data for the engine, but does not remove or replace synthetic path generation.

## Dashboard status

No dashboard change is made in Phase 5-2.

## Release decision

```text
PHASE5_2_IMPORTED_HISTORICAL_PATH_ENGINE_ADAPTER_CREATED_NO_DASHBOARD_CHANGE
```
