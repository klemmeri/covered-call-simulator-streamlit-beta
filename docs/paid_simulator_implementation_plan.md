# Covered Call Simulator — Paid Simulator Implementation Plan

## 1. Purpose of This Document

This document translates the paid simulator data model into a practical implementation plan.

Previous planning file:

```text
docs\paid_simulator_data_model.md
```

This implementation plan answers:

- What should we build first?
- What Python files should be created?
- What functions and classes are needed?
- What should the first paid-engine MVP do?
- What should be deferred?
- How should the Streamlit public site eventually connect to the paid simulator engine?

The goal is to move from public prototype to a working configurable paid simulator without overbuilding the future professional version too early.

---

## 2. Product Build Priority

The near-term product should focus on:

> Configurable covered-call simulation with account-aware inputs, active historical training, total-equity feedback, and professional reports.

Do not start with:

- Broker integration.
- Real order placement.
- Real-time option-chain simulation.
- Institutional parameter sweeps.
- Portfolio optimization.
- Hedge-fund analytics.

Those may come later. The first paid engine should be reliable, understandable, and account-aware.

---

## 3. Recommended First MVP

The first paid simulator MVP should support one ticker, one covered-call position, and one session at a time.

### MVP User Workflow

```text
1. User enters ticker.
2. User enters account size.
3. User selects risk tier.
4. User selects target delta.
5. User selects target DTE.
6. Simulator checks account feasibility.
7. Simulator creates a candidate option table.
8. User selects one call candidate.
9. Simulator shows pre-trade impact.
10. User sells simulated covered call.
11. Simulator tracks position state.
12. User can wait, close, or roll.
13. Simulator updates total equity.
14. Simulator compares result with buy-and-hold.
15. Simulator generates a styled HTML report.
```

### MVP Should Track

```text
cash
shares
stock value
short call liability
premium collected
option buyback cost
realized option P/L
unrealized option P/L
total equity
buy-and-hold benchmark
event log
```

### MVP Can Initially Simplify

```text
Use one underlying.
Use one covered-call contract.
Use daily steps before intraday steps.
Use estimated option prices if historical option-chain data is unavailable.
Handle assignment at expiration only.
Use simple transaction costs.
Use simplified liquidity scoring.
Export HTML before PDF.
```

---

## 4. Proposed File Structure

Recommended new app files:

```text
app\paid_simulator\__init__.py
app\paid_simulator\models.py
app\paid_simulator\account.py
app\paid_simulator\option_candidates.py
app\paid_simulator\pre_trade.py
app\paid_simulator\events.py
app\paid_simulator\position.py
app\paid_simulator\benchmarks.py
app\paid_simulator\replay.py
app\paid_simulator\feedback.py
app\paid_simulator\reports.py
app\paid_simulator\demo_data.py
app\paid_simulator\runner.py
```

Optional later:

```text
app\paid_simulator\option_pricing.py
app\paid_simulator\liquidity.py
app\paid_simulator\assignment.py
app\paid_simulator\persistence.py
```

Public site page can later import from this engine, but the engine should be testable without Streamlit.

---

## 5. File Responsibilities

### 5.1 models.py

Defines core dataclasses.

Suggested classes:

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
TrainingFeedback
SessionReport
```

This file should contain data containers only. Avoid complex business logic here.

---

### 5.2 account.py

Handles account-size and position-size logic.

Core functions:

```text
get_position_size_cap(risk_tier, ticker)
calculate_minimum_equity_required(price, position_size_cap)
check_account_feasibility(ticker_snapshot, simulation_input)
```

Important formula:

```text
stock_value_required = price * 100
minimum_equity_required = stock_value_required / position_size_cap
```

Important output:

```text
passes_account_screen
minimum_equity_required
reason
```

---

### 5.3 option_candidates.py

Builds and filters candidate calls.

Core functions:

```text
build_option_candidate_table(...)
filter_by_dte(...)
filter_by_delta(...)
filter_by_liquidity(...)
select_candidate_by_method(...)
```

Initial MVP can use simulated or simplified candidate options.

Later version should use real option-chain data.

Candidate methods:

```text
Closest to target delta
Fixed percent OTM
Fixed dollar OTM
Highest annualized premium subject to delta limit
Liquidity-filtered best match
```

---

### 5.4 pre_trade.py

Calculates pre-trade covered-call impact.

Core function:

```text
calculate_pre_trade_impact(stock_price, strike_price, option_price, contract_multiplier=100)
```

Outputs:

```text
premium_cash
stock_value
upside_to_strike
gross_if_assigned
premium_yield
if_assigned_return
downside_buffer
assignment_pressure
```

This module supports the public-page section:

```text
Pre-trade impact preview
```

---

### 5.5 events.py

Defines trade/action events.

Core event types:

```text
SESSION_START
BUY_SHARES
SELL_COVERED_CALL
WAIT
CLOSE_SHORT_CALL
ROLL_CALL
EXPIRE_WORTHLESS
ASSIGNED
SESSION_END
```

Core functions:

```text
create_session_start_event(...)
create_sell_call_event(...)
create_wait_event(...)
create_close_call_event(...)
create_roll_call_event(...)
create_assignment_event(...)
```

Each event should be easy to convert into a row in `trade_events_df`.

---

### 5.6 position.py

Updates account state after each event and market step.

Core functions:

```text
initialize_position_state(...)
apply_trade_event(...)
mark_position_to_market(...)
calculate_total_equity(...)
```

Important total-equity formula:

```text
total_equity = cash + stock_value - short_call_market_value
```

This is the most important module.

If total equity is wrong, the simulator will teach the wrong lesson.

---

### 5.7 benchmarks.py

Calculates comparison benchmarks.

Initial benchmarks:

```text
buy_and_hold
hold_to_expiration
close_at_50_percent_profit
```

Later benchmarks:

```text
wait_10_days
adaptive_regime_rule
user_active_simulation
```

Core functions:

```text
calculate_buy_and_hold_equity(...)
calculate_rule_benchmark(...)
build_benchmark_snapshot(...)
```

Benchmarks are required because the user should not judge success by premium alone.

---

### 5.8 replay.py

Runs the historical replay loop.

MVP replay logic:

```text
initialize session
load price path
step through time
show available actions
apply user or scripted action
update position state
update equity curve
update benchmark
write event log
```

Core functions:

```text
initialize_replay_session(...)
advance_replay_step(...)
apply_user_action(...)
run_scripted_demo_replay(...)
```

For the first version, this can be scripted rather than fully interactive.

---

### 5.9 feedback.py

Generates training messages.

Core functions:

```text
evaluate_decision_quality(...)
generate_entry_feedback(...)
generate_strike_feedback(...)
generate_roll_feedback(...)
generate_close_feedback(...)
generate_benchmark_feedback(...)
```

Example feedback:

```text
The roll created a credit, but it extended the obligation and left the position capped.
Evaluate rolls by total equity and future exposure, not only by credit received.
```

---

### 5.10 reports.py

Generates styled reports.

Core functions:

```text
build_session_report(...)
render_html_report(...)
export_trade_log_csv(...)
export_equity_curve_csv(...)
```

Initial format:

```text
HTML
```

Later:

```text
PDF
CSV
DOCX
Client-ready report
```

Reports should reinforce:

> Premium collected is not the same as profit.

---

### 5.11 demo_data.py

Provides deterministic test/demo inputs.

Purpose:

- Avoid relying on live data during development.
- Make examples reproducible.
- Support public preview pages.

Core functions:

```text
build_demo_price_path()
build_demo_option_chain()
build_demo_simulation_input()
```

---

### 5.12 runner.py

Runs a complete paid simulator demo outside Streamlit.

Core function:

```text
run_paid_simulator_demo()
```

Outputs:

```text
session_summary_df
trade_events_df
position_states_df
equity_curve_df
benchmark_df
training_feedback_df
html_report
```

This file should be executable from PyCharm.

---

## 6. Recommended Build Sequence

### Step 1 — Create package folder

Create:

```text
app\paid_simulator
```

Add:

```text
__init__.py
```

---

### Step 2 — Build models.py

Create dataclasses for:

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
TrainingFeedback
SessionReport
```

Keep simple.

Do not add heavy logic yet.

---

### Step 3 — Build account.py

Implement:

```text
get_position_size_cap()
calculate_minimum_equity_required()
check_account_feasibility()
```

Test with:

```text
SPY
QQQ
IWM
SOXL
```

---

### Step 4 — Build option_candidates.py with demo data

Initial version can use simulated option candidates.

Do not require live option chains yet.

Implement:

```text
build_demo_option_candidates()
select_candidate_by_method()
```

---

### Step 5 — Build pre_trade.py

Implement pre-trade impact calculation.

Verify:

```text
premium received
upside to strike
gross if assigned
premium yield
downside buffer
if-assigned return
```

---

### Step 6 — Build position.py

Implement the core state updater.

This is the key milestone.

Must correctly update:

```text
cash
shares
stock value
short call liability
total equity
```

---

### Step 7 — Build events.py

Implement event creation and event-to-dict conversion.

Events should be easy to store in a DataFrame.

---

### Step 8 — Build replay.py

Create a simple scripted replay:

```text
start with 100 shares
sell a call
wait
stock rises
roll
stock pulls back
close call
review session
```

This should match the public-site story.

---

### Step 9 — Build benchmarks.py

Implement buy-and-hold benchmark first.

Then add a simple mechanical covered-call benchmark.

---

### Step 10 — Build reports.py

Generate a styled HTML report using the same design direction as the Report Preview page.

---

### Step 11 — Build runner.py

Create one executable demo run.

The output should be saved to:

```text
outputs\paid_simulator_demo
```

Suggested outputs:

```text
session_summary.csv
trade_events.csv
position_states.csv
equity_curve.csv
benchmark.csv
training_feedback.csv
session_report.html
```

---

### Step 12 — Connect public site later

Do not connect the public site until the engine is stable.

When ready, update:

```text
public_site\app.py
```

to read paid-engine demo outputs or call a safe demo runner.

---

## 7. First PyCharm Workflow

Recommended PyCharm sequence:

1. Create folder:

```text
app\paid_simulator
```

2. Create file:

```text
app\paid_simulator\__init__.py
```

3. Create file:

```text
app\paid_simulator\models.py
```

4. Add data classes.

5. Create:

```text
app\paid_simulator\runner.py
```

6. Run:

```text
runner.py
```

from PyCharm.

Only after the dataclasses work should we add calculation modules.

---

## 8. Testing Strategy

Initial tests can be simple script-based checks.

Eventually create:

```text
tests\test_paid_simulator_account.py
tests\test_paid_simulator_pre_trade.py
tests\test_paid_simulator_position.py
tests\test_paid_simulator_replay.py
```

Important tests:

```text
account feasibility calculation
premium calculation
upside-to-strike calculation
total-equity calculation
sell call event
close call event
roll call event
assignment event
buy-and-hold benchmark
```

Test edge cases:

```text
missing price
account too small
strike below stock price
wide bid/ask spread
zero option premium
short call ITM
expiration reached
```

---

## 9. Output Standards

Every simulator run should be able to produce:

```text
human-readable tables
CSV files
HTML report
clear data timestamps
clear disclaimer
```

Every output should distinguish:

```text
historical
current
delayed
illustrative
missing
```

No output should imply a trade recommendation.

---

## 10. Coding Standards

Use:

```text
dataclasses
type hints
plain functions
pandas DataFrames
small modules
explicit calculations
clear docstrings
```

Avoid:

```text
large monolithic scripts
hidden global state
broker dependencies
live data assumptions
overly clever abstractions
premature web-app integration
```

The paid simulator should be testable without Streamlit.

---

## 11. First MVP Definition of Done

The first engine MVP is complete when it can:

```text
1. Accept a SimulationInput.
2. Build a TickerSnapshot.
3. Check account feasibility.
4. Generate option candidates.
5. Select a candidate.
6. Calculate pre-trade impact.
7. Create a sell-call TradeEvent.
8. Update PositionState.
9. Step through a scripted replay.
10. Track total equity.
11. Compare with buy-and-hold.
12. Generate a styled HTML report.
```

If it cannot produce a correct total-equity path, it is not done.

---

## 12. Deferred Features

Defer until after MVP:

```text
real-time data
broker integration
live option-chain updates
real order placement
saved user accounts
payment integration
client portals
portfolio-level overlays
institutional parameter sweeps
```

---

## 13. Critical Risk Areas

### 13.1 Total Equity Errors

This is the largest conceptual risk.

The simulator must treat the short call as a liability.

Incorrect:

```text
total equity = stock value + cash
```

Correct:

```text
total equity = cash + stock value - short call market value
```

### 13.2 Premium Misinterpretation

Users may think premium collected equals profit.

The simulator should repeatedly show:

```text
premium collected
option liability
stock value
total equity
benchmark comparison
```

### 13.3 Rolling Misinterpretation

Users may think a net-credit roll is automatically good.

The simulator should show:

```text
net credit/debit
new upside cap
extended obligation
new assignment risk
effect on total equity
```

### 13.4 Regime Overconfidence

Users may treat regime labels as predictions.

The product should state:

> Regime labels are probabilistic scenario inputs, not trading signals.

---

## 14. Recommended Next Coding Step

The next practical coding step is:

```text
Create app\paid_simulator\models.py
```

with full dataclasses for the core data model.

Start small.

Do not connect it to Streamlit yet.

Suggested immediate files:

```text
app\paid_simulator\__init__.py
app\paid_simulator\models.py
app\paid_simulator\runner.py
```

The first runner can simply instantiate sample objects and print them.

---

## 15. Final Implementation Principle

Every new module should support the central product promise:

> Help users practice, understand, and review covered-call decisions before risking capital.

The implementation should remain focused on:

```text
account-aware simulation
active covered-call decision practice
total-equity feedback
benchmark comparison
professional reports
```
