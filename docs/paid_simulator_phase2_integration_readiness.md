# Paid Simulator Phase 2 Integration Readiness

This document describes the readiness checkpoint before Phase 2 scaffold results are integrated into the main branded Streamlit dashboard.

## Current principle

The v0.1 dashboard is stable and should remain protected. Phase 2 modeling work should remain separate until its scaffold outputs are consistently generated and interpretable.

## What the readiness check verifies

The checker verifies that the following exist:

- Scenario model scaffold
- Scenario price-path scaffold
- Option-payoff scaffold
- Scenario-payoff connector
- Scenario-payoff report adapter
- Phase 2 vs v0 comparison adapter
- Phase 2 standalone viewer
- Phase 2 pipeline checker
- Required Phase 2 CSV and HTML outputs
- Phase 2 documentation

It also performs light CSV structure checks for expected scenario, payoff, relative-result, and comparison fields.

## Run command

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2_integration_readiness_check.py
```

Expected status:

```text
Overall Phase 2 integration-readiness status: PASS
```

## Meaning of PASS

A PASS means the Phase 2 scaffold is ready to be displayed inside the main dashboard as a new optional tab or developer-only panel.

It does not mean the Phase 2 model is production-quality. The payoff logic remains a scaffold and uses simplified assumptions.

## Recommended next step after PASS

Add a developer-only tab to the main dashboard:

```text
Phase 2 scaffold
```

That tab should read existing Phase 2 scaffold CSV/HTML outputs and display them without replacing the v0.1 simulator logic.

## Integration rule

Do not replace the current v0.1 paid simulator output with Phase 2 output yet. Phase 2 should be shown as experimental/scaffold output until its assumptions are reviewed and upgraded.
