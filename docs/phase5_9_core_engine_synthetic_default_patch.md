# Phase 5-9 — Core Engine Synthetic-Default Patch

## Purpose

Phase 5-9 creates the first guarded core-engine integration contract for historical-path support while preserving the existing synthetic simulator workflow.

This checkpoint is intentionally conservative. It does not expose historical mode in the dashboard, and it does not make historical mode the default.

## Files added

```text
app\paid_simulator\phase5_core_engine_synthetic_default_patch.py
app\run_paid_simulator_phase5_9_core_engine_synthetic_default_patch_check.py
docs\phase5_9_core_engine_synthetic_default_patch.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_9_engine_file_status.csv
outputs\tables\paid_simulator\phase5_9_prior_artifact_status.csv
outputs\tables\paid_simulator\phase5_9_engine_mode_contract.csv
outputs\tables\paid_simulator\phase5_9_core_engine_patch_readiness.csv
outputs\tables\paid_simulator\phase5_9_core_engine_synthetic_default_patch_summary.csv
outputs\reports\paid_simulator\phase5_9_core_engine_synthetic_default_patch.json
outputs\reports\paid_simulator\phase5_9_core_engine_synthetic_default_patch_report.txt
```

## Guardrails

- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Unknown modes fall back to synthetic.
- No dashboard change is required.
- No customer workflow change is required.
- No core engine file is replaced in this checkpoint.

## Recommended next checkpoint

Phase 5-10 should be the first actual controlled replacement of a core engine-adjacent file or the addition of a safe engine utility module that `price_paths.py` can later call.

The preferred first integration target remains:

```text
app\price_paths.py
```

The change should be minimal and backward compatible.
