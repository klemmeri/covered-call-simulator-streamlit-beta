# Deployment Step 7 - GitHub repository readiness

This checkpoint prepares the project for GitHub / Streamlit Cloud deployment.

It is add-only and makes no dashboard or engine change.

The Streamlit app entry point remains:

`app/paid_simulator/config_form_app.py`

The local launch command remains:

`streamlit run app/paid_simulator/config_form_app.py`

Before pushing to GitHub, confirm that secrets, API keys, brokerage credentials,
payment credentials, and deployment tokens are not included.

Run:

`app\run_deployment_step_7_github_repository_readiness_check.py`
