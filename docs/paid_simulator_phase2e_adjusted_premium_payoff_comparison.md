# Phase 2E Adjusted Premium Payoff Comparison

Generated: 2026-06-12

## Purpose

This Phase 2E scaffold compares the controlled adjusted-premium output against the existing premium-aware payoff result.

The key point is safety: this package does not overwrite the original option-premium scaffold, the premium-aware payoff scaffold, or the main dashboard. It writes a separate comparison layer so the premium adjustment can be inspected before any tuned assumptions are promoted.

## Files added

```text
app\paid_simulator\adjusted_premium_payoff_comparison.py
app\run_paid_simulator_adjusted_premium_payoff_comparison_check.py
docs\paid_simulator_phase2e_adjusted_premium_payoff_comparison.md
```

## Inputs

```text
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
outputs\tables\paid_simulator\premium_model_adjusted_premiums.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
```

The third input is used as prior-model context.

## Outputs

```text
outputs\tables\paid_simulator\adjusted_premium_payoff_comparison.csv
outputs\reports\paid_simulator\adjusted_premium_payoff_comparison.html
outputs\reports\paid_simulator\adjusted_premium_payoff_summary.txt
outputs\reports\paid_simulator\phase2e_adjusted_premium_payoff_comparison_check_report.txt
```

## What it calculates

For each modeled scenario, the scaffold calculates:

```text
Buy-and-hold P/L
Original premium-model covered-call P/L
Adjusted premium-model covered-call P/L
Adjusted covered-call minus buy-and-hold
Intrinsic call loss
Original premium income
Adjusted premium income
Adjusted minus original model P/L
Adjusted minus prior premium-aware relative result
Assignment flag
Plain-English interpretation
```

## Why this matters

Phase 2E first adjusted the option premium itself. This step asks the more important trading question:

```text
If the tuned premium assumption changes, how much does the modeled covered-call payoff change?
```

That is a necessary checkpoint before using the tuned premium model more broadly.

## Expected check result

Run:

```text
app\run_paid_simulator_adjusted_premium_payoff_comparison_check.py
```

Expected final line:

```text
Overall Phase 2E adjusted premium payoff comparison status: PASS
```

## Next step

After this passes, the next safe step is to add a standalone Phase 2E adjustment viewer, then a Phase 2E pipeline checker, before adding anything to the main dashboard.
