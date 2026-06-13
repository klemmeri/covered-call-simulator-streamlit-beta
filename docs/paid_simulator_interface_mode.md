# Paid Simulator Interface Mode

This update adds a sidebar **Dashboard mode** selector to the paid simulator Streamlit dashboard.

## Modes

### Customer view
Shows the tabs a customer or nontechnical user needs:

- Overview
- Setup & run
- Latest results
- Preset comparison
- Report
- Help & assumptions

This hides local-development and housekeeping tabs so the dashboard feels more like a paid product interface.

### Developer view
Shows every tab, including local diagnostics and maintenance tools:

- Overview
- Setup & run
- Latest results
- Run history
- Preset comparison
- Report
- App status
- Maintenance
- Help & assumptions

## Why this matters

The simulator now has enough features that one interface is no longer ideal for every use case.
Customer view keeps the product focused on decision support, while Developer view preserves the tools needed for local testing, release checks, and maintenance.

## Files changed

- `app/paid_simulator/config_form_app.py`

## Files preserved

- `app/run_paid_simulator_form.py`
- `app/paid_simulator/product_info.py`
- `app/paid_simulator/dashboard_status.py`
