# Phase 4-4 Consolidated Historical Path Adapter Repair

This repair replaces `app\paid_simulator\phase4_historical_price_path_adapter.py` with a consolidated version that preserves the checkpoint-facing function name and all expected summary fields.

It includes:

- `build_phase4_4_summary()`
- `PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_READY`
- `PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_CREATED_NO_DASHBOARD_CHANGE`
- `dashboard_changed = False`
- `no_dashboard_change = False`
- `mode = historical_import`
- `input_mode = historical_import`
- `underlying_price_input_rows`
- `historical_path_output_rows`
- default path ID `historical_path_001`

No dashboard file is changed.
