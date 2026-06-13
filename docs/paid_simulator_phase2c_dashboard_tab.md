# Paid Simulator Phase 2C Dashboard Tab

## Purpose

This package adds a Developer-view-only **Phase 2C validation** tab to the main paid-simulator dashboard.

The tab is intended for model-development review. It does not replace the stable customer-facing v0.1 dashboard workflow, and it does not expose Phase 2C diagnostics in Customer view.

## Files

Replaced:

```text
app\paid_simulator\config_form_app.py
```

Added:

```text
app\run_paid_simulator_phase2c_dashboard_tab_check.py
docs\paid_simulator_phase2c_dashboard_tab.md
```

## New dashboard tab

The new tab appears only when the sidebar is set to:

```text
Dashboard mode: Developer view
```

The tab name is:

```text
Phase 2C validation
```

## What the tab displays

The tab displays:

```text
Phase 2C validation file status
Validation summary text
Validation checks table
Option premium estimates
Premium-aware payoff output
Buttons to run the Phase 2C validation pipeline
Button to open the standalone Phase 2C validation viewer
Links/tools for Phase 2C validation reports
```

## Inputs expected

The tab expects the Phase 2C validation pipeline to have produced:

```text
outputs\tables\paid_simulator\premium_model_validation_scaffold.csv
outputs\reports\paid_simulator\premium_model_validation_scaffold.html
outputs\reports\paid_simulator\premium_model_validation_summary.txt
```

It also reads Phase 2B premium-model outputs:

```text
outputs\tables\paid_simulator\option_premium_scaffold.csv
outputs\tables\paid_simulator\premium_aware_payoff_scaffold.csv
```

## Test

Run:

```text
app\run_paid_simulator_phase2c_dashboard_tab_check.py
```

Expected result:

```text
PASS: The Developer-view-only Phase 2C validation tab is installed and the Phase 2C validation outputs are present.
```

## Interpretation

A passing dashboard-tab check means the Phase 2C validation layer is visible from the main dashboard and the expected output files are present.

A WATCH or REVIEW item inside the validation report is not automatically a code failure. It means the premium-model assumption should be inspected before the model is promoted into the customer-facing workflow.
