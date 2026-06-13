# Deployment Step 6 — Deployment handoff and manual hosting instructions

This checkpoint creates the final deployment handoff for the Streamlit-compatible MVP path.

It is add-only and makes no dashboard or engine change.

The handoff covers:

- final local backup
- repository readiness
- Streamlit entry point
- local launch command
- hosted launch
- synthetic default check
- historical opt-in check
- scenario-not-forecast caution
- customer access control
- post-hosting smoke test

Run:

`app\run_deployment_step_6_deployment_handoff_manual_hosting_check.py`

Use this local Streamlit command before hosting:

`streamlit run app/paid_simulator/config_form_app.py`
