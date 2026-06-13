# Phase 3 Interactive Payoff Dashboard Tab

This package adds a Developer-view-only tab to the main paid simulator dashboard.

## Files

- `app/paid_simulator/config_form_app.py` — replaced to add the tab.
- `app/run_paid_simulator_phase3_dashboard_tab_check.py` — verifies the tab installation.
- `docs/paid_simulator_phase3_dashboard_tab.md` — this note.

## New dashboard tab

The tab is named:

`Phase 3 interactive payoff`

It is visible only in Developer view.

## Purpose

This tab exposes the first Phase 3 interactive graphical covered-call payoff prototype inside the main dashboard while keeping the customer dashboard isolated.

It provides:

- File-status checks for Phase 3 viewer and pipeline files.
- A button to run the Phase 3 interactive payoff pipeline.
- A button to open the standalone Phase 3 interactive payoff viewer.
- A display area for the saved payoff snapshot CSV when it exists.
- Links to open the Phase 3 snapshot HTML and report folder.

## Important limitation

The Phase 3 prototype is manual-input only. It does not yet use live ticker data or option-chain data.
