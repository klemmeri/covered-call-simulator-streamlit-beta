# Phase 3D Dashboard Tab Marker Fix

This small fix updates only the Phase 3D dashboard-tab checker.

## Reason

The previous checker required the exact source marker:

```text
phase3d_integrated_payoff_overlay_viewer
```

Some dashboard builds reference the Phase 3D standalone viewer through the launcher filename or through user-facing text rather than that exact internal string. This caused a false REVIEW even though the Phase 3D tab, pipeline marker, source files, documentation, and context outputs were present.

## Changed file

```text
app\run_paid_simulator_phase3d_dashboard_tab_check.py
```

## Expected result

After installing this fix and rerunning the checker, the expected result is:

```text
Overall Phase 3D dashboard-tab status: PASS
```

or:

```text
Overall Phase 3D dashboard-tab status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```

The optional snapshot review is acceptable until a Phase 3D setup has been saved from the standalone viewer.
