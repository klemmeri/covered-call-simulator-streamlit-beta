# Phase 5-4 — Controlled Historical Path Engine Patch

## Purpose

Phase 5-4 creates a controlled, opt-in engine integration layer for imported historical price paths.

This is the first step that behaves like an engine patch, but it remains deliberately conservative:

- synthetic mode remains the default;
- historical-import mode must be explicitly requested;
- the Streamlit dashboard is not changed;
- the main simulator engine is not made dependent on imported data yet.

## Added files

```text
app\paid_simulator\phase5_controlled_engine_patch_historical_paths.py
app\run_paid_simulator_phase5_4_controlled_engine_patch_check.py
docs\phase5_4_controlled_engine_patch_historical_paths.md
```

## Inputs

The patch uses the best available historical path source:

```text
outputs\tables\paid_simulator\phase5_2_engine_ready_historical_path.csv
```

If unavailable, it falls back to:

```text
outputs\tables\paid_simulator\phase4_4_historical_price_path.csv
inputs\market_data\sample_underlying_prices.csv
```

If historical data cannot be read safely, the patch reverts to a small deterministic synthetic placeholder path.

## Outputs

```text
outputs\tables\paid_simulator\phase5_4_controlled_engine_patched_path.csv
outputs\tables\paid_simulator\phase5_4_controlled_engine_patch_summary.csv
outputs\reports\paid_simulator\phase5_4_controlled_engine_patch_historical_paths.json
outputs\reports\paid_simulator\phase5_4_controlled_engine_patch_historical_paths_report.txt
```

## Design rule

This phase is not a dashboard feature. It is an internal engine-integration checkpoint. Historical mode is opt-in and controlled.

## Check script

Run:

```text
app\run_paid_simulator_phase5_4_controlled_engine_patch_check.py
```

Expected final line:

```text
Overall Phase 5-4 checkpoint status: PASS
```
