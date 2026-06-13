# Paid Simulator Checkpoint Handoff

This checkpoint records the current working state of the paid Covered Call Simulator prototype.

## Project root

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Use this folder as the extraction target for all update zip files.

## Current clean demo config

The current recommended demo setting is:

```json
"desired_contracts": 1
```

This produces a valid green-path result:

```text
Decision signal: Sizing rule passed
Next action: Review upside tradeoff
```

The two-contract warning path has already been tested and works:

```json
"desired_contracts": 2
```

Expected warning-path behavior:

```text
Decision signal: Analyze with caution
Next action: Reduce contract count or adjust sizing
Sizing warning appears in the Position Sizing section
```

After warning-path testing, return the config to:

```json
"desired_contracts": 1
```

## Main run commands

Run the paid simulator from PyCharm:

```text
app\run_paid_simulator.py
```

Then optionally run the health check:

```text
app\run_paid_simulator_health_check.py
```

Expected health-check result:

```text
PASS: Paid simulator outputs are present and structurally valid.
```

## Current verified output files

The simulator currently creates:

```text
outputs\tables\paid_simulator\scenario_comparison.csv
outputs\tables\paid_simulator\config_echo.csv
outputs\reports\paid_simulator\scenario_comparison_report.html
```

The launcher opens the HTML report automatically.

## Current verified console sections

The PyCharm console output includes:

```text
Active paid simulator config
Position-sizing summary
Scenario comparison
Scenario comparison summary
Paid simulator decision summary
Saved outputs
Simulation note
Smoke test complete
```

The new console decision summary reports:

```text
Decision signal
Next action
Best environment
Worst environment
Desired contracts
Maximum contracts
Position-size cap
```

## Current verified HTML report sections

The paid simulator report currently contains:

```text
Covered Call Strategy Stress Test
Print / Save PDF
Summary
Plain-English Takeaway
Decision signal
Next action
Covered-Call Profile
Strategy Setup
Methodology and Assumptions
Selected Option
Position Sizing
What Changed Versus Buy-and-Hold?
Comparison Chart
How to Interpret the Scenario Labels
Market Path Comparison Table
Detailed Path Reports
How to Read This Stress Test
Important Limitations
```

## Current verified one-contract results

With:

```json
"desired_contracts": 1
```

expected approximate scenario differences are:

```text
Moderate Uptrend:      -$493
Downtrend:             +$452
Sideways Choppy:         -$1
Volatile Two-Sided:    -$209
Strong Rally:        -$2,880
```

The health check confirmed:

```text
Scenario comparison CSV columns: PASS
Config echo CSV fields: PASS
Decision signal: Sizing rule passed
Next action: Review upside tradeoff
Overall health-check result: PASS
```

## Current verified two-contract results

With:

```json
"desired_contracts": 2
```

expected approximate scenario differences are:

```text
Moderate Uptrend:      -$986
Downtrend:             +$904
Sideways Choppy:         -$2
Volatile Two-Sided:    -$418
Strong Rally:        -$5,760
```

This verifies that path P/L scales to `desired_contracts`.

## Important accounting checkpoint

Do not revert the buy-and-hold benchmark fix.

The benchmark must remain anchored to the original entry price throughout the path.

Prior audit result:

```text
max_buy_hold_benchmark_error: 0.0
max_final_equity_identity_error: 0.0
max_reported_difference_error: 0.0
```

## Key files in the paid simulator

```text
app\run_paid_simulator.py
app\run_paid_simulator_health_check.py
app\paid_simulator\runner.py
app\paid_simulator\scenario_comparison.py
app\paid_simulator\scenario_comparison_report.py
app\paid_simulator\scenario_library.py
app\paid_simulator\session_config.py
app\paid_simulator\position_sizing.py
app\paid_simulator\trade_execution.py
app\paid_simulator\path_update.py
app\paid_simulator\path_runner.py
docs\paid_simulator_workflow.md
docs\paid_simulator_checkpoint_handoff.md
```

## Current standard install workflow

When installing a generated zip:

1. Download the zip.
2. Right-click the zip in Windows.
3. Choose **Extract All**.
4. Extract into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

5. Choose:

```text
Replace the files in the destination
```

6. Run:

```text
app\run_paid_simulator.py
```

7. Run:

```text
app\run_paid_simulator_health_check.py
```

## Recommended next development direction

The report layer is now strong enough for a paid-simulator prototype. The next development phase should move from report polish to product capability.

Recommended next step:

```text
Start building a simple paid-simulator input screen.
```

The first UI goal should be modest:

```text
Allow the user to edit the paid simulator config from a browser form
and then run the existing simulator using those inputs.
```

Suggested fields for the first UI form:

```text
Ticker
Account size
Risk tier
Position-size cap
Desired contracts
Target delta
Target DTE
Management rule
Rolling rule
Re-entry rule
Transaction cost
Slippage assumption
Demo price
```

The initial UI does not need real market data. It can continue using the current illustrative engine and config file.

## Suggested next files to create

The next likely files are:

```text
app\paid_simulator\config_form_app.py
app\run_paid_simulator_form.py
```

Purpose:

```text
config_form_app.py
    Streamlit form for editing config\paid_simulator_config.json.

run_paid_simulator_form.py
    Launcher that starts the Streamlit config form from PyCharm.
```

Keep the first version simple. The form should write the JSON config, then instruct the user to run:

```text
app\run_paid_simulator.py
```

A later version can add an integrated Run Simulation button.
