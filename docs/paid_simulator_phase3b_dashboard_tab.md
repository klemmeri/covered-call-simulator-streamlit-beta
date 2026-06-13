# Phase 3B Scenario-Overlay Dashboard Tab

This package adds a Developer-view-only tab to the main paid simulator dashboard.

## Files

- `app/paid_simulator/config_form_app.py` - replaced to add the tab.
- `app/run_paid_simulator_phase3b_dashboard_tab_check.py` - verifies the tab installation.
- `docs/paid_simulator_phase3b_dashboard_tab.md` - this note.

The package also includes the Phase 3B scenario-overlay model, viewer, and pipeline files so the dashboard tab has the files it expects.

## New dashboard tab

The tab is named:

`Phase 3B scenario overlay`

It is visible only in Developer view.

## Purpose

This tab brings the standalone Phase 3B scenario-overlay diagnostics into the main dashboard. It lets us inspect modeled stress-test outcomes for the interactive covered-call payoff setup without exposing unfinished controls to customer view.

## What the tab shows

- Phase 3B file status.
- Button to run the Phase 3B scenario-overlay pipeline.
- Button to open the standalone Phase 3B scenario-overlay viewer.
- Scenario-overlay summary text.
- Scenario-overlay table and relative-result chart.
- Links to the Phase 3B HTML and text reports.

## Important limitation

The scenario overlay is modeled and diagnostic. It is not a forecast, not live data, and not a trade recommendation.
