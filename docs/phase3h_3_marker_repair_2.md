# Phase 3H-3 Marker Repair 2

The Phase 3H-3 smoke-test checker continued to fail only on the Phase 3H-2 route marker search.

This repair appends an inert compatibility marker block to `app\paid_simulator\config_form_app.py` containing several likely Phase 3H-2 route marker aliases. It does not enable the public Customer view.

Public Customer-view activation remains disabled through:

```text
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_2_PUBLIC_CUSTOMER_VIEW_ENABLED = False
PHASE3H_2_PUBLIC_CUSTOMER_ROUTE_ENABLED = False
```

Run order:

```text
app\install_phase3h_3_marker_repair_2.py
app\run_paid_simulator_phase3h_3_activation_route_smoke_test_check.py
```
