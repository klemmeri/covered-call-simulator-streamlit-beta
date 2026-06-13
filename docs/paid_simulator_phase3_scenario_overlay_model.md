# Phase 3B Scenario-Overlay Model

This add-only package introduces the first scenario-overlay layer for the Phase 3 interactive covered-call dashboard.

## Purpose

The Phase 3 interactive payoff viewer shows the direct payoff profile for a manually entered covered-call setup. The scenario-overlay model extends that idea by testing the same setup against a small set of deterministic price-move scenarios.

This is still a scaffold. It is not live market data and it is not a final commercial recommendation engine.

## Added files

```text
app\paid_simulator\phase3_scenario_overlay_model.py
app\run_paid_simulator_phase3_scenario_overlay_check.py
docs\paid_simulator_phase3_scenario_overlay_model.md
```

## Inputs

The model tries to read:

```text
outputs\tables\paid_simulator\phase3_interactive_payoff_snapshot.csv
```

If no saved interactive payoff snapshot exists, it uses a default SPY demo setup.

## Outputs

```text
outputs\tables\paid_simulator\phase3_scenario_overlay.csv
outputs\reports\paid_simulator\phase3_scenario_overlay.html
outputs\reports\paid_simulator\phase3_scenario_overlay_summary.txt
outputs\reports\paid_simulator\phase3_scenario_overlay_check_report.txt
```

## Scenario cases

The scaffold creates these deterministic overlay cases:

```text
Sharp pullback
Moderate pullback
Flat / pin
Mild rally
Strike test
Strong rally
```

Each case calculates:

```text
Ending price
Buy-and-hold P/L
Covered-call P/L
Covered-call minus buy-and-hold
Premium income
Intrinsic call loss
Assignment flag
Plain-English interpretation
```

## Test

Run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase3_scenario_overlay_check.py
```

Expected:

```text
Overall Phase 3B scenario-overlay status: PASS
```

## Next step

After this passes, the next step is a standalone Phase 3B scenario-overlay viewer, then a Developer-view-only dashboard tab.
