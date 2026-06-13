# Phase 5-14 — Simulator Candidate Promotion

This checkpoint promotes the validated Phase 5-13 simulator integration candidate into the live simulator-facing file:

```text
app\simulator.py
```

The promotion remains guarded:

- synthetic mode remains the default;
- historical-import mode remains explicit only;
- unknown modes remain safe;
- no dashboard change is made;
- no public customer workflow is changed.

The checkpoint writes a status report and validates that the live simulator still exposes the expected `SimulationEngine` class and `run()` method.

## Run

```text
app\run_paid_simulator_phase5_14_simulator_promotion_check.py
```

Expected result:

```text
Overall Phase 5-14 checkpoint status: PASS
```
