# Deployment Step 3 — Local Streamlit launch smoke test

This step prepares the project for a local Streamlit launch before hosted deployment.

It is add-only and makes no dashboard or engine change.

The check verifies:

- the dashboard entry point exists;
- the dashboard entry point has valid Python syntax;
- synthetic scenarios remain visible as the default workflow;
- imported historical data remains visible as an explicit opt-in workflow;
- historical data remains described as scenario input, not a forecast;
- `requirements.txt` and `.streamlit/config.toml` exist;
- core packages are importable;
- the local launch command is written to `deployment_streamlit_local_launch_command.txt`.

Run:

`app\run_deployment_step_3_local_streamlit_launch_smoke_test_check.py`

If the check passes, manually test the dashboard with:

`streamlit run app/paid_simulator/config_form_app.py`

Then open the local URL shown by Streamlit, usually:

`http://localhost:8501`
