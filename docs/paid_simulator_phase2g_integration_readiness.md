# Phase 2G Integration Readiness

This document accompanies `app/run_paid_simulator_phase2g_integration_readiness_check.py`.

## Purpose

The Phase 2G integration-readiness checker verifies that the controlled model-promotion planning layer is installed and connected before a checkpoint package is created.

Phase 2G remains an internal, Developer-view-only layer. It does not promote any model into the customer-facing dashboard.

## The checker verifies

- The Phase 2G model-promotion planning module exists.
- The Phase 2G standalone model-promotion viewer exists.
- The Phase 2G pipeline checker exists.
- The Phase 2G dashboard-tab checker exists.
- The Phase 2F checkpoint checker exists.
- The model-promotion plan CSV, HTML, and text outputs exist.
- The Phase 2G planning, viewer, and pipeline check reports exist.
- The Phase 2F and earlier context outputs are available.
- The main dashboard contains the expected Phase 2G Developer-view tab markers.
- The model-promotion summary contains flexible wording consistent with an internal promotion plan.

## Output

The checker writes:

```text
outputs/reports/paid_simulator/phase2g_integration_readiness_report.txt
```

## Expected status

```text
Overall Phase 2G integration-readiness status: PASS
```

A `REVIEW` status usually means a text marker changed wording. A missing source file, output file, or zero-row CSV is more serious.

## Next step

After this passes, create the Phase 2G checkpoint package.
