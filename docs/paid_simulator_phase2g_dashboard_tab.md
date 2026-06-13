# Phase 2G Model-Promotion Dashboard Tab

## Purpose

This package adds a Developer-view-only **Phase 2G model promotion** tab to the main paid-simulator dashboard.

The tab is an internal model-governance view. It helps inspect whether the adjusted premium model should remain a research model or become a candidate for controlled internal promotion.

## Files added or replaced

Replaced:

```text
app\paid_simulator\config_form_app.py
```

Added:

```text
app\run_paid_simulator_phase2g_dashboard_tab_check.py
docs\paid_simulator_phase2g_dashboard_tab.md
```

## What the tab shows

The Phase 2G tab shows:

```text
Phase 2G file status
Model-promotion plan text summary
Model-promotion plan table
Promotion-plan counts
Promotion-candidate filter
Phase 2F model-decision evidence
Phase 2E adjusted-payoff context
Phase 2D tuning context
Phase 2C validation context
Button to run the Phase 2G pipeline
Button to open the standalone Phase 2G viewer
Links to Phase 2G reports
```

## Customer-view protection

The Phase 2G tab is only included in Developer view. Customer view remains focused on the standard customer workflow.

## Test command

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2g_dashboard_tab_check.py
```

Expected result:

```text
PASS: The Developer-view-only Phase 2G model-promotion tab is installed and the Phase 2G outputs are present.
```

## Next step

After this passes, the next safe step is a Phase 2G integration-readiness checker.
