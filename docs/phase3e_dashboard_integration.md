# Phase 3E-7A — Developer Dashboard Integration Adapter

This checkpoint prepares the Phase 3E customer payoff workbench for dashboard integration without yet replacing the main dashboard file.

## What this package adds

```text
app\paid_simulator\phase3e_customer_workbench_dashboard.py
app\run_paid_simulator_phase3e_dashboard_integration_check.py
docs\phase3e_dashboard_integration.md
```

## Purpose

Phase 3E-7A creates a guarded Developer-view dashboard adapter for the customer payoff workbench.

The adapter provides:

1. A stable tab title.
2. Explicit customer-view protection language.
3. A Streamlit-compatible render function.
4. A non-Streamlit render model for command-line checks.
5. A dashboard integration snippet for the later full dashboard replacement step.

## Why this is safer than immediately replacing the dashboard

The file below is the main dashboard entry point:

```text
app\paid_simulator\config_form_app.py
```

Replacing it blindly is the main integration risk because it may disturb existing Phase 1B through Phase 3D dashboard tabs.

This checkpoint does not replace that file. Instead, it verifies that the Phase 3E tab renderer can exist independently and that the existing dashboard file remains untouched.

## Check script

Run:

```text
app\run_paid_simulator_phase3e_dashboard_integration_check.py
```

Expected final line:

```text
Overall Phase 3E-7A checkpoint status: PASS
```

## Output files

The check script writes:

```text
outputs\reports\paid_simulator\phase3e_dashboard_integration_checkpoint_report.txt
outputs\reports\paid_simulator\phase3e_dashboard_integration_render_model.json
outputs\reports\paid_simulator\phase3e_dashboard_integration_snippet.txt
outputs\tables\paid_simulator\phase3e_dashboard_integration_sections.csv
```

## Next checkpoint

The next bundled checkpoint should be Phase 3E-7B.

Recommended scope:

1. Add the Developer-view dashboard tab using a guarded full replacement or patch.
2. Verify that Phase 3D tabs remain available.
3. Verify that Phase 3E is not exposed in Customer view.
4. Verify that the dashboard imports and renders successfully.
5. Keep the workbench hidden behind Developer view until Phase 3E completion passes.
