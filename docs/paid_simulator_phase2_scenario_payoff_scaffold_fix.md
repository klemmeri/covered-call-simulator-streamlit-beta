# Phase 2 Scenario-Payoff Scaffold Fix

This fix replaces the original scenario-payoff connector with a more defensive version.

## Problem fixed

The previous connector expected this function in `scenario_model.py`:

```text
build_default_scenarios
```

but the installed scenario-model scaffold used a different helper name. The result was:

```text
cannot import name 'build_default_scenarios'
```

## Fix

The replacement `scenario_payoff_runner.py` now supports several possible scenario loader names:

```text
build_default_scenarios
get_default_scenarios
default_scenarios
build_scenarios
get_scenarios
load_default_scenarios
```

It also checks for scenario-list constants:

```text
DEFAULT_SCENARIOS
SCENARIOS
PHASE2_SCENARIOS
```

If none are found, it uses a small internal fallback scenario set so the scaffold checker remains usable.

## Output

The checker writes:

```text
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
```

This remains a Phase 2 scaffold output and does not replace the v0.1 paid simulator dashboard output.
