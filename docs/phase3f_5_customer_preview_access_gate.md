# Phase 3F-5 — Controlled Customer-Preview Access Gate

This checkpoint adds a formal access-gate model for the Phase 3F customer-preview workflow.

## Purpose

The Phase 3F preview path now has a dedicated model that distinguishes among:

1. ordinary Customer view access,
2. protected customer-preview access,
3. public customer release.

The ordinary Customer view remains disabled for Phase 3F preview features.

## Files added

```text
app\paid_simulator\phase3f_customer_preview_access_gate.py
app\run_paid_simulator_phase3f_5_access_gate_check.py
docs\phase3f_5_customer_preview_access_gate.md
```

## Important guardrail

This checkpoint does not modify:

```text
app\paid_simulator\config_form_app.py
```

It validates that previous Phase 3E and Phase 3F dashboard markers remain present and that the customer-facing release is still protected.

## Check script

Run:

```text
app\run_paid_simulator_phase3f_5_access_gate_check.py
```

Expected final line:

```text
Overall Phase 3F-5 checkpoint status: PASS
```

## Outputs

The check script writes:

```text
outputs\reports\paid_simulator\phase3f_5_access_gate_checkpoint_report.txt
outputs\reports\paid_simulator\phase3f_5_access_gate_checkpoint.json
outputs\tables\paid_simulator\phase3f_5_access_gate_checklist.csv
```

## Interpretation

A PASS means the project has a formal preview-access gate. It does not mean the workflow is publicly released to the ordinary Customer view.
