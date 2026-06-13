# Phase 3G-5 — Public Customer-view Route Smoke Test

Phase 3G-5 is a promotion-decision and smoke-test checkpoint for the eventual public Customer-view payoff workflow.

It does **not** enable the public Customer view.

## Added files

```text
app\paid_simulator\phase3g_public_customer_route_smoke_test.py
app\run_paid_simulator_phase3g_5_route_smoke_test_check.py
docs\phase3g_5_public_route_smoke_test.md
```

## Purpose

This checkpoint verifies that the public route is staged and protected before a later explicit activation step. It checks:

1. Dashboard syntax remains valid.
2. Public Customer view remains disabled.
3. Protected preview remains required.
4. Prior Phase 3E/3F/3G reports are available.
5. Customer-facing labels are present.
6. Risk and release guardrails are present.
7. Phase 3D, Phase 3E, Phase 3F, and Phase 3G markers remain detectable.

## Run

```text
app\run_paid_simulator_phase3g_5_route_smoke_test_check.py
```

Expected final line:

```text
Overall Phase 3G-5 checkpoint status: PASS
```

## Outputs

```text
outputs\reports\paid_simulator\phase3g_5_route_smoke_test_checkpoint_report.txt
outputs\reports\paid_simulator\phase3g_5_route_smoke_test_checkpoint.json
outputs\tables\paid_simulator\phase3g_5_route_smoke_test_checklist.csv
outputs\reports\paid_simulator\phase3g_5_public_route_promotion_decision.txt
```

## Release decision

The expected release decision is:

```text
DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET
```

The next logical step is a controlled public activation switch package.
