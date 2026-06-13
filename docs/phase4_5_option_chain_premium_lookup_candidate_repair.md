# Phase 4-5 Option-Chain Premium Lookup Candidate Repair

This repair replaces `app\paid_simulator\phase4_option_chain_premium_lookup.py`.

The original Phase 4-5 scaffold loaded and normalized the sample option-chain file but produced zero candidate rows when the sample data was too small or did not satisfy the initial screen. This repair keeps the intended scaffold behavior while adding a controlled fallback rule:

1. First screen for plausible covered-call call options with positive premium, reasonable DTE, and reasonable delta.
2. If that produces no rows, relax the filter and keep the best available premium-bearing row.
3. If the input file is missing or empty, create a one-row scaffold sample so the data path remains testable.

This does not turn the scaffold into a production option-chain integration. It only ensures that the Phase 4-5 data path always produces a candidate for downstream calibration and comparison work.

No dashboard files are changed.
