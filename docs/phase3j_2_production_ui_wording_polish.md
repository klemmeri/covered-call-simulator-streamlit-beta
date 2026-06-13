# Phase 3J-2 — Production UI Wording and Polish

This checkpoint defines customer-facing wording and UI-polish requirements for the activated payoff workflow.

It does not modify the dashboard.

## Purpose

Phase 3J-2 verifies that the production-polish stage keeps the customer workflow understandable and conservative before deeper UI changes are made.

## Required customer labels

- current price
- strike
- premium
- breakeven
- max profit
- downside cushion
- assignment zone
- warning

## Production guardrails

- Do not remove developer diagnostics until replacement checks pass.
- Do not weaken downside-risk, capped-upside, or assignment-risk disclosures.
- Do not present scenario overlays as forecasts or guarantees.
- Do not expose unfinished developer controls in the public Customer view.

## Check script

Run:

```text
app\run_paid_simulator_phase3j_2_ui_wording_polish_check.py
```

Expected final line:

```text
Overall Phase 3J-2 checkpoint status: PASS
```
