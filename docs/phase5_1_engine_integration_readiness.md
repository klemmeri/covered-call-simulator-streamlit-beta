# Phase 5-1 — Engine Integration Readiness Map

## Purpose

Phase 5 begins the transition from Phase 4 scaffolding to actual simulator-engine integration.

Phase 4 produced imported-data artifacts for:

- historical underlying prices,
- option-chain-style premium data,
- premium calibration,
- imported-data strategy comparison.

Phase 5-1 does not modify the simulator engine yet. It maps the likely engine touchpoints and confirms that the next work should harden the engine before exposing imported-data controls in the paid dashboard.

## Files added

```text
app\paid_simulator\phase5_engine_integration_readiness.py
app\run_paid_simulator_phase5_1_engine_integration_readiness_check.py
docs\phase5_1_engine_integration_readiness.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_1_engine_integration_touchpoints.csv
outputs\tables\paid_simulator\phase5_1_engine_integration_artifact_status.csv
outputs\tables\paid_simulator\phase5_1_engine_integration_sequence.csv
outputs\tables\paid_simulator\phase5_1_engine_integration_readiness_summary.csv
outputs\reports\paid_simulator\phase5_1_engine_integration_readiness.json
outputs\reports\paid_simulator\phase5_1_engine_integration_readiness_report.txt
```

## Design decision

No dashboard change is made in this checkpoint.

The dashboard should not expose imported-data controls until the simulator engine can actually consume imported historical paths and option-chain premium inputs reliably.

## Recommended Phase 5 sequence

1. Phase 5-1 — Engine integration readiness map.
2. Phase 5-2 — Imported historical path engine adapter.
3. Phase 5-3 — Synthetic fallback preservation check.
4. Phase 5-4 — Option-chain premium source adapter for strategy logic.
5. Phase 5-5 — Integrated engine comparison: synthetic vs imported data.
6. Phase 5-6 — Phase 5 completion handoff for Phase 6 dashboard integration.

## Check script

Run:

```text
app\run_paid_simulator_phase5_1_engine_integration_readiness_check.py
```

Expected final line:

```text
Overall Phase 5-1 checkpoint status: PASS
```
