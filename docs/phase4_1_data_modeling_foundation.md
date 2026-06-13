# Phase 4-1 — Data/Modeling Foundation

Phase 4 begins after the Phase 3 customer-facing workflow has been activated and verified.

This checkpoint does not change the dashboard. It creates a controlled foundation for data and modeling upgrades.

## Purpose

The next major value improvement is not another customer workflow gate. It is improving the simulator engine so the customer-facing workflow can eventually use better inputs and more credible model assumptions.

## Phase 4 upgrade areas

1. Real ticker data ingestion
2. Option-chain-style input scaffold
3. Volatility and premium model calibration
4. Strategy-comparison metrics

## Guardrails

- No dashboard change in Phase 4-1.
- No brokerage connection or automated trading behavior.
- No claim that regime detection or premium modeling is an oracle.
- Imported data must pass schema validation before use.
- Customer-facing outputs must retain warning and estimate language.

## Check script

Run:

```text
app\run_paid_simulator_phase4_1_foundation_check.py
```

Expected result:

```text
Overall Phase 4-1 checkpoint status: PASS
```
