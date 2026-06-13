# Phase 4-5 Row-Count Field Repair

This narrow repair replaces `app\paid_simulator\phase4_option_chain_premium_lookup.py`.

It preserves the candidate fallback behavior from the prior Phase 4-5 repair and adds the exact row-count summary keys expected by the checkpoint script:

- `raw_option_chain_rows`
- `normalized_option_chain_rows`
- `candidate_rows`

No dashboard files are changed.
