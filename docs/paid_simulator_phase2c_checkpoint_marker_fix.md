# Phase 2C Checkpoint Marker Fix

This package replaces the Phase 2C checkpoint checker with a slightly more tolerant marker check for the premium-model validation summary file.

## Reason for the fix

The Phase 2C checkpoint check reported `REVIEW` even though all source files, runner files, generated CSV files, HTML reports, dashboard markers, and row checks passed.

The only failing item was a strict text-marker search for:

```text
Premium-model validation
```

The existing summary file used a slightly different wording, so the checkpoint checker treated the summary as incomplete even though the validation outputs were present.

## What changed

The checker now accepts reasonable variants such as:

```text
Premium-model validation
Premium model validation
Phase 2C premium-model validation
Phase 2C premium model validation
premium_model_validation
```

It also normalizes hyphens and underscores before checking.

## Files replaced

```text
app\run_paid_simulator_phase2c_checkpoint_check.py
```

## Expected result

After installing this package, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2c_checkpoint_check.py
```

Expected final line:

```text
Overall Phase 2C checkpoint status: PASS
```
