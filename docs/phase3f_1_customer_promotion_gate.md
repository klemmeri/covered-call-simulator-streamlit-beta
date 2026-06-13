# Phase 3F-1 — Customer Promotion Release Gate

## Purpose

Phase 3E produced a customer-ready payoff workbench, but it is still protected behind Developer-view controls. Phase 3F begins the controlled promotion process.

This checkpoint does **not** expose Phase 3E to the Customer view. It verifies whether the current Phase 3E workbench is safe to use as the basis for a future customer-facing preview workflow.

## Files added

```text
app\paid_simulator\phase3f_customer_promotion_gate.py
app\run_paid_simulator_phase3f_1_customer_promotion_gate_check.py
docs\phase3f_1_customer_promotion_gate.md
```

## What the check verifies

The Phase 3F-1 check verifies:

1. The main Streamlit dashboard file exists.
2. The main Streamlit dashboard file has valid Python syntax.
3. Core Phase 3E modules exist.
4. Core Phase 3E modules have valid Python syntax.
5. Phase 3E dashboard, visual, and completion reports exist.
6. Developer-view Phase 3E integration markers remain present.
7. Customer view is not prematurely enabled for Phase 3E or Phase 3F.
8. Customer-facing payoff labels are present.
9. Risk and warning language is present.

## Why this gate exists

The project is moving from developer-only validation toward a customer-facing workflow. That transition should not happen by simply exposing internal controls. The customer view needs a clean preview shell with simple language, limited choices, and guardrails.

## Recommended next checkpoint after this passes

Phase 3F-2 should add a **Customer Preview Shell** that is still protected and testable. It should be separate from the fully public Customer view until the final promotion gate passes.

Possible Phase 3F-2 files:

```text
app\paid_simulator\phase3f_customer_preview_shell.py
app\run_paid_simulator_phase3f_2_customer_preview_shell_check.py
docs\phase3f_2_customer_preview_shell.md
```

## Run command

Run this in PyCharm:

```text
app\run_paid_simulator_phase3f_1_customer_promotion_gate_check.py
```

Expected final line:

```text
Overall Phase 3F-1 checkpoint status: PASS
```
