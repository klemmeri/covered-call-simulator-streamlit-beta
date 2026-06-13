# Phase 2 Scenario-Assumptions Import Fix

This fix restores the expected `get_default_scenario_assumptions()` function and adds compatibility aliases for earlier scaffold naming conventions.

It also aligns the scenario-assumption modeled returns with the current price-path scaffold returns:

- Downtrend: -8.0%
- Sideways Choppy: 0.0%
- Moderate Uptrend: +5.0%
- Strong Rally: +12.0%
- Volatile Whipsaw: +2.0%

After installing this fix, run:

```text
app\run_paid_simulator_scenario_assumptions_check.py
```

Then run:

```text
app\run_paid_simulator_phase2_assumption_consistency_check.py
```
