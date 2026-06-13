# Phase 3 Interactive Payoff Pipeline Check

This package adds a pipeline checker for the first Phase 3 interactive covered-call payoff viewer.

## Purpose

The checker confirms that the first Phase 3 graphical payoff prototype is installed and that its own viewer check runs successfully.

It intentionally treats the interactive payoff snapshot files as optional. Those files are created only after the Streamlit viewer is opened and a setup is saved/exported.

## Files added

```text
app\run_paid_simulator_phase3_interactive_payoff_pipeline_check.py
docs\paid_simulator_phase3_interactive_payoff_pipeline_check.md
```

## What the checker verifies

```text
Phase 3 interactive payoff viewer source file
Phase 3 viewer launcher
Phase 3 viewer check script
Phase 3 viewer documentation
Phase 2G checkpoint context
Phase 3 viewer check execution
Optional Phase 3 payoff snapshot CSV/HTML outputs
Phase 3 pipeline documentation
```

## Output report

The checker writes:

```text
outputs\reports\paid_simulator\phase3_interactive_payoff_pipeline_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3_interactive_payoff_pipeline_check.py
```

Expected result:

```text
Overall Phase 3 interactive payoff pipeline status: PASS
```

## Notes

This is a safe Phase 3 bridge step. It does not integrate the interactive payoff viewer into the main paid dashboard yet. That should come only after the standalone viewer and pipeline are confirmed stable.
