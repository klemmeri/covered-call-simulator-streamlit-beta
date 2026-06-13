# Covered Call Simulator — Public Disclaimer

## 1. Purpose of This Document

This document provides public-facing disclaimer language for the Covered Call Simulator website.

The disclaimer should be used on:

- The website footer.
- The simulator page.
- The pricing page.
- The report export page.
- Downloaded reports.
- Any public-facing page that discusses simulated results, covered calls, option strategies, market regimes, or tradability.

The language should be clear, direct, and non-alarmist.

The main point:

> The Covered Call Simulator is an educational and analytical tool. It is not financial advice, investment advice, or a trade recommendation.

---

## 2. Short Footer Disclaimer

Use this short version in the website footer.

Suggested footer text:

> The Covered Call Simulator is for education and research only. It does not provide financial advice, investment advice, or trade recommendations. Options involve risk and are not suitable for all investors. Simulated results are hypothetical and may not reflect actual trading outcomes.

---

## 3. Standard Website Disclaimer

Use this version on the main disclaimer page and near simulator outputs.

Suggested text:

> The Covered Call Simulator is an educational and analytical tool. It is not financial advice, investment advice, tax advice, legal advice, or a trade recommendation. The simulator is designed to help users compare covered-call rules, account-size assumptions, option-selection assumptions, and market-regime scenarios. It does not recommend that any user buy, sell, hold, or write any security or option contract.

> Simulated results are hypothetical. They are based on assumptions, historical data, estimated option behavior, modeled option prices, or user-selected inputs. Actual trading results may differ materially from simulated results because of market conditions, liquidity, bid/ask spreads, commissions, taxes, assignment, execution quality, volatility changes, and user behavior.

> Options involve risk and are not suitable for all investors. Covered calls can lose money if the underlying security declines. Covered calls can also underperform the underlying security in strong rising markets because upside may be capped by the short call.

---

## 4. Options Risk Disclaimer

Use this section on pages that discuss covered calls, deltas, DTE, strike selection, rolling, or assignment.

Suggested text:

> Options involve risk and are not suitable for all investors. A covered call requires ownership of the underlying shares and the sale of a call option against those shares. Although the option premium may provide partial downside offset, the investor remains exposed to losses in the underlying security.

> Covered calls can also limit upside potential. If the underlying security rises above the call strike, the investor may miss part of the upside, may need to buy back the short call at a loss, may roll the position, or may be assigned.

> Rolling a covered call does not eliminate risk. Rolling may defer a decision, increase trade complexity, increase transaction costs, or lock in unfavorable economics. A roll that produces a credit may still reduce total return if it caps future upside or extends risk exposure.

---

## 5. Simulation Disclaimer

Use this section near simulation results and exported reports.

Suggested text:

> Simulation results are hypothetical and should not be interpreted as actual trading performance. Simulated results depend on assumptions about price movement, option pricing, volatility, transaction costs, liquidity, assignment, and trade management. Different assumptions can produce different results.

> Past market behavior does not guarantee future results. Historical replay and backtested results can help users study how a strategy might have behaved under past conditions, but they cannot predict how the same strategy will perform in the future.

> The simulator should be used to compare scenarios, not to identify guaranteed trades.

---

## 6. Regime Detection Disclaimer

Use this section anywhere the website discusses bullish, bearish, sideways, high-volatility, or low-volatility market regimes.

Suggested text:

> Market-regime labels are scenario inputs and probabilistic guidance. They are not market predictions. Regime detection is imperfect and should not be treated as an oracle.

> The simulator may classify recent completed daily bars as bullish, bearish, sideways, high volatility, or low volatility. These labels are used to help compare covered-call rules under different market conditions. They do not guarantee that future market behavior will match the detected regime.

Short version:

> Regime detection is probabilistic guidance, not an oracle.

---

## 7. Current Price and Market Data Disclaimer

Use this section near current tradability checks and quote displays.

Suggested text:

> Current-price data may be delayed, incomplete, or unavailable. The simulator may use near-current prices, latest daily bars, or other available market data depending on the data source. Users should verify prices, option quotes, bid/ask spreads, and liquidity with their brokerage platform before making any trading decision.

> A ticker shown as tradable in the simulator only means that it passes the selected account-size and position-size screen. It does not mean the ticker is recommended, liquid enough for the user’s specific trade, or expected to outperform.

Short version:

> Tradable means the ticker passes the selected account-size and position-size screen. It is not a trade recommendation.

---

## 8. Option Chain and Liquidity Disclaimer

Use this section when the paid version supports custom tickers, delta, DTE, strike selection, and option liquidity screening.

Suggested text:

> The simulator may screen option chains for bid/ask spreads, open interest, volume, DTE availability, and strikes near a selected target delta. These screens are intended to identify whether a ticker appears suitable for meaningful covered-call analysis. They do not guarantee that an actual trade can be executed at the displayed price or that liquidity will remain available.

> Option markets can change quickly. Bid/ask spreads, open interest, option volume, and implied volatility may differ by broker, exchange, data source, and time of day.

> Users should independently verify option-chain liquidity before placing any order.

---

## 9. Replay Simulator Disclaimer

Use this section for the Real-Life Replay Simulator.

Suggested text:

> The Real-Life Replay Simulator allows users to practice covered-call decisions on historical price paths without seeing future data. This feature is intended for education and decision practice. It does not guarantee that similar decisions will work in future markets.

> Replay results depend on the selected period, ticker, option assumptions, user decisions, transaction costs, liquidity assumptions, and benchmark rules. A user’s result in replay mode should not be interpreted as evidence of future skill or expected future performance.

> Historical replay can help users understand path dependence, rolling decisions, missed upside, drawdowns, and total-equity behavior. It should not be treated as a predictive trading system.

---

## 10. Total Equity Plot Disclaimer

Use this section near the moving equity curve.

Suggested text:

> The total-equity plot is designed to show the combined effect of stock value, option premium, open option value, realized option profit or loss, and cash. It is intended to help users evaluate total account behavior rather than focusing only on premium collected.

> Premium collected is not the same as profit. A covered-call strategy may collect option premium while still losing money because of underlying price declines, option buyback losses, missed upside, assignment, or poor timing.

Short version:

> Premium collected is not the same as profit. Watch total equity, not just income.

---

## 11. Tax Disclaimer

Use this section in the main disclaimer page and exported reports.

Suggested text:

> The Covered Call Simulator does not provide tax advice. Options transactions, covered calls, assignments, rolls, dividends, wash sales, qualified covered-call treatment, holding periods, and short-term versus long-term gains may have tax consequences. Users should consult a qualified tax professional regarding their own situation.

---

## 12. No Fiduciary Relationship

Suggested text:

> Use of the Covered Call Simulator does not create a fiduciary, advisory, brokerage, client, or professional relationship. The user remains responsible for all investment decisions, trading decisions, tax decisions, and risk management decisions.

---

## 13. Brokerage and Execution Disclaimer

Suggested text:

> The simulator does not execute trades and is not a brokerage platform. Users must place any trades through their own brokerage account. Actual execution prices may differ from simulated or displayed values because of bid/ask spreads, order type, market movement, liquidity, commissions, fees, exchange rules, and broker-specific execution practices.

---

## 14. Report Export Disclaimer

Use this in exported PDF, CSV, Excel, or Markdown reports.

Suggested text:

> This report was generated by the Covered Call Simulator for educational and analytical purposes only. It is not financial advice, investment advice, tax advice, or a trade recommendation. Results are hypothetical and depend on the assumptions used in the simulation. Actual trading results may differ materially.

Recommended report footer:

> Educational use only. Not financial advice. Not a trade recommendation. Options involve risk.

---

## 15. Suggested Disclaimer Placement

Recommended placement by page:

### Home Page

Use the short footer disclaimer.

### Simulator Page

Use:

- Standard website disclaimer.
- Current price and market data disclaimer.
- Simulation disclaimer.
- Regime detection disclaimer.

### Strategies Page

Use:

- Options risk disclaimer.
- Simulation disclaimer.

### Account Sizing Page

Use:

- Current tradability disclaimer.
- Account-size screen explanation.

### Market Regimes Page

Use:

- Regime detection disclaimer.

### Pricing Page

Use:

- Short disclaimer.
- Reminder that paid tools are analytical, not advisory.

### Replay Simulator Page

Use:

- Replay simulator disclaimer.
- Total equity plot disclaimer.
- Simulation disclaimer.

### Exported Reports

Use:

- Report export disclaimer.
- Options risk disclaimer.
- Simulation disclaimer.

---

## 16. Recommended Short Disclaimers for UI Components

### Trading Readiness

> Trading Readiness confirms data freshness only. It is not a trade recommendation.

### Practical Action

> This is an operating-status label for the simulator. It is not a trade recommendation.

### Tradable

> Tradable means the ticker passes the selected account-size and position-size screen. It does not mean the ticker should be traded.

### Regime

> Regime labels are scenario inputs based on completed data. They are not predictions.

### Replay

> Replay mode hides the future to help users practice decisions. Historical replay does not predict future results.

### Equity Curve

> Total equity includes stock value, option value, realized P/L, and cash. Premium collected alone is not profit.

---

## 17. Master Disclaimer

This is the full version that can be used on the main Disclaimers page.

> The Covered Call Simulator is an educational and analytical tool. It is not financial advice, investment advice, tax advice, legal advice, or a trade recommendation. The simulator does not recommend that any user buy, sell, hold, write, close, roll, or exercise any security or option contract.

> Simulated results are hypothetical and depend on the assumptions used in the model. Actual trading results may differ materially from simulated results because of market movement, liquidity, bid/ask spreads, commissions, fees, taxes, assignment, volatility changes, execution quality, user behavior, and other factors.

> Options involve risk and are not suitable for all investors. Covered calls can lose money if the underlying security declines and can underperform the underlying security in rising markets because upside may be capped by the short call. Rolling a covered call does not eliminate risk and may increase complexity or reduce total return.

> Market-regime labels are probabilistic guidance and scenario inputs, not predictions. Regime detection is imperfect and should not be treated as an oracle.

> Current-price and option-chain data may be delayed, incomplete, or unavailable. Users should verify all prices, quotes, liquidity, and option-chain information with their brokerage platform before making any trading decision.

> Historical replay and backtested results are for education and research only. They do not guarantee future performance.

> The Covered Call Simulator does not provide tax advice. Users should consult qualified financial, tax, legal, or investment professionals before making decisions based on their own circumstances.

---

## 18. Current Recommendation

Use short disclaimers throughout the product interface and keep the full disclaimer on a dedicated page.

The most important recurring messages are:

- Not financial advice.
- Not a trade recommendation.
- Options involve risk.
- Simulated results are hypothetical.
- Regime detection is probabilistic guidance, not an oracle.
- Tradable does not mean recommended.
- Premium collected is not the same as profit.
