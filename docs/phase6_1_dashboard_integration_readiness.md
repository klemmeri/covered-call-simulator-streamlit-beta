# Phase 6-1 — Dashboard Integration Readiness

This checkpoint begins Phase 6 of the Covered Call Simulator project.

Phase 6 is the dashboard-integration phase. The purpose is to expose the Phase 5 engine work through the paid Streamlit dashboard without disturbing the working synthetic-mode customer workflow.

## Scope

This checkpoint is intentionally add-only.

It does not modify:

- `app\paid_simulator\config_form_app.py`
- `app\price_paths.py`
- `app\simulator.py`
- any public customer workflow

## Purpose

Phase 6-1 creates a readiness map for future dashboard changes.

It confirms that:

- Phase 5 has closed.
- The paid dashboard file exists.
- The promoted engine files exist.
- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Dashboard touchpoints are mapped before the live dashboard is patched.

## Outputs

The checkpoint creates:

- `outputs\tables\paid_simulator\phase6_1_dashboard_integration_artifact_status.csv`
- `outputs\tables\paid_simulator\phase6_1_dashboard_integration_touchpoints.csv`
- `outputs\tables\paid_simulator\phase6_1_recommended_dashboard_integration_sequence.csv`
- `outputs\tables\paid_simulator\phase6_1_dashboard_integration_readiness_summary.csv`
- `outputs\reports\paid_simulator\phase6_1_dashboard_integration_readiness.json`
- `outputs\reports\paid_simulator\phase6_1_dashboard_integration_readiness_report.txt`

## Recommended next checkpoint

Phase 6-2 should create a dashboard mode-selector candidate.

That checkpoint should still avoid patching the live dashboard. The live dashboard patch should wait until the candidate UI contract is validated.

## Commercial framing caution

Historical-import mode should be presented as a scenario-analysis input, not as a forecast engine. Regime or historical-data interpretation should be framed as probabilistic guidance rather than an oracle.
