# Phase 5-8 — Controlled Core-Engine Patch with Synthetic-Default Protection

## Purpose

Phase 5-8 creates the first core-engine-facing patch contract for historical-path integration while preserving the current synthetic simulator workflow.

This checkpoint is intentionally conservative:

- synthetic mode remains the default;
- historical-import mode remains explicit only;
- no dashboard changes are made;
- no public customer workflow is changed;
- no core engine files are replaced in this checkpoint.

## Added files

```text
app\paid_simulator\phase5_controlled_core_engine_patch.py
app\run_paid_simulator_phase5_8_controlled_core_engine_patch_check.py
docs\phase5_8_controlled_core_engine_patch.md
```

## Outputs

```text
outputs\tables\paid_simulator\phase5_8_controlled_core_engine_patch_contract.csv
outputs\tables\paid_simulator\phase5_8_engine_mode_matrix.csv
outputs\tables\paid_simulator\phase5_8_controlled_core_engine_patch_preview.csv
outputs\tables\paid_simulator\phase5_8_controlled_core_engine_patch_summary.csv
outputs\reports\paid_simulator\phase5_8_controlled_core_engine_patch.json
outputs\reports\paid_simulator\phase5_8_controlled_core_engine_patch_report.txt
```

## Design rule

Historical data should enter the production engine only through an explicit mode selection. The simulator must not silently switch away from synthetic mode.

## Next checkpoint

Recommended next checkpoint:

```text
Phase 5-9 — Core engine synthetic-default patch
```

That should be the first checkpoint that carefully patches a core engine file, with synthetic-mode regression checks included.
