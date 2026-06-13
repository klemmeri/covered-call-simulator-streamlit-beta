# Paid Simulator Dashboard v0.1 — Release Notes

## Current release status

The paid simulator dashboard is currently a local Streamlit prototype. The latest verified state has passed:

- Paid simulator health check
- App status tab check
- Release-check script
- Config JSON validation
- Scenario comparison row check
- Run-history row check
- Preset-comparison row check

## Current major dashboard capabilities

- Preset-based configuration loading
- Config editing and JSON save
- Config backup on save
- Configuration validation
- Paid simulator run button
- Health check button
- Overview dashboard
- Latest results summary
- Plain-English interpretation
- Decision guidance
- Scenario detail cards
- Markdown decision memo export
- PDF decision memo export
- Run history dashboard
- Preset comparison dashboard
- Recommended preset display
- HTML report open/folder buttons
- App status tab
- Maintenance tab
- Help & assumptions tab

## Current output files

The dashboard and simulator currently use or generate these key outputs:

```text
config\paid_simulator_config.json
outputs\tables\paid_simulator\scenario_comparison.csv
outputs\tables\paid_simulator\config_echo.csv
outputs\tables\paid_simulator\run_history.csv
outputs\tables\paid_simulator\preset_comparison.csv
outputs\reports\paid_simulator\scenario_comparison_report.html
outputs\reports\paid_simulator\decision_memos
```

## Current commercial-product direction

The dashboard is moving from development prototype toward commercial packaging. The near-term goal is not to add more simulator complexity, but to make the existing workflow clearer, more stable, and more customer-facing.

## Recommended next integration step

Integrate the product metadata from:

```text
app\paid_simulator\product_info.py
```

into the Streamlit dashboard header, Overview tab, App status tab, and generated decision memos.

This will standardize the product name, version, build label, and limitations across the interface and exported artifacts.
