# Phase 6-8 — Dashboard historical-mode runner wiring candidate

This checkpoint defines the dashboard-to-runner wiring contract before applying
a live dashboard runner patch.

It is add-only and makes no dashboard change.

Validated behavior:

- Synthetic scenarios map to the synthetic runner mode.
- Imported historical data maps to historical_import.
- Unknown dashboard modes fall back to synthetic.
- Historical data remains scenario input, not a forecast.
- Synthetic mode remains the default.
- Historical mode remains explicit opt-in only.

Run:

`app\run_paid_simulator_phase6_8_dashboard_historical_runner_wiring_candidate_check.py`
