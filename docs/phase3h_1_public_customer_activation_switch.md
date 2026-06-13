# Phase 3H-1 — Public Customer-view Activation Switch Scaffold

## Purpose

Phase 3H begins the controlled public Customer-view activation sequence for the customer-ready payoff workflow.

This checkpoint does **not** enable the public Customer view. It creates a formal activation-switch model and validates that the project is still in a conservative release state.

## Added files

```text
app\paid_simulator\phase3h_public_customer_activation_switch.py
app\run_paid_simulator_phase3h_1_activation_switch_check.py
docs\phase3h_1_public_customer_activation_switch.md
```

## Release state

```text
Public Customer view: disabled
Protected preview: required
Dashboard modification: none in this checkpoint
```

## Expected decision

```text
PHASE3H_1_SWITCH_SCAFFOLD_READY_PUBLIC_CUSTOMER_VIEW_DISABLED
```

## Check script

Run:

```text
app\run_paid_simulator_phase3h_1_activation_switch_check.py
```

Expected final line:

```text
Overall Phase 3H-1 checkpoint status: PASS
```
