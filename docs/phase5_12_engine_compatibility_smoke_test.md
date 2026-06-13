# Phase 5-12 — Engine Compatibility Smoke Test After `price_paths.py` Promotion

## Purpose

Phase 5-12 verifies that the live promoted `app\price_paths.py` file still satisfies the engine-facing compatibility contract after Phase 5-11.

This checkpoint is intentionally conservative. It does not change the dashboard, and it does not patch additional core engine files.

## Guardrails

- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Unknown modes remain safe and should not break the engine path.
- `generate_price_paths(config)` remains present.
- No dashboard/customer workflow changes are introduced.

## Files added

```text
app\paid_simulator\phase5_engine_compatibility_smoke_test.py
app\run_paid_simulator_phase5_12_engine_compatibility_smoke_test_check.py
docs\phase5_12_engine_compatibility_smoke_test.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_12_engine_compatibility_smoke_test_rows.csv
outputs\tables\paid_simulator\phase5_12_engine_compatibility_smoke_test_summary.csv
outputs\reports\paid_simulator\phase5_12_engine_compatibility_smoke_test.json
outputs\reports\paid_simulator\phase5_12_engine_compatibility_smoke_test_report.txt
```

## Run command

```text
app\run_paid_simulator_phase5_12_engine_compatibility_smoke_test_check.py
```

Expected final line:

```text
Overall Phase 5-12 checkpoint status: PASS
```

## Next checkpoint

If Phase 5-12 passes, the next logical checkpoint is Phase 5-13 — simulator engine integration candidate. That should create a candidate for `app\simulator.py` before replacing the live file.
