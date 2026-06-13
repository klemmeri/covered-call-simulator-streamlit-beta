# Phase 2F Model-Decision Dashboard Tab

## Purpose

This package adds a Developer-view-only **Phase 2F model decision** tab to the main paid-simulator dashboard.

The tab consolidates the model-development evidence from the original premium-aware model, the adjusted-premium model, validation checks, tuning recommendations, and the Phase 2F model-decision summary.

## Files added or replaced

Replaced:

```text
app\paid_simulator\config_form_app.py
```

Added:

```text
app\run_paid_simulator_phase2f_dashboard_tab_check.py
docs\paid_simulator_phase2f_dashboard_tab.md
```

## What the tab shows

The Phase 2F model-decision tab shows:

```text
Phase 2F file status
Model-decision text summary
Model-decision table
Decision-count table
Promotion-candidate filter
Original premium-aware payoff context
Premium-model validation context
Phase 2D tuning context
Phase 2E adjusted-payoff context
Buttons to run the Phase 2F pipeline
Button to open the standalone Phase 2F viewer
Links to Phase 2F reports
```

## Customer-view protection

The Phase 2F tab is only included in Developer view. Customer view remains focused on the standard product workflow.

## Test command

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_dashboard_tab_check.py
```

Expected result:

```text
PASS: The Developer-view-only Phase 2F model-decision tab is installed and the Phase 2F outputs are present.
```

## Next step

After this passes, the next safe step is a Phase 2F integration-readiness checker.
