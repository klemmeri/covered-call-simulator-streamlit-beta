# Phase 2B Premium Model Viewer

This add-on creates a standalone Streamlit viewer for Phase 2B premium-aware modeling outputs.

## Added files

```text
app\paid_simulator\phase2b_premium_viewer.py
app\run_paid_simulator_phase2b_premium_viewer.py
app\run_paid_simulator_phase2b_premium_viewer_check.py
docs\paid_simulator_phase2b_premium_viewer.md
```

## Purpose

The viewer is a development tool. It does not replace the v0.1 paid simulator dashboard.

It displays:

- option premium estimates,
- premium-aware payoff results,
- premium-aware versus older Phase 2 scaffold comparison,
- links to the generated HTML scaffold reports.

## Expected inputs

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_vs_scaffold_comparison.csv
outputs\reports\paid_simulator\premium_aware_payoff_scaffold.html
outputs\reports\paid_simulator\premium_vs_scaffold_comparison.html
```

## Test

Run:

```text
app\run_paid_simulator_phase2b_premium_viewer_check.py
```

Expected result:

```text
Overall Phase 2B premium-viewer status: PASS
```

Then launch:

```text
app\run_paid_simulator_phase2b_premium_viewer.py
```

## Notes

This is intentionally standalone. After it is validated, the premium-aware outputs can be integrated into the Developer-view Phase 2 scaffold tab of the main dashboard.
