# Phase 2 Assumptions Viewer Tab

This update connects the Phase 2 scenario-assumptions scaffold into the standalone Phase 2 Scaffold Viewer.

## Files changed

- `app/paid_simulator/phase2_scaffold_viewer.py`

## Files added

- `app/run_paid_simulator_phase2_assumptions_viewer_check.py`
- `docs/paid_simulator_phase2_assumptions_viewer_tab.md`

## New viewer tab

The standalone Phase 2 viewer now includes:

- `Overview`
- `Scenario assumptions`
- `Scenario payoffs`
- `Phase 2 vs v0`
- `Price paths`

## Purpose

The `Scenario assumptions` tab makes the model assumptions explicit before the payoff outputs are interpreted. This prevents the Phase 2 scaffold from becoming a black box.

It displays:

- Scenario count
- Lowest and highest modeled return
- Modeled total return chart
- Assumption cards for each scenario
- Raw assumptions table behind an expander

## Test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2_assumptions_viewer_check.py
```

Expected result:

```text
Overall Phase 2 assumptions-viewer status: PASS
```

Then run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2_viewer.py
```

Open the `Scenario assumptions` tab.
