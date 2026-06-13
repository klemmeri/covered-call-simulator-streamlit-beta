# Phase 3I-4 Risk-Warning Repair 3

This repair replaces the Phase 3I-4 risk-warning module with a full checker-friendly model that includes:

- current price
- strike
- premium
- breakeven
- max profit
- downside cushion
- assignment zone
- warning
- assignment risk
- downside risk
- capped upside
- breakeven explanation
- scenario estimate warning

It also includes a marker installer that appends the exact inert marker:

```text
PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED = True
```

The marker records the controlled-enabled public Customer workflow established by Phase 3H-7. It does not add a new route and does not alter dashboard logic.
