# Phase 3C Rich Payoff Dashboard Tab

This package adds a Developer-view-only Phase 3C tab to the main paid simulator dashboard.

## Files

- `app/paid_simulator/config_form_app.py` - replaced to add the tab.
- `app/run_paid_simulator_phase3c_dashboard_tab_check.py` - verifies the tab installation.
- `docs/paid_simulator_phase3c_dashboard_tab.md` - this note.

The package also includes the standalone Phase 3C rich payoff viewer and pipeline checker so the dashboard tab has the files it expects.

## New dashboard tab

The tab is named:

`Phase 3C rich payoff`

It is visible only in Developer view.

## Purpose

This tab brings the richer graphical payoff prototype into the main dashboard as a developer diagnostic panel.

It also repairs the Developer-view tab list so the Phase 3 and Phase 3B tabs are explicitly present in the tab list before adding Phase 3C.

## What the tab shows

- Phase 3C file status.
- Button to run the Phase 3C rich payoff pipeline.
- Button to open the standalone Phase 3C rich payoff viewer.
- Saved setup details if a Phase 3C snapshot exists.
- Saved scenario overlay from the Phase 3C snapshot.
- Links to Phase 3C snapshot and pipeline reports.

## Important limitation

Phase 3C is still a prototype. It uses manual inputs, not live market data. It remains Developer-view only until the graph, validation, and customer-facing warnings are polished.
