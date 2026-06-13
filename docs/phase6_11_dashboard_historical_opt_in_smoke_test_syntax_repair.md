# Phase 6-11 syntax repair

This repair replaces the malformed Phase 6-11 check script and also refreshes the passive support module.

Replaced files:

- `app\run_paid_simulator_phase6_11_dashboard_historical_opt_in_smoke_check.py`
- `app\paid_simulator\phase6_dashboard_historical_opt_in_smoke_test.py`

No dashboard code is changed.

Validated behavior:

- Synthetic scenarios remain the default.
- Imported historical data maps to `historical_import` only when explicitly selected.
- Unknown modes fall back to synthetic.
- None/missing mode falls back to synthetic.
- Historical data is scenario input, not a forecast.
