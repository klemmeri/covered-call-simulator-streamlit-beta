# Phase 3I-3 — Customer Save/Reload/Export Workflow Verification

This checkpoint verifies the post-activation customer workflow around saving,
reloading, refreshing, and exporting a covered-call payoff setup.

## Scope

This package does not modify `app\paid_simulator\config_form_app.py`.

It adds a standalone verification model and a checkpoint script that confirms:

- customer-facing labels are present;
- core payoff metrics are generated;
- setup save/reload works through JSON;
- export output works through CSV;
- warning/risk language remains present;
- prior Phase 3H and Phase 3I reports are available.

## Files added

```text
app\paid_simulator\phase3i_customer_save_reload_export_verification.py
app\run_paid_simulator_phase3i_3_save_reload_export_check.py
docs\phase3i_3_customer_save_reload_export_verification.md
```

## Expected checkpoint result

```text
Overall Phase 3I-3 checkpoint status: PASS
```

## Output files

```text
outputs\saved_setups\paid_simulator\phase3i_3_customer_setup.json
outputs\tables\paid_simulator\phase3i_3_customer_export_summary.csv
outputs\reports\paid_simulator\phase3i_3_save_reload_export_checkpoint_report.txt
outputs\reports\paid_simulator\phase3i_3_save_reload_export_checkpoint.json
outputs\tables\paid_simulator\phase3i_3_save_reload_export_checklist.csv
outputs\reports\paid_simulator\phase3i_3_save_reload_export_release_decision.txt
```
