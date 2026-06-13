# Phase 2E Premium-Adjustment Dashboard Tab

## Purpose

This package adds a Developer-view-only **Phase 2E adjustment** tab to the main paid-simulator dashboard.

The tab lets the developer inspect the controlled premium-model adjustment inside the main dashboard without exposing it to customer view.

## Files added or replaced

Replaced:

```text
app\paid_simulator\config_form_app.py
```

Added:

```text
app\run_paid_simulator_phase2e_dashboard_tab_check.py
docs\paid_simulator_phase2e_dashboard_tab.md
```

## What the tab shows

The Phase 2E adjustment tab shows:

```text
Phase 2E file status
Adjustment summary
Adjusted premium estimates
Adjusted payoff comparison
Original premium context
Phase 2D tuning context
Buttons to run the Phase 2E pipeline
Button to open the standalone Phase 2E adjustment viewer
Links to Phase 2E reports
```

## Customer-view protection

The Phase 2E adjustment tab is only included in Developer view. Customer view remains focused on the normal product workflow.

## Test command

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2e_dashboard_tab_check.py
```

Expected result:

```text
PASS: The Developer-view-only Phase 2E adjustment tab is installed and the Phase 2E outputs are present.
```

## Next step

After this passes, the next safe step is a Phase 2E integration-readiness checker.
