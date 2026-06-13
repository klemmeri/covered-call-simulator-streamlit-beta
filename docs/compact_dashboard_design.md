# Covered Call Simulator — Compact Dashboard Design

## Purpose

The dashboard should turn the simulator’s research output into a simple user-facing decision screen.

The user should be able to answer four questions quickly:

```text
1. What is the current market regime?
2. What covered-call management rule is suggested?
3. Is the rule supported by historical and rolling-window tests?
4. Is the trade practical for my account size?
```

The dashboard should not look like a research notebook.

It should look like a compact decision aid.

## Core Dashboard Message

The dashboard should communicate:

```text
The adaptive rule is not trying to predict the market perfectly.

It uses regime guidance, DTE, and transaction costs to select the covered-call behavior that has worked best under similar simulated and historical conditions.

Then it checks whether the trade is practical for the account size.
```

## Main Dashboard Sections

The dashboard should have six sections.

```text
1. Strategy Status
2. Current Market Snapshot
3. Suggested Rule
4. Validation Summary
5. Tradability Check
6. Interpretation / Cautions
```

## 1. Strategy Status

This should be the top card.

Example:

```text
Strategy Status: PASS

Current Candidate Rule:
AdaptiveRegimeDTECost

Meaning:
Use market regime, DTE, and transaction costs to choose between Hold, Close50, and Wait10d.
```

Suggested visual format:

```text
[ Strategy Status: PASS ]

Rule: AdaptiveRegimeDTECost
Validation: Passed historical-window and rolling-window tests
Tradability Layer: Available
```

This section should be short. The details belong lower on the page.

## 2. Current Market Snapshot

This section shows the current regime for each ticker.

Columns:

```text
Ticker
Latest Price
Rolling Return
Rolling Volatility
Detected Regime
Practical Rule
```

Example:

```text
Ticker   Price    Regime            Rule
SPY      736.48   bullish_market    Wait10d
QQQ      706.29   bullish_market    Wait10d
IWM      285.24   bullish_market    Wait10d
TQQQ      73.16   high_volatility   Wait10d
SOXL     194.20   high_volatility   Wait10d
```

Plain-English summary beneath the table:

```text
All currently tested tickers map to Wait10d under the 252-day rolling regime snapshot.
```

Important caution:

```text
Regime detection is guidance, not a prediction.
```

## 3. Suggested Rule

This section explains what the suggested rule means.

If the current practical rule is `Wait10d`, show:

```text
Suggested Rule: Wait10d

Close the short call after capturing 50% of the premium.
Then wait 10 trading days before selling the next call.

Why:
In bullish or upward-drifting markets, immediately reselling calls can create too much upside drag.
```

If the current practical rule is `Close50`, show:

```text
Suggested Rule: Close50

Close the short call after capturing 50% of the premium.
Immediately sell a new covered call.

Why:
In bearish markets, repeated call selling may help offset weakness in the underlying.
```

If the current practical rule is `HoldToExpiration`, show:

```text
Suggested Rule: Hold to Expiration

Sell the covered call and usually leave it open until expiration.

Why:
When DTE is short or transaction costs are high, frequent trading may not add enough value.
```

## 4. Validation Summary

This section summarizes whether the rule has support.

Use two cards.

### Historical-Window Validation

Example:

```text
Historical-Window Validation: PASS

Ticker/window cases tested: 25
Adaptive worse cases: 0
Unstable best-rule tickers: 0
```

Plain-English explanation:

```text
Across broad historical windows, Wait10d was the stable best rule for the tested tickers.
```

### Rolling Strategy Validation

Example:

```text
Rolling Strategy Validation: PASS

Rolling windows tested: 115
Adaptive worse cases: 0
Unstable best-rule tickers: 5
```

Plain-English explanation:

```text
The best fixed rule changed across rolling windows, but the adaptive rule was not materially worse than the best fixed rule in any completed rolling-window case.
```

This section should emphasize:

```text
The rolling test supports adaptiveness.
```

because bearish windows often favor Close50 while bullish or upward-drifting windows often favor Wait10d.

## 5. Tradability Check

This section determines whether the user can actually trade the ticker.

It should answer:

```text
Can this account hold 100 shares without exceeding the position-size cap?
```

### Fixed-Account Position Sizing

Inputs:

```text
Account equity
Ticker
Allocation cap
Leveraged ETF cap
```

Outputs:

```text
Max contracts
Required shares
Dollar allocation
Tradable / not tradable
```

Example for $100,000 account:

```text
TQQQ:
    Max contracts: 1
    Status: Tradable

SPY:
    Max contracts: 0
    Status: Too expensive under current cap
```

### Minimum Account Equity for One Contract

Example:

```text
TQQQ: $73,160 at 10% cap
IWM:  $142,619.95 at 20% cap
SOXL: $194,200 at 10% cap
QQQ:  $353,144.99 at 20% cap
SPY:  $368,241.64 at 20% cap
```

Plain-English explanation:

```text
A covered call requires 100 shares. High-priced ETFs may require a large account if position size is capped.
```

### Position-Size Tiers

Show three risk-posture scenarios.

```text
Conservative:
    normal ETF cap:      10%
    leveraged ETF cap:    5%

Balanced:
    normal ETF cap:      20%
    leveraged ETF cap:   10%

Aggressive:
    normal ETF cap:      35%
    leveraged ETF cap:   20%
```

Example tier result for $100,000:

```text
Conservative: 0 tradable tickers
Balanced:     1 tradable ticker
Aggressive:   3 tradable tickers
```

Important wording:

```text
These are allocation scenarios, not recommendations.
```

## 6. Interpretation / Cautions

This section should be plain and direct.

Use short caution boxes.

### Caution 1 — Covered Calls Are Not Magic

```text
Covered calls trade upside for income.

They may underperform buy-and-hold in strong bull markets.
```

### Caution 2 — Regime Detection Is Imperfect

```text
The regime detector uses historical return and volatility.

It is guidance, not a market forecast.
```

### Caution 3 — Tradability Is Separate From Strategy

```text
A ticker may have a valid covered-call rule but still be impractical for the account size.
```

### Caution 4 — Simulation Is Not a Guarantee

```text
The simulator compares rules under modeled assumptions.

Actual results can differ because of market behavior, fills, taxes, liquidity, dividends, and assignment.
```

## Recommended Page Layout

A simple layout:

```text
------------------------------------------------------------
Covered Call Simulator Dashboard
------------------------------------------------------------

[ Strategy Status Card ]

[ Current Market Snapshot Table ]

[ Suggested Rule Card ]

[ Validation Summary ]
    [ Historical Window Validation ]
    [ Rolling Strategy Validation ]

[ Tradability Check ]
    [ Fixed Account Sizing ]
    [ Minimum Equity for 1 Contract ]
    [ Conservative / Balanced / Aggressive Tiers ]

[ Interpretation and Cautions ]
```

## Suggested Dashboard Inputs

The user-facing dashboard should eventually allow these inputs:

```text
Account equity
Ticker list
Risk tier
Normal ETF allocation cap
Leveraged ETF allocation cap
DTE
Transaction-cost assumptions
```

Initial default values:

```text
Account equity:             $100,000
Risk tier:                  Balanced
Normal ETF cap:             20%
Leveraged ETF cap:          10%
DTE:                        30
Commission per contract:    $0.65
Slippage per share:         $0.01
Rolling regime window:      252 trading days
```

## Suggested Dashboard Outputs

The dashboard should output:

```text
Detected regime
Suggested covered-call rule
Rule explanation
Historical validation status
Rolling validation status
Maximum tradable contracts
Minimum account equity for one contract
Tradability under conservative, balanced, and aggressive tiers
Cautions
```

## Data Files Feeding the Dashboard

Current source files:

```text
outputs\tables\comparison\strategy_dashboard_report.txt
outputs\tables\comparison\current_regime_snapshot.csv
outputs\tables\comparison\historical_window_calibration_winners.csv
outputs\tables\comparison\rolling_strategy_calibration_stability.csv
outputs\tables\comparison\position_sizing_summary.csv
outputs\tables\comparison\account_size_sensitivity_summary.csv
outputs\tables\comparison\position_size_tiers_summary.csv
```

The most important user-facing source is:

```text
outputs\tables\comparison\strategy_dashboard_report.txt
```

The most important machine-readable files are:

```text
current_regime_snapshot.csv
position_sizing_summary.csv
account_size_sensitivity_summary.csv
position_size_tiers_summary.csv
```

## First Version Website Scope

The first website version should be small.

It should not include every report.

It should show:

```text
1. Current rule recommendation
2. Current regime table
3. Tradability table
4. Position-size tier summary
5. Explanation of the adaptive rule
```

Do not include:

```text
all Monte Carlo path-level outputs
all cycle-level outputs
all sensitivity reports
all diagnostic logs
```

Those belong in the research layer, not the user-facing dashboard.

## Recommended First Web App Structure

A simple local Streamlit app is the easiest first version.

Possible file:

```text
dashboard\app.py
```

Possible folders:

```text
dashboard\
    app.py

outputs\
    tables\
        comparison\
            strategy_dashboard_report.txt
            current_regime_snapshot.csv
            position_sizing_summary.csv
            account_size_sensitivity_summary.csv
            position_size_tiers_summary.csv
```

Why Streamlit is a good first choice:

```text
simple Python
fast to build
easy to read CSV files
good for tables and cards
no complicated web programming
```

The website can later be converted to a more polished commercial interface.

## Suggested Streamlit Page Sections

```text
st.title("Covered Call Simulator Dashboard")

st.subheader("Strategy Status")
st.metric("Adaptive Rule", "AdaptiveRegimeDTECost")
st.success("Strategy Status: PASS")

st.subheader("Current Market Snapshot")
st.dataframe(current_regime_snapshot)

st.subheader("Tradability")
st.dataframe(position_sizing_summary)

st.subheader("Minimum Account Equity")
st.dataframe(one_contract_summary)

st.subheader("Position-Size Tiers")
st.dataframe(position_size_tiers)

st.subheader("Explanation")
st.markdown(user_facing_adaptive_rule_explanation)
```

## Final Design Principle

The dashboard should avoid giving the impression that the simulator predicts the market.

The correct framing is:

```text
Given the detected regime and the tested assumptions,
this rule has historically and statistically behaved better than the alternatives.
```

The dashboard should always separate:

```text
strategy choice
```

from:

```text
position-size practicality
```

That is the main value of the current design.
