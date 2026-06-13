# Phase 6-11 — Dashboard end-to-end historical opt-in smoke test

This checkpoint verifies the historical-mode opt-in workflow after the Phase 6-9
runner-wiring helper.

It is add-only and makes no dashboard change.

Validated behavior:

- Synthetic scenarios remain the default.
- Imported historical data maps to historical_import only when explicitly selected.
- Unknown modes fall back to synthetic.
- None/missing mode falls back to synthetic.
- Historical data is scenario input, not a forecast.

Run:

`app\run_paid_simulator_phase6_11_dashboard_historical_opt_in_smoke_check.py`
