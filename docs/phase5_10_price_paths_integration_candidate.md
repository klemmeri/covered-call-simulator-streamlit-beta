# Phase 5-10 — Controlled `price_paths.py` Integration Candidate

## Purpose

Phase 5-10 creates and validates a candidate replacement for:

```text
app\price_paths.py
```

The package does **not** overwrite the live file. Instead, it adds:

```text
app\price_paths_phase5_10_candidate.py
```

This lets us test the proposed engine behavior before promoting it into the live simulator.

## Safety Rules

- Synthetic mode remains the default.
- Historical-import mode must be explicitly requested.
- Unknown modes fall back to synthetic.
- No dashboard change is made.
- No customer workflow change is made.
- The public function name `generate_price_paths(config)` is preserved.

## Files Added

```text
app\price_paths_phase5_10_candidate.py
app\paid_simulator\phase5_price_paths_integration_candidate.py
app\run_paid_simulator_phase5_10_price_paths_candidate_check.py
docs\phase5_10_price_paths_integration_candidate.md
```

## Outputs Created

```text
outputs\tables\paid_simulator\phase5_10_price_paths_synthetic_preview.csv
outputs\tables\paid_simulator\phase5_10_price_paths_historical_preview.csv
outputs\tables\paid_simulator\phase5_10_price_paths_integration_candidate_summary.csv
outputs\reports\paid_simulator\phase5_10_price_paths_integration_candidate.json
outputs\reports\paid_simulator\phase5_10_price_paths_integration_candidate_report.txt
```

## Next Step

If this checkpoint passes, the next checkpoint should be:

```text
Phase 5-11 — Review and promote price_paths.py candidate
```

That checkpoint can safely replace the live `app\price_paths.py` file only after the candidate behavior is validated.
