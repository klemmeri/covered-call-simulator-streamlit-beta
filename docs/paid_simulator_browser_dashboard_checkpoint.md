# Paid Simulator Browser Dashboard Checkpoint

Project root:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Checkpoint purpose:

This document records the current development state of the Covered Call Simulator paid browser interface after the Streamlit dashboard expansion. It is intended to preserve continuity across chats and prevent the main product goals from being lost.

---

## 1. Current working state

The paid simulator now has a working Streamlit browser interface launched from:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_form.py
```

The main Streamlit app file is:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\paid_simulator\config_form_app.py
```

The form edits:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\config\paid_simulator_config.json
```

The core simulator still runs from:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator.py
```

The health check still runs from:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_health_check.py
```

The verified paid simulator output files are:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\tables\paid_simulator\scenario_comparison.csv
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\tables\paid_simulator\config_echo.csv
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\reports\paid_simulator\scenario_comparison_report.html
```

The latest known health-check state was:

```text
PASS: Paid simulator outputs are present and structurally valid.
```

---

## 2. Current Streamlit dashboard tabs

The browser interface has been reorganized into tabs.

Current tab structure:

```text
Overview
Setup & run
Latest results
Run history
Preset comparison
Report
Help & assumptions
Maintenance
```

### Overview

Read-only executive summary of the current simulator state, including configuration status, latest result metrics, decision guidance, and recommended next action.

### Setup & run

Primary user workflow:

```text
Choose preset
Edit setup fields
Validate configuration
Save configuration
Run simulator
Run health check
```

### Latest results

Displays the latest scenario comparison, including:

```text
Best relative result
Worst relative result
Average relative result
Plain-English interpretation
Decision guidance
Scenario detail cards
Decision memo export
Decision memo PDF export
```

### Run history

Tracks repeated simulator runs in:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\tables\paid_simulator\run_history.csv
```

### Preset comparison

Runs multiple preset configurations and records results in:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\tables\paid_simulator\preset_comparison.csv
```

Includes a recommended preset panel and compact comparison output.

### Report

Provides access to the full generated HTML report:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\reports\paid_simulator\scenario_comparison_report.html
```

### Help & assumptions

Customer-facing explanation of what the simulator does, input definitions, output definitions, usage guidance, and limitations.

### Maintenance

Safe housekeeping tools:

```text
Reset config to clean demo
Clear run history CSV
Clear preset comparison CSV
Open project root
Open paid simulator outputs folder
Open decision memo folder
```

---

## 3. Current input fields

The browser form currently supports these paid simulator inputs:

```text
Ticker
Account size
Risk tier
Max position size / position-size cap
Contracts / desired contracts
Call delta target
Days to expiration / target DTE
Management rule
Rolling rule
Re-entry rule
Transaction cost
Slippage assumption
Stock price / demo price
```

Advanced settings are collapsed where appropriate to reduce clutter.

---

## 4. Presets currently supported

The current preset system includes:

```text
Clean demo - balanced, 1 contract
Conservative income - lower delta
Aggressive income - higher cap
Shorter-term theta demo
```

The preset comparison feature can run selected presets in sequence and identify the best preset by average relative result.

---

## 5. Current decision-output logic

The dashboard is intended to help the user answer:

```text
Is this covered-call setup worth opening under the modeled scenarios?
```

Current decision-oriented outputs include:

```text
Plain-English interpretation
Decision guidance
Recommended next action
Recommended preset
Scenario detail cards
Decision memo export
PDF decision memo export
```

The decision logic is intentionally cautious. Covered calls can underperform buy-and-hold in strong rallies because the short call caps upside. Therefore, negative relative performance versus buy-and-hold is not automatically a bug. It may reflect the expected covered-call tradeoff.

---

## 6. Current generated memo outputs

Markdown and PDF decision memos are saved under:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\outputs\reports\paid_simulator\decision_memos
```

These are intended to become customer-facing export artifacts.

---

## 7. Important design principle

The paid product should not merely show raw simulation output. It should help the user make a decision.

Preferred product flow:

```text
1. Configure setup
2. Validate setup
3. Run simulator
4. Summarize expected tradeoff
5. Give decision guidance
6. Allow scenario inspection
7. Export a memo/report
8. Track and compare alternative assumptions
```

Raw tables should generally be hidden behind expanders. Decision summaries should appear before diagnostics.

---

## 8. Current limitations

The current paid simulator remains a structured demo/prototype. It is not yet a production trading engine.

Known limitations:

```text
Scenario paths are modeled examples, not forecasts.
Option prices and Greeks are simplified/demo-oriented unless connected to live data later.
Regime detection should be treated as probabilistic guidance, not an oracle.
Covered-call underperformance in strong rallies is expected.
The browser interface is local Streamlit, not yet a deployed commercial website.
```

---

## 9. Recommended next development phase

The next recommended phase is to improve the dashboard’s commercial polish and reliability before adding major new simulation complexity.

Recommended near-term tasks:

```text
1. Add an App Status / Version panel.
2. Add a startup self-check that confirms required files and output folders exist.
3. Add a dashboard theme pass: consistent section headers, compact metrics, less vertical whitespace.
4. Add clearer labels for negative relative performance so users understand underperformance versus buy-and-hold.
5. Add a "customer mode" toggle to hide development diagnostics.
6. Add a "developer mode" toggle to expose raw CSVs, file paths, and troubleshooting tools.
7. Add documentation links from the Help tab to checkpoint docs.
```

Recommended medium-term tasks:

```text
1. Add real option-chain input or import capability.
2. Add user-defined scenario paths.
3. Add regime templates: calm, choppy, rally, selloff, high-vol, low-vol.
4. Add position-sizing recommendations tied to account size and risk tier.
5. Add a deployable website version after local Streamlit workflow is stable.
```

---

## 10. File replacement convention

For future development, continue using full replacement files or zips.

Default replacement files for browser-dashboard changes:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_form.py
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\paid_simulator\config_form_app.py
```

When installing a zip, extract directly into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Allow Windows to merge/replace files.

