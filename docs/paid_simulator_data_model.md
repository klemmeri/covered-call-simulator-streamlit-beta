# Covered Call Simulator — Paid Simulator Data Model

## 1. Purpose of This Document

This document defines the initial data model for the future paid version of the Covered Call Simulator.

The public website prototype now explains the product story:

> A covered-call simulator, training tool, and decision-practice environment that helps users compare rules, practice covered-call management, review total-equity outcomes, and understand account-size constraints before risking capital.

The next development step is to define the objects the real paid simulator must track.

The paid simulator should support:

- Custom ticker analysis.
- Account-aware covered-call feasibility checks.
- User-selected delta and DTE assumptions.
- Simulated option selection.
- Simulated covered-call placement.
- Closing, rolling, waiting, and assignment handling.
- Historical active replay.
- Total-equity tracking.
- Benchmark comparison.
- Downloadable reports.

This document is a planning document. It is not executable code.

---

## 2. Design Principle

The simulator should be organized around **position state**, not just option premium.

The core principle is:

> Premium collected is not the same as profit. Total equity is the main scorecard.

Therefore, every simulation should be able to track:

- Shares.
- Cash.
- Short option liability.
- Realized option P/L.
- Unrealized option P/L.
- Stock value.
- Total equity.
- Benchmark equity.
- Missed upside.
- Trade decisions.
- Reportable session results.

---

## 3. Major Data Objects

The paid simulator should eventually use these major objects:

```text
SimulationInput
TickerSnapshot
OptionCandidate
SelectedOption
TradeEvent
PositionState
EquitySnapshot
BenchmarkSnapshot
TrainingFeedback
SessionReport
```

These can be implemented as Python dataclasses, Pydantic models, dictionaries, or pandas DataFrames. For early development, dataclasses plus DataFrames will probably be simplest.

---

## 4. SimulationInput

### Purpose

Stores the user's simulation assumptions.

### Fields

```text
session_id
created_timestamp
mode
ticker
account_size
risk_tier
position_size_cap
target_delta
target_dte
strike_selection_method
management_rule
profit_take_percent
rolling_rule
reentry_rule
transaction_cost_per_contract
slippage_assumption
data_source
```

### Example

```text
ticker: SPY
account_size: 100000
risk_tier: Balanced
position_size_cap: 0.10
target_delta: 0.30
target_dte: 30
strike_selection_method: Closest to target delta
management_rule: Close at 50% profit
rolling_rule: Roll only for net credit
reentry_rule: Wait 10 days
```

### Notes

This object should be stored with every report so results are reproducible.

---

## 5. TickerSnapshot

### Purpose

Stores current or historical ticker-level data used by the simulator.

### Fields

```text
ticker
timestamp
price
previous_close
daily_return
data_status
quote_type
is_price_available
is_optionable
has_sufficient_liquidity
```

### Example

```text
ticker: SPY
timestamp: 2026-06-10 10:15 ET
price: 545.25
data_status: current
is_optionable: True
has_sufficient_liquidity: True
```

### Notes

The simulator should always distinguish:

```text
historical
delayed
near-real-time
current
illustrative
missing
```

A public or paid result should never imply live data if the data are stale, delayed, or illustrative.

---

## 6. AccountFeasibility

### Purpose

Determines whether one covered-call contract is practical for the selected account.

### Fields

```text
ticker
price
shares_required
contract_multiplier
stock_value_required
account_size
position_size_cap
minimum_equity_required
passes_account_screen
reason
```

### Formula

```text
stock_value_required = price * 100
minimum_equity_required = stock_value_required / position_size_cap
```

### Example

```text
price: 545.25
shares_required: 100
stock_value_required: 54525
position_size_cap: 0.10
minimum_equity_required: 545250
passes_account_screen: False
reason: One contract exceeds selected position-size cap.
```

### Important Language

"Tradable" means the ticker passes the selected account-size and position-size screen. It does not mean a trade is recommended.

---

## 7. OptionCandidate

### Purpose

Represents one possible covered-call candidate.

### Fields

```text
ticker
expiration_date
dte
strike
option_type
bid
ask
mid
last
volume
open_interest
implied_volatility
delta
gamma
theta
vega
spread_width
spread_percent
moneyness
liquidity_score
is_candidate
candidate_reason
```

### Example

```text
ticker: SPY
expiration_date: 2026-07-10
dte: 30
strike: 560
option_type: call
bid: 2.25
ask: 2.39
mid: 2.32
delta: 0.30
open_interest: 10234
volume: 1842
spread_width: 0.14
moneyness: OTM
liquidity_score: Good
```

### Candidate Selection Logic

The first paid version should support:

```text
Closest to target delta
Fixed percent OTM
Fixed dollar OTM
Highest annualized premium subject to delta limit
Liquidity-filtered best match
```

---

## 8. SelectedOption

### Purpose

Stores the option the user actually selects for a simulated trade.

### Fields

```text
option_candidate_id
ticker
expiration_date
dte
strike
delta
bid
ask
mid
selected_price
selected_price_source
estimated_premium
estimated_transaction_cost
estimated_net_credit
selection_timestamp
selection_reason
```

### Example

```text
strike: 560
dte: 30
delta: 0.30
selected_price: 2.32
estimated_premium: 232
estimated_transaction_cost: 1.00
estimated_net_credit: 231
selection_reason: Closest to target delta with acceptable spread.
```

---

## 9. PreTradeImpact

### Purpose

Shows the user the tradeoff before a simulated covered call is placed.

### Fields

```text
stock_price
strike
premium_per_share
premium_cash
stock_value
upside_to_strike
gross_if_assigned
premium_yield
if_assigned_return
downside_buffer
assignment_pressure
notes
```

### Example Metrics

```text
Premium received
Upside to strike
Gross if assigned
Premium yield
Downside buffer
If-assigned return
```

### Important Lesson

The pre-trade impact preview should make the tradeoff explicit:

> More premium usually means less upside room, while farther OTM calls usually leave more upside but collect less income.

---

## 10. TradeEvent

### Purpose

Represents every user or rule-based action in the simulation.

### Event Types

```text
BUY_SHARES
SELL_COVERED_CALL
CLOSE_SHORT_CALL
ROLL_CALL
WAIT
EXPIRE_WORTHLESS
ASSIGNED
SELL_SHARES
DIVIDEND
FEE
SESSION_START
SESSION_END
```

### Fields

```text
event_id
session_id
timestamp
event_type
ticker
stock_price
shares_delta
cash_delta
option_symbol
option_quantity_delta
option_price
option_cash_delta
transaction_cost
realized_option_pl
realized_stock_pl
event_note
user_decision
rule_trigger
```

### Example

```text
event_type: SELL_COVERED_CALL
stock_price: 545.25
option_symbol: SPY_20260710_560_C
option_quantity_delta: -1
option_price: 2.32
option_cash_delta: 232
transaction_cost: 1.00
cash_delta: 231
event_note: User sold 30 DTE 0.30 delta covered call.
```

---

## 11. PositionState

### Purpose

Stores the account state after every event.

### Fields

```text
session_id
timestamp
ticker
shares
stock_price
stock_value
cash
short_call_symbol
short_call_quantity
short_call_strike
short_call_expiration
short_call_mark
short_call_market_value
realized_option_pl
unrealized_option_pl
realized_stock_pl
total_realized_pl
total_equity
capped_upside
assignment_status
days_to_expiration
moneyness
```

### Total Equity Formula

For one covered call:

```text
total_equity = cash + stock_value - short_call_market_value
```

Where:

```text
short_call_market_value = current_short_call_mark * 100
```

Because the short call is a liability, it reduces total equity.

### Important

This is the core object of the simulator. If PositionState is wrong, the simulator is wrong.

---

## 12. EquitySnapshot

### Purpose

Stores time-series values for plotting the total-equity curve.

### Fields

```text
timestamp
step_number
stock_price
cash
stock_value
short_call_value
total_equity
premium_collected_to_date
realized_option_pl
unrealized_option_pl
missed_upside
benchmark_buy_hold_equity
benchmark_rule_equity
```

### Charts

The paid simulator should eventually plot:

```text
Total equity over time
Stock price over time
Short call value over time
Buy-and-hold benchmark
Mechanical rule benchmark
Missed upside
```

### Important

The equity curve should be the central feedback mechanism.

---

## 13. BenchmarkSnapshot

### Purpose

Stores comparison values.

### Benchmarks

```text
Buy and hold
Hold covered call to expiration
Close at 50% profit
Wait 10 days
Adaptive regime rule
User active simulation
```

### Fields

```text
timestamp
benchmark_name
equity
cash
stock_value
option_value
realized_pl
unrealized_pl
notes
```

### Purpose

Benchmarks prevent users from evaluating a covered-call session only by premium collected.

---

## 14. TrainingFeedback

### Purpose

Stores the training interpretation after a decision or session.

### Fields

```text
feedback_id
session_id
timestamp
decision_area
feedback_type
message
severity
related_event_id
related_metric
suggested_lesson
```

### Feedback Types

```text
INFO
GOOD
WATCHLIST
WARNING
LESSON
```

### Example

```text
decision_area: Rolling
feedback_type: WATCHLIST
message: The roll created a net credit, but it extended the obligation and left the position capped.
suggested_lesson: Evaluate rolls by total equity and future exposure, not only by credit received.
```

---

## 15. SessionReport

### Purpose

Defines the output report after a simulation or training session.

### Fields

```text
session_id
created_timestamp
session_type
ticker
starting_equity
ending_equity
active_return
buy_hold_ending_equity
rule_benchmark_ending_equity
premium_collected
option_buyback_costs
net_option_pl
missed_upside
max_drawdown
number_of_calls_sold
number_of_rolls
number_of_closes
number_of_assignments
decision_summary
training_takeaway
disclaimer_text
```

### Export Formats

Near-term:

```text
HTML
CSV trade log
CSV equity curve
```

Later:

```text
PDF
DOCX
Client-ready report
```

---

## 16. DataFrame Outputs

The simulator should eventually produce these DataFrames:

```text
session_summary_df
trade_events_df
position_states_df
equity_curve_df
option_candidates_df
benchmark_df
training_feedback_df
report_sections_df
```

### session_summary_df

One row per simulation session.

### trade_events_df

One row per trade/action/event.

### position_states_df

One row after each event or market step.

### equity_curve_df

One row per time step for plotting.

### option_candidates_df

One row per available call candidate.

### benchmark_df

One row per benchmark per step.

### training_feedback_df

One row per feedback item.

---

## 17. Minimum Viable Paid Engine

The first real paid simulator should not attempt to do everything.

Minimum required:

```text
SimulationInput
TickerSnapshot
AccountFeasibility
OptionCandidate
SelectedOption
PreTradeImpact
TradeEvent
PositionState
EquitySnapshot
BenchmarkSnapshot
SessionReport
```

Minimum user workflow:

```text
1. User enters ticker and account size.
2. Simulator checks account feasibility.
3. Simulator generates candidate calls.
4. User selects a call.
5. Simulator shows pre-trade impact.
6. User sells simulated covered call.
7. Simulator tracks position state.
8. User can close, roll, wait, or continue.
9. Simulator updates total equity.
10. Simulator generates report.
```

---

## 18. Avoid in First Version

Do not include in the first paid engine:

```text
Broker integration
Real trade placement
Real-time professional simulation
Portfolio optimizer
Institutional parameter sweeps
Tax-lot optimizer
Complex margin model
Full hedge-fund analytics platform
```

These can come later only if the core product is validated.

---

## 19. Open Design Questions

Questions to answer before coding the paid engine:

1. Should the first real replay use daily bars or intraday bars?
2. Should option prices initially be estimated or loaded from historical option-chain data?
3. Should the first version simulate assignment only at expiration?
4. How should dividends be handled?
5. How should transaction costs be represented?
6. What liquidity filters should be required?
7. Should rolling be user-driven only, rule-driven only, or both?
8. How many benchmarks are needed in the first version?
9. Should reports be generated as HTML first, then PDF later?
10. Should saved sessions require user accounts immediately, or later?

---

## 20. Recommended Implementation Sequence

Recommended coding sequence:

```text
1. Define dataclasses or schema objects.
2. Build account feasibility function.
3. Build option candidate table from available data.
4. Build pre-trade impact calculator.
5. Build TradeEvent structure.
6. Build PositionState updater.
7. Build total-equity calculation.
8. Build simple benchmark calculations.
9. Build historical replay loop.
10. Build report generator.
11. Connect to public paid simulator page.
12. Add training feedback layer.
```

---

## 21. Final Design Rule

Every paid simulator feature should answer this question:

> Does this help the user make, understand, or review covered-call decisions more clearly?

If the answer is no, defer it.

The product should remain focused on:

> Covered-call training, decision practice, account-aware simulation, total-equity feedback, and professional reports.
