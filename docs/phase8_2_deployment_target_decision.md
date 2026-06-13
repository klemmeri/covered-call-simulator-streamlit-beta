# Phase 8-2 — Deployment target decision

This checkpoint compares practical deployment targets for the paid Covered Call
Simulator before implementation work begins.

It is add-only and makes no dashboard or engine change.

Recommendation for the MVP:

- Use Streamlit Community Cloud or Streamlit-compatible paid hosting first.
- Defer a full custom web app until payment/access-control requirements justify it.
- Keep the current Streamlit dashboard workflow intact.
- Treat payment and customer access as separate implementation items.

Run:

`app\run_paid_simulator_phase8_2_deployment_target_decision_check.py`
