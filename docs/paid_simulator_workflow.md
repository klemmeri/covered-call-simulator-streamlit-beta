# Paid Simulator Workflow

This document summarizes the current verified workflow for the paid Covered Call Simulator prototype.

## Project root

All project files are under:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Use this folder as the extraction target when installing update zip files.

## Main launcher

Run this file from PyCharm:

```text
app\run_paid_simulator.py
```

This launcher runs:

```text
app\paid_simulator\runner.py
```

and opens the generated browser report automatically.

## Active config file

The paid simulator is controlled by:

```text
config\paid_simulator_config.json
```

The current clean demo setting is:

```json
"desired_contracts": 1
```

This produces a valid sizing result:

```text
Decision signal: Sizing rule passed
Requested contracts: 1 | Maximum contracts allowed: 1 | Position-size cap: 10.00%
```

The warning path has also been tested by temporarily setting:

```json
"desired_contracts": 2
```

That correctly produces:

```text
Decision signal: Analyze with caution
Requested contracts: 2 | Maximum contracts allowed: 1 | Position-size cap: 10.00%
```

## Verified current behavior

The paid simulator currently verifies the following:

```text
Multi-contract path scaling:       Verified
One-contract green path:           Verified
Two-contract warning path:         Verified
Position-size screen:              Verified
Decision signal box:               Verified
Next action box:                   Verified
Plain-English Takeaway:            Verified
Covered-Call Profile section:      Verified
Strategy Setup section:            Verified
Methodology and Assumptions:       Verified
Selected Option section:           Verified
Position Sizing section:           Verified
Buy-and-hold explanation section:  Verified
Market Path Comparison labels:     Verified
Scenario label guide:              Verified
Print / Save PDF button:           Verified
Console decision summary:          Verified
Detailed Path Reports links:       Verified
```

## Current report output

The simulator writes the main comparison report to:

```text
outputs\reports\paid_simulator\scenario_comparison_report.html
```

It also writes the comparison CSV to:

```text
outputs\tables\paid_simulator\scenario_comparison.csv
```

The launcher opens the HTML report automatically.

## Current report sections

The main HTML report currently contains:

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

## Current console sections

The PyCharm console output currently contains:

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

The new console decision summary mirrors the key HTML report conclusions:

```text
Paid simulator decision summary
--------------------------------------------------------------------------------------------
Decision signal:        Sizing rule passed
Next action:            Review upside tradeoff
Best environment:       Downtrend (+$452.00)
Worst environment:      Strong Rally (-$2,880.00)
Desired contracts:      1
Maximum contracts:      1
Position-size cap:      10.00%
--------------------------------------------------------------------------------------------
```

## Current clean-demo state

The recommended default for demonstrations is:

```json
"desired_contracts": 1
```

This keeps the report in the green path:

```text
Decision signal: Sizing rule passed
Next action: Review upside tradeoff
```

This is cleaner for a first paid-user demonstration because the setup is valid under the selected position-size rule.

## Warning-path test

To test the warning path, temporarily set:

```json
"desired_contracts": 2
```

Expected behavior:

```text
Decision signal: Analyze with caution
Next action: Reduce contract count or adjust sizing
Sizing warning appears in the Position Sizing section
Console decision summary also changes to Analyze with caution
```

After the test, return the config to:

```json
"desired_contracts": 1
```

## Verified one-contract output

With:

```json
"desired_contracts": 1
```

the scenario results return to the expected one-contract values:

```text
Moderate Uptrend:      about -$493
Downtrend:             about +$452
Sideways Choppy:       about -$1
Volatile Two-Sided:    about -$209
Strong Rally:          about -$2,880
```

The report should show:

```text
Best covered-call relative result:  +$452.00
Worst covered-call relative result: -$2,880.00
```

## Verified two-contract output

With:

```json
"desired_contracts": 2
```

the scenario results scale approximately 2x:

```text
Moderate Uptrend:      about -$986
Downtrend:             about +$904
Sideways Choppy:       about -$2
Volatile Two-Sided:    about -$418
Strong Rally:          about -$5,760
```

The report should show the caution decision signal because 2 contracts violates the 10% position-size cap for the current account size and SPY price.

## Important accounting checkpoint

Do not revert the benchmark accounting fix.

The previous audit showed:

```text
max_buy_hold_benchmark_error: 0.0
max_final_equity_identity_error: 0.0
max_reported_difference_error: 0.0
```

The buy-and-hold benchmark must remain anchored to the original entry price throughout the path.

## Key paid simulator files

```text
app\paid_simulator\runner.py
app\paid_simulator\scenario_comparison.py
app\paid_simulator\scenario_comparison_report.py
app\paid_simulator\scenario_library.py
app\paid_simulator\session_config.py
app\paid_simulator\position_sizing.py
app\paid_simulator\trade_execution.py
app\paid_simulator\path_update.py
app\paid_simulator\path_runner.py
```

## Standard PyCharm run workflow

1. Open the project in PyCharm.
2. Confirm the project root is:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

3. Open:

```text
config\paid_simulator_config.json
```

4. For a clean demo, use:

```json
"desired_contracts": 1
```

5. Run:

```text
app\run_paid_simulator.py
```

6. Confirm the browser report opens.
7. Check the decision signal, next action, and summary values in both the HTML report and the PyCharm console.

## Standard update zip install workflow

When installing a generated update zip:

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

## Current paid-report purpose

The current report is designed as a paid-simulator prototype report. It is not just a developer output. It now tells a paid user:

```text
What setup was tested
Which option was selected
Whether sizing passed
What the practical next action is
How the covered call behaved versus buy-and-hold
Which market paths helped or hurt
What assumptions and limitations apply
```

## Recommended next enhancements

The next logical development items are:

1. Add a compact **Config Echo CSV** for easier audit.
2. Add input controls later through the website UI instead of editing `paid_simulator_config.json` directly.
3. Add a true option-pricing model later, replacing simplified marks.
4. Add dividend and early-assignment assumptions later.
5. Preserve regime-detection language as probabilistic guidance, not an oracle.

## Current recommended default

Leave the config at:

```json
"desired_contracts": 1
```

This is the best default for a clean paid-simulator demonstration because it shows a valid trade setup and a green sizing pass.
