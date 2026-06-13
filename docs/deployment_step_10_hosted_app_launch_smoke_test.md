# Deployment Step 10 — Hosted app launch and smoke-test checklist

This checkpoint creates the manual hosted smoke-test checklist for the deployed
Streamlit app.

It makes no dashboard or engine change.

Use this Streamlit Cloud entry point:

`app/paid_simulator/config_form_app.py`

Manual hosted checks:

1. Confirm the Streamlit Cloud build finishes without errors.
2. Open the hosted app URL.
3. Switch to Customer view.
4. Confirm synthetic scenarios remain the default.
5. Confirm imported historical data is explicit opt-in only.
6. Confirm historical-data caution wording is visible.
7. Run a basic covered-call scenario.
8. Confirm risk wording remains responsible.
9. Optionally open the hosted app in a second browser/private window.

Run:

`app\run_deployment_step_10_hosted_app_launch_smoke_test_check.py`
