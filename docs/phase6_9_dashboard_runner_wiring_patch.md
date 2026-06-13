# Phase 6-9 — Controlled dashboard runner wiring patch

This checkpoint appends a bounded passive helper block to:

`app\paid_simulator\config_form_app.py`

The helper maps dashboard data-mode labels to internal runner modes:

- Synthetic scenarios -> synthetic
- Imported historical data -> historical_import
- Unknown mode -> synthetic fallback

Preserved behavior:

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Historical data is scenario input, not a forecast.
- No customer workflow change is made by this helper.

Run:

`app\run_paid_simulator_phase6_9_dashboard_runner_wiring_patch_check.py`
