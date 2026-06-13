# Phase 4-4 Repair — Historical Price Path Adapter

This repair replaces only:

`app\paid_simulator\phase4_historical_price_path_adapter.py`

The prior module used a dataclass. The Phase 4-4 checkpoint imports modules dynamically with `importlib.util.spec_from_file_location`. Under Python 3.13, the dataclass decorator can fail in this dynamic-import pattern when the module is not present in `sys.modules` during execution.

The repair removes the dataclass dependency and returns/serializes a plain dictionary instead. The functional behavior is unchanged:

- Load the underlying-price CSV scaffold.
- Normalize and validate OHLCV rows.
- Build a single historical price path.
- Write the Phase 4-4 CSV, JSON, and text-report outputs.
- Make no dashboard changes.

After installing this repair, rerun:

`app\run_paid_simulator_phase4_4_historical_price_path_adapter_check.py`

Expected final line:

`Overall Phase 4-4 checkpoint status: PASS`
