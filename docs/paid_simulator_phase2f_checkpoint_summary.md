# Phase 2F checkpoint summary

## Purpose

This checkpoint verifies the Phase 2F model-decision milestone for the Covered Call Simulator paid dashboard.

Phase 2F consolidates the evidence from the premium-aware model, validation checks, tuning recommendations, and adjusted-premium payoff comparison into a model-decision summary. The checkpoint confirms that the files, outputs, reports, dashboard tab markers, and supporting documentation are all present.

## Added files

```text
app\run_paid_simulator_phase2f_checkpoint_check.py
docs\paid_simulator_phase2f_checkpoint_summary.md
```

## Expected command

Run this from PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2f_checkpoint_check.py
```

## Expected result

```text
Overall Phase 2F checkpoint status: PASS
```

## Output report

The checker writes:

```text
outputs\reports\paid_simulator\phase2f_checkpoint_report.txt
```

## What this confirms

The checkpoint verifies:

```text
Option-premium model
Premium-aware payoff runner
Premium-vs-scaffold comparison
Premium-model validation module
Premium-model tuning module
Premium-model adjustment module
Adjusted-premium payoff comparison module
Model-decision summary module
Phase 2F model-decision viewer
Phase 2F model-decision pipeline check
Phase 2F dashboard tab
Phase 2F integration-readiness check
Phase 2B through Phase 2E context outputs
Phase 2F CSV/HTML/text outputs
Main dashboard Phase 2F tab markers
Phase 2F documentation
```

## Notes

This is still a development checkpoint, not a customer-facing trading recommendation layer. The Phase 2F labels are internal model-development labels that help decide whether the adjusted-premium model is ready for controlled promotion, should remain a research model, or needs further review.
