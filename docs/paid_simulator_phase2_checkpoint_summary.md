# Paid Simulator Phase 2 Scaffold Checkpoint Summary

## Project

Covered Call Strategy Stress Test — Paid Simulator Dashboard

## Checkpoint purpose

This checkpoint records the point where the Phase 2 scaffold is installed, passing, and visible from Developer view without disturbing the v0.1 customer-facing dashboard.

## Verified state before this checkpoint

The following checks were reported as passing:

- v0.1 release check
- App status check
- Customer-view readiness check
- Beta-demo readiness check
- Phase 2 scaffold pipeline check
- Phase 2 standalone viewer check
- Phase 2 integration-readiness check
- Phase 2 dashboard-tab check

## Current Phase 2 scaffold components

### Source modules

- `app/paid_simulator/scenario_model.py`
- `app/paid_simulator/scenario_price_paths.py`
- `app/paid_simulator/option_payoff_model.py`
- `app/paid_simulator/scenario_payoff_runner.py`
- `app/paid_simulator/scenario_payoff_report_adapter.py`
- `app/paid_simulator/phase2_v0_comparison_adapter.py`
- `app/paid_simulator/phase2_scaffold_viewer.py`

### Runner/check scripts

- `app/run_paid_simulator_phase2_readiness_check.py`
- `app/run_paid_simulator_scenario_model_check.py`
- `app/run_paid_simulator_price_path_check.py`
- `app/run_paid_simulator_option_payoff_check.py`
- `app/run_paid_simulator_scenario_payoff_check.py`
- `app/run_paid_simulator_scenario_payoff_report_check.py`
- `app/run_paid_simulator_phase2_v0_comparison_check.py`
- `app/run_paid_simulator_phase2_pipeline_check.py`
- `app/run_paid_simulator_phase2_viewer.py`
- `app/run_paid_simulator_phase2_viewer_check.py`
- `app/run_paid_simulator_phase2_integration_readiness_check.py`
- `app/run_paid_simulator_phase2_dashboard_tab_check.py`
- `app/run_paid_simulator_phase2_checkpoint_check.py`

### Generated Phase 2 outputs

- `outputs/tables/paid_simulator/scenario_price_paths_scaffold.csv`
- `outputs/tables/paid_simulator/option_payoff_scaffold.csv`
- `outputs/tables/paid_simulator/scenario_payoff_scaffold.csv`
- `outputs/tables/paid_simulator/scenario_payoff_report_scaffold.csv`
- `outputs/reports/paid_simulator/scenario_payoff_report_scaffold.html`
- `outputs/tables/paid_simulator/phase2_v0_comparison_scaffold.csv`
- `outputs/reports/paid_simulator/phase2_v0_comparison_scaffold.html`

## Dashboard integration status

The main dashboard now includes a Developer-view-only tab called:

- `Phase 2 scaffold`

This tab should not appear in Customer view. It allows inspection of scaffold outputs and running of Phase 2 checks from within the main dashboard.

## Design rule going forward

Phase 2 remains scaffolded and diagnostic until the model assumptions are reviewed. Do not expose Phase 2 results to Customer view as authoritative output until the assumptions are explicitly promoted from scaffold to production logic.

## Recommended next development step

Add a formal Phase 2 model-assumption review document and then begin replacing heuristic payoff assumptions with a more explicit option-pricing approximation layer.

Recommended next file:

- `docs/paid_simulator_phase2_model_assumption_review.md`

Recommended next code step after that:

- Improve or replace `option_payoff_model.py` with a documented pricing approximation that separates intrinsic payoff, premium estimate, volatility assumptions, and assignment behavior.
