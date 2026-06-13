# Phase 3D Integrated Viewer Marker Fix

This small package replaces only:

```text
app\run_paid_simulator_phase3d_integrated_overlay_viewer_check.py
```

The prior checker was too strict. It required exact source text markers such as `Covered-call payoff` and `Buy-and-hold`, even though the viewer may use equivalent labels or column names such as `covered_call_pl` and `buy_and_hold_pl`.

This fix keeps the same file and output checks, but accepts reasonable wording variations for those viewer markers.

Expected result after installing and rerunning the checker:

```text
Overall Phase 3D integrated viewer status: PASS
```

or, if no saved snapshot exists yet:

```text
Overall Phase 3D integrated viewer status: PASS WITH OPTIONAL SNAPSHOT REVIEW
```
