# Phase 3F-3 Repair 5 — Preview Route Model Shape

This repair replaces only `app\paid_simulator\phase3f_customer_preview_route.py`.

It fixes the remaining Phase 3F-3 checker mismatches by making the preview route model expose:

- `marker = PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY`
- `customer_enabled = False`
- at least four preview sections
- at least three guardrails
- a `.to_dict()` method
- a fallback render return value that is a plain dictionary

It does not modify `app\paid_simulator\config_form_app.py`.
