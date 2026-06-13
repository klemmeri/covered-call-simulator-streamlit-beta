# Paid Simulator Customer Demo Walkthrough

## Product

**Covered Call Strategy Stress Test**  
**Version:** Paid Simulator Dashboard v0.1  
**Stage:** Local prototype / pre-release dashboard

This walkthrough is intended for a short customer-facing demonstration of the paid simulator dashboard. It focuses on what the user sees, what decisions the app supports, and how the output should be interpreted.

## Core message

The dashboard is designed to help a user understand the income, risk, and upside tradeoffs of a covered-call setup before opening or comparing positions. It is a decision-support tool, not a trade recommendation engine.

## Demo setup

Use **Customer view** unless you are demonstrating development or diagnostic tools.

Default clean demo configuration:

| Field | Value |
|---|---:|
| Ticker | SPY |
| Account size | 600000 |
| Risk tier | Balanced |
| Max position size | 10% |
| Contracts | 1 |
| Call delta target | 0.30 |
| Days to expiration | 30 |
| Stock price | 545.25 |

## Recommended demo sequence

### 1. Start on Overview

Show the product title and explain the dashboard purpose:

> This app stress-tests a covered-call setup across modeled market paths and compares the covered call to buy-and-hold.

Point out:

- Configuration status
- Latest best/worst/average result
- Current interpretation
- Decision guidance
- Recommended next action

### 2. Open Setup & run

Show the preset selector and core setup fields.

Explain:

- A lower delta is usually more conservative.
- A higher delta usually collects more premium but caps more upside.
- The position-size cap prevents the requested contract count from exceeding the selected sizing limit.

Click:

1. **Save config**
2. **Run simulator**
3. Optionally **Run health check**

### 3. Open Latest results

Point out the main decision metrics:

- Market paths tested
- Best relative result
- Worst relative result
- Average relative result

Explain relative result:

> Relative result means covered-call result minus buy-and-hold result. Positive means the covered call helped in that scenario. Negative means buy-and-hold did better.

Show the interpretation and decision guidance. Emphasize that a covered call can be sensible even when it underperforms buy-and-hold in a strong rally, because the strategy is income/risk-shaping rather than return-maximizing.

### 4. Open Scenario detail cards

Open the downtrend and strong-rally cards.

Explain:

- Downtrend: premium may cushion the stock result.
- Strong rally: the short call may cap upside and create relative underperformance.

### 5. Export a decision memo

Click either:

- **Export Markdown memo**
- **Export PDF memo**

Explain that this creates a customer-facing summary of the configuration, results, interpretation, decision guidance, scenario table, and limitations.

### 6. Open Preset comparison

Run or review the latest preset comparison.

Explain:

> The preset comparison helps identify which setup performs best across the same modeled market paths. The best preset is not guaranteed to be profitable; it is simply the least unfavorable or most favorable under the modeled scenario set.

### 7. Open Report

Show the full HTML report as the polished standalone report output.

## Important limitations to state clearly

- The market paths are modeled scenarios, not forecasts.
- The dashboard is not investment advice.
- A negative relative result does not necessarily mean the covered call lost money; it may mean it underperformed buy-and-hold.
- A positive relative result does not guarantee future outperformance.
- Real-world results can differ because of fills, bid/ask spreads, volatility changes, dividends, early assignment, taxes, and broker execution details.

## Suggested closing statement

> The value of the dashboard is that it makes the covered-call tradeoff explicit before the trade is opened. It shows where the setup helps, where it lags, how position sizing behaves, and whether a more conservative or aggressive preset looks better under the same scenario set.
