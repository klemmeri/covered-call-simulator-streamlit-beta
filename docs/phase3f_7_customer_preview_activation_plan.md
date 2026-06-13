# Phase 3F-7 — Controlled Customer-Preview Activation Plan

This checkpoint creates a formal activation-plan model for moving the protected customer-preview workflow toward a controlled preview state.

It does not enable public customer release.

## Added files

- `app/paid_simulator/phase3f_customer_preview_activation_plan.py`
- `app/run_paid_simulator_phase3f_7_activation_plan_check.py`
- `docs/phase3f_7_customer_preview_activation_plan.md`

## Guardrails

- Ordinary Customer view remains disabled for Phase 3F public release.
- Protected preview remains allowed for controlled testing.
- No dashboard file is modified by this package.
- Any future dashboard switch should use a guarded installer and timestamped backup.

## Check script

Run:

```text
app\run_paid_simulator_phase3f_7_activation_plan_check.py
```

Expected final line:

```text
Overall Phase 3F-7 checkpoint status: PASS
```
