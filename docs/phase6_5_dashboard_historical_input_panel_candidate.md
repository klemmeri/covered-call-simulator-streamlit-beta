# Phase 6-5 — Dashboard Historical-Mode Input Panel Candidate

## Purpose

Phase 6-5 defines the candidate paid-dashboard input-panel contract for imported historical data.

This is intentionally add-only. It does not patch `app\paid_simulator\config_form_app.py`.

## Guardrails

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown or invalid mode selections fall back to synthetic mode.
- Historical data is presented as scenario input, not as a forecast.
- Missing historical or option-chain inputs must not break the existing synthetic workflow.

## Files added

- `app\paid_simulator\phase6_dashboard_historical_input_panel_candidate.py`
- `app\run_paid_simulator_phase6_5_dashboard_historical_input_panel_candidate_check.py`
- `docs\phase6_5_dashboard_historical_input_panel_candidate.md`

## Outputs created

- `outputs\tables\paid_simulator\phase6_5_dashboard_historical_input_panel_contract.csv`
- `outputs\tables\paid_simulator\phase6_5_dashboard_historical_input_panel_summary.csv`
- `outputs\reports\paid_simulator\phase6_5_dashboard_historical_input_panel_candidate.json`
- `outputs\reports\paid_simulator\phase6_5_dashboard_historical_input_panel_candidate_report.txt`

## Expected checkpoint result

`Overall Phase 6-5 checkpoint status: PASS`

## Next checkpoint

Phase 6-6 should be a controlled dashboard historical input panel patch.
