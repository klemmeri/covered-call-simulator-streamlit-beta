# Phase 2 Option-Payoff Scaffold

This package adds a standalone payoff approximation layer for the paid covered-call simulator.

## Added files

```text
app\paid_simulator\option_payoff_model.py
app\run_paid_simulator_option_payoff_check.py
```

## Purpose

The existing v0.1 local prototype is stable and should not be disturbed while Phase 2 modeling is developed. This scaffold introduces a separate payoff module that can be tested independently before it is connected to the dashboard or simulator engine.

## Current model

The model approximates a single covered-call cycle using:

```text
start price
end price
short-call strike
short-call premium
contracts
transaction cost
slippage
```

It calculates:

```text
stock P/L
call intrinsic loss
premium income
buy-and-hold P/L
covered-call P/L
covered-call minus buy-and-hold
assignment flag
```

## Important limitation

This is not yet a full option-pricing engine. The included premium and strike estimators are stable demonstration heuristics, not Black-Scholes, binomial, or market-chain pricing models.

## Next likely step

Connect this payoff scaffold to the scenario price-path scaffold so each modeled path can generate a row-by-row covered-call result.
