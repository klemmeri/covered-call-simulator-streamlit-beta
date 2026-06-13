# Covered Call Simulator — Handoff to New Chat

## Project root

All project files are in:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Use this as the project root when extracting any zip files.

Do not extract project-update zips into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app
```

or:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\paid_simulator
```

unless explicitly instructed. Most update zips should be extracted into the project root:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

When Windows asks about duplicate files, choose:

```text
Replace the files in the destination
```

---

## Current main paid simulator launcher

The clean top-level launcher is:

```text
app\run_paid_simulator.py
```

Run this from PyCharm.

It executes:

```text
app\paid_simulator\runner.py
```

with the correct working directory:

```text
app\paid_simulator
```

The launcher also opens the generated browser report automatically.

---

## Current config file

The paid simulator is now controlled by:

```text
config\paid_simulator_config.json
```

Current config is expected to include fields similar to:

```json
{
  "session_id": "demo_session_001",
  "ticker": "SPY",
  "account_size": 600000.0,
  "risk_tier": "Balanced",
  "position_size_cap": 0.10,
  "desired_contracts": 2,
  "target_delta": 0.30,
  "target_dte": 30,
  "strike_selection_method": "Closest to target delta",
  "management_rule": "Close at 50% profit",
  "profit_take_percent": 0.50,
  "rolling_rule": "Roll only for net credit",
  "reentry_rule": "Wait 10 days",
  "transaction_cost_per_contract": 1.00,
  "slippage_assumption": 0.01,
  "data_source": "illustrative",
  "mode": "historical_active_replay",
  "demo_price": 545.25,
  "demo_previous_close": 543.80,
  "demo_daily_return": 0.0027
}
```

The config system was tested successfully. The PyCharm output showed:

```text
Config exists:  True
Account size:   $600,000.00
```

Changing `account_size` from `100000.0` to `600000.0` worked correctly.

---

## Current verified output

The latest successful run of:

```text
app\run_paid_simulator.py
```

showed the active config:

```text
Config file:    C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\config\paid_simulator_config.json
Config exists:  True
Ticker:         SPY
Account size:   $600,000.00
Risk tier:      Balanced
Position cap:   10.00%
Target delta:   0.3
Target DTE:     30
Demo price:     $545.25
```

It also showed the position-sizing summary:

```text
Position-sizing summary
--------------------------------------------------------------------------------------------
Ticker:                         SPY
Account size:                   $600,000.00
Risk tier:                      Balanced
Position-size cap:              10.00%
Underlying price:               $545.25
Contract multiplier:            100
Stock value per contract:       $54,525.00
Allowed position value:         $60,000.00
Minimum equity for 1 contract:  $545,250.00
Maximum contracts allowed:      1
Passes account screen:          True
Remaining position capacity:    $5,475.00
Extra equity needed for 1:      $0.00
```

After adding `desired_contracts`, the browser report correctly showed:

```text
Desired contracts:         2
Maximum contracts allowed: 1
Passes screen:             False
Desired position value:    $109,050.00
Allowed position value:    $60,000.00
Equity needed for desired: $1,090,500.00
Extra equity needed:       $490,500.00
```

This is correct because, with a $600,000 account and 10% position cap, the allowed position value is only $60,000. Two SPY covered-call contracts require approximately $109,050 of stock exposure.

---

## Current scenario comparison behavior

Before multi-contract path scaling, the scenario comparison was still modeled on one covered-call contract.

The corrected one-contract scenario comparison was:

```text
Scenario                  Covered Call      Buy & Hold      Difference     Final Stock
--------------------------------------------------------------------------------------------
Moderate Uptrend           $601,314.00     $601,807.00        -$493.00         $563.32
Downtrend                  $598,406.00     $597,954.00        +$452.00         $524.79
Sideways Choppy            $600,158.00     $600,159.00          -$1.00         $546.84
Volatile Two-Sided         $600,661.00     $600,870.00        -$209.00         $553.95
Strong Rally               $603,228.00     $606,108.00      -$2,880.00         $606.33
```

Summary:

```text
Best scenario: Downtrend (+$452.00)
Worst scenario: Strong Rally (-$2,880.00)
```

This is economically sensible: covered calls help in a downtrend and lag in a strong rally.

---

## Important accounting fix already completed

A previous accounting audit found that the buy-and-hold benchmark had been wrong because it was being reset at each path step.

That was fixed.

The audit after the fix showed:

```text
max_buy_hold_benchmark_error: 0.0
max_final_equity_identity_error: 0.0
max_reported_difference_error: 0.0
```

The corrected benchmark now uses the original entry stock price through the entire path.

This fix is important. Do not revert it.

---

## Current output files

The paid simulator produces:

```text
outputs\tables\paid_simulator\scenario_comparison.csv
```

and:

```text
outputs\reports\paid_simulator\scenario_comparison_report.html
```

The launcher opens the HTML report automatically.

Per-scenario detailed reports are also generated, for example:

```text
outputs\reports\paid_simulator\demo_session_001_moderate_uptrend_paid_simulator_report.html
outputs\reports\paid_simulator\demo_session_001_downtrend_paid_simulator_report.html
outputs\reports\paid_simulator\demo_session_001_sideways_choppy_paid_simulator_report.html
outputs\reports\paid_simulator\demo_session_001_volatile_two_sided_paid_simulator_report.html
outputs\reports\paid_simulator\demo_session_001_strong_rally_paid_simulator_report.html
```

---

## Current scenario library

The paid simulator currently tests five deterministic scenarios:

```text
moderate_uptrend
downtrend
sideways_choppy
volatile_two_sided
strong_rally
```

They are defined in:

```text
app\paid_simulator\scenario_library.py
```

The scenario system is working.

---

## Key paid simulator modules

Current paid simulator package:

```text
app\paid_simulator\__init__.py
app\paid_simulator\account.py
app\paid_simulator\accounting_audit.py
app\paid_simulator\html_chart.py
app\paid_simulator\html_report.py
app\paid_simulator\models.py
app\paid_simulator\option_candidates.py
app\paid_simulator\path_report.py
app\paid_simulator\path_runner.py
app\paid_simulator\path_update.py
app\paid_simulator\position_sizing.py
app\paid_simulator\pre_trade.py
app\paid_simulator\report_reader.py
app\paid_simulator\runner.py
app\paid_simulator\scenario_comparison.py
app\paid_simulator\scenario_comparison_report.py
app\paid_simulator\scenario_library.py
app\paid_simulator\session_config.py
app\paid_simulator\trade_execution.py
```

Important current responsibilities:

```text
session_config.py
    Reads config\paid_simulator_config.json and builds SimulationInput / TickerSnapshot.

position_sizing.py
    Calculates stock value per contract, allowed position value, minimum equity,
    max contracts allowed, desired contract pass/fail, and extra equity needed.

scenario_comparison.py
    Runs all scenarios and writes scenario_comparison.csv.

scenario_comparison_report.py
    Builds scenario_comparison_report.html, including Summary, Position Sizing,
    Comparison Chart, Scenario Comparison Table, Individual Scenario Reports,
    Interpretation, and Important Limitations.

trade_execution.py
    Builds opening covered-call trade and position state.

path_update.py / path_runner.py
    Run the multi-step path and benchmark accounting.

run_paid_simulator.py
    Top-level PyCharm launcher.
```

---

## Most recent generated zip pending installation

The latest generated update was:

```text
paid_simulator_multicontract_path_step.zip
```

It was created to make the actual path simulation scale to:

```json
"desired_contracts": 2
```

The user had not yet installed and tested this zip before asking for the handoff.

That zip updates:

```text
app\paid_simulator\trade_execution.py
app\paid_simulator\path_update.py
app\paid_simulator\scenario_comparison.py
app\paid_simulator\runner.py
app\paid_simulator\scenario_comparison_report.py
```

Expected effect after installing and running:

```text
Downtrend difference should roughly double from +$452 to about +$904.
Strong Rally difference should roughly double from -$2,880 to about -$5,760.
```

The report should still show the sizing warning because `desired_contracts = 2` fails the 10% cap.

Important: this update should be installed next, then tested by running:

```text
app\run_paid_simulator.py
```

---

## Expected next test after installing multi-contract path scaling

After installing `paid_simulator_multicontract_path_step.zip`, with this config:

```json
"account_size": 600000.0,
"position_size_cap": 0.10,
"desired_contracts": 2
```

The position-sizing report should still show:

```text
Desired contracts:              2
Maximum contracts allowed:      1
Desired contracts pass screen:  False
```

But the scenario P/L differences should now scale to two contracts.

Expected approximate differences:

```text
Moderate Uptrend:      about -$986
Downtrend:             about +$904
Sideways Choppy:       about -$2
Volatile Two-Sided:    about -$418
Strong Rally:          about -$5,760
```

If these do not scale, inspect:

```text
app\paid_simulator\trade_execution.py
app\paid_simulator\path_update.py
app\paid_simulator\scenario_comparison.py
```

The intended logic is:

```text
shares = 100 * desired_contracts
short_call_quantity = -desired_contracts
premium = selected_option.estimated_premium * desired_contracts
short-call liability = option_mark * 100 * desired_contracts
buy-and-hold benchmark uses the same share count as the covered-call stock position
```

---

## Important caution

The simulator currently uses illustrative demo inputs:

```text
SPY price:        $545.25
Option premium:   $454 per contract
Strike:           573
Delta:            0.31
DTE:              30
```

The option candidate data is still synthetic / illustrative, not live market data.

The option-mark model is simplified:

```text
new option mark ~= old mark + delta * stock move - small time decay
bounded by intrinsic value and 0.01
```

The simulator is not yet using a full option-pricing model, real options chains, bid/ask dynamics, dividends, early assignment, taxes, or volatility changes.

---

## Public-facing wording to preserve

Use cautious language:

```text
Tradable means the ticker passes the selected account-size and position-size screen.
It does not mean the trade is recommended.
```

Also preserve:

```text
Regime detection is probabilistic guidance, not an oracle.
```

Do not present the simulator as a trade signal service.

---

## User preferences

The user prefers:

```text
Full replacement scripts/files rather than partial patches.
Step-by-step PyCharm instructions.
Downloadable zip files for project updates.
Replacing files via Windows Extract All.
Clear "run this file next" instructions.
```

When suggesting new project files, also generate the actual file or zip immediately.

---

## Recommended next action in the new chat

1. Confirm whether `paid_simulator_multicontract_path_step.zip` has been installed.
2. If not, provide step-by-step instructions to extract it into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

3. Run:

```text
app\run_paid_simulator.py
```

4. Verify that scenario differences scale approximately 2x for `desired_contracts = 2`.
5. If it works, the next logical enhancement is to add an explicit **Sizing Warning** banner/card to the HTML report when:

```text
desired_contracts_pass_screen = False
```

This banner should say something like:

```text
Sizing warning: The requested number of contracts exceeds the selected position-size cap.
The simulation is shown for analysis, but this contract count is not tradable under the current sizing rule.
```

If adding this banner, generate a full replacement zip immediately.
