# Phase 5-16 — Historical Import Engine-Runner Candidate

This checkpoint adds a safe runner-facing contract for historical-import mode.

It does not modify the dashboard and does not replace any additional live core engine files.
Synthetic mode remains the default, and historical-import mode remains explicit only.

## Added files

- `app\paid_simulator\phase5_historical_import_engine_runner_candidate.py`
- `app\run_paid_simulator_phase5_16_historical_import_engine_runner_check.py`
- `docs\phase5_16_historical_import_engine_runner_candidate.md`

## Outputs

- `outputs\tables\paid_simulator\phase5_16_historical_import_engine_runner_path_preview.csv`
- `outputs\tables\paid_simulator\phase5_16_historical_import_engine_runner_contract.csv`
- `outputs\tables\paid_simulator\phase5_16_historical_import_engine_runner_summary.csv`
- `outputs\reports\paid_simulator\phase5_16_historical_import_engine_runner_candidate.json`
- `outputs\reports\paid_simulator\phase5_16_historical_import_engine_runner_candidate_report.txt`

## Design intent

Phase 5-16 verifies that a historical path can be normalized into a runner-ready format
without changing the public workflow. It is a preparation step before a controlled runner
or workflow entry point is introduced.

## Safety rules

- Synthetic mode remains the default.
- Historical-import mode must be explicitly selected.
- Dashboard behavior is unchanged.
- No customer workflow is changed.
- No additional live core engine file is replaced in this checkpoint.
