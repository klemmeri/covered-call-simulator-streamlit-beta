# Phase 6-6 — Controlled dashboard historical input-panel patch

This checkpoint appends a bounded helper block to:

`app\paid_simulator\config_form_app.py`

The helper is passive and guarded. It does not change the default customer workflow.

Preserved behavior:

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown modes fall back to synthetic.
- Historical data is described as scenario input, not a forecast.

Run:

`app\run_paid_simulator_phase6_6_dashboard_historical_input_panel_patch_check.py`
