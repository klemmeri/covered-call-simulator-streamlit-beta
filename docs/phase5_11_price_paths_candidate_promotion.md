# Phase 5-11 — price_paths.py Candidate Promotion

## Purpose

Phase 5-11 promotes the validated Phase 5-10 candidate into the live engine-facing file:

```text
app\price_paths.py
```

This is the first intentional live engine-file replacement in Phase 5.

## Safety rules preserved

- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Unknown modes fall back to synthetic.
- The public function `generate_price_paths(config)` remains available.
- No dashboard change is made.
- No public customer workflow change is made.

## Outputs

The checkpoint creates:

```text
outputs\tables\paid_simulator\phase5_11_live_price_paths_synthetic_preview.csv
outputs\tables\paid_simulator\phase5_11_live_price_paths_historical_preview.csv
outputs\tables\paid_simulator\phase5_11_price_paths_candidate_promotion_summary.csv
outputs\reports\paid_simulator\phase5_11_price_paths_candidate_promotion.json
outputs\reports\paid_simulator\phase5_11_price_paths_candidate_promotion_report.txt
```

## Interpretation

A PASS means the live `app\price_paths.py` file can generate synthetic paths by default and historical paths only when explicitly requested.

The next checkpoint should be a compatibility smoke test against the broader simulator engine, because changing `price_paths.py` is now a real engine-facing change.
