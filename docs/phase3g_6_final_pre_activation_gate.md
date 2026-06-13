# Phase 3G-6 — Final Pre-Activation Decision Gate

This checkpoint consolidates the Phase 3G public Customer-view release path before any public activation is allowed.

It does not modify `app\paid_simulator\config_form_app.py` and it does not enable the public Customer view.

## Purpose

Phase 3G-6 verifies that:

1. The dashboard remains syntactically valid.
2. Phase 3D, Phase 3E, Phase 3F, and Phase 3G readiness markers remain present.
3. The protected preview path remains the only customer-like route.
4. Public Customer-view activation remains disabled.
5. Customer-facing labels and risk guardrails remain available.
6. Prior completion and release-gate reports exist.

## Release decision

The expected decision is:

```text
DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET
```

A later checkpoint must explicitly enable the public Customer view if and when the project is ready.

## Check script

Run:

```text
app\run_paid_simulator_phase3g_6_final_pre_activation_check.py
```

Expected final line:

```text
Overall Phase 3G-6 checkpoint status: PASS
```
