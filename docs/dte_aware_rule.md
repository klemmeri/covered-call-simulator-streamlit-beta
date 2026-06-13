# DTE-Aware Adaptive Rule Design

## Purpose

The current Covered Call Simulator has a working cost-aware adaptive rule:

```text
adaptive_close50_wait10_by_regime_and_cost
```

That rule adapts to:

```text
market regime
transaction costs
```

The DTE sensitivity test showed that DTE also matters. The next possible improvement is a rule that adapts to:

```text
market regime
DTE
transaction costs
```

This document describes the proposed DTE-aware rule before implementing it in `portfolio.py`.

## Current Finding

The DTE sensitivity test compared:

```text
HoldToExpiration
Close50
Wait10d
AdaptiveClose50Wait10
AdaptiveClose50Wait10CostAware
```

across:

```text
7 DTE
14 DTE
21 DTE
30 DTE
45 DTE
```

The 1000-path robustness run showed that only one regime was fully stable across all tested DTE values:

```text
bearish_market
```

In `bearish_market`, `Close50` was the winner for every tested DTE.

All other regimes showed some DTE sensitivity.

## DTE Decision Map

The current decision map is:

```text
Regime             7DTE       14DTE      21DTE      30DTE      45DTE
baseline           Wait10d    Hold       Wait10d    Wait10d    Hold
sideways_market    Hold       Hold       Close50    Close50    Close50
bullish_market     Wait10d    Wait10d    Wait10d    Wait10d    Hold
bearish_market     Close50    Close50    Close50    Close50    Close50
high_volatility    Wait10d    Wait10d    Wait10d    Wait10d    Hold
low_volatility     Wait10d    Hold       Wait10d    Wait10d    Hold
```

## Proposed New Rule Name

Suggested internal rule name:

```text
adaptive_by_regime_dte_cost
```

Suggested display label:

```text
AdaptiveRegimeDTECost
```

This is shorter than:

```text
adaptive_close50_wait10_by_regime_dte_and_cost
```

but still describes the logic.

## Proposed Rule Logic

### Bearish Market

```text
If regime is bearish_market:
    Use Close50 at all tested DTE values.
```

Reason:

```text
Close50 won at 7, 14, 21, 30, and 45 DTE.
```

### Sideways Market

```text
If regime is sideways_market:

    If DTE <= 14:
        Use HoldToExpiration.

    If DTE >= 21:
        Use Close50 unless transaction costs are high.
```

Transaction-cost override:

```text
If commission >= $1.25 per contract
or slippage >= $0.025 per share:

    Use HoldToExpiration instead of Close50.
```

Reason:

```text
At short DTE values, holding to expiration performed better.
At 21, 30, and 45 DTE, Close50 performed better under low transaction costs.
However, earlier transaction-cost testing showed that Close50 can lose its edge in sideways markets when trading costs become high.
```

### Bullish Market

```text
If regime is bullish_market:

    If DTE <= 30:
        Use Wait10d.

    If DTE >= 45:
        Use HoldToExpiration.
```

Reason:

```text
Wait10d won at 7, 14, 21, and 30 DTE.
HoldToExpiration won at 45 DTE.
```

### High-Volatility Market

```text
If regime is high_volatility:

    If DTE <= 30:
        Use Wait10d.

    If DTE >= 45:
        Use HoldToExpiration.
```

Reason:

```text
The high-volatility regime had the same winner pattern as bullish_market.
```

### Baseline Market

```text
If regime is baseline:

    If DTE is 7, 21, or 30:
        Use Wait10d.

    If DTE is 14 or 45:
        Use HoldToExpiration.
```

Reason:

```text
The 1000-path DTE test showed this exact pattern.
However, the 14-DTE HoldToExpiration result is somewhat irregular and should be treated carefully.
```

### Low-Volatility Market

```text
If regime is low_volatility:

    If DTE is 7, 21, or 30:
        Use Wait10d.

    If DTE is 14 or 45:
        Use HoldToExpiration.
```

Reason:

```text
The low-volatility regime had the same DTE pattern as baseline.
The 14-DTE HoldToExpiration result should also be treated carefully here.
```

## Simplified Practical Version

A simpler version of the rule would avoid hard-coding the irregular 14-DTE result in baseline and low-volatility regimes.

Simplified version:

```text
If bearish_market:
    Use Close50.

If sideways_market:
    If DTE <= 14:
        Use HoldToExpiration.
    Otherwise:
        Use Close50 unless transaction costs are high.

If bullish_market, high_volatility, baseline, or low_volatility:
    If DTE < 45:
        Use Wait10d.
    If DTE >= 45:
        Use HoldToExpiration.
```

This simplified rule is smoother and less likely to overfit.

The tradeoff is that it ignores the 14-DTE HoldToExpiration result in:

```text
baseline
low_volatility
```

## Recommended Implementation Choice

Use the simplified version first.

Reason:

```text
It captures the main DTE pattern without overfitting the 14-DTE anomaly.
```

Recommended first implementation:

```text
adaptive_by_regime_dte_cost
```

with logic:

```text
If bearish_market:
    Close50.

If sideways_market:
    If DTE <= 14:
        HoldToExpiration.
    If DTE >= 21:
        Close50 unless transaction costs are high.
        If transaction costs are high, HoldToExpiration.

If baseline, bullish_market, high_volatility, or low_volatility:
    If DTE < 45:
        Wait10d.
    If DTE >= 45:
        HoldToExpiration.
```

## Why Not Overfit the Exact Table?

The exact decision map says:

```text
baseline 14 DTE       -> HoldToExpiration
low_volatility 14 DTE -> HoldToExpiration
```

But this creates a less intuitive rule:

```text
7 DTE  -> Wait10d
14 DTE -> Hold
21 DTE -> Wait10d
30 DTE -> Wait10d
45 DTE -> Hold
```

That pattern may be real, but it may also be simulation noise or a local artifact of the option pricing and path assumptions.

A smoother rule is preferable unless repeated tests confirm the irregular 14-DTE result.

## Proposed Development Steps

1. Add the new rule to `portfolio.py`.

2. Add the new rule to `main.py`.

3. Add the display label to `reports.py`.

4. Update `check_strategy_map.py` to validate the new rule.

5. Update `summarize_results.py` to mention the DTE-aware rule.

6. Run standard mode:

```text
RUN_MODE = "standard"
```

7. Run robustness mode:

```text
RUN_MODE = "robustness"
```

8. Compare the new DTE-aware rule against:

```text
AdaptiveClose50Wait10
AdaptiveClose50Wait10CostAware
```

## Current Recommendation

Do not remove the existing adaptive rules.

Keep:

```text
AdaptiveClose50Wait10
AdaptiveClose50Wait10CostAware
```

Add the new DTE-aware rule as a third adaptive rule.

This allows side-by-side comparison before making it the default recommendation.
