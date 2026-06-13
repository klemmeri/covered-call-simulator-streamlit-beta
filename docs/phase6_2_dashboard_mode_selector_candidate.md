# Phase 6-2 — Dashboard Mode Selector Candidate

This checkpoint defines the paid-dashboard mode-selection contract before any live dashboard patch is made.

## Purpose

Phase 6 begins the dashboard/customer workflow integration work. Before patching `app\paid_simulator\config_form_app.py`, this checkpoint defines the mode selector that will eventually let the paid dashboard distinguish between:

1. **Synthetic scenarios** — the current default workflow.
2. **Imported historical data** — an explicit opt-in workflow using prepared historical-path artifacts.

## Safety rules

- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Unknown mode values fall back to synthetic.
- Historical results are examples based on the selected input path, not forecasts.
- No dashboard file is modified in this checkpoint.

## Files added

```text
app\paid_simulator\phase6_dashboard_mode_selector_candidate.py
app\run_paid_simulator_phase6_2_dashboard_mode_selector_candidate_check.py
docs\phase6_2_dashboard_mode_selector_candidate.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase6_2_dashboard_mode_selector_modes.csv
outputs\tables\paid_simulator\phase6_2_dashboard_mode_selector_guardrails.csv
outputs\tables\paid_simulator\phase6_2_dashboard_mode_selector_customer_copy.csv
outputs\tables\paid_simulator\phase6_2_dashboard_mode_selector_candidate_summary.csv
outputs\reports\paid_simulator\phase6_2_dashboard_mode_selector_candidate.json
outputs\reports\paid_simulator\phase6_2_dashboard_mode_selector_candidate_report.txt
```

## Next checkpoint

Phase 6-3 should create a dashboard patch candidate or a controlled dashboard patch for `config_form_app.py`, depending on how much risk is acceptable. The preferred approach is a candidate or narrow controlled patch that adds the selector without disturbing the existing paid workflow.
