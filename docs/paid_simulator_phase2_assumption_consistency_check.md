# Paid Simulator Phase 2 Assumption-Consistency Check

This document describes the add-only Phase 2 assumption-consistency checker.

## Purpose

The Phase 2 scaffold now contains separate components for:

- Scenario assumptions
- Scenario price paths
- Option payoff approximation
- Scenario payoff outputs
- Phase 2 versus v0 comparison outputs

The consistency checker verifies that these pieces agree before the Phase 2 logic is integrated further into the main paid simulator dashboard.

## Added file

```text
app\run_paid_simulator_phase2_assumption_consistency_check.py
```

## Files checked

```text
outputs\tables\paid_simulator\scenario_assumptions_scaffold.csv
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
outputs\tables\paid_simulator\scenario_payoff_report_scaffold.csv
outputs\tables\paid_simulator\phase2_v0_comparison_scaffold.csv
```

## Checks performed

The checker confirms:

1. Required scaffold output files exist.
2. Each file has rows.
3. Scenario-name columns can be detected.
4. Scenario sets are consistent across assumptions, price paths, and payoff outputs.
5. If return columns are available, modeled-return assumptions are consistent with final generated price-path returns.

## Expected result

```text
Overall assumption-consistency status: PASS
```

A `REVIEW` result means one of the scaffold outputs, names, or return assumptions needs attention before deeper Phase 2 integration.
