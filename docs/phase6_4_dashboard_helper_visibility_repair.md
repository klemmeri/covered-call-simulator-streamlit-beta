# Phase 6-4 Dashboard Helper Visibility Repair

This narrow repair appends the dashboard helper function expected by the Phase 6-4 visibility smoke test.

## Repair target

`app\paid_simulator\config_form_app.py`

## Issue

The dashboard contained the Phase 6-3 ready marker, but the visibility smoke test could not find the expected helper function:

`phase6_3_resolve_dashboard_data_mode`

## Repair behavior

The repair appends a passive helper block that preserves the Phase 6 dashboard-mode contract:

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown or blank selections fall back to synthetic mode.
- Historical data is described as scenario input, not a forecast.

## Run order

1. Run `app\run_paid_simulator_phase6_4_dashboard_helper_visibility_repair.py`.
2. Then rerun `app\run_paid_simulator_phase6_4_dashboard_mode_selector_visibility_check.py`.

Expected final line after the visibility check:

`Overall Phase 6-4 checkpoint status: PASS`
