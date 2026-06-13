# Paid Simulator Phase 2 Scenario-Payoff Scaffold

## Purpose

This scaffold connects the first three Phase 2 modeling pieces:

1. `app\paid_simulator\scenario_model.py`
2. `app\paid_simulator\scenario_price_paths.py`
3. `app\paid_simulator\option_payoff_model.py`

The new runner is:

```text
app\paid_simulator\scenario_payoff_runner.py
```

The PyCharm check script is:

```text
app\run_paid_simulator_scenario_payoff_check.py
```

## Output

The check writes:

```text
outputs\tables\paid_simulator\scenario_payoff_scaffold.csv
```

This CSV has one row per scenario. It combines:

- scenario metadata
- start price
- final modeled price
- realized path return
- covered-call payoff approximation
- buy-and-hold P/L
- covered-call P/L
- covered-call minus buy-and-hold
- assignment flag, if provided by the payoff model

## Design principle

This is a scaffold, not the production engine. It is deliberately separate from the existing paid simulator dashboard so the modeling layer can be improved without breaking the working v0.1 local prototype.

## Next development step

After this scaffold passes, the next logical step is to create a Phase 2 report-comparison output that can sit beside the existing v0.1 `scenario_comparison.csv` without replacing it.

Recommended next files:

```text
app\paid_simulator\phase2_report_adapter.py
app\run_paid_simulator_phase2_report_check.py
```
