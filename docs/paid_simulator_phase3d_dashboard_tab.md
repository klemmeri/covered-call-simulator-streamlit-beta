# Phase 3D Integrated Overlay Dashboard Tab

Date: 2026-06-12

This package adds a Developer-view-only **Phase 3D integrated overlay** tab to the main Covered Call Strategy Stress Test dashboard.

## Purpose

Phase 3D combines two previously separate prototype layers:

1. The richer Phase 3C covered-call payoff graph.
2. The Phase 3B scenario-overlay stress test.

The tab keeps the workflow internal while the graphical interface is still being tested.

## Files Added or Replaced

Replaced:

- `app/paid_simulator/config_form_app.py`

Added or included:

- `app/run_paid_simulator_phase3d_dashboard_tab_check.py`
- `app/paid_simulator/phase3d_integrated_payoff_overlay_viewer.py`
- `app/run_paid_simulator_phase3d_integrated_overlay_viewer.py`
- `app/run_paid_simulator_phase3d_integrated_overlay_viewer_check.py`
- `app/run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py`
- `docs/paid_simulator_phase3d_dashboard_tab.md`

## Dashboard Behavior

The new tab appears only in Developer view:

- `Phase 3D integrated overlay`

It does not appear in Customer view.

The tab provides:

- Phase 3D file-status diagnostics.
- A button to run the Phase 3D integrated overlay pipeline.
- A button to open the standalone Phase 3D viewer.
- Saved Phase 3D snapshot display when available.
- Phase 3B scenario-overlay context.
- Report-opening tools.
- Developer notes.

## Validation

Run:

```text
app/run_paid_simulator_phase3d_dashboard_tab_check.py
```

Expected result:

```text
Overall Phase 3D dashboard-tab status: PASS
```

or:

```text
Overall Phase 3D dashboard-tab status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable until a setup is saved from the Phase 3D viewer.
