# Deployment Step 2 - Streamlit entry point and requirements readiness

This step prepares the project for a Streamlit-compatible MVP deployment.

It does not change the dashboard or engine.

## Streamlit entry point

Use this file as the hosted Streamlit entry point:

```text
app/paid_simulator/config_form_app.py
```

Local run command:

```text
streamlit run app/paid_simulator/config_form_app.py
```

## Requirements file

For most Streamlit hosting platforms, the deployment root should include:

```text
requirements.txt
```

This package adds a minimal hosting requirements file with:

```text
streamlit
pandas
numpy
matplotlib
```

The prior `requirements_streamlit_mvp.txt` remains available as the project-specific MVP requirements reference.

## Deployment policy

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Historical data is scenario input, not a forecast.
- Do not add secrets, payment tokens, brokerage credentials, or private keys to the repository.
