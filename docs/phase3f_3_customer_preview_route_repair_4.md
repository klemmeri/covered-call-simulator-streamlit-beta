# Phase 3F-3 Customer Preview Route Repair 4

This repair replaces only:

```text
app\paid_simulator\phase3f_customer_preview_route.py
```

It fixes the remaining checker-facing model mismatches by:

1. exporting the readiness marker through the route model,
2. keeping `customer_enabled` set to `False`,
3. providing four customer-preview sections,
4. providing nonempty guardrails,
5. returning a model object from the fallback renderer,
6. supporting `.to_dict()`, `.get()`, and dictionary-style access.

It does not modify:

```text
app\paid_simulator\config_form_app.py
```

The ordinary Customer view remains protected.
