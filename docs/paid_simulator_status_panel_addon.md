# Paid Simulator Status Panel Add-On

This add-on introduces read-only dashboard status utilities for the Covered Call Simulator project.

## Added files

```text
app\paid_simulator\dashboard_status.py
app\run_paid_simulator_status.py
```

## Purpose

The status utilities check whether the paid simulator dashboard has the expected working files and generated outputs:

- `config\paid_simulator_config.json`
- `app\run_paid_simulator.py`
- `app\run_paid_simulator_health_check.py`
- `app\run_paid_simulator_form.py`
- `app\paid_simulator\config_form_app.py`
- `outputs\tables\paid_simulator\scenario_comparison.csv`
- `outputs\tables\paid_simulator\config_echo.csv`
- `outputs\reports\paid_simulator\scenario_comparison_report.html`
- `outputs\tables\paid_simulator\run_history.csv`
- `outputs\tables\paid_simulator\preset_comparison.csv`

## Safe behavior

These files are read-only utilities. They do not alter simulator logic, the config JSON, or generated output files.

## Standalone test

Run this in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_status.py
```

The console should show an overall status of `PASS` or `REVIEW`, followed by required-file and output-file tables.

## Intended next integration

After the standalone checker is verified, the same `dashboard_status.py` functions can be used to add a true `App status` tab inside the Streamlit dashboard.
