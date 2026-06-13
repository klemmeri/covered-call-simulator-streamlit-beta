# Covered Call Simulator - Landing Page Copy

## Page Purpose

This document drafts the public-facing landing page copy for the Covered Call Simulator website.

The landing page should explain the product clearly, attract income-focused investors, and avoid implying that the simulator provides trade signals or guaranteed results.

Core message:

> Test covered-call rules before risking capital.

The landing page should present the simulator as an educational and analytical decision-support tool.

---

## 1. Hero Section

### Headline

Test covered-call rules before risking capital.

### Subheadline

Compare covered-call management rules across account sizes, ETFs, stocks, and market-regime scenarios using a practical simulator built for income-focused investors.

### Primary Call to Action

Try the Free Simulator

### Secondary Call to Action

See How It Works

### Short Supporting Text

Covered calls can look simple until the underlying moves, the option goes in-the-money, or the account is too small for the ticker. The Covered Call Simulator helps you compare rules, position-size assumptions, and market scenarios before making real trades.

---

## 2. Problem Section

### Section Headline

Covered-call decisions are easy to describe and harder to manage.

### Body Copy

Selling a covered call is straightforward: own 100 shares, sell a call, collect premium.

The hard part is deciding what to do next.

Should you hold to expiration? Close after capturing part of the premium? Wait before selling another call? Roll when the call moves in-the-money? Choose a lower delta? Use a shorter expiration? Avoid a ticker because one contract is too large for the account?

Most covered-call advice focuses on the premium collected. But premium is only one part of the trade. A realistic analysis also needs to consider:

- Stock movement.
- Option value changes.
- Missed upside.
- Assignment risk.
- Position size.
- Account size.
- Market regime.
- Transaction costs.
- The rule used to manage the trade.

### Closing Line

The simulator helps put these tradeoffs into one structured framework.

---

## 3. Solution Section

### Section Headline

A simulator for comparing covered-call rules, not guessing tomorrow's market.

### Body Copy

The Covered Call Simulator lets you compare how different covered-call management rules behave under different assumptions.

You can evaluate questions such as:

- What happens if I hold covered calls to expiration?
- What happens if I close after capturing 50% of the premium?
- What happens if I wait before selling another call?
- How do results change in bullish, bearish, sideways, high-volatility, or low-volatility markets?
- Which tickers are practical for my account size?
- How does changing delta or DTE affect the behavior of the strategy?

The goal is not to predict the next move. The goal is to understand how your rules behave before you rely on them with real money.

---

## 4. How It Works Section

### Section Headline

How the simulator works

### Step 1 - Choose a ticker

Start with a stock or ETF. The free version uses a limited preset list. The paid version is designed to support user-selected stocks and ETFs, subject to option availability and liquidity checks.

### Step 2 - Set account assumptions

Choose account size and risk tier. The simulator checks whether one covered-call contract is practical under the selected position-size limits.

### Step 3 - Choose option assumptions

Select the option assumptions that shape the covered-call trade, such as target delta, days to expiration, and strike-selection method.

### Step 4 - Choose a management rule

Compare rules such as holding to expiration, closing at 50% profit, waiting before re-entry, or using an adaptive regime-based rule.

### Step 5 - Compare outcomes

Review the results across scenarios, including premium collected, total equity, missed upside, assignment risk, and account-size feasibility.

### Step 6 - Interpret cautiously

The simulator provides scenario-based guidance. It is not a trade signal and does not guarantee future results.

---

## 5. Main Features Section

### Section Headline

What you can analyze

### Feature 1 - Covered-call rule comparison

Compare covered-call management rules side by side instead of relying on one rule of thumb.

Possible rules include:

- Hold to expiration.
- Close at 50% profit.
- Wait before re-entry.
- Adaptive regime-based rule.

### Feature 2 - Account-aware tradability

A ticker may be popular, but that does not mean it is practical for every account.

The simulator estimates the minimum equity needed for one covered-call contract based on:

- Current or near-current price.
- 100 shares per contract.
- Selected position-size cap.
- Normal ETF or leveraged ETF classification.
- User-selected risk tier.

### Feature 3 - Option-parameter controls

Paid users should be able to test the variables covered-call traders actually use, including:

- Target delta.
- Days to expiration.
- Strike-selection method.
- Profit-taking rule.
- Re-entry delay.
- Roll assumptions.
- Transaction cost assumptions.

### Feature 4 - Custom ticker support

The paid version should allow users to enter any stock or ETF, provided it has listed options and enough liquidity for meaningful analysis.

Ticker screening should check:

- Whether options are listed.
- Whether the underlying is liquid enough.
- Whether the option chain has usable bid and ask quotes.
- Whether spreads are reasonable.
- Whether open interest or option volume is sufficient.
- Whether the selected delta and DTE are available.

### Feature 5 - Market-regime scenarios

The simulator can compare how rules behave under different market-regime labels, such as:

- Bullish.
- Bearish.
- Sideways.
- High volatility.
- Low volatility.

Regime detection should be treated as probabilistic guidance, not an oracle.

### Feature 6 - Real-life replay simulator

A future paid feature should allow users to watch a historical price path unfold over time and make covered-call decisions without seeing the future.

The user could decide when to sell a call, choose strike and DTE, watch the option move, and decide whether to hold, close, roll, or wait.

This turns the simulator into a realistic practice environment rather than only a static report.

---

## 6. Replay Simulator Section

### Section Headline

Practice covered-call decisions on historical price paths.

### Body Copy

Covered-call management is path-dependent. A rule can look obvious after the fact but feel difficult while the trade is unfolding.

The replay simulator is designed to let users experience that decision process.

Users should be able to:

- Select a stock or ETF.
- Select a historical start date.
- Watch the price move forward one step at a time.
- Choose when to sell a covered call.
- Select delta, DTE, and strike.
- Watch the call move out-of-the-money or in-the-money.
- Decide whether to hold, close, roll, or wait.
- Compare their decisions against rule-based benchmarks.

### Moving Equity Curve

The replay simulator should include a moving total-equity plot.

The equity curve should update as the simulation progresses and should include:

- Stock value.
- Cash.
- Premium collected.
- Open short-call value.
- Realized option profit or loss.
- Total covered-call equity.

Useful benchmark overlays could include:

- Buy-and-hold equity.
- Hold-to-expiration covered-call rule.
- Close-at-50%-profit rule.
- Wait-10-days rule.
- Adaptive regime rule.
- User-managed replay result.

### Suggested Display Text

Watch the trade unfold. See how premium, missed upside, option losses, and stock movement combine into total account equity.

### Important Note

Premium collected is not the same as profit. The equity curve helps show whether the covered-call decisions improved total account value or merely generated visible option income.

---

## 7. Free vs Paid Section

### Section Headline

Start simple. Upgrade when you want control.

### Free Version

The free version is designed as an educational preview.

Possible free features:

- Limited preset ticker list.
- Fixed account-size assumption.
- Basic rule comparison.
- Basic current tradability estimate.
- Simple educational interpretation.

Suggested free positioning:

> Learn how covered-call rules behave under fixed assumptions.

### Paid Version

The paid version is designed as a configurable research workflow.

Possible paid features:

- User-selected stocks and ETFs.
- Optionability and liquidity screening.
- Custom account size.
- Risk-tier controls.
- Target delta selection.
- DTE selection.
- Strike-selection controls.
- Rolling and re-entry assumptions.
- Regime-based rule comparison.
- Exportable reports.
- Real-life replay simulator.
- Moving total-equity plot.

Suggested paid positioning:

> Test covered-call rules using your own ticker, account size, delta, DTE, and management assumptions.

---

## 8. Why It Matters Section

### Section Headline

The best covered-call rule depends on the path.

### Body Copy

Covered-call results depend on more than the initial premium.

A strategy that works well in a sideways market may lag badly in a strong rally. A rule that protects profits in one environment may close too early in another. A high-yielding ticker may be impractical if one contract is too large for the account.

The simulator is built around that reality.

It helps users compare rules, account-size limits, and scenario behavior instead of assuming one covered-call method is always best.

### Closing Line

The goal is not to find a magic rule. The goal is to understand the tradeoffs.

---

## 9. Example Result Section

### Section Headline

Example output

### Example Copy

For a USD 100,000 Balanced account, the simulator may find that one ticker is practical while others are too large for the selected position-size limits.

Example interpretation:

> TQQQ is currently tradable under the selected account and risk settings. The current completed-bar regime maps to Wait 10 Days. Other displayed tickers require more equity for one covered-call contract under the selected position-size limits.

### Important Note

This does not mean TQQQ should be traded. It means TQQQ passes the current account-size and position-size screen under the selected assumptions.

---

## 10. Regime Detection Wording

### Section Headline

Market regimes are guidance, not predictions.

### Body Copy

The simulator may classify market conditions using completed daily-bar data. These regime labels are used to compare covered-call rule behavior across different environments.

They should not be treated as predictions.

Recommended wording:

> Regime detection is probabilistic guidance, not an oracle.

Additional wording:

> The simulator uses regime labels as scenario inputs. They help compare how different covered-call rules may behave under different market conditions. They are not forecasts or trade signals.

---

## 11. Trust and Disclaimer Section

### Section Headline

Built for analysis, not trade signals.

### Body Copy

The Covered Call Simulator is an educational and analytical tool. It is designed to help users compare covered-call rules and account assumptions.

It does not provide financial advice, investment advice, or trade recommendations.

Options involve risk. Covered calls can lose money if the underlying declines and can underperform the underlying in strong bull markets. Simulated results are hypothetical and may not reflect actual trading outcomes.

### Short Footer Disclaimer

Educational use only. Not financial advice. Options involve risk and are not suitable for all investors.

---

## 12. Call-to-Action Section

### Headline

See how your covered-call rules behave before you trade.

### Body Copy

Start with the free simulator to compare basic covered-call rules. Upgrade when you want custom tickers, account-size controls, option-parameter settings, and replay-based practice.

### Primary Button

Try the Free Simulator

### Secondary Button

View Paid Features

---

## 13. Footer Copy

Suggested footer text:

Covered Call Simulator is an educational and analytical tool for comparing covered-call management rules. It is not financial advice and does not provide trade recommendations. Options involve risk. Simulated results are hypothetical.

Suggested footer links:

- Home
- How It Works
- Simulator
- Strategies
- Account Sizing
- Market Regimes
- Pricing
- Disclaimers
- About

---

## 14. Recommended Page Structure

Suggested landing page order:

1. Hero section.
2. Problem section.
3. Solution section.
4. How it works.
5. Main features.
6. Replay simulator preview.
7. Free vs paid.
8. Why it matters.
9. Example result.
10. Regime detection wording.
11. Trust and disclaimer section.
12. Final call to action.
13. Footer.

---

## 15. Current Status

This landing-page copy should be treated as a draft for the public website.

The next useful documents are:

- `docs\free_vs_paid_features.md`
- `docs\public_disclaimer.md`
- `docs\simulator_user_workflow.md`

Recommended next file:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\docs\free_vs_paid_features.md
```
