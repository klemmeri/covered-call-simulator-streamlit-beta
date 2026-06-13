# Deployment Step 1 - Streamlit MVP preflight

This is the first post-Phase-10 deployment step. It is not a new numbered build phase.

Purpose:

- confirm the project still has the dashboard and core engine files needed for a Streamlit MVP;
- create a separate `requirements_streamlit_mvp.txt` file for deployment review;
- provide a basic `.streamlit/config.toml` suitable for hosted Streamlit-style deployment;
- avoid changing dashboard or engine behavior.

Run:

`app\run_deployment_step_1_streamlit_mvp_preflight_check.py`

Expected final line:

`Overall deployment Step 1 status: PASS`

Next practical step after this passes:

- choose whether to copy `requirements_streamlit_mvp.txt` to root `requirements.txt` for Streamlit deployment;
- identify the Streamlit entry point file to deploy;
- test a hosted app launch.
