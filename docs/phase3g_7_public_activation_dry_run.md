# Phase 3G-7 — Public Customer-view Activation Dry Run

This checkpoint simulates the public Customer-view activation path without enabling public access.

## Purpose

Phase 3G-7 confirms that the release path is coherent while preserving the conservative decision:

```text
DRY_RUN_ONLY_DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW
```

## Files added

```text
app\paid_simulator\phase3g_public_customer_activation_dry_run.py
app\run_paid_simulator_phase3g_7_activation_dry_run_check.py
docs\phase3g_7_public_activation_dry_run.md
```

## Dashboard status

This package does not modify:

```text
app\paid_simulator\config_form_app.py
```

The public Customer view remains disabled. Protected preview remains required.

## Check script

Run:

```text
app\run_paid_simulator_phase3g_7_activation_dry_run_check.py
```

Expected final line:

```text
Overall Phase 3G-7 checkpoint status: PASS
```

## Outputs

```text
outputs\reports\paid_simulator\phase3g_7_activation_dry_run_checkpoint_report.txt
outputs\reports\paid_simulator\phase3g_7_activation_dry_run_checkpoint.json
outputs\tables\paid_simulator\phase3g_7_activation_dry_run_checklist.csv
outputs\reports\paid_simulator\phase3g_7_activation_dry_run_release_decision.txt
```
