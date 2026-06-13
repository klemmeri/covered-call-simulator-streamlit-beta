# Phase 5-7 — Synthetic-default regression guard

## Purpose

Phase 5-7 creates a regression guard before the main simulator engine is patched.
The goal is to preserve the existing synthetic-path workflow while allowing the
historical-import work from Phase 4 and early Phase 5 to continue as an explicit
opt-in mode.

## Development rule

Synthetic mode remains the default until a later dashboard-facing release
intentionally exposes a customer workflow for imported data.

Historical mode remains explicit only.

## Files added

```text
app\paid_simulator\phase5_synthetic_default_regression_guard.py
app\run_paid_simulator_phase5_7_synthetic_default_regression_guard_check.py
docs\phase5_7_synthetic_default_regression_guard.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_7_engine_file_regression_guard_status.csv
outputs\tables\paid_simulator\phase5_7_prior_artifact_status.csv
outputs\tables\paid_simulator\phase5_7_synthetic_default_regression_guards.csv
outputs\tables\paid_simulator\phase5_7_synthetic_default_regression_guard_summary.csv
outputs\reports\paid_simulator\phase5_7_synthetic_default_regression_guard.json
outputs\reports\paid_simulator\phase5_7_synthetic_default_regression_guard_report.txt
```

## What this checkpoint does not do

It does not patch:

```text
app\price_paths.py
app\simulator.py
app\strategy.py
app\portfolio.py
app\config.py
app\paid_simulator\config_form_app.py
```

## Release decision

```text
PHASE5_7_SYNTHETIC_DEFAULT_REGRESSION_GUARD_CREATED_NO_ENGINE_PATCH_NO_DASHBOARD_CHANGE
```

## Next recommended checkpoint

Phase 5-8 should be a small controlled core-engine patch with a synthetic-default
regression test attached.
