
# Deployment Step 9 — Streamlit Cloud app setup

This step prepares the manual Streamlit Cloud app setup checklist.

It makes no dashboard or engine change.

Use this Streamlit entry point when creating the app:

`app/paid_simulator/config_form_app.py`

Local run command:

`streamlit run app/paid_simulator/config_form_app.py`

Recommended setup:

1. Confirm the final local backup exists.
2. Confirm the GitHub repository is private for beta/MVP use.
3. Open Streamlit Cloud.
4. Create a new app from the GitHub repository.
5. Set the main file path to `app/paid_simulator/config_form_app.py`.
6. Confirm `requirements.txt` exists in the repository root.
7. Confirm no secrets, broker credentials, tokens, passwords, or payment credentials are committed.
8. Deploy and watch the build logs.
9. Run the hosted smoke-test checklist from Deployment Step 5.

Run:

`app\run_deployment_step_9_streamlit_cloud_app_setup_check.py`
