# Phase 3G-3 — Public Customer-view Pre-Activation Verification

This checkpoint verifies that the project is ready for the next guarded activation step, while keeping the ordinary Customer view disabled.

## Added files

```text
app\paid_simulator\phase3g_public_customer_pre_activation_verification.py
app\run_paid_simulator_phase3g_3_pre_activation_check.py
docs\phase3g_3_public_customer_pre_activation_verification.md
```

## What this checkpoint confirms

1. The dashboard remains syntactically valid.
2. The Phase 3G-3 model imports and renders in bare PyCharm mode.
3. Public Customer-view activation remains disabled.
4. Protected preview remains required.
5. Release requirements are present.
6. Guardrails are present.
7. Customer-facing labels remain represented.
8. Phase 3D, Phase 3E, and Phase 3F dashboard markers remain present.

## Installation reminder

Extract the zip directly into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Do not extract into the `app` folder.

## Check script

Run:

```text
app\run_paid_simulator_phase3g_3_pre_activation_check.py
```

Expected final line:

```text
Overall Phase 3G-3 checkpoint status: PASS
```
