# Covered Call Strategy Stress Test - Phase 2 Decision Plan

## Current milestone

The project has reached a stable local-prototype milestone:

- Product: Covered Call Strategy Stress Test
- Version: Paid Simulator Dashboard v0.1
- Stage: Local prototype / pre-release dashboard
- Clean-demo config: verified
- Customer view: verified
- Developer view: verified
- Beta-demo readiness: verified
- Release package: created

## Why Phase 2 matters

The dashboard is now strong enough as a local product shell. The next work should improve the underlying commercial value. There are two natural directions:

1. Commercial website integration
2. More realistic option-pricing and scenario-modeling improvements

The recommended order is to improve the modeling first, then wrap it in a website. A polished website around weak assumptions is less valuable than a strong simulator that can later be placed behind a web interface.

## Recommended Phase 2 path

### Phase 2A - Modeling and analytics upgrade

Goal: improve the realism and credibility of the simulator while keeping the current dashboard stable.

Recommended additions:

1. Add a formal scenario-engine module separate from the dashboard.
2. Add scenario assumptions files that can be inspected and edited.
3. Improve option-premium estimates using implied-volatility style assumptions.
4. Add dividend/early-assignment placeholders, even if initially disabled.
5. Add scenario diagnostics that explain why a covered call helped or lagged.
6. Add tests/checkers for scenario consistency.
7. Preserve the clean demo as a controlled customer-facing example.

### Phase 2B - Website integration

Goal: convert the local prototype into a deployable product.

Recommended additions:

1. Choose a web stack after the model interface stabilizes.
2. Separate core simulation functions from Streamlit-specific UI code.
3. Define a paid/free feature boundary.
4. Add saved-user sessions or downloadable reports.
5. Add disclaimers and terms-of-use text.
6. Add a landing page and payment/subscription flow only after the simulator model is credible.

## Near-term next step

Build a Phase 2 modeling scaffold that does not break the current v0.1 dashboard.

Recommended files:

- app/paid_simulator/scenario_model.py
- app/run_paid_simulator_scenario_model_check.py
- docs/paid_simulator_phase2_modeling_scaffold.md

The first version should be add-only and should not replace the working dashboard.

## Product principle

Do not present scenario detection as an oracle. Scenario and regime labels should be treated as modeled assumptions or probabilistic guidance, not as market predictions.

## Restore point

Before any Phase 2 changes, preserve the v0.1 release zip:

covered_call_strategy_stress_test_v0_1_local_prototype_release.zip

This is the known-good local prototype restore point.
