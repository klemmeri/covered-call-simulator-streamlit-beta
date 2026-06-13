# Phase 3J-3 — Final Customer Browser Checklist

This checkpoint creates the final manual browser checklist for the activated customer-facing covered-call payoff workflow.

It does not modify the dashboard. It verifies that the checklist module imports, renders a dictionary model, includes customer-facing payoff terms, and writes a browser checklist under `outputs\reports\paid_simulator`.

Run:

```text
app\run_paid_simulator_phase3j_3_final_browser_check.py
```

Expected final line:

```text
Overall Phase 3J-3 checkpoint status: PASS
```

Afterward, run the dashboard manually:

```text
streamlit run app\paid_simulator\config_form_app.py
```

Use the generated checklist:

```text
outputs\reports\paid_simulator\phase3j_3_final_customer_browser_checklist.md
```
