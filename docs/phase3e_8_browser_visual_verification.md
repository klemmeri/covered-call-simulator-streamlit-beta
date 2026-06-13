# Phase 3E-8 — Browser Visual Verification Bundle

## Purpose

Phase 3E-8 verifies the browser-facing behavior of the Phase 3E customer payoff workbench after the guarded Developer-view dashboard integration.

This package is intentionally low-risk. It does not replace the main dashboard and does not modify the Customer view. It adds a check script that verifies files, imports, markers, panel labels, and then writes a browser visual verification checklist.

## Added file

```text
app\run_paid_simulator_phase3e_8_visual_verification_check.py
```

## Outputs

The check script writes:

```text
outputs\reports\paid_simulator\phase3e_8_browser_visual_checklist.md
outputs\reports\paid_simulator\phase3e_8_visual_verification.json
outputs\reports\paid_simulator\phase3e_8_visual_verification_checkpoint_report.txt
```

## Check script

Run:

```text
app\run_paid_simulator_phase3e_8_visual_verification_check.py
```

Expected final line:

```text
Overall Phase 3E-8 checkpoint status: PASS
```

## Browser verification

After the script passes, run the dashboard in Streamlit:

```text
streamlit run app\paid_simulator\config_form_app.py
```

Then use the generated checklist:

```text
outputs\reports\paid_simulator\phase3e_8_browser_visual_checklist.md
```

## Required visual outcome

1. The dashboard opens without a red traceback.
2. Customer view remains clean and does not show Phase 3E developer/test controls.
3. Developer view still contains prior Phase 3D material.
4. Developer view exposes the Phase 3E customer payoff workbench/helper/panel.
5. The Phase 3E workbench uses customer-facing labels.
6. Risk warnings are visible or clearly staged.
7. Save, reload, refresh, or export workflow language is visible or staged.

## Next checkpoint

If the script and browser checklist pass, the next checkpoint is:

```text
Phase 3E-9 — Customer workflow polish and final Phase 3E completion report
```
