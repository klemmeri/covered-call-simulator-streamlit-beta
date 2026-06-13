# Covered Call Simulator — Free vs Paid Features

## 1. Purpose of This Document

This document defines the initial free-versus-paid feature structure for the Covered Call Simulator website.

The goal is to separate the product into two clear levels:

- A free educational version that demonstrates the simulator’s value.
- A paid configurable version that lets users test covered-call rules using their own assumptions.

The distinction should be simple:

> Free version = educational preview with fixed assumptions.

> Paid version = configurable covered-call simulator with account-aware, option-aware, and replay-based analysis.

The paid version should feel like a practical workflow tool, not merely a larger report.

---

## 2. Product Philosophy

The Covered Call Simulator should not be presented as a trade signal service.

It should be presented as a decision-support and education tool that helps users understand:

- How covered-call rules behave under different market conditions.
- How account size affects tradability.
- How option-selection choices affect outcomes.
- How rolling, closing, waiting, and assignment can change total equity.
- Why premium collected is not the same as profit.
- Why a covered-call strategy should be evaluated by total return, not just income.

Important product language:

> The simulator helps users compare covered-call decisions before risking capital.

Important limitation language:

> The simulator is not financial advice and does not recommend specific trades.

---

## 3. Free Version Overview

The free version should be simple, useful, and controlled.

It should demonstrate the core idea of the simulator without exposing the full configuration engine.

The free version should answer a narrow set of questions:

- What is a covered-call rule?
- How can different management rules produce different outcomes?
- Why does account size matter?
- Why can covered calls underperform in strong bull markets?
- Why does the underlying asset still drive much of the outcome?

The free version should be easy enough for a non-expert investor to understand.

Free-version positioning:

> Try a simple covered-call rule comparison using fixed assumptions.

---

## 4. Paid Version Overview

The paid version should allow users to model covered-call decisions using assumptions closer to their own trading process.

It should add:

- Custom tickers.
- Custom account size.
- Custom risk tier.
- User-selected delta.
- User-selected DTE.
- Strike-selection rules.
- Rolling assumptions.
- Profit-taking assumptions.
- Re-entry delay assumptions.
- Transaction-cost assumptions.
- Optionability and liquidity checks.
- Exportable reports.
- Real-Life Replay Simulator.
- Moving total-equity plot.

Paid-version positioning:

> Build and compare covered-call rules using your own account size, ticker choices, option-selection assumptions, and management rules.

---

## 5. Feature Comparison Table

| Feature | Free Version | Paid Version |
|---|---:|---:|
| Basic covered-call education | Yes | Yes |
| Limited preset tickers | Yes | Yes |
| Custom stock or ETF ticker | No | Yes |
| Optionability check | No | Yes |
| Option liquidity screen | No | Yes |
| Fixed account size | Yes | No |
| Custom account size | No | Yes |
| Fixed risk tier | Yes | No |
| Conservative / Balanced / Aggressive risk tiers | No | Yes |
| Basic rule comparison | Yes | Yes |
| Hold to expiration rule | Yes | Yes |
| Close at 50% profit rule | Yes | Yes |
| Wait 10 days rule | Limited or preview | Yes |
| Adaptive regime rule | Preview only | Yes |
| User-selectable target delta | No | Yes |
| User-selectable DTE | No | Yes |
| Strike-selection methodology | No | Yes |
| Rolling assumptions | No | Yes |
| Re-entry delay | No | Yes |
| Transaction-cost assumptions | Fixed | User configurable |
| Current tradability check | Limited | Yes |
| Account-size sensitivity | Limited | Yes |
| Position-size tier analysis | No | Yes |
| Regime-based comparison | Limited | Yes |
| Exportable report | No | Yes |
| Real-Life Replay Simulator | No or one demo | Yes |
| Moving total-equity plot | Demo only | Yes |
| Benchmark comparison | Limited | Yes |
| Saved scenarios | No | Future paid feature |
| Portfolio-level analysis | No | Future professional feature |

---

## 6. Free Version Feature Set

The free version should include enough functionality to show that the simulator is useful.

Recommended free features:

- Three preset tickers.
- One fixed account size.
- One fixed risk tier.
- One or two simple management rules.
- Basic outcome comparison.
- Basic account-size explanation.
- Limited current tradability check.
- Educational interpretation.
- Clear risk disclaimer.

Suggested free tickers:

- SPY
- QQQ
- IWM

Suggested free assumptions:

- Account size: $100,000.
- Risk tier: Balanced.
- Target delta: 0.30.
- DTE: 30 days.
- Transaction cost: fixed default.
- Assignment handling: simplified.

Suggested free rules:

- Hold to expiration.
- Close at 50% profit.

The free version should avoid too many controls. Its job is to make the concept clear.

---

## 7. Paid Version Feature Set

The paid version should unlock the full configurable simulator.

Recommended paid features:

- Any optionable, liquid stock or ETF.
- Custom account size.
- Custom risk tier.
- User-selectable delta.
- User-selectable DTE.
- User-selectable strike-selection rule.
- User-selectable profit-taking rule.
- User-selectable rolling rule.
- User-selectable re-entry delay.
- Transaction-cost assumptions.
- Current tradability.
- Regime-based rule comparison.
- Account-size sensitivity.
- Position-size tier analysis.
- Exportable reports.
- Real-Life Replay Simulator.
- Moving total-equity plot.

The paid version should help the user model a covered-call workflow that resembles how they actually trade.

---

## 8. Custom Ticker Support

The paid version should allow users to enter any stock or ETF ticker, provided the ticker has listed options and sufficient liquidity.

The simulator should not blindly accept every ticker.

A ticker should be screened for:

- Listed options.
- Underlying price availability.
- Underlying trading volume.
- Option-chain availability.
- Option bid/ask quotes.
- Reasonable bid/ask spreads.
- Open interest.
- Option volume.
- Availability of the selected DTE range.
- Availability of strikes near the selected target delta.
- Account-size tradability.

Possible ticker status labels:

- Tradable.
- Optionable but illiquid.
- Not optionable.
- Too large for selected account.
- Insufficient option-chain data.
- No suitable strike near selected delta.
- No suitable expiration near selected DTE.

Suggested user-facing warning:

> This ticker has listed options, but the option chain appears too illiquid for reliable covered-call simulation.

This feature should be paid because it requires broader data access, more validation logic, and more computational workflow.

---

## 9. User-Selectable Option Parameters

The paid version should allow users to control the option-selection assumptions that covered-call traders actually use.

Important paid inputs:

### Target Delta

Users should be able to select a target short-call delta, such as:

- 0.15
- 0.20
- 0.25
- 0.30
- 0.35
- 0.40

The simulator should then select the call strike closest to the target delta, subject to liquidity constraints.

### Days to Expiration

Users should be able to select a DTE target or range, such as:

- 7 DTE
- 14 DTE
- 21 DTE
- 30 DTE
- 45 DTE
- 60 DTE

The simulator should select the closest available expiration.

### Strike-Selection Method

Possible strike-selection choices:

- Closest to target delta.
- Fixed percentage out-of-the-money.
- Fixed dollar amount out-of-the-money.
- Closest strike above current price.
- Highest annualized premium subject to delta limit.
- Liquidity-filtered best match.

### Profit-Taking Rule

Possible choices:

- Hold to expiration.
- Close at 25% profit.
- Close at 50% profit.
- Close at 75% profit.
- Close when DTE falls below threshold.
- Close based on combined stock-plus-option P/L.

### Rolling Rule

Possible choices:

- Never roll.
- Roll when ITM.
- Roll when delta exceeds threshold.
- Roll when short call reaches a loss multiple.
- Roll out only.
- Roll out and up.
- Roll only for a net credit.
- Roll based on total position equity.

### Re-Entry Rule

Possible choices:

- Sell new call immediately.
- Wait fixed number of days.
- Wait for price recovery.
- Wait for volatility threshold.
- Wait for regime condition.
- Wait after assignment.

These controls are central to making the paid version valuable.

---

## 10. Real-Life Replay Simulator

The paid version should eventually include a Real-Life Replay Simulator.

This mode would allow users to watch a historical price path unfold over time without seeing the future. The user would make covered-call decisions as if trading live.

The replay simulator should allow the user to:

- Select a stock or ETF with listed, liquid options.
- Select a historical start period.
- Watch the underlying price move forward one bar at a time.
- Choose when to sell a covered call.
- Select target delta, DTE, and strike.
- Observe whether the short call moves out-of-the-money or in-the-money.
- Decide whether to hold, close, roll, wait, or accept assignment.
- Track premium collected, option value, stock value, total equity, and missed upside.
- Compare the user’s decisions against rule-based benchmarks.

Possible replay controls:

- Step forward one day.
- Step forward one week.
- Pause.
- Reset.
- Speed control.
- Hide future data.
- Reveal benchmark after completion.

Possible user actions:

- Sell a covered call.
- Close the short call.
- Roll out to a later expiration.
- Roll up to a higher strike.
- Roll down to a lower strike.
- Wait.
- Let the option expire.
- Accept assignment in the simulation.

The purpose of replay mode is to teach path dependence. A covered-call rule that looks simple in a summary table can feel much harder to follow when the user must make decisions without knowing the future.

Suggested positioning:

> Practice covered-call decisions on historical price paths without seeing the future.

---

## 11. Moving Total-Equity Plot

The Real-Life Replay Simulator should include a moving total-equity plot.

The plot should update as the simulated time series advances and after each user decision.

The plot should show:

- Starting account equity.
- Stock value.
- Cash.
- Premium collected.
- Open short-call mark-to-market value.
- Realized option gains or losses.
- Total covered-call equity.

Useful benchmark overlays:

- Buy-and-hold equity.
- Hold-to-expiration covered-call rule.
- Close-at-50%-profit rule.
- Wait-10-days rule.
- Adaptive regime rule.
- User-managed replay equity.

The purpose of the equity curve is to prevent users from focusing only on premium collected.

Important lesson:

> Premium collected is not the same as profit.

The moving equity plot should show whether covered-call decisions improved total wealth, reduced volatility, increased drawdown, capped upside, or simply created visible income while reducing total return.

Suggested display label:

> Total Equity Over Time

Suggested explanatory text:

> The equity curve combines stock value, option premium, open option value, realized option P/L, and cash. This helps show whether the covered-call decisions improved total account equity compared with buy-and-hold and rule-based benchmarks.

---

## 12. Benchmarks

The paid version should compare user results against simple benchmarks.

Recommended benchmarks:

- Buy and hold.
- Hold covered call to expiration.
- Close at 50% profit.
- Wait 10 days.
- Adaptive regime rule.

Optional future benchmarks:

- No-trade cash benchmark.
- Underlying with protective stop.
- Covered call with rolling for credit only.
- Covered call with fixed delta and fixed DTE.
- Covered call with volatility-based entry.

Benchmarks should be shown as comparisons, not recommendations.

Suggested wording:

> Benchmarks are included to help users compare outcomes. They are not recommendations.

---

## 13. Reports

The paid version should include exportable reports.

Recommended report contents:

- Ticker.
- Account size.
- Risk tier.
- Option-selection assumptions.
- Rule assumptions.
- Simulation period.
- Total return.
- Maximum drawdown.
- Premium collected.
- Option P/L.
- Stock P/L.
- Missed upside.
- Assignment events.
- Roll events.
- Benchmark comparison.
- Interpretation summary.
- Disclaimer.

Possible export formats:

- PDF.
- CSV.
- Excel.
- Markdown.

The first paid version could start with CSV and PDF.

---

## 14. Suggested Pricing Structure

The first pricing structure should be simple.

### Free

Educational preview.

Includes:

- Limited ticker list.
- Fixed account size.
- Fixed risk tier.
- Basic rule comparison.
- Simple educational interpretation.

### Individual

Configurable covered-call simulator.

Includes:

- Custom stock and ETF tickers.
- Optionability and liquidity screening.
- Custom account size.
- Risk-tier selection.
- User-selectable delta and DTE.
- Rule comparison.
- Current tradability.
- Exportable reports.
- Real-Life Replay Simulator.
- Moving total-equity plot.

### Future Professional

Advanced tools for advisors, educators, or serious researchers.

Possible future features:

- Portfolio-level covered-call simulations.
- Larger scenario library.
- Saved simulations.
- Client-ready reports.
- Custom rule design.
- More detailed historical option-chain analysis.
- Batch ticker screening.

---

## 15. Recommended Development Order

The paid-version features should not all be built at once.

Recommended order:

### Phase 1 — Free Public Simulator

Build a simple public simulator with fixed assumptions.

Focus:

- Clean user interface.
- Simple rule comparison.
- Plain-English interpretation.
- Clear disclaimers.

### Phase 2 — Paid Configurable Inputs

Add core paid controls.

Focus:

- Custom account size.
- Risk tier.
- User-selected delta.
- User-selected DTE.
- Rule selection.
- Exportable reports.

### Phase 3 — Custom Ticker and Liquidity Screen

Add broad ticker support.

Focus:

- Custom stock and ETF input.
- Optionability check.
- Liquidity check.
- DTE availability.
- Strike availability.
- Account-size screen.

### Phase 4 — Real-Life Replay Simulator

Add historical replay mode.

Focus:

- Moving price path.
- User decision points.
- Covered-call actions.
- Rolling decisions.
- Total-equity plot.
- Benchmark overlays.

### Phase 5 — Advanced Paid / Professional Features

Add larger-scale tools.

Focus:

- Saved scenarios.
- Portfolio-level analysis.
- Batch ticker screening.
- Client-ready reports.
- More detailed historical option-chain modeling.

---

## 16. Key Product Message

The paid version should be built around configurability and realism.

The central paid-version message:

> Test covered-call rules using your own account size, ticker choices, delta, DTE, and management assumptions.

The central replay-mode message:

> Practice covered-call decisions on historical price paths without seeing the future.

The central equity-curve message:

> Premium collected is not the same as profit. Watch total equity, not just income.

---

## 17. Current Recommendation

The free version should remain intentionally limited.

The paid version should unlock:

- Custom tickers.
- Liquidity screening.
- User-selected delta.
- User-selected DTE.
- Rule configuration.
- Account-size sensitivity.
- Exportable reports.
- Real-Life Replay Simulator.
- Moving total-equity plot.

This structure gives the product a clear business logic:

> Users can learn the idea for free, but pay for configurability, realism, and workflow depth.
