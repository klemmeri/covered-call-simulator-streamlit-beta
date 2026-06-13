# Phase 6-10 — Dashboard end-to-end synthetic-default regression

This checkpoint verifies that the dashboard still defaults to the synthetic
workflow after the historical-mode input-panel and runner-wiring helpers.

It is add-only and makes no dashboard change.

Validated behavior:

- Synthetic scenarios remain the default.
- The default runner mode is synthetic.
- Historical mode is not selected by default.
- Historical mode remains explicit opt-in only.
- Unknown modes fall back to synthetic.
- Historical data is scenario input, not a forecast.

Run:

`app\run_paid_simulator_phase6_10_dashboard_synthetic_default_regression_check.py`
