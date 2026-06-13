# Phase 6-3 — Controlled Dashboard Mode Selector Patch

This checkpoint introduces the controlled dashboard mode-selector integration block for the paid simulator.

The design remains deliberately conservative:

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown modes fall back to synthetic.
- Historical data is described as scenario input, not a forecast.
- The patch appends a guarded helper function to `app\paid_simulator\config_form_app.py` rather than rewriting the full dashboard.

## Files added

```text
app\paid_simulator\phase6_dashboard_mode_selector_patch.py
app\run_paid_simulator_phase6_3_dashboard_mode_selector_patch_check.py
docs\phase6_3_dashboard_mode_selector_patch.md
```

## Dashboard file touched by the check script

```text
app\paid_simulator\config_form_app.py
```

The check script appends a marked Phase 6-3 integration block only if the marker is not already present.

## Outputs

```text
outputs\tables\paid_simulator\phase6_3_dashboard_mode_selector_modes.csv
outputs\tables\paid_simulator\phase6_3_dashboard_mode_selector_patch_summary.csv
outputs\reports\paid_simulator\phase6_3_dashboard_mode_selector_patch.json
outputs\reports\paid_simulator\phase6_3_dashboard_mode_selector_patch_report.txt
```

## Next checkpoint

After Phase 6-3 passes, the next checkpoint should be Phase 6-4 — Dashboard mode selector visibility smoke test.
