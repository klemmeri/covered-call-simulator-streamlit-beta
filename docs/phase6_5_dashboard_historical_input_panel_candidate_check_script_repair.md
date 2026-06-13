# Phase 6-5 tolerant check-script repair

This repair replaces the Phase 6-5 check script:

`app\run_paid_simulator_phase6_5_dashboard_historical_input_panel_candidate_check.py`

The candidate module is already writing the caution information, but the previous
check script was too brittle about one exact internal field name. This repaired
check validates the actual business requirement instead:

- synthetic mode remains the default;
- historical mode remains explicit opt-in only;
- unknown modes fall back to synthetic;
- historical data is described as scenario input, not a forecast;
- the contract CSV contains the expected customer-facing mode labels and caution.

No dashboard code is changed by this repair.
