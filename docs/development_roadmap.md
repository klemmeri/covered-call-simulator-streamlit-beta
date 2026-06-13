# Covered Call Simulator — Development Roadmap

## 1. Purpose of This Roadmap

This roadmap defines the recommended development sequence for the Covered Call Simulator public website and product.

The project has evolved from a simple covered-call rule-comparison simulator into a broader product concept:

> A covered-call simulator, training tool, and decision-practice environment that helps users compare rules, practice covered-call management, review total-equity outcomes, and understand account-size constraints before risking capital.

The product should not be positioned as a trade signal service. Its value is education, structured simulation, active practice, and disciplined evaluation.

---

## 2. Current Product Positioning

The current product direction is:

> Test covered-call decisions before risking capital.

The product helps users answer questions such as:

- How do different covered-call rules behave?
- What happens if I hold to expiration?
- What happens if I close at 50% profit?
- How does account size affect which tickers are practical?
- How does delta, DTE, and strike selection affect the tradeoff?
- What happens if the short call moves near or into the money?
- When does rolling help, and when does it merely extend risk?
- How does premium collected compare with total account equity?
- How does the result compare with buy-and-hold?
- How does the result compare with a mechanical rule benchmark?

The central training message is:

> Premium collected is not the same as profit. Total equity is the main scorecard.

---

## 3. Current Public Website Prototype Status

The public Streamlit prototype is separate from the internal development dashboard.

Current public app path:

```text
public_site\app.py
```

Current launcher:

```text
app\run_public_site.py
```

Recommended local URL:

```text
http://localhost:8502
```

The public site currently includes these navigation sections:

```text
Start Here
Product
Simulator Previews
Training / Reports
Education
Legal
Developer Docs
```

Current pages include:

```text
Home
How It Works
FAQ
Product Roadmap
Pricing
Contact / Waitlist Preview
Free Simulator Preview
Paid Simulator Preview
Active CC Simulation Preview
Replay Simulator Preview
Training Mode Preview
Report Preview
Strategies Compared
Account Sizing
Market Regimes
Disclaimers
About
Planning Docs Preview
```

The latest public app version in this workflow is:

```text
public_site_app_v45.py
```

---

## 4. Key Product Concept

The Covered Call Simulator should eventually have three major layers:

### 4.1 Free Preview

A simple public-facing educational version.

Purpose:

- Demonstrate the product idea.
- Show basic covered-call rule comparison.
- Explain account-size constraints.
- Introduce total-equity thinking.
- Provide useful education without exposing the full engine.

Likely free assumptions:

- Preset tickers.
- Fixed account size.
- Fixed risk tier.
- Fixed target delta.
- Fixed DTE.
- Limited rule comparison.
- Limited report output.

### 4.2 Individual / Pro Paid Version

The first serious paid product.

Purpose:

- Let users configure realistic covered-call assumptions.
- Practice active covered-call decisions on historical paths.
- Compare user decisions with benchmarks.
- Produce professional session reports.

Likely Individual / Pro features:

- Custom stock or ETF ticker.
- Custom account size.
- Conservative / Balanced / Aggressive risk tiers.
- Target delta selection.
- Target DTE selection.
- Strike-selection method.
- Optionability and liquidity checks.
- Account-size tradability screen.
- Rule comparison.
- Historical active replay.
- Simulated covered-call placement.
- Simulated close, roll, wait, and assignment handling.
- Total-equity curve.
- Buy-and-hold benchmark.
- Mechanical rule benchmark.
- Training scorecard.
- Downloadable styled HTML reports.

### 4.3 Future Professional Version

A later, more advanced tier.

Purpose:

- Serve advisors, educators, professional users, and possibly small research teams.
- Provide richer training demonstrations and more realistic active simulation.

Possible Future Professional features:

- Real-time or near-real-time active simulation.
- Intraday price updates.
- Option-chain updates.
- More realistic bid/ask and liquidity modeling.
- Saved sessions.
- Client or classroom demonstrations.
- Client-ready reports.
- More export formats.
- Portfolio-level covered-call overlays.
- Batch ticker screening.
- Deeper analytics.

This version should not be built before the Individual / Pro product is validated.

---

## 5. Roadmap Phases

### Phase 1 — Public Product Story

Status: mostly complete in prototype.

Goal:

Make the website clearly explain what the product is, who it is for, and why active covered-call simulation is valuable.

Completed prototype elements:

- Home page emphasizing active covered-call decision practice.
- How It Works page explaining the full workflow.
- FAQ page.
- Pricing page.
- Product Roadmap page.
- Contact / Waitlist Preview page.
- Disclaimers page.
- About page.
- Organized sidebar navigation.
- Recommended Tour.

Primary deliverable:

A public prototype that explains the product without requiring the full paid engine.

---

### Phase 2 — Free Simulator Preview

Status: partially prototyped.

Goal:

Offer a useful, limited, educational simulator preview.

Core free features:

- Fixed assumptions.
- Preset tickers.
- Basic management-rule comparison.
- Account-size tradability estimate.
- Current snapshot when data is available.
- Simple rule interpretation.
- Clear disclaimer.

The free preview should answer:

> How do covered-call outcomes change when the management rule changes?

The free preview should not try to be a full trading platform.

---

### Phase 3 — Configurable Individual / Pro Simulator

Status: planned.

Goal:

Build the first paid product around configurability and account-aware analysis.

Required features:

- Custom ticker input.
- Ticker validation.
- Optionability check.
- Current price handling.
- Account-size input.
- Risk-tier selection.
- Target delta input.
- Target DTE input.
- Strike-selection logic.
- Position-size cap logic.
- Rule comparison.
- Scenario/regime comparison.
- Exportable reports.

Important paid-version principle:

> Paid users are not paying for predictions. They are paying for configurability, workflow depth, reports, and decision practice.

---

### Phase 4 — Historical Active Training Simulator

Status: planned; concept prototyped.

Goal:

Turn the simulator into a repeat-use covered-call training tool.

The user should be able to:

- Start with shares and cash.
- Step through a historical price path without seeing the future.
- Inspect candidate covered calls.
- Select strike and expiration.
- Sell a simulated covered call.
- Watch the short call move OTM, near the money, or ITM.
- Close the short call.
- Roll up, out, or up-and-out.
- Wait.
- Accept assignment in the simulation.
- Review total-equity results.

The active simulator should track:

- Stock value.
- Cash.
- Premium collected.
- Open short-call value.
- Realized option P/L.
- Unrealized option P/L.
- Total equity.
- Missed upside.
- Assignment condition.
- Buy-and-hold benchmark.
- Mechanical rule benchmark.
- Decision log.

Core message:

> Covered-call management is path-dependent. Users need to practice decisions as the market unfolds.

---

### Phase 5 — Training Mode

Status: concept prototyped.

Goal:

Organize the product into structured learning modules.

Suggested modules:

#### Beginner

- What is a covered call?
- Why does premium reduce some downside?
- Why does the short call cap upside?
- What does assignment mean?
- Why is premium not the same as profit?

#### Intermediate

- Delta selection.
- DTE selection.
- Strike choice.
- Closing at profit targets.
- Waiting before re-entry.
- Comparing rules.

#### Advanced

- Rolling decisions.
- Rolling for credit.
- Rolling up and out.
- Managing ITM calls.
- Regime sensitivity.
- Benchmark-aware review.

#### Future Professional

- Intraday active simulation.
- Live or near-live option-chain updates.
- Client/classroom demonstrations.
- Saved sessions.
- Professional reports.

Training Mode should emphasize:

- Decision repetition.
- Immediate feedback.
- Mistake discovery.
- Rule development.
- Process discipline.

---

### Phase 6 — Reports and Review Outputs

Status: concept prototyped.

Goal:

Give users a professional output after simulation sessions.

Current prototype direction:

- Styled HTML session report.
- Professional typography.
- Summary cards.
- Tables.
- Highlight boxes.
- Disclaimer footer.

Reports should include:

- Session setup.
- Ticker.
- Account size.
- Target delta.
- Target DTE.
- Strategy mode.
- Trade log.
- Equity curve.
- Premium collected.
- Missed upside.
- Roll impact.
- Buy-and-hold comparison.
- Rule benchmark comparison.
- Decision-quality notes.
- Training takeaway.
- Disclaimer.

Near-term export formats:

- HTML.
- CSV for trade logs.
- Possibly PDF later.

The report should reinforce:

> Judge the session by total equity and benchmark comparison, not by premium collected alone.

---

### Phase 7 — Waitlist / Interest Capture

Status: prototype only.

Goal:

Collect early user interest and validate product-market fit.

The waitlist should eventually capture:

- User type.
- Feature interest.
- Likely pricing tier.
- Main problem user wants solved.
- Email.
- Consent.
- Privacy acknowledgment.

Important:

The prototype form currently does not send, store, or transmit data.

Future deployment should include:

- Privacy language.
- Consent handling.
- Spam protection.
- Secure storage.
- Email list integration.
- Unsubscribe mechanism.

---

### Phase 8 — Future Professional Version

Status: later.

Goal:

Build an advanced tier only after the Individual / Pro product is validated.

Possible features:

- Real-time active covered-call simulation.
- Near-real-time price updates.
- Option-chain updates.
- Intraday training mode.
- More realistic bid/ask and fill assumptions.
- Saved sessions.
- Advisor/client demonstration mode.
- Client-ready reports.
- Batch ticker screening.
- Portfolio-level overlays.

Important caution:

Real-time simulation is data- and infrastructure-heavy. It should not be built before the historical replay and training product is stable.

---

### Phase 9 — Possible Institutional Research Engine

Status: possible long-term direction only.

Goal:

If the engine becomes sufficiently robust, it may be useful for more professional research.

Potential users:

- Advisors.
- Covered-call educators.
- Newsletter or research providers.
- Family offices.
- Small quant funds.
- Option-income product teams.
- Asset managers testing overlay strategies.

Institutional research questions might include:

- Which deltas perform best after transaction costs?
- When does closing at 50% outperform holding?
- Does rolling only for credit improve or hurt long-run performance?
- How do covered-call overlays behave in strong bull markets?
- Can regime filters reduce missed upside?
- How does real historical option-chain replay change the results?
- Which rules improve risk-adjusted return rather than just income?

This is not the near-term commercial product. It is a possible future evolution.

---

## 6. Recommended Build Order

Recommended sequence:

```text
1. Stabilize public prototype
2. Validate public product message
3. Build reliable free simulator preview
4. Build configurable paid simulator
5. Add historical active replay
6. Add training scorecard
7. Add styled HTML reports
8. Add saved sessions
9. Add payment/subscription layer
10. Consider Future Professional real-time simulation
```

Do not build first:

- Broker integration.
- Real order placement.
- Complex institutional analytics.
- Real-time option-chain engine.
- Portfolio optimizer.
- Hedge-fund research platform.

The near-term product should remain focused:

> Covered-call training, decision practice, account-aware simulation, and professional session reports.

---

## 7. Key Implementation Priorities

### 7.1 Public Site Stability

- Keep public site separate from the internal dashboard.
- Keep internal diagnostics out of the public interface.
- Preserve clear navigation.
- Keep disclaimers visible.
- Avoid presenting simulation output as advice.

### 7.2 Data Handling

- Show data timestamps.
- Detect stale output files.
- Distinguish historical, delayed, near-real-time, and illustrative data.
- Handle missing prices gracefully.
- Handle unavailable option data gracefully.

### 7.3 Option Modeling

Eventually needed:

- Ticker validation.
- Optionability check.
- Expiration selection by DTE.
- Strike selection by target delta.
- Bid/ask spread handling.
- Open interest and volume checks.
- Simplified fill assumptions.
- Transaction cost assumptions.
- Assignment modeling.
- Rolling logic.

### 7.4 Simulation Engine

Eventually needed:

- Path-level results.
- Cycle-level results.
- Trade/event log.
- Position state tracking.
- Cash tracking.
- Short-call mark-to-market.
- Realized and unrealized option P/L.
- Total-equity calculation.
- Benchmarks.
- Report export.

### 7.5 Training Logic

Eventually needed:

- Scenario definitions.
- Lesson modules.
- User decisions.
- Feedback messages.
- Scorecard metrics.
- Mistake detection.
- Benchmark explanations.

---

## 8. Current Public Prototype Pages and Purpose

### Home

Introduces the product as a covered-call simulator and training tool.

### How It Works

Explains the full workflow from assumptions to simulated trade management and reports.

### FAQ

Answers common questions about active simulation, training mode, paper trading, data timing, pricing tiers, and total-equity evaluation.

### Product Roadmap

Shows the recommended development sequence.

### Pricing

Explains Free, Individual / Pro, and Future Professional tiers.

### Contact / Waitlist Preview

Prototype interest form for validating user demand.

### Free Simulator Preview

Shows limited simulator output and account-size logic.

### Paid Simulator Preview

Shows future configurable paid controls.

### Active CC Simulation Preview

Shows the active covered-call training concept, including:

- Passive moving market demo.
- ITM threshold line.
- Simulated option-chain placement panel.
- Pre-trade impact preview.
- Post-trade position preview.
- Management triggers.
- Simulated decision log.
- Session review scorecard.
- Decision-quality notes.

### Replay Simulator Preview

Shows the planned historical replay concept.

### Training Mode Preview

Shows structured learning modules and training scorecard categories.

### Report Preview

Shows styled HTML session report concept.

### Strategies Compared

Explains covered-call management rules.

### Account Sizing

Explains one-contract minimum equity logic.

### Market Regimes

Explains direction and volatility as separate regime dimensions.

### Disclaimers

Covers paper simulation, hypothetical results, data timing, no real trade placement, training-mode limitations, and options risk.

### About

Explains product philosophy and intended users.

### Planning Docs Preview

Developer-facing planning reference.

---

## 9. Product Boundaries

The product should not claim:

- Guaranteed income.
- Guaranteed outperformance.
- Market prediction.
- Trade recommendations.
- Personalized financial advice.
- Tax advice.
- Real fill certainty.
- Real assignment certainty.

The product should consistently say:

- The simulator is educational.
- Results are hypothetical.
- Training actions are paper simulation only.
- Options involve risk.
- Covered calls can lose money.
- Covered calls can underperform in strong bull markets.
- Regime detection is probabilistic guidance, not an oracle.
- Total equity matters more than premium collected.

---

## 10. Near-Term Next Steps

Recommended next coding/documentation steps:

1. Keep testing the public site navigation.
2. Clean up any visual inconsistencies in long pages.
3. Review Pricing page after roadmap/navigation changes.
4. Review Product Roadmap page for business clarity.
5. Ensure Disclaimers appear on all high-risk pages.
6. Decide whether to add screenshots or mock images later.
7. Begin designing the real paid simulator data model.
8. Define a first historical replay scenario.
9. Define required option-chain fields.
10. Define the session report schema.

---

## 11. First Real Paid Engine Requirements

A first real paid engine should minimally support:

```text
Ticker
Current price
Account size
Risk tier
Position-size cap
Target delta
Target DTE
Strike selection
Expiration selection
Covered-call premium estimate
Rule choice
Trade log
Position state
Total equity
Benchmark comparison
Report output
```

The first paid engine does not need:

```text
Real-time data
Broker integration
Institutional analytics
Portfolio optimization
Perfect option pricing
Live order simulation
```

---

## 12. Final Roadmap Principle

The project should proceed in this order:

> Clarity first. Reliability second. Configurability third. Active training fourth. Real-time professional features last.

The strongest near-term commercial thesis is:

> A covered-call training system that lets investors practice decisions, see total-equity consequences, and compare outcomes before risking capital.
