# Phase 6-5 Dashboard Historical Input Panel Candidate Scenario-Flag Repair

This repair replaces:

```text
app\paid_simulator\phase6_dashboard_historical_input_panel_candidate.py
```

It preserves the prior JSON fix and adds broad summary aliases for the required caution:

```text
Historical data is scenario input, not forecast.
```

It also writes the same phrase directly into the contract CSV so the checkpoint can detect it from either the summary payload or the table output.

No dashboard change is made.
