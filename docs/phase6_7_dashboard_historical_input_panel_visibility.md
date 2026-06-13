# Phase 6-7 — Dashboard historical input-panel visibility smoke test

This checkpoint verifies that the Phase 6-6 dashboard historical input-panel
helper is visible in the dashboard file.

It is add-only and does not apply another dashboard patch.

Validated behavior:

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown modes fall back to synthetic.
- Historical data is scenario input, not a forecast.
- The Phase 6-6 helper block is bounded and detectable.

Run:

`app\run_paid_simulator_phase6_7_dashboard_historical_input_panel_visibility_check.py`
