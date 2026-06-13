# User-Facing Explanation — Adaptive Covered-Call Rule

## What This Simulator Is Trying to Answer

A covered-call strategy has two separate questions.

The first question is:

```text
What should I do with the short call?
```

The second question is:

```text
Is this trade actually practical for my account size?
```

The simulator now addresses both.

The strategy layer studies which covered-call management rule works best under different market conditions.

The tradability layer checks whether the account can actually hold 100 shares of the ETF under reasonable position-size limits.

This distinction matters. A ticker may have a good covered-call rule, but still be too expensive or too concentrated for a smaller account.

## The Current Candidate Rule

The current strongest candidate rule is called:

```text
AdaptiveRegimeDTECost
```

In plain English, it means:

```text
Use a different covered-call management rule depending on market regime, option duration, and transaction costs.
```

The rule does not assume that one covered-call method is always best.

Instead, it asks:

```text
Is the market falling?
Is the market drifting higher?
Is the market sideways?
Is the option short-term or long-term?
Are transaction costs low enough to justify frequent trading?
```

Then it chooses the covered-call management approach that has performed best under those conditions in the simulator.

## The Three Basic Covered-Call Choices

The simulator compares three practical covered-call behaviors.

### 1. Hold to Expiration

This means the investor sells the covered call and usually leaves it alone until expiration.

This rule trades less often.

It may reduce transaction costs.

It may be useful when frequent adjustments do not add much value.

### 2. Close at 50% Profit and Immediately Resell

This means the investor buys back the short call after capturing half of the premium, then immediately sells a new call.

This rule keeps the option-income engine active.

It often works better in falling or weak markets, because repeated option sales can help offset stock weakness.

The risk is that in a rising market, immediately reselling calls can repeatedly cap the upside.

### 3. Close at 50% Profit, Then Wait 10 Trading Days

This means the investor buys back the short call after capturing half of the premium, but does not immediately sell another call.

Instead, the strategy waits 10 trading days before selling the next call.

This gives the stock or ETF more room to rise.

It often works better in bullish, baseline, or high-volatility upward-drifting markets, because it reduces repeated upside drag.

## Why the Adaptive Rule Exists

A fixed covered-call rule can work well in one market and poorly in another.

For example:

```text
In bearish markets:
    Close at 50% profit and immediately resell often performs better.

In bullish or upward-drifting markets:
    Close at 50% profit, then wait before reselling often performs better.
```

This makes sense.

In a falling market, selling calls repeatedly can help generate income while the stock struggles.

In a rising market, selling calls too frequently can keep capping the upside.

The adaptive rule tries to avoid forcing the same behavior onto every market.

## The Current Practical Rule

The current adaptive rule can be summarized as follows.

### Bearish Market

```text
Close at 50% profit and immediately resell.
```

Reason:

```text
In bearish markets, repeated call selling can help offset weakness in the underlying ETF.
```

### Sideways Market

```text
Use DTE and transaction costs to decide.
```

If the option has very short DTE:

```text
Hold to expiration.
```

If the option has moderate DTE and costs are low:

```text
Close at 50% profit and immediately resell.
```

If transaction costs are high:

```text
Hold to expiration.
```

Reason:

```text
In sideways markets, frequent trading can help, but only if the transaction costs do not consume the edge.
```

### Bullish, Baseline, High-Volatility, or Low-Volatility Market

```text
Close at 50% profit, then wait 10 trading days before reselling.
```

Reason:

```text
In rising or upward-drifting markets, immediately reselling calls can create too much upside drag.
```

For longer-dated options, the simulator may favor holding to expiration instead of repeatedly closing and reopening.

## Why Waiting Can Help

Covered calls earn income by selling option premium.

But they also give up some upside.

If the ETF rises strongly, the short call can limit gains.

When the strategy immediately sells a new call every time the old one is closed, it keeps putting a new cap on the position.

That can be costly in a strong market.

Waiting 10 trading days after closing a profitable call gives the underlying ETF time to participate in upside moves before another call is sold.

This is not always best, but it has been the preferred behavior in the simulator for bullish, baseline, and high-volatility upward-drifting conditions.

## What the Tests Showed

The simulator tested the adaptive rule across several layers.

### Broad Historical Window Tests

The simulator tested multiple historical lookback windows:

```text
1 year
2 years
3 years
5 years
full available period
```

Across these broad historical windows, the best covered-call behavior was consistently:

```text
Wait10d
```

This means that, in broad growth-oriented historical windows, immediately reselling calls after every 50% profit tended to create too much upside drag.

### Rolling Window Tests

The simulator also tested rolling 252-day windows.

These windows move through time and capture changing market conditions.

The rolling tests showed that the best fixed rule was not always the same.

```text
Bearish rolling windows often favored Close50.

Bullish or upward-drifting rolling windows often favored Wait10d.
```

This is exactly why an adaptive rule is useful.

The adaptive rule was not materially worse than the best fixed rule in any completed rolling-window case.

### Current Snapshot

Using the current 252-day rolling regime snapshot, all tested tickers currently map to:

```text
Wait10d
```

The tested tickers were:

```text
SPY
QQQ
IWM
TQQQ
SOXL
```

The current detected regimes were either:

```text
bullish_market
high_volatility
```

Under those regimes, the current practical rule is:

```text
Close at 50% profit, then wait 10 trading days before selling the next call.
```

## Important Caution

This simulator does not prove that covered calls beat buy-and-hold.

In fact, in strong growth markets, covered calls often underperform buy-and-hold because the short call limits upside.

The simulator is answering a narrower question:

```text
If you are going to use covered calls, which management rule appears least damaging or most useful under the current conditions?
```

That is different from saying:

```text
Covered calls are always better than simply holding the ETF.
```

They are not.

Covered calls trade some upside for income.

That tradeoff can be useful for some investors and unattractive for others.

## Practical Tradability

A strategy can be mathematically valid but impractical for a smaller account.

A fully covered call requires:

```text
100 shares per option contract
```

That means one covered call on a high-priced ETF can require a large amount of capital.

For example, if an ETF trades near $700, then one covered-call contract requires roughly:

```text
100 x $700 = $70,000
```

If the investor wants no more than 20% of the account in one ticker, then the account would need to be roughly:

```text
$70,000 / 0.20 = $350,000
```

This is why the simulator includes a tradability layer.

It checks:

```text
How many contracts fit?
What account size is required?
Which tickers are tradable under conservative, balanced, or aggressive allocation caps?
```

## Conservative, Balanced, and Aggressive Sizing

The simulator currently uses three example sizing tiers.

### Conservative

```text
Normal ETF cap:      10%
Leveraged ETF cap:    5%
Total covered-call cap: 50%
```

### Balanced

```text
Normal ETF cap:      20%
Leveraged ETF cap:   10%
Total covered-call cap: 80%
```

### Aggressive

```text
Normal ETF cap:      35%
Leveraged ETF cap:   20%
Total covered-call cap: 100%
```

These are not recommendations.

They are scenarios.

They help show how the answer changes when the investor allows more or less concentration.

## What the Dashboard Now Shows

The dashboard now combines:

```text
current market regime
current practical covered-call rule
historical-window validation
rolling-window validation
fixed-account position sizing
minimum account size for one contract
conservative / balanced / aggressive tradability
```

This lets the user see both:

```text
Which rule appears appropriate?
```

and:

```text
Can I actually trade this ticker in my account?
```

## Plain-English Summary

The current simulator result can be summarized this way:

```text
The best covered-call rule depends on the market.

In bearish markets, closing at 50% profit and immediately reselling can help maintain income.

In bullish or upward-drifting markets, immediately reselling calls can cap too much upside.

In those conditions, closing at 50% profit and waiting before reselling often works better.

In sideways markets, the best choice depends on DTE and transaction costs.

The current adaptive rule combines these ideas.
```

The current candidate rule is:

```text
AdaptiveRegimeDTECost
```

The current dashboard status is:

```text
Strategy status: PASS
Tradability layer: available
```

## Final User-Facing Explanation

The simulator does not try to predict the market perfectly.

It treats regime detection as guidance, not certainty.

The goal is not to find a magic rule.

The goal is to avoid using the wrong rule in the wrong environment.

A good covered-call strategy should recognize that:

```text
falling markets
sideways markets
rising markets
short-DTE options
long-DTE options
low-cost trading
high-cost trading
small accounts
large accounts
```

are not the same problem.

The adaptive rule is designed around that idea.
