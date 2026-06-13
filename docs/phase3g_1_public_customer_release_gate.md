# Phase 3G-1 — Public Customer-View Release Gate

Phase 3G-1 starts the public-release stage for the customer payoff workflow.

This checkpoint does **not** enable the public Customer view. It creates a release-gate model that separates:

1. Developer-view workbench testing.
2. Protected customer-preview access.
3. Public Customer-view release.

The public Customer-view release remains disabled until a later explicit release checkpoint.

## Files added

```text
app\paid_simulator\phase3g_public_customer_release_gate.py
app\run_paid_simulator_phase3g_1_public_release_gate_check.py
docs\phase3g_1_public_customer_release_gate.md
```

## Check script

Run:

```text
app\run_paid_simulator_phase3g_1_public_release_gate_check.py
```

Expected final line:

```text
Overall Phase 3G-1 checkpoint status: PASS
```

## Outputs

```text
outputs\reports\paid_simulator\phase3g_1_public_release_gate_checkpoint_report.txt
outputs\reports\paid_simulator\phase3g_1_public_release_gate_checkpoint.json
outputs\tables\paid_simulator\phase3g_1_public_release_gate_checklist.csv
```

## Guardrail

This package does not modify `app\paid_simulator\config_form_app.py`.
