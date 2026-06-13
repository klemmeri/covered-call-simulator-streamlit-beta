# Phase 3I-7 — Customer Workflow Completion Gate

## Purpose

Phase 3I-7 consolidates the activated customer workflow checks after public Customer-view activation. It verifies that the customer-facing payoff workflow has passed these post-activation checkpoints:

1. Browser/customer workflow verification.
2. Customer workflow smoke test.
3. Save/reload/export verification.
4. Risk-warning and disclosure verification.
5. Customer explanation and wording verification.
6. Customer output/report verification.

## Dashboard impact

This package does not modify `app\paid_simulator\config_form_app.py`.

## Expected release decision

```text
PHASE3I_COMPLETE_CUSTOMER_WORKFLOW_VERIFIED
```

## Check script

Run:

```text
app\run_paid_simulator_phase3i_7_completion_gate_check.py
```

Expected final line:

```text
Overall Phase 3I-7 checkpoint status: PASS
```

## Output files

The check script writes:

```text
outputs\reports\paid_simulator\phase3i_7_completion_gate_checkpoint_report.txt
outputs\reports\paid_simulator\phase3i_7_completion_gate_checkpoint.json
outputs\tables\paid_simulator\phase3i_7_completion_gate_checklist.csv
outputs\reports\paid_simulator\phase3i_7_completion_release_decision.txt
```
