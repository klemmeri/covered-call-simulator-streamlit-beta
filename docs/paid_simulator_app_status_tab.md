# Paid Simulator App Status Tab

This checkpoint adds an **App status** tab to the Streamlit paid simulator dashboard.

## Files added or replaced

- `app/paid_simulator/config_form_app.py`
- `app/run_paid_simulator_form.py`
- `app/paid_simulator/dashboard_status.py`
- `app/run_paid_simulator_status.py`
- `docs/paid_simulator_app_status_tab.md`

## What the App status tab checks

- Active dashboard build/version label
- Project root
- Active paid simulator config summary
- Required application files
- Generated output files
- Optional dashboard files such as run history and preset comparison CSVs

## Expected result

The tab should show **Overall status: PASS** when all required files and main outputs are present.
If some generated outputs are missing, run the paid simulator from the **Setup & run** tab.
