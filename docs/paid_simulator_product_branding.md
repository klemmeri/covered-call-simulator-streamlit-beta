# Paid Simulator Product Branding Checkpoint

## Product name

**Covered Call Strategy Stress Test**

## Version label

**Paid Simulator Dashboard v0.1**

## Build label

**2026-06-11 local checkpoint**

## Release stage

**Local prototype / pre-release dashboard**

## Product subtitle

A paid-simulator dashboard for comparing covered-call setups across modeled market paths.

## Positioning statement

The dashboard is designed to help a user understand the income, risk, and upside tradeoffs of a covered-call setup before opening or comparing positions. It is a decision-support tool, not a trade recommendation engine.

## Primary customer workflow

1. Choose or edit a covered-call setup.
2. Validate sizing and assumptions.
3. Run the simulator across modeled market paths.
4. Review best, worst, and average relative outcomes versus buy-and-hold.
5. Inspect scenario details and decision guidance.
6. Export a Markdown or PDF decision memo.
7. Compare presets and review run history.

## Key product limitations

- Market paths are modeled scenarios, not forecasts.
- Regime detection, if later added, should be treated as probabilistic guidance, not an oracle.
- Covered calls may lag sharply in strong rallies because upside can be capped.
- Historical or simulated outcomes do not guarantee future performance.
- Transaction costs, slippage, tax treatment, early assignment, dividends, and broker execution details can materially affect real results.

## Implementation note

The metadata is stored in:

```text
app\paid_simulator\product_info.py
```

The PyCharm test runner is:

```text
app\run_paid_simulator_product_info.py
```

This checkpoint is intentionally add-only. It does not replace or modify the working Streamlit dashboard files.
