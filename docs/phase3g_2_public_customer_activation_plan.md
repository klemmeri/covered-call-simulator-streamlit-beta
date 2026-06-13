# Phase 3G-2 — Public Customer-view Activation Plan

This checkpoint defines the activation plan for eventually promoting the protected customer-preview workflow into the ordinary Customer view.

It does **not** enable public Customer view.

## Added files

- `app/paid_simulator/phase3g_public_customer_activation_plan.py`
- `app/run_paid_simulator_phase3g_2_activation_plan_check.py`
- `docs/phase3g_2_public_customer_activation_plan.md`

## Policy

The ordinary Customer view remains disabled until a later explicit release checkpoint. Phase 3G-2 only validates the release-plan model, guardrails, customer-facing label requirements, prior reports, and dashboard markers.

## Run

```text
app\run_paid_simulator_phase3g_2_activation_plan_check.py
```

Expected result:

```text
Overall Phase 3G-2 checkpoint status: PASS
```
