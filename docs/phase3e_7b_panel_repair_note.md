# Phase 3E-7B Repair Note

This repair fixes a narrow mismatch between the Phase 3E-7B Streamlit panel and the Phase 3E-6 customer workbench view model.

## Failure observed

```text
FAIL Build/render panel TypeError("build_customer_workbench_view_model() missing 1 required positional argument: 'setup'")
```

## Cause

The Phase 3E-6 view-model builder correctly requires a `CustomerPayoffWorkbenchInput` setup object, but the Phase 3E-7B panel called it without that setup.

The panel also used early planned section names (`input_fields`, `warnings`) while the actual Phase 3E-6 view model uses (`input_panel`, `risk_warnings`).

## Repair

The replacement panel now:

- Builds a default customer payoff setup before calling `build_customer_workbench_view_model`.
- Accepts both current and planned section-key names.
- Keeps the panel Developer-view only.
- Still does not modify `app\paid_simulator\config_form_app.py`.

## Check script

Run the same check again:

```text
app\run_paid_simulator_phase3e_7b_panel_check.py
```

Expected final line:

```text
Overall Phase 3E-7B checkpoint status: PASS
```
