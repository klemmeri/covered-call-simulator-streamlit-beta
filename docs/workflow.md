# Covered Call Simulator Workflow Notes

This project simulates and compares covered-call management rules across market regimes, DTE assumptions, transaction-cost assumptions, historical ticker profiles, rolling regime classifications, and rolling strategy-validation windows.

Project folder:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

## 1. Current Project Status

The research layer is now stable.

The simulator currently runs:

```text
6 market regimes x 11 management-rule variants = 66 experiments
```

The main simulator supports:

```text
standard mode:
    250 simulated paths per experiment

robustness mode:
    1000 simulated paths per experiment
```

The core research conclusion is:

```text
AdaptiveRegimeDTECost remains the strongest current candidate rule.
```

The most recent compact dashboard report gave a final status of:

```text
PASS
```

The dashboard confirmed that `AdaptiveRegimeDTECost` was not materially worse than the best fixed rule in either:

```text
historical-window validation
rolling-window strategy validation
```

## 2. Monte Carlo Method

The simulator uses a Monte Carlo method.

It does not test only one possible future stock path. Instead, it creates many possible future stock-price paths, runs each covered-call rule on each path, and summarizes the average result.

Each simulated path is one possible future year for the stock or ETF.

For each path, the simulator asks:

```text
How would HoldToExpiration perform?
How would Close50 perform?
How would Wait10d perform?
How would the adaptive rule perform?
```

Then the simulator compares the average performance across all paths.

Robustness mode is useful because more paths reduce random noise.

## 3. Market Regimes

The six market regimes are:

```text
baseline
sideways_market
bullish_market
bearish_market
high_volatility
low_volatility
```

Regime detection should be treated as probabilistic guidance, not as an oracle.

## 4. Current Management Rules

The simulator currently tests:

```text
hold_to_expiration
close_at_50_percent_profit
close_at_50_percent_profit_then_wait_1d
close_at_50_percent_profit_then_wait_3d
close_at_50_percent_profit_then_wait_5d
close_at_50_percent_profit_then_wait_10d
close_at_50_percent_profit_then_pullback_or_wait_2pct_10d
close_at_50_percent_profit_then_pullback_or_wait_3pct_10d
adaptive_close50_wait10_by_regime
adaptive_close50_wait10_by_regime_and_cost
adaptive_by_regime_dte_cost
```

Display labels:

```text
adaptive_close50_wait10_by_regime          -> AdaptiveClose50Wait10
adaptive_close50_wait10_by_regime_and_cost -> AdaptiveClose50Wait10CostAware
adaptive_by_regime_dte_cost                -> AdaptiveRegimeDTECost
```

## 5. Current Candidate Rule

The current candidate rule is:

```text
AdaptiveRegimeDTECost
```

Rule name in code:

```text
adaptive_by_regime_dte_cost
```

This rule adapts to:

```text
market regime
DTE
transaction costs
```

### Rule Logic

```text
If regime is bearish_market:
    Close at 50% profit and immediately resell.

If regime is sideways_market:
    If DTE <= 14:
        Hold to expiration.

    If DTE >= 21:
        Close at 50% profit and immediately resell,
        unless transaction costs are high.

    If transaction costs are high:
        Hold to expiration.

If regime is baseline, bullish_market, high_volatility, or low_volatility:
    If DTE < 45:
        Close at 50% profit, then wait 10 trading days before reselling.

    If DTE >= 45:
        Hold to expiration.
```

At the current default DTE and low transaction costs, this rule behaves like the simpler adaptive rules. Its advantage is that it has explicit logic for short-DTE and long-DTE cases.

## 6. Transaction-Cost Model

Current standard assumptions in `app\config.py`:

```python
option_commission_per_contract: float = 0.65
option_slippage_per_share: float = 0.01
```

Transaction-cost accounting:

```text
Selling a call:
    gross premium = model option price x shares
    sell slippage = option_slippage_per_share x shares
    sell commission = option_commission_per_contract x contracts
    net premium = gross premium - slippage - commission

Buying back a call:
    gross buyback = model option price x shares
    buyback slippage = option_slippage_per_share x shares
    buyback commission = option_commission_per_contract x contracts
    total buyback cost = gross buyback + slippage + commission
```

Sideways-market high-cost threshold:

```text
commission >= $1.25 per contract
or
slippage >= $0.025 per share
```

## 7. Key Research Results

### 7.1 Transaction-Cost Sensitivity

Scripts:

```text
app\cost_sensitivity.py
app\cost_threshold_search.py
```

Main conclusion:

```text
bearish_market:
    Close50 remains preferred across tested transaction costs.

sideways_market:
    Close50 stops being preferred when transaction costs are high.
```

The sideways-market high-cost threshold is:

```text
commission = $1.25 per contract
slippage = $0.025 per share
```

### 7.2 DTE Sensitivity

Scripts:

```text
app\dte_sensitivity.py
app\dte_decision_map.py
```

DTE values tested:

```text
7
14
21
30
45
```

Confirmed DTE decision map:

```text
Regime             7DTE       14DTE      21DTE      30DTE      45DTE
baseline           Wait10d    Hold       Wait10d    Wait10d    Hold
sideways_market    Hold       Hold       Close50    Close50    Close50
bullish_market     Wait10d    Wait10d    Wait10d    Wait10d    Hold
bearish_market     Close50    Close50    Close50    Close50    Close50
high_volatility    Wait10d    Wait10d    Wait10d    Wait10d    Hold
low_volatility     Wait10d    Hold       Wait10d    Wait10d    Hold
```

This result justified adding DTE to the adaptive rule.

### 7.3 Delta Sensitivity

Scripts:

```text
app\delta_sensitivity.py
app\delta_decision_map.py
```

Target deltas tested:

```text
0.20
0.25
0.30
0.35
0.40
```

Conclusion:

```text
Do not add target_delta to adaptive rule logic yet.
```

The only exception was `low_volatility` at `target_delta = 0.20`, where `HoldToExpiration` was slightly preferred. The edge was only:

```text
0.0003
```

This was below the materiality threshold:

```text
0.0050
```

### 7.4 Ticker-Style Calibration

Script:

```text
app\ticker_calibration.py
```

Ticker-like profiles tested:

```text
SPY_like
QQQ_like
IWM_like
TQQQ_like
SOXL_like
```

Conclusion:

```text
Do not add ticker-specific logic yet.
```

All tested ticker-like profiles favored `Wait10d` or adaptive behavior.

### 7.5 Historical Ticker Calibration

Scripts:

```text
app\download_historical_prices.py
app\historical_ticker_calibration.py
```

Historical data:

```text
SPY
QQQ
IWM
TQQQ
SOXL
```

Date range:

```text
2020-01-02 to 2026-06-09
```

Detected full-period regimes:

```text
IWM   -> baseline
QQQ   -> bullish_market
SPY   -> bullish_market
TQQQ  -> high_volatility
SOXL  -> high_volatility
```

Main conclusion:

```text
Every completed ticker selected Wait10d as the best rule.
AdaptiveRegimeDTECost was not materially worse than the best rule.
```

Important caution:

```text
This does not mean covered calls beat buy-and-hold.

It means that, among the covered-call management rules tested, Wait10d was the least damaging rule in these upward-drifting or high-volatility historical profiles.
```

### 7.6 Historical Window Calibration

Script:

```text
app\historical_window_calibration.py
```

Historical windows tested:

```text
1Y
2Y
3Y
5Y
Full
```

Main result:

```text
Ticker/window cases completed:   25
Adaptive materially worse cases: 0
Tickers with unstable best rule: 0
```

Stable best rule:

```text
Wait10d
```

Interpretation:

```text
Wait10d was stable across broad historical lookback windows.

Even when IWM's detected regime changed between baseline and bullish_market, the best rule remained Wait10d.
```

### 7.7 Rolling Regime Detection

Script:

```text
app\rolling_regime_detection.py
```

Rolling windows tested:

```text
63 trading days
126 trading days
252 trading days
504 trading days
```

Preferred rolling window:

```text
252 trading days
```

Reason:

```text
63 days is too reactive.
504 days is stable but can lag.
252 days is roughly one trading year and gives a useful balance.
```

Latest 252-day classifications:

```text
IWM   -> bullish_market
QQQ   -> bullish_market
SPY   -> bullish_market
TQQQ  -> high_volatility
SOXL  -> high_volatility
```

### 7.8 Current Regime Snapshot

Script:

```text
app\current_regime_snapshot.py
```

The current 252-day snapshot maps all tested tickers to:

```text
Wait10d
```

Latest result:

```text
IWM   -> bullish_market    -> Wait10d
QQQ   -> bullish_market    -> Wait10d
SPY   -> bullish_market    -> Wait10d
TQQQ  -> high_volatility   -> Wait10d
SOXL  -> high_volatility   -> Wait10d
```

### 7.9 Rolling Strategy Calibration

Script:

```text
app\rolling_strategy_calibration.py
```

This goes beyond rolling regime detection.

Rolling regime detection asks:

```text
What regime was this ticker in?
```

Rolling strategy calibration asks:

```text
Which covered-call rule would have been preferred in each rolling historical window?
```

Settings:

```text
rolling window:
    252 trading days

rolling step:
    63 trading days

paths per experiment:
    250
```

Main result:

```text
Ticker/window cases completed:   115
Adaptive materially worse cases: 0
Tickers with unstable best rule: 5
```

Interpretation:

```text
The best fixed rule changes across rolling windows.

Bearish windows tend to favor Close50.

Bullish, baseline, and high-volatility upward-drifting windows tend to favor Wait10d.
```

This validates the adaptive logic.

Strongest validation result so far:

```text
AdaptiveRegimeDTECost was not materially worse than the best fixed rule in any of the 115 rolling ticker/window cases.
```

### 7.10 Strategy Dashboard Report

Script:

```text
app\strategy_dashboard_report.py
```

This script does not run new simulations.

It reads:

```text
outputs\tables\comparison\current_regime_snapshot.csv
outputs\tables\comparison\historical_window_calibration_winners.csv
outputs\tables\comparison\rolling_strategy_calibration_stability.csv
```

It creates:

```text
outputs\tables\comparison\strategy_dashboard_report.txt
```

Dashboard result:

```text
PASS
```

Dashboard conclusion:

```text
AdaptiveRegimeDTECost remains the strongest current candidate rule.

It was not materially worse than the best fixed rule in the historical-window or rolling-window validation tests.
```

This is now the compact status report for the research layer.

## 8. Regime Detection

Script:

```text
app\regime_detection.py
```

The first-pass detector uses:

```text
annual_return
annual_volatility
```

Current thresholds:

```python
BEARISH_RETURN_THRESHOLD = -0.020
SIDEWAYS_ABS_RETURN_THRESHOLD = 0.020
BULLISH_RETURN_THRESHOLD = 0.120
LOW_VOLATILITY_THRESHOLD = 0.150
SIDEWAYS_VOLATILITY_MAX = 0.220
BULLISH_VOLATILITY_MAX = 0.350
HIGH_VOLATILITY_THRESHOLD = 0.400
```

Rule order:

```text
1. If annual_return <= bearish threshold:
       bearish_market

2. Else if annual_volatility >= high-volatility threshold:
       high_volatility

3. Else if return is very near zero and volatility is not high:
       sideways_market

4. Else if return is strongly positive and volatility is not excessive:
       bullish_market

5. Else if volatility is very low:
       low_volatility

6. Otherwise:
       baseline
```

Diagnostic scripts:

```text
app\regime_detection_test.py
app\regime_detection_borderline_test.py
```

Borderline test result:

```text
Borderline cases tested:       25
Adaptive materially worse:     0
```

Recommendation:

```text
Keep regime detection standalone for now.
Do not wire regime detection into app\main.py yet.
```

## 9. Important Scripts

### Core Simulator

```text
app\main.py
```

Runs the full simulator batch.

Use:

```python
RUN_MODE = "standard"
```

for normal development.

Use:

```python
RUN_MODE = "robustness"
```

for 1000-path robustness testing.

### Portfolio Engine

```text
app\portfolio.py
```

Implements:

```text
hold_to_expiration
close_at_50_percent_profit
close_at_50_percent_profit_then_wait
close_at_50_percent_profit_then_pullback_or_wait
adaptive_close50_wait10_by_regime
adaptive_close50_wait10_by_regime_and_cost
adaptive_by_regime_dte_cost
transaction-cost accounting
```

### Reports

```text
app\reports.py
```

Creates:

```text
path-level reports
cycle-level reports
comparison reports
strategy_map.csv
```

### Final Summary

```text
app\summarize_results.py
```

Creates:

```text
outputs\tables\comparison\final_recommendation_report.txt
```

### Strategy Map Checker

```text
app\check_strategy_map.py
```

Expected result:

```text
OVERALL RESULT: PASS
```

### Strategy Dashboard

```text
app\strategy_dashboard_report.py
```

Creates the compact dashboard report:

```text
outputs\tables\comparison\strategy_dashboard_report.txt
```

This is now the best single-file summary of the research layer.

## 10. Main Output Files

Important outputs:

```text
outputs\tables\comparison\experiment_comparison.csv
outputs\tables\comparison\cycle_level_comparison.csv
outputs\tables\comparison\management_rule_comparison.csv
outputs\tables\comparison\management_rule_decision_summary.csv
outputs\tables\comparison\strategy_map.csv
outputs\tables\comparison\final_recommendation_report.txt
outputs\tables\comparison\key_rule_comparison_report.txt
outputs\tables\comparison\dte_sensitivity_report.txt
outputs\tables\comparison\dte_decision_map_report.txt
outputs\tables\comparison\delta_sensitivity_report.txt
outputs\tables\comparison\delta_decision_map_report.txt
outputs\tables\comparison\ticker_calibration_report.txt
outputs\tables\comparison\historical_ticker_calibration_report.txt
outputs\tables\comparison\historical_window_calibration_report.txt
outputs\tables\comparison\rolling_regime_detection_report.txt
outputs\tables\comparison\current_regime_snapshot_report.txt
outputs\tables\comparison\rolling_strategy_calibration_report.txt
outputs\tables\comparison\strategy_dashboard_report.txt
outputs\tables\comparison\regime_detection_report.txt
outputs\tables\comparison\regime_detection_test_report.txt
outputs\tables\comparison\regime_detection_borderline_report.txt
outputs\tables\comparison\adaptive_rule_chart_report.txt
outputs\tables\comparison\cost_sensitivity_report.txt
outputs\tables\comparison\cost_threshold_search_report.txt
```

## 11. Recommended Workflow

### Normal Use

```text
1. Set RUN_MODE = "standard" in app\main.py.
2. Run app\main.py.
3. Run app\check_strategy_map.py.
4. Run app\summarize_results.py.
5. Run app\strategy_dashboard_report.py.
6. Read outputs\tables\comparison\strategy_dashboard_report.txt.
```

### Robustness Testing

```text
1. Set RUN_MODE = "robustness" in app\main.py.
2. Run app\main.py.
3. Run app\check_strategy_map.py.
4. Run app\summarize_results.py.
5. Run app\strategy_dashboard_report.py.
6. Compare the result with standard mode.
7. Set RUN_MODE back to "standard" afterward.
```

### Historical Data Refresh

```text
1. Run app\download_historical_prices.py.
2. Run app\historical_ticker_calibration.py.
3. Run app\historical_window_calibration.py.
4. Run app\rolling_regime_detection.py.
5. Run app\current_regime_snapshot.py.
6. Run app\rolling_strategy_calibration.py.
7. Run app\strategy_dashboard_report.py.
```

## 12. Development Recommendation

Do not wire the diagnostic scripts into `app\main.py` yet.

Keep the following standalone:

```text
regime_detection.py
historical_ticker_calibration.py
historical_window_calibration.py
rolling_regime_detection.py
current_regime_snapshot.py
rolling_strategy_calibration.py
strategy_dashboard_report.py
```

The research layer is now stable enough to begin thinking about a user-facing dashboard or website layer.

Possible next development steps:

```text
1. Add taxable-account versus IRA assumptions.
2. Add position-sizing rules.
3. Begin designing a compact website/dashboard version.
4. Create a user-facing explanation of the adaptive rule.
```

## 13. Current Practical Conclusion

Current candidate rule:

```text
AdaptiveRegimeDTECost
```

Current practical snapshot:

```text
All five tested tickers currently map to Wait10d under the 252-day rolling regime snapshot.
```

But the adaptive rule should remain in place because:

```text
rolling strategy calibration shows that bearish windows tend to favor Close50
```

Therefore:

```text
Use Wait10d in bullish, baseline, and high-volatility upward-drifting regimes.

Use Close50 in bearish regimes.

Use DTE/cost-aware logic in sideways regimes.

Keep AdaptiveRegimeDTECost as the current strongest candidate rule.
```
