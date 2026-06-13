# Phase 2B Premium-Aware vs Older Phase 2 Payoff Comparison

## Purpose

This add-only scaffold compares the older Phase 2 payoff output with the newer premium-aware payoff output.

The goal is to isolate the impact of the new option-premium model before integrating it into the main paid simulator dashboard.

## Added files

```text
app\paid_simulator\premium_vs_scaffold_comparison.py
app\run_paid_simulator_premium_vs_scaffold_check.py
docs\paid_simulator_phase2b_premium_vs_scaffold_comparison.md
```

## Inputs

```text
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
```

## Outputs

```text
outputs\tables\paid_simulator\premium_vs_scaffold_comparison.csv
outputs\reports\paid_simulator\premium_vs_scaffold_comparison.html
```

## Output fields

The comparison output includes:

```text
scenario
old_phase2_relative_result
premium_aware_relative_result
premium_minus_old
comparison_classification
plain_english_interpretation
```

When available, it also carries premium-model fields such as:

```text
estimated_call_premium
estimated_call_strike
estimated_call_delta
estimated_implied_volatility
```

## Interpretation

A positive `premium_minus_old` value means the premium-aware model produced a higher relative result than the older Phase 2 scaffold.

A negative value means the premium-aware model produced a lower relative result.

This is a development diagnostic, not a customer-facing trade recommendation.

## Test

Run this in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_premium_vs_scaffold_check.py
```

Expected result:

```text
Overall premium-vs-scaffold comparison status: PASS
```

## Next step

After this passes, the next logical Phase 2B step is to add a premium-aware comparison tab or section to the standalone Phase 2 viewer, still keeping it out of Customer view until validated.
