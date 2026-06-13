# Covered Call Simulator — Simulator User Workflow

## 1. Purpose of This Document

This document defines the user workflow for the Covered Call Simulator.

It describes how a user should move through:

- The free simulator.
- The paid configurable simulator.
- The Real-Life Replay Simulator.

The purpose is to define the user experience before building the public-facing website or simulator interface.

The simulator should remain a decision-support and education tool. It should not be presented as a trade signal service.

Important recurring language:

> The simulator is for education and research only. It is not financial advice or a trade recommendation.

> Regime detection is probabilistic guidance, not an oracle.

> Tradable does not mean recommended.

> Premium collected is not the same as profit.

---

## 2. Product Modes

The public product should eventually have three major simulator modes:

1. Free Simulator
2. Paid Configurable Simulator
3. Real-Life Replay Simulator

Each mode has a different purpose.

### Free Simulator

Purpose:

> Demonstrate the basic value of comparing covered-call management rules using simple fixed assumptions.

The free simulator should be simple and educational.

### Paid Configurable Simulator

Purpose:

> Let users test covered-call strategies using their own account size, ticker choices, delta, DTE, strike-selection assumptions, and management rules.

The paid simulator should feel like a practical workflow tool.

### Real-Life Replay Simulator

Purpose:

> Let users practice covered-call decisions on a historical price path without seeing the future.

The replay simulator should teach path dependence, rolling decisions, missed upside, and total-equity behavior.

---

## 3. Free Simulator Workflow

### Step 1 — Start Free Simulator

The user clicks:

> Try the Free Simulator

The free simulator opens with a simple guided layout.

### Step 2 — Choose a Preset Ticker

The user selects from a small preset list.

Suggested free tickers:

- SPY
- QQQ
- IWM

The ticker list should be intentionally limited.

### Step 3 — Use Fixed Account Assumptions

The free simulator uses fixed account assumptions.

Suggested defaults:

- Account size: $100,000
- Risk tier: Balanced
- Target delta: 0.30
- DTE: 30 days
- Transaction cost: default estimate
- Assignment handling: simplified

The user should see these assumptions, but should not be able to change all of them in the free version.

### Step 4 — Choose a Basic Rule Comparison

The free simulator should allow a simple comparison between:

- Hold to expiration.
- Close at 50% profit.

Optional free preview:

- Wait 10 days.

The adaptive regime rule should probably be shown as a paid-preview feature rather than fully unlocked.

### Step 5 — Run Comparison

The user clicks:

> Run Comparison

The simulator returns:

- Rule comparison table.
- Total return estimate.
- Premium collected.
- Missed upside.
- Account-size estimate.
- Plain-English interpretation.
- Disclaimer.

### Step 6 — Interpret Results

The simulator should explain results in simple language.

Example interpretation:

> Under these assumptions, the Close at 50% rule captured premium earlier and reduced exposure after much of the option value had decayed. However, the result still depended heavily on the underlying ETF price path.

The simulator should also remind the user:

> This result is hypothetical and based on fixed assumptions. It is not a trade recommendation.

### Step 7 — Upgrade Prompt

The free version should invite the user to explore the paid version.

Possible upgrade message:

> Want to test your own ticker, account size, delta, DTE, and rolling rules? Upgrade to the configurable simulator.

---

## 4. Free Simulator Screen Layout

Recommended free simulator sections:

1. Ticker
2. Fixed Assumptions
3. Rule Comparison
4. Results Summary
5. Interpretation
6. Upgrade Prompt
7. Disclaimer

### Free Simulator Controls

Allowed controls:

- Ticker selection.
- Basic rule comparison.

Locked or fixed controls:

- Account size.
- Risk tier.
- Delta.
- DTE.
- Custom ticker.
- Rolling rule.
- Replay simulator.

The free version should not overwhelm the user.

---

## 5. Paid Configurable Simulator Workflow

### Step 1 — Open Paid Simulator

The user enters the paid simulator from:

- Pricing page.
- Upgrade prompt.
- Dashboard.
- Saved account page.

The paid simulator should begin with a guided setup.

### Step 2 — Enter Ticker

The user enters any stock or ETF ticker.

The simulator checks whether the ticker is:

- Valid.
- A stock or ETF.
- Optionable.
- Liquid enough for analysis.
- Practical for the selected account size.

### Step 3 — Run Ticker Eligibility Screen

The simulator displays a ticker status.

Possible statuses:

- Tradable.
- Optionable but illiquid.
- Not optionable.
- Too large for selected account.
- Insufficient option-chain data.
- No suitable DTE.
- No suitable strike near target delta.
- Missing quote data.

If the ticker fails, the simulator should explain why.

Example warning:

> This ticker has listed options, but the option chain appears too illiquid for reliable covered-call simulation.

### Step 4 — Choose Account Settings

The user chooses:

- Account size.
- Risk tier.
- Per-position cap.
- Total covered-call allocation cap.

Suggested risk tiers:

- Conservative.
- Balanced.
- Aggressive.

The simulator calculates:

- Minimum equity for one covered-call contract.
- Whether the ticker is practical.
- How many contracts may fit under the selected limits.

### Step 5 — Choose Option Parameters

The user selects:

- Target delta.
- DTE.
- Strike-selection method.
- Expiration selection.
- Liquidity constraints.

Suggested delta choices:

- 0.15
- 0.20
- 0.25
- 0.30
- 0.35
- 0.40

Suggested DTE choices:

- 7
- 14
- 21
- 30
- 45
- 60

Suggested strike-selection methods:

- Closest to target delta.
- Fixed percentage out-of-the-money.
- Fixed dollar amount out-of-the-money.
- Closest strike above current price.
- Highest annualized premium subject to delta limit.
- Liquidity-filtered best match.

### Step 6 — Choose Management Rule

The user selects one or more covered-call management rules.

Possible rules:

- Hold to expiration.
- Close at 25% profit.
- Close at 50% profit.
- Close at 75% profit.
- Wait fixed number of days.
- Roll when ITM.
- Roll when delta exceeds threshold.
- Roll only for a net credit.
- Adaptive regime rule.

### Step 7 — Choose Scenario or Regime

The user can select:

- Historical period.
- Market-regime scenario.
- Recent completed-bar regime.
- Bullish scenario.
- Bearish scenario.
- Sideways scenario.
- High-volatility scenario.
- Low-volatility scenario.

Important wording:

> Regime labels are scenario inputs, not predictions.

### Step 8 — Run Simulation

The user clicks:

> Run Simulation

The simulator produces:

- Rule comparison.
- Current tradability.
- Account-size requirement.
- Premium collected.
- Stock P/L.
- Option P/L.
- Total equity.
- Missed upside.
- Assignment events.
- Roll events.
- Drawdown.
- Benchmark comparison.
- Interpretation.

### Step 9 — Review Results

The paid simulator should present results in layers.

Recommended result sections:

1. Practical Action
2. Tradability
3. Rule Comparison
4. Equity Curve
5. Risk Metrics
6. Option Activity
7. Benchmark Comparison
8. Interpretation
9. Export Report

### Step 10 — Export Report

The user can export:

- PDF.
- CSV.
- Markdown.
- Excel in a later version.

The report should include all assumptions and disclaimers.

---

## 6. Paid Simulator Screen Layout

Recommended paid simulator sections:

1. Ticker Setup
2. Ticker Eligibility
3. Account Settings
4. Option Parameters
5. Management Rules
6. Scenario / Regime Selection
7. Run Simulation
8. Results Summary
9. Equity Curve
10. Rule Comparison
11. Risk and Drawdown
12. Export Report
13. Disclaimer

The paid simulator should be workflow-driven rather than table-driven.

---

## 7. Real-Life Replay Simulator Workflow

### Step 1 — Open Replay Simulator

The user clicks:

> Practice with Historical Replay

The replay simulator should explain its purpose:

> Replay mode lets you practice covered-call decisions on a historical price path without seeing the future.

### Step 2 — Select Ticker

The user selects or enters a ticker.

The ticker must pass:

- Price data availability.
- Optionability.
- Liquidity screen.
- Account-size screen.

### Step 3 — Select Replay Period

The user chooses:

- Historical start date.
- Replay length.
- Bar size.

Suggested bar sizes:

- Daily.
- Weekly.
- Future: intraday.

The simulator should hide future prices.

### Step 4 — Set Starting Account

The user chooses:

- Starting account equity.
- Number of shares.
- Cash reserve.
- Risk tier.

The simulator should verify that the user can hold at least 100 shares if selling covered calls.

### Step 5 — Start Replay

The price chart begins at the selected start date.

The user sees only information available at that time.

Displayed information:

- Current date.
- Current stock price.
- Current equity.
- Current cash.
- Shares held.
- Open option position, if any.
- Available action buttons.

### Step 6 — User Chooses an Action

Possible user actions:

- Sell covered call.
- Wait.
- Close short call.
- Roll out.
- Roll up.
- Roll down.
- Roll out and up.
- Let expire.
- Accept assignment.
- Reset replay.

### Step 7 — Select Call Parameters

When selling or rolling a call, the user chooses:

- Target delta.
- DTE.
- Strike.
- Expiration.
- Liquidity constraint.

The simulator should display the selected call information:

- Strike.
- Expiration.
- Estimated delta.
- Premium.
- Bid/ask spread.
- Open interest.
- DTE.
- Moneyness.

### Step 8 — Advance Time

The user advances the replay.

Controls:

- Step one day.
- Step one week.
- Play.
- Pause.
- Reset.

As time advances, the simulator updates:

- Stock price.
- Option value.
- DTE remaining.
- Moneyness.
- Unrealized option P/L.
- Total equity.
- Missed upside.
- Assignment status.

### Step 9 — Manage the Position

If the short call moves ITM, the user can decide whether to:

- Hold.
- Close.
- Roll.
- Let assignment happen.
- Wait.

The simulator should show the consequences of each decision.

### Step 10 — End Replay

At the end, the simulator shows:

- Final total equity.
- Total return.
- Buy-and-hold comparison.
- Rule-based benchmark comparison.
- Premium collected.
- Realized option P/L.
- Stock P/L.
- Missed upside.
- Roll count.
- Assignment count.
- Maximum drawdown.
- User decision summary.

---

## 8. Replay Simulator Screen Layout

Recommended replay screen sections:

1. Replay Setup
2. Price Chart
3. Current Position
4. Action Panel
5. Option Selection Panel
6. Total Equity Plot
7. Event Log
8. Benchmark Comparison
9. Replay Summary

### Price Chart

The price chart should show the underlying price path up to the current replay date only.

### Current Position

Show:

- Shares held.
- Average stock cost.
- Current stock price.
- Short call strike.
- Short call expiration.
- Short call value.
- DTE remaining.
- Moneyness.
- Unrealized stock P/L.
- Unrealized option P/L.
- Total equity.

### Action Panel

Buttons:

- Sell Call.
- Close Call.
- Roll Call.
- Wait.
- Advance.
- Reset.

### Event Log

The event log should record:

- Date.
- Action.
- Strike.
- Expiration.
- Premium.
- Cost to close.
- Roll credit/debit.
- Realized P/L.
- Notes.

---

## 9. Moving Total-Equity Plot Workflow

The total-equity plot should update after each time step and each user action.

Main line:

- User-managed replay equity.

Benchmark overlays:

- Buy and hold.
- Hold to expiration.
- Close at 50%.
- Wait 10 days.
- Adaptive regime rule.

The plot should make it clear whether the user’s decisions improved or harmed total wealth.

The plot should include:

- Total account equity.
- Stock value.
- Cash.
- Open option value.
- Realized P/L.

Important explanatory text:

> Premium collected is not the same as profit. The equity curve shows the combined effect of stock value, option value, realized gains or losses, and cash.

---

## 10. User Decision Log

The simulator should maintain a decision log.

Columns:

- Date.
- Replay step.
- Action.
- Stock price.
- Shares held.
- Strike.
- Expiration.
- DTE.
- Delta.
- Premium.
- Cost to close.
- Roll credit or debit.
- Realized option P/L.
- Stock P/L.
- Cash.
- Total equity.
- Notes.

The decision log should be exportable in the paid version.

---

## 11. Interpretation Layer

Every simulator mode should provide a plain-English interpretation.

The interpretation should explain:

- What happened.
- Why total equity changed.
- Whether the strategy outperformed buy-and-hold.
- Whether premium income offset missed upside.
- Whether rolls helped or hurt.
- Whether drawdown improved or worsened.
- Whether the ticker was practical for the account size.

The interpretation should avoid making a recommendation.

Suggested language:

> This simulation suggests that the covered-call rule reduced upside participation during this period. Although premium was collected, total equity underperformed buy-and-hold because the underlying rose strongly above the short-call strike.

---

## 12. Disclaimers in Workflow

Disclaimers should appear at appropriate points.

### Before Simulation

> Simulated results are hypothetical and are not financial advice.

### Near Tradability

> Tradable means the ticker passes the selected account-size and position-size screen. It is not a trade recommendation.

### Near Regime Output

> Regime detection is probabilistic guidance, not an oracle.

### Near Equity Curve

> Premium collected is not the same as profit. Watch total equity, not just income.

### Near Export

> This report is for educational use only. It is not financial advice or a trade recommendation.

---

## 13. MVP Workflow

The first public MVP should not include everything.

Recommended MVP workflow:

1. User opens simulator.
2. User selects one of a few preset tickers.
3. User sees fixed assumptions.
4. User compares Hold to Expiration versus Close at 50%.
5. User sees total return, premium collected, and missed upside.
6. User sees a simple interpretation.
7. User sees upgrade prompt.

The replay simulator should not be part of the first MVP.

---

## 14. Paid MVP Workflow

The first paid MVP should include:

1. Custom account size.
2. Risk tier.
3. User-selected delta.
4. User-selected DTE.
5. Rule comparison.
6. Current tradability.
7. Exportable report.

The first paid MVP does not need full replay mode immediately.

---

## 15. Replay MVP Workflow

The first replay MVP should include:

1. One ticker.
2. One historical period.
3. Daily stepping.
4. Sell call.
5. Wait.
6. Close call.
7. Basic roll.
8. Total-equity plot.
9. Buy-and-hold comparison.
10. Event log.

More advanced rolling rules can come later.

---

## 16. Recommended Next Implementation Step

Before writing website code, create a simple public-site prototype using the existing planning documents.

Recommended next code milestone:

```text
public_site/app.py
```

The first public-site prototype should include:

- Home page.
- How It Works page.
- Free Simulator Preview page.
- Pricing page.
- Disclaimer page.

The simulator preview can initially use static placeholder results.

After the public-site shell works, connect it to existing simulator outputs.

---

## 17. Current Recommendation

Do not build the replay simulator first.

The best sequence is:

1. Public website shell.
2. Free simulator preview.
3. Paid configurable simulator.
4. Custom ticker and liquidity screen.
5. Exportable reports.
6. Replay simulator.
7. Moving total-equity plot.

The replay simulator is a strong paid feature, but it should come after the simpler public product is understandable and usable.
