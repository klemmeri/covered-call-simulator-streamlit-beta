# Paid Simulator Phase 2 Price-Path Scaffold

## Purpose

This add-only scaffold converts the Phase 2 scenario definitions into deterministic modeled price paths.

It does not replace the existing paid simulator engine. It is a research layer that prepares the project for more credible scenario modeling.

## Added files

```text
app\paid_simulator\scenario_price_paths.py
app\run_paid_simulator_price_path_check.py
docs\paid_simulator_phase2_price_path_scaffold.md
```

## Output file

The checker writes:

```text
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
```

## Current modeling approach

Each scenario has a total modeled return and a path shape. The price-path scaffold converts that into a deterministic sequence of prices.

Initial path shapes include:

```text
linear
front_loaded
back_loaded
choppy
whipsaw
```

## Why deterministic first

The first Phase 2 modeling layer is deterministic on purpose. It makes the dashboard easier to test and debug before adding random simulation, volatility sampling, regime assumptions, option repricing, or Monte Carlo logic.

## Next logical step

After this scaffold passes, the next step is to connect these generated paths to a standalone option-payoff approximation module, then compare its output against the current paid simulator results before replacing anything.
