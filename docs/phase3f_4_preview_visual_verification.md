# Phase 3F-4 — Protected Customer-Preview Visual Verification

## Purpose

Phase 3F-4 verifies the protected customer-preview route after the Phase 3F-3 dashboard route passed.

This checkpoint does not enable the preview in the ordinary Customer view. It verifies that the protected preview route is ready for visual inspection and remains behind the intended guardrails.

## Added files

```text
app\run_paid_simulator_phase3f_4_preview_visual_check.py
docs\phase3f_4_preview_visual_verification.md
```

## Files not modified

```text
app\paid_simulator\config_form_app.py
```

## Check script

Run:

```text
app\run_paid_simulator_phase3f_4_preview_visual_check.py
```

Expected final line:

```text
Overall Phase 3F-4 checkpoint status: PASS
```

## Outputs

```text
outputs\reports\paid_simulator\phase3f_4_preview_visual_checkpoint_report.txt
outputs\reports\paid_simulator\phase3f_4_preview_visual_checkpoint.json
outputs\tables\paid_simulator\phase3f_4_preview_visual_checklist.csv
outputs\reports\paid_simulator\phase3f_4_browser_preview_checklist.md
```

## Manual visual check

After the script passes, run:

```text
streamlit run app\paid_simulator\config_form_app.py
```

Confirm:

1. The dashboard opens without a red traceback.
2. The ordinary Customer view does not show Phase 3F preview controls.
3. Developer view still contains Phase 3D and Phase 3E material.
4. The protected Phase 3F preview route/helper remains available.
5. Customer-facing labels and risk/guardrail language are visible or staged in the route model.
