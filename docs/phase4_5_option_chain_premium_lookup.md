# Phase 4-5 — Option-chain Premium Lookup Scaffold

## Purpose

Phase 4-5 adds a scaffold for selecting covered-call candidate contracts from an option-chain-style CSV file.

This is a modeling/data improvement phase. It does not change the dashboard.

## Inputs

The scaffold reads:

```text
inputs\market_data\sample_option_chain.csv
```

The loader is intentionally tolerant of common column-name variations. It normalizes columns such as:

- symbol
- quote date
- expiration date
- option type
- strike
- bid
- ask
- mid
- delta
- DTE
- implied volatility
- underlying price

## Selection logic

The scaffold filters for call options with valid bid, ask, mid, delta, and DTE values.

It ranks candidate covered calls by closeness to:

```text
target delta = 0.30
target DTE   = 30
```

The score also includes a small bid-ask spread penalty.

## Outputs

The checkpoint writes:

```text
outputs\tables\paid_simulator\phase4_5_option_chain_candidates.csv
outputs\tables\paid_simulator\phase4_5_best_covered_call_candidate.csv
outputs\tables\paid_simulator\phase4_5_option_chain_premium_lookup_summary.csv
outputs\reports\paid_simulator\phase4_5_option_chain_premium_lookup.json
outputs\reports\paid_simulator\phase4_5_option_chain_premium_lookup_report.txt
```

## Check script

Run:

```text
app\run_paid_simulator_phase4_5_option_chain_premium_lookup_check.py
```

Expected final line:

```text
Overall Phase 4-5 checkpoint status: PASS
```

## Release decision

```text
PHASE4_5_OPTION_CHAIN_PREMIUM_LOOKUP_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE
```

## Notes

This scaffold does not yet replace the premium model. It prepares the project for Phase 4-6, where model premium estimates can be compared against option-chain sample premiums.
