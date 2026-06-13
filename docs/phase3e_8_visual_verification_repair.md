# Phase 3E-8 Visual Verification Repair

This repair resolves the Phase 3E-8 checkpoint failure caused by a missing exported panel constant.

## Failure repaired

The checkpoint expected this export:

```python
PHASE3E_PANEL_TITLE
```

The panel module rendered correctly enough for source-label checks, but it did not expose that constant. The repair replaces the panel adapter with a more stable compatibility version that exports:

```python
PHASE3E_PANEL_TITLE
PHASE3E_PANEL_PROTECTION_NOTE
build_panel_render_model
render_phase3e_customer_workbench_panel
```

The renderer accepts both of these parameter styles:

```python
render_phase3e_customer_workbench_panel(streamlit_module=...)
render_phase3e_customer_workbench_panel(st=...)
```

## Safety boundary

This repair does not modify:

```text
app\paid_simulator\config_form_app.py
```

Customer view remains protected.
