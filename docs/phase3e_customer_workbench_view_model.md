# Phase 3E-6 — Customer Payoff Workbench View Model

## Purpose

Phase 3E-6 prepares the customer payoff workbench for later dashboard integration without changing the dashboard yet.

The new module converts the Phase 3E-5 workbench result into dashboard-ready sections:

1. Covered-call setup input panel
2. Payoff summary metric cards
3. Risk warnings
4. Scenario overlay table
5. Workflow actions

This keeps the customer-facing calculation logic separate from the eventual Streamlit rendering layer.

## Files added

```text
app\paid_simulator\phase3e_customer_workbench_view_model.py
app\run_paid_simulator_phase3e_customer_view_model_check.py
docs\phase3e_customer_workbench_view_model.md
```

## Check script

Run from PyCharm:

```text
app\run_paid_simulator_phase3e_customer_view_model_check.py
```

Expected final line:

```text
Overall Phase 3E-6 checkpoint status: PASS
```

## Outputs created by the check

```text
outputs\reports\paid_simulator\phase3e_customer_workbench_view_model.json
outputs\tables\paid_simulator\phase3e_customer_workbench_view_model_sections.csv
outputs\reports\paid_simulator\phase3e_customer_workbench_view_model_integration_notes.txt
```

## What this checkpoint proves

- Customer-facing input fields are defined cleanly.
- Customer-facing action labels exist for update, save, reload, and export.
- Payoff metrics and warning boxes are converted into renderable section data.
- Scenario overlay rows are available without developer controls.
- The module can support a later Streamlit dashboard tab without moving business logic into the UI.

## Next likely checkpoint

Phase 3E-7 should add a Developer-view dashboard tab that renders this view model in Streamlit. That step may require replacing:

```text
app\paid_simulator\config_form_app.py
```

The customer view should remain protected until the Developer-view tab passes.
