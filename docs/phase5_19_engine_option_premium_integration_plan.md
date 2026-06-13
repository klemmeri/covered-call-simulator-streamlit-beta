# Phase 5-19 — Engine-Level Option-Premium Integration Plan

This checkpoint creates the plan for integrating imported option-chain premium information into the core Covered Call Simulator engine.

It is intentionally add-only:

- No dashboard change.
- No customer workflow change.
- No core engine file replacement.
- Synthetic mode remains the default.
- Historical/imported-data behavior remains explicit only.

## Why this checkpoint exists

Phase 5 has already promoted the historical price-path capability into the engine-facing path while preserving the synthetic default. The next natural integration point is option premium handling.

Option premium integration should be handled more carefully than price paths because premium affects the central covered-call economics:

- option credit received,
- breakeven,
- assignment outcome,
- net option effect,
- strategy comparison versus buy-and-hold.

## Planned engine touchpoints

The likely engine files are:

- `app\strategy.py`
- `app\portfolio.py`
- `app\simulator.py`
- `app\config.py`

Dashboard integration should wait until the engine behavior is stable.

## Output files

This checkpoint writes:

- `outputs\tables\paid_simulator\phase5_19_engine_option_premium_integration_plan_summary.csv`
- `outputs\tables\paid_simulator\phase5_19_option_premium_engine_touchpoints.csv`
- `outputs\tables\paid_simulator\phase5_19_option_premium_patch_order.csv`
- `outputs\tables\paid_simulator\phase5_19_prior_option_artifact_status.csv`
- `outputs\reports\paid_simulator\phase5_19_engine_option_premium_integration_plan.json`
- `outputs\reports\paid_simulator\phase5_19_engine_option_premium_integration_plan_report.txt`

## Recommended next checkpoint

After Phase 5-19 passes, close Phase 5 with:

`Phase 5-20 — Phase 5 completion handoff`

Then begin Phase 6 with dashboard integration or option-premium engine integration, depending on whether the priority is customer workflow or deeper model realism.
