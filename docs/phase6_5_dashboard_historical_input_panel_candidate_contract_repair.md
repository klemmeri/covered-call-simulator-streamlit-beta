# Phase 6-5 Dashboard Historical Input Panel Candidate Contract Repair

This repair replaces the Phase 6-5 candidate module with a consolidated version that preserves the JSON export fix and adds explicit checkpoint-facing summary fields.

It does not change the dashboard.

The repaired module explicitly records:

- synthetic mode remains the default
- historical-import mode remains explicit opt-in only
- unknown modes fall back to synthetic
- historical data is a scenario input, not a forecast
- the input-panel contract row count
- no dashboard patch was applied by this checkpoint

Run:

```text
app\run_paid_simulator_phase6_5_dashboard_historical_input_panel_candidate_check.py
```
