# Phase 3E-7B — Customer Workbench Streamlit Panel

This checkpoint adds the Streamlit panel layer for the Phase 3E customer payoff workbench.

It is still guarded:

- It does not expose Phase 3E in the Customer view.
- It does not replace `app\paid_simulator\config_form_app.py`.
- It renders through a Streamlit-like object during the check script, so the checkpoint can run from PyCharm without launching a browser.

## Added files

```text
app\paid_simulator\phase3e_customer_workbench_streamlit_panel.py
app\run_paid_simulator_phase3e_7b_panel_check.py
docs\phase3e_7b_customer_workbench_panel.md
```

## What the panel includes

- Developer-view-only protection notice.
- Customer-facing setup input labels.
- Key payoff metric cards.
- Warning/info boxes.
- Scenario overlay display.
- Save, reload, refresh, and export action labels.
- A Developer-view integration snippet for the eventual dashboard tab.

## Check script

Run:

```text
app\run_paid_simulator_phase3e_7b_panel_check.py
```

Expected final line:

```text
Overall Phase 3E-7B checkpoint status: PASS
```

## Output files

The check writes:

```text
outputs\reports\paid_simulator\phase3e_7b_panel_checkpoint_report.txt
outputs\reports\paid_simulator\phase3e_7b_panel_summary.json
outputs\reports\paid_simulator\phase3e_7b_fake_streamlit_calls.json
outputs\reports\paid_simulator\phase3e_7b_developer_tab_snippet.txt
```

## Next checkpoint

After this passes, the next bundled checkpoint should perform the guarded dashboard-file integration. That is the point where `config_form_app.py` may be backed up and replaced or patched.
