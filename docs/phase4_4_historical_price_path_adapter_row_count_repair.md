# Phase 4-4 Historical Price Path Adapter Row-Count Repair

This repair replaces:

```text
app\paid_simulator\phase4_historical_price_path_adapter.py
```

Purpose:

- Preserve the required `build_phase4_4_summary()` function.
- Preserve the default historical path ID `historical_path_001`.
- Explicitly report the row-count fields expected by the Phase 4-4 checkpoint:
  - `underlying_price_input_rows`
  - `historical_path_output_rows`
- Avoid dataclasses for Python 3.13 dynamic-import compatibility.
- Make no dashboard change.

Run the existing checkpoint script after installing:

```text
app\run_paid_simulator_phase4_4_historical_price_path_adapter_check.py
```

Expected final line:

```text
Overall Phase 4-4 checkpoint status: PASS
```
