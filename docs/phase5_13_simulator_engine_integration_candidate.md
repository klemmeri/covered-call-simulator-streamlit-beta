# Phase 5-13 — Simulator Engine Integration Candidate

This checkpoint adds a candidate simulator engine integration file without replacing the live `app\simulator.py` file.

## Purpose

Phase 5-13 validates the shape of the next simulator integration step before touching the live simulator engine.

The candidate confirms:

- synthetic mode remains the default;
- historical-import mode remains explicit only;
- unknown modes fall back to synthetic;
- a `SimulationEngine` class with a `run()` method is present;
- path-level and cycle-level output shapes are preserved at a minimal checkpoint level;
- no dashboard change is made;
- no customer workflow change is made;
- the live `app\simulator.py` file is not replaced yet.

## Files added

```text
app\simulator_phase5_13_candidate.py
app\paid_simulator\phase5_simulator_engine_integration_candidate.py
app\run_paid_simulator_phase5_13_simulator_engine_candidate_check.py
docs\phase5_13_simulator_engine_integration_candidate.md
```

## Outputs created

```text
outputs\tables\paid_simulator\phase5_13_simulator_engine_candidate_rows.csv
outputs\tables\paid_simulator\phase5_13_simulator_engine_candidate_summary.csv
outputs\reports\paid_simulator\phase5_13_simulator_engine_candidate.json
outputs\reports\paid_simulator\phase5_13_simulator_engine_candidate_report.txt
```

## Run command

```text
app\run_paid_simulator_phase5_13_simulator_engine_candidate_check.py
```

Expected final line:

```text
Overall Phase 5-13 checkpoint status: PASS
```

## Next recommended checkpoint

Phase 5-14 should review and promote the simulator candidate only after this checkpoint passes.
