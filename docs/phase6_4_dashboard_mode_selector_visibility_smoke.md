# Phase 6-4 — Dashboard Mode Selector Visibility Smoke Test

This checkpoint verifies that the guarded Phase 6 dashboard mode-selector helper introduced in Phase 6-3 is present and readable.

It does not apply another dashboard patch.

## Guardrails

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown modes fall back to synthetic.
- Historical data is presented as scenario input, not a forecast.
- No public/customer workflow change is introduced here.

## Files Added

- `app/paid_simulator/phase6_dashboard_mode_selector_visibility_smoke.py`
- `app/run_paid_simulator_phase6_4_dashboard_mode_selector_visibility_check.py`
- `docs/phase6_4_dashboard_mode_selector_visibility_smoke.md`

## Check Script

Run:

```text
app\run_paid_simulator_phase6_4_dashboard_mode_selector_visibility_check.py
```

Expected final line:

```text
Overall Phase 6-4 checkpoint status: PASS
```
