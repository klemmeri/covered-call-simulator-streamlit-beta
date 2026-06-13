# Covered Call Simulator — Website Plan

## 1. Purpose of the Website

The website will present the Covered Call Simulator as a practical research, training, and comparison tool for investors who want to evaluate covered-call management rules before risking capital.

The product should not be presented as a trade signal service. Its core value is helping users compare rules, account-size constraints, ticker behavior, market-regime scenarios, and user-selected covered-call assumptions in a structured way.

Core positioning:

> A covered-call simulator that helps investors compare management rules, position-size limits, option-selection assumptions, and market-regime scenarios before risking capital.

The simulator should help answer questions such as:

- Should I hold covered calls to expiration?
- Should I close covered calls after capturing 50% of the premium?
- Should I wait a fixed number of days before selling another call?
- How does the answer change in bullish, bearish, sideways, high-volatility, or low-volatility markets?
- Which tickers are practical for my account size?
- How much capital is required to write one covered-call contract safely under my position-size rules?
- How do target delta, DTE, strike-selection method, and rolling behavior change the result?
- Would my own decisions have improved or harmed total equity during a historical replay?

The website should emphasize education, scenario comparison, disciplined position sizing, and realistic decision practice.

---

## 2. Target User

The primary user is an individual investor who understands the basic idea of covered calls but wants a better way to compare covered-call management rules.

Likely users include:

- Retired or semi-retired investors seeking income.
- ETF investors considering covered calls on SPY, QQQ, IWM, TQQQ, SOXL, or similar products.
- Investors who already sell covered calls but are unsure when to close, roll, wait, or hold.
- Investors who want to understand how account size affects whether a ticker is practical.
- Investors who want to test their own delta, DTE, and rolling assumptions.
- Quantitatively curious investors who want simulation-based evidence rather than simple rules of thumb.

The website should avoid assuming the user is an options professional. It should explain concepts clearly while still offering enough depth for serious investors.

---

## 3. Product Positioning

The Covered Call Simulator should be positioned as a decision-support and training tool, not a black-box recommendation engine.

Recommended product framing:

> Compare covered-call rules under different market conditions, account-size assumptions, and option-selection settings.

The product should help users think in terms of:

- Probability.
- Scenario behavior.
- Position sizing.
- Regime sensitivity.
- Option-selection assumptions.
- Trade management rules.
- Rolling decisions.
- Capital requirements.
- Practical tradability.
- Total equity, not premium alone.

It should not promise:

- Guaranteed income.
- Predictive market timing.
- A best ticker.
- A best rule for all conditions.
- A guaranteed market-regime classification.
- A guarantee that historical replay decisions will work in the future.

Important language:

> Regime detection is probabilistic guidance, not an oracle.

---

## 4. Product Modes

The product should eventually have two major simulator modes.

### Mode 1 — Strategy Comparison Simulator

This is the current core concept. It compares predefined covered-call rules across tickers, account-size assumptions, and market-regime scenarios.

This mode is best for answering:

- Which rule performs better under this scenario?
- Which tickers are practical for this account size?
- How do risk-tier assumptions affect tradability?
- How does the adaptive rule compare with fixed rules?

### Mode 2 — Real-Life Replay Simulator

This is the interactive paid workflow. It lets the user watch a historical price path unfold over time without seeing the future. The user can decide when to sell a covered call, choose delta and DTE, and manage the position as the market moves.

This mode is best for answering:

- How would I behave if I had to make decisions one step at a time?
- Would I close, hold, roll, or wait?
- Did my decisions improve total equity compared with simple rule-based benchmarks?
- Did premium collection actually improve the account, or did it hide missed upside or option buyback losses?

---

## 5. Free Version

The free version should be simple, useful, and educational.

Its purpose is to demonstrate the value of the simulator without exposing the full analytical engine.

Possible free features:

- Limited preset ticker list.
- Fixed account size.
- Fixed risk tier.
- Fixed option assumptions.
- Limited strategy comparison.
- Basic covered-call rule explanation.
- Simple current tradability estimate.
- Limited regime summary.
- Educational explanation of covered-call tradeoffs.

Suggested free tickers:

- SPY.
- QQQ.
- IWM.

Suggested free rules:

- Hold to expiration.
- Close at 50% profit.

Suggested free assumptions:

- Account size: $100,000.
- Risk tier: Balanced.
- Target delta: 0.30.
- DTE: 30 days.
- Transaction costs: fixed default.

Free-version goal:

> Show users how covered-call outcomes change when the management rule changes.

The free version should be a clear educational preview, not the full configurable research platform.

---

## 6. Paid Version

The paid version should focus on deeper analysis, broader coverage, user configurability, and workflow tools.

Paid-version goal:

> Provide a configurable, account-aware covered-call simulator that helps users evaluate rules using their own ticker, account, delta, DTE, liquidity, and management assumptions.

Possible paid features:

- User-selected ticker input.
- Support for any stock or ETF with listed, sufficiently liquid options.
- Custom account size.
- Conservative / Balanced / Aggressive position-size tiers.
- User-selectable target delta.
- User-selectable DTE or DTE range.
- User-selectable strike-selection method.
- User-selectable profit-taking rule.
- User-selectable re-entry delay.
- User-selectable roll assumptions.
- User-selectable transaction cost assumptions.
- Assignment-handling assumptions.
- Current tradability checks.
- Regime-based rule comparison.
- Exportable reports.
- More market scenarios.
- More rule comparisons.
- More detailed account-size sensitivity.
- More detailed position-size tier analysis.
- Real-Life Replay Simulator.
- Moving total-equity plot.

Expanded market scenarios:

- Bullish.
- Bearish.
- Sideways.
- High volatility.
- Low volatility.

Rule comparisons:

- Hold to expiration.
- Close at 50% profit.
- Wait 10 days.
- Adaptive regime rule.
- User-configured rule.

The paid version should feel like a workflow tool, not just a larger information page.

---

## 7. Custom Ticker Support

The paid version should allow users to enter any stock or ETF ticker, provided the security has listed options and sufficient liquidity for meaningful covered-call analysis.

The simulator should first run an optionability and liquidity screen before presenting results. A ticker should not be treated as suitable merely because it has options. The option chain should also be liquid enough for realistic analysis.

Ticker eligibility checks should include:

- Whether the stock or ETF has listed options.
- Whether the underlying has sufficient trading volume.
- Whether the relevant option expirations are available.
- Whether the option chain has usable bid/ask quotes.
- Whether bid/ask spreads are reasonably narrow.
- Whether open interest and/or option volume are sufficient.
- Whether the selected delta and DTE range can be found.
- Whether one covered-call contract is practical for the user’s account size.

The simulator should classify ticker eligibility with labels such as:

- Tradable.
- Optionable but illiquid.
- Not optionable.
- Too large for selected account.
- Insufficient option-chain data.

Suggested warning:

> This ticker has listed options, but the option chain appears too illiquid for reliable covered-call simulation.

The paid version should support broad ticker flexibility while still protecting users from simulations based on unrealistic or untradeable option assumptions.

---

## 8. User-Selectable Option Parameters

The paid version should allow users to configure the option-selection variables that covered-call traders actually use.

Important user-selectable parameters:

- Target delta.
- DTE or DTE range.
- Strike-selection method.
- Minimum premium.
- Maximum bid/ask spread.
- Minimum open interest.
- Minimum option volume.
- Profit-taking threshold.
- Re-entry delay.
- Roll trigger.
- Roll target delta.
- Roll target DTE.
- Roll-for-credit requirement.
- Assignment handling.
- Transaction cost assumption.

Example configuration:

- Ticker: QQQ.
- Account size: $100,000.
- Risk tier: Balanced.
- Target delta: 0.30.
- DTE: 30 to 45 days.
- Profit-taking rule: close at 50% of credit captured.
- Roll rule: roll out and up for a net credit if the short call becomes ITM.

This configurability is a major reason to pay for the product.

---

## 9. Real-Life Replay Simulator

The paid version should eventually include a real-life replay simulator.

This mode would allow the user to watch a historical price series unfold over time without seeing the future. The user could decide when to open a covered call, choose the target delta and DTE, and then manage the position as the underlying moves.

The replay simulator should allow the user to:

- Select a stock or ETF with listed, liquid options.
- Select a historical start date.
- Watch the underlying price move forward one bar at a time.
- Choose when to sell a covered call.
- Select strike, target delta, and DTE.
- Observe whether the short call moves out-of-the-money or in-the-money.
- Decide whether to hold, close, roll, or wait.
- Track premium collected, unrealized P/L, missed upside, and assignment risk.
- Compare the user’s decisions against rule-based benchmarks.

Possible user actions:

- Sell a covered call.
- Close the short call.
- Roll out to a later expiration.
- Roll up to a higher strike.
- Roll down to a lower strike.
- Wait without selling a new call.
- Let the option expire.
- Accept assignment in the simulation.

The purpose of this mode is to make the simulator feel more like real covered-call decision-making. It should help users understand that covered-call management is path-dependent. A rule that looks simple in a final performance table can feel much harder to execute when the user must make decisions without knowing the future.

Suggested positioning:

> Practice covered-call decisions on historical price paths without seeing the future.

The replay simulator should not be presented as a game or a prediction tool. It should be framed as a training and decision-support environment.

Important limitation:

> Historical replay can help users practice decisions, but it does not guarantee that similar decisions will work in future markets.

---

## 10. Moving Total-Equity Plot

The replay simulator should include a moving total-equity plot that updates as the simulated market path advances.

The plot should show how the user’s covered-call position evolves over time, including the combined effect of the underlying stock, option premium, open option value, realized gains or losses, and cash.

The core equity curve should show:

- Starting account equity.
- Current stock value.
- Cash from option premium.
- Open short-call mark-to-market value.
- Realized gains or losses from closed calls.
- Total covered-call account equity.

The plot should update after each simulated time step and after each user action, such as selling a call, closing a call, rolling the call, waiting, or accepting assignment.

Useful benchmark overlays could include:

- Buy-and-hold equity.
- Hold-to-expiration covered-call rule.
- Close-at-50%-profit rule.
- Wait-10-days rule.
- Adaptive regime rule.
- User-managed replay result.

The purpose of the moving equity plot is to show whether the user’s decisions are actually improving the equity curve compared with simple benchmarks.

The replay simulator should make it clear that premium collected is not the same as profit. A short call can show collected income while total equity suffers because of missed upside, option buyback losses, or underlying price declines.

Suggested display label:

> Total Equity Over Time

Suggested explanatory text:

> The equity curve updates as the historical replay unfolds. It combines stock value, option premium, open option value, realized option P/L, and cash. This helps show whether the covered-call decisions improved total account equity compared with buy-and-hold and rule-based benchmarks.

---

## 11. Public Website Pages

The initial website should be simple and focused.

Recommended pages:

1. Home.
2. How It Works.
3. Simulator.
4. Strategies Compared.
5. Account Sizing.
6. Market Regimes.
7. Replay Simulator.
8. Pricing.
9. Disclaimers.
10. About.

---

## 12. Home Page

The home page should quickly explain what the product does.

Possible headline:

> Test covered-call rules before risking capital.

Possible subheadline:

> Compare covered-call management rules across account sizes, ETFs, option-selection settings, and market-regime scenarios using a practical simulator built for income-focused investors.

The home page should include:

- A short explanation of the simulator.
- A sample result.
- A simple comparison of covered-call rules.
- A mention of configurable paid features.
- A mention of replay-based decision practice.
- A clear statement that the tool is educational and analytical.
- A call to action to try the free simulator.

Suggested call to action:

> Try the Free Simulator

Secondary call to action:

> See How It Works

---

## 13. How It Works Page

This page should explain the simulator in plain English.

Suggested structure:

### Step 1 — Choose a ticker

The user selects an ETF or stock candidate. Paid users can enter custom stock or ETF tickers, subject to optionability and liquidity checks.

### Step 2 — Choose an account size

The simulator checks whether one covered-call contract is practical under the selected account-size assumptions.

### Step 3 — Choose option assumptions

Paid users can select assumptions such as target delta, DTE, strike-selection method, transaction cost, and liquidity filters.

### Step 4 — Choose a management rule

The simulator compares rules such as holding to expiration, closing at 50% profit, waiting before re-entering, rolling, or using an adaptive regime rule.

### Step 5 — Compare outcomes

The simulator summarizes performance across scenarios and shows the tradeoffs between return, volatility, missed upside, and capital requirement.

### Step 6 — Practice decisions in replay mode

Paid users can watch a historical price path unfold and manage a covered call as if they were trading live.

### Step 7 — Interpret results cautiously

The simulator provides scenario guidance and decision practice, not a trade command.

---

## 14. Simulator Page

The simulator page should become the core product page.

For the first public version, the simulator should not expose every internal dashboard section.

Recommended public simulator sections:

- Ticker selection.
- Account size.
- Risk tier.
- Option parameters.
- Liquidity screen.
- Rule comparison.
- Current tradability.
- Scenario summary.
- Equity curve summary.
- Educational interpretation.

Option parameters should include:

- Delta.
- DTE.
- Strike-selection approach.
- Profit-taking rule.
- Re-entry rule.
- Roll assumptions.

Internal dashboard sections that should probably remain hidden or simplified:

- Raw dashboard report.
- Full current-price snapshot.
- Full regime snapshot.
- Full position-size tiers table.
- Full account-size sensitivity table.
- Raw diagnostic files.

The public simulator should be cleaner than the internal Streamlit dashboard.

---

## 15. Replay Simulator Page

The replay simulator deserves its own public page once it becomes part of the paid product.

This page should explain:

- How historical replay works.
- Why the future path is hidden during replay.
- How users choose when to sell, close, roll, or wait.
- How total equity is calculated.
- How user decisions compare with benchmarks.
- Why replay is training, not prediction.

Possible headline:

> Practice covered-call decisions without seeing the future.

Possible subheadline:

> Watch a historical price path unfold, choose when to sell or roll covered calls, and see how your decisions affect total equity compared with simple rule-based benchmarks.

---

## 16. Strategies Compared Page

This page should explain the covered-call management rules.

Rules to explain:

### Hold to Expiration

The investor sells a covered call and generally holds it until expiration.

Advantages:

- Simple.
- Low maintenance.
- Easy to understand.

Disadvantages:

- Can leave money on the table.
- May be slow to adapt.
- Can produce assignment or missed-upside issues.

### Close at 50% Profit

The investor buys back the short call after capturing 50% of the original credit.

Advantages:

- Captures time decay earlier.
- Reduces exposure after much of the premium has been earned.
- Can free capital for another trade.

Disadvantages:

- More active.
- May increase transaction frequency.
- May not outperform in every market regime.

### Wait 10 Days

The investor waits before selling another covered call.

Advantages:

- Can reduce overtrading.
- May allow the underlying to recover or trend.
- Can help avoid immediately selling calls after unfavorable moves.

Disadvantages:

- May miss premium collection opportunities.
- Depends heavily on the market environment.
- Requires patience and discipline.

### Adaptive Regime Rule

The simulator maps completed-bar market conditions to a practical rule.

Advantages:

- More flexible.
- Can respond to broad market behavior.
- Helps compare rule behavior across regimes.

Disadvantages:

- Regime detection is imperfect.
- It should not be treated as a forecast.
- It adds complexity.

Important wording:

> The adaptive rule is a scenario-based guide, not a market prediction.

---

## 17. Account Sizing Page

This page should explain why some tickers are too large for a given account.

Core formula:

> Estimated minimum equity = 100 shares × current price ÷ selected per-position cap

Example:

If a ticker trades at $70 and the selected cap is 10%, then one covered-call contract requires approximately:

> 100 × $70 ÷ 0.10 = $70,000

This page should explain:

- Why covered calls require 100 shares per contract.
- Why high-priced ETFs may require large accounts.
- Why leveraged ETFs should use smaller position-size caps.
- Why account size affects which tickers are practical.
- Why “tradable” does not mean “recommended.”

Suggested wording:

> Tradable means the ticker passes the selected account-size and position-size screen. It does not mean the ticker is expected to outperform or that a trade should be opened today.

---

## 18. Market Regimes Page

This page should explain how the simulator uses market regimes.

Regime categories:

- Bullish.
- Bearish.
- Sideways.
- High volatility.
- Low volatility.

Important framing:

> Regime detection is probabilistic guidance, not an oracle.

The page should explain that regimes are based on completed daily bars and are used to compare rule behavior under different market conditions.

The page should also explain that option-selection assumptions can materially affect covered-call outcomes. Paid users should be able to test different inputs such as target delta and DTE to see how strategy behavior changes across regimes.

Recommended wording:

> The simulator uses regime labels as scenario inputs. These labels help compare how different covered-call rules might behave under different market conditions. They are not predictions and should not be treated as trading signals.

---

## 19. Pricing Page

The pricing page should keep the first version simple.

Possible pricing structure:

### Free

For users who want to understand the basic covered-call rule comparison.

Includes:

- Limited ticker list.
- Fixed account-size assumption.
- Fixed delta and DTE assumptions.
- Basic rule comparison.
- Basic educational explanation.

### Individual

For investors who want configurable account-aware analysis.

Includes:

- More tickers.
- Custom ticker input subject to optionability and liquidity checks.
- Custom account size.
- Risk-tier selection.
- User-selectable delta and DTE assumptions.
- User-selectable rule assumptions.
- Current tradability.
- Regime-based rule comparison.
- Exportable reports.
- Replay simulator.
- Moving total-equity plot.

### Future Professional Tier

For advisors, educators, or advanced users.

Possible future features:

- Larger ticker universe.
- Portfolio-level simulations.
- Custom rule design.
- More export formats.
- Saved reports.
- Historical scenario library.
- Replay assignments for students or clients.

The first version does not need to implement all tiers immediately. The page can begin with Free and Individual.

---

## 20. Disclaimers Page

The disclaimers should be visible, clear, and non-alarmist.

Important points:

- The simulator is for education and research.
- It is not financial advice.
- It does not recommend specific trades.
- It does not guarantee income.
- Options involve risk.
- Covered calls can lose money if the underlying declines.
- Covered calls can underperform the underlying in strong bull markets.
- Regime detection is uncertain.
- Historical replay is training, not prediction.
- Current-price data may be delayed.
- Option-chain data may be delayed or incomplete.
- Tax treatment depends on the user’s situation.

Suggested disclaimer language:

> The Covered Call Simulator is an educational and analytical tool. It is not financial advice, investment advice, or a trade recommendation. Simulated results are hypothetical and may not reflect actual trading outcomes. Options involve risk and are not suitable for all investors.

---

## 21. About Page

The About page should emphasize the project’s analytical foundation.

Possible positioning:

> The Covered Call Simulator was built to answer a practical question: how do covered-call management rules behave under different market conditions, account-size constraints, and option-selection assumptions?

The About page can mention:

- The project is simulation-based.
- It focuses on practical covered-call management.
- It emphasizes account sizing and rule comparison.
- It includes user-configurable option assumptions.
- It may include historical replay for decision practice.
- It avoids presenting a single universal “best” rule.

Tone should be credible, careful, and direct.

---

## 22. Public Features vs Internal Dashboard Features

The internal dashboard is useful for development and diagnostics. The public website should be simpler.

Public-facing features:

- Clean rule comparison.
- Current tradability result.
- Account-size explanation.
- Option-parameter selection.
- Liquidity screen.
- Regime-rule summary.
- Simple charts or tables.
- Equity curve summary.
- Plain-English interpretation.
- Replay mode for paid users.

Internal-only or advanced diagnostic features:

- Raw dashboard report.
- Raw CSV snapshots.
- Full file timestamp table.
- Full account-size sensitivity table.
- Full position-size tier table.
- Refresh/run instructions.
- Development diagnostics.

The public product should not expose implementation details unless they directly help the user.

---

## 23. Recommended Initial Website Structure

Initial site map:

```text
/
    Home

/how-it-works
    How the simulator works

/simulator
    Free simulator or simulator preview

/replay
    Real-life replay simulator explanation or paid feature preview

/strategies
    Covered-call rules compared

/account-sizing
    Minimum equity and position-size logic

/regimes
    Market-regime explanation

/pricing
    Free vs paid

/disclaimers
    Risk and educational-use disclaimer

/about
    Project background
```

---

## 24. Recommended Development Milestones

### Milestone 1 — Documentation

Create product planning documents:

- `docs\website_plan.md`
- `docs\landing_page_copy.md`
- `docs\free_vs_paid_features.md`
- `docs\public_disclaimer.md`
- `docs\replay_simulator_spec.md`

### Milestone 2 — Static Website Prototype

Build a simple static site or Streamlit public-facing prototype with:

- Home page.
- How It Works page.
- Simulator preview page.
- Replay simulator preview page.
- Pricing page.
- Disclaimer page.

### Milestone 3 — Public Simulator Prototype

Create a simplified simulator interface that hides internal diagnostics and presents:

- Ticker.
- Account size.
- Risk tier.
- Option parameters.
- Rule comparison.
- Current tradability.
- Plain-English interpretation.

### Milestone 4 — Paid Configurable Simulator

Add paid-user configuration:

- Custom ticker input.
- Optionability check.
- Liquidity screen.
- Delta selection.
- DTE selection.
- Strike-selection method.
- Rolling and exit assumptions.
- Transaction cost assumptions.

### Milestone 5 — Exportable Reports

Add simple downloadable reports for paid users.

### Milestone 6 — Real-Life Replay Simulator

Add the historical replay workflow:

- Moving price path.
- User-selected covered-call actions.
- Rolling and closing decisions.
- Total-equity plot.
- Buy-and-hold benchmark.
- Rule-based benchmark overlays.

### Milestone 7 — Payment / Subscription Layer

Add paid access only after the public simulator workflow is clear and stable.

---

## 25. Recommended Next File

The next useful file is:

```text
docs\landing_page_copy.md
```

This file should draft the actual public-facing home page copy.

It should include:

- Hero headline.
- Hero subheadline.
- Main call to action.
- Problem section.
- Solution section.
- Feature section.
- Free vs paid teaser.
- Replay simulator teaser.
- Disclaimer language.
- Footer wording.

Recommended landing-page headline:

> Test covered-call rules before risking capital.

Recommended landing-page subheadline:

> Compare covered-call management rules across account sizes, ETFs, option-selection settings, and market-regime scenarios using a practical simulator built for income-focused investors.

---

## 26. Current Status

The internal Streamlit dashboard is now a polished development baseline.

Completed dashboard improvements include:

- Trading Readiness guard.
- Data Snapshot row.
- Refresh / Run Guidance.
- Current Decision section.
- Practical Action card.
- Why this rule card.
- Tradable Candidates summary.
- Compact Strategy Overview.
- Position-Size Assumptions.
- Clean Current Price Snapshot.
- Clean Market Regime Snapshot.
- Clean Account Tradability Check.
- Compact Data Status.
- Compact Rule Summary.
- Collapsed diagnostic sections.
- ET timestamp handling.
- Cache invalidation based on file modified timestamps.

The next project phase should focus on turning the simulator into a clear public-facing product, starting with landing-page copy and a public simulator concept.
