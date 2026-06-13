# Phase 2B Integration Readiness Check

This document describes the Phase 2B premium-model integration readiness checker.

## Purpose

Phase 2B introduced a more realistic premium-aware modeling layer while keeping the working v0.1 dashboard safe. The purpose of this checker is to verify that the premium-model layer is installed, that its outputs exist, and that the main dashboard includes the Developer-view-only Phase 2B premium-model tab.

This is a checkpoint tool, not a trading model.

## Added file

```text
app\run_paid_simulator_phase2b_integration_readiness_check.py
```

## What it checks

The script checks for the Phase 2B model files:

```text
app\paid_simulator\option_premium_model.py
app\paid_simulator\premium_aware_payoff_runner.py
app\paid_simulator\premium_vs_scaffold_comparison.py
app\paid_simulator\phase2b_premium_viewer.py
```

It checks for Phase 2B runner/check files:

```text
app\run_paid_simulator_option_premium_check.py
app\run_paid_simulator_premium_aware_payoff_check.py
app\run_paid_simulator_premium_vs_scaffold_check.py
app\run_paid_simulator_phase2b_premium_viewer.py
app\run_paid_simulator_phase2b_premium_viewer_check.py
app\run_paid_simulator_phase2b_pipeline_check.py
app\run_paid_simulator_phase2b_dashboard_tab_check.py
```

It checks for output files:

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
outputs\tables\paid_simulator\premium_vs_scaffold_comparison.csv
outputs\reports\paid_simulator\premium_aware_payoff_scaffold.html
outputs\reports\paid_simulator\premium_vs_scaffold_comparison.html
```

It also checks that the main dashboard file appears to contain the Developer-view Phase 2B premium-model tab.

## Output

The checker writes a text report to:

```text
outputs\reports\paid_simulator\phase2b_integration_readiness_report.txt
```

## How to run

From PyCharm, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2b_integration_readiness_check.py
```

Expected result:

```text
Overall Phase 2B integration-readiness status: PASS
```

## Meaning of PASS

A PASS means that the Phase 2B premium-model layer is installed and connected well enough for checkpointing and further validation.

It does not mean the premium model is final. The next modeling step is to validate and improve the assumptions, especially implied volatility, skew, target-delta strike selection, dividends, and assignment behavior.
