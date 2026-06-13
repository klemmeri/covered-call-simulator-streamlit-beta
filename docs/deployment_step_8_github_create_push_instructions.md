# Deployment Step 8 - GitHub create/push instructions

This checkpoint creates a practical checklist for creating or updating the GitHub
repository that Streamlit Cloud will use.

It makes no dashboard or engine change.

Recommended first approach:

- create a private GitHub repository first;
- push the Streamlit MVP release candidate;
- use `app/paid_simulator/config_form_app.py` as the Streamlit entry point;
- do not commit secrets, tokens, credentials, or unnecessary generated outputs;
- connect the repository to Streamlit Cloud after the push.

Run:

`app\run_deployment_step_8_github_create_push_instructions_check.py`
