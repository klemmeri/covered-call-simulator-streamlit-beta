# Phase 3H-3 Marker Repair

This repair addresses a narrow Phase 3H-3 smoke-test failure.

The smoke test passed all structural checks except this one:

```text
FAIL Phase 3H-2 route marker remains present
```

The repair appends an inert compatibility marker to:

```text
app\paid_simulator\config_form_app.py
```

The appended marker is:

```text
PHASE3H_2_PUBLIC_ACTIVATION_ROUTE_READY
```

The public Customer-view activation flag remains disabled:

```text
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False
```

This repair does not expose the public Customer workflow.

Run order:

```text
app\install_phase3h_3_marker_repair.py
app\run_paid_simulator_phase3h_3_activation_route_smoke_test_check.py
```
