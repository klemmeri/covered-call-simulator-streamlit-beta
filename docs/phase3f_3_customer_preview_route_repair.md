# Phase 3F-3 Customer Preview Route Repair

This repair replaces only the Phase 3F-3 preview route module.

## Problem repaired

The checkpoint failed on:

```text
Preview route module imports and renders: AttributeError("'NoneType' object has no attribute '__dict__'")
```

That failure is consistent with dynamic import behavior interacting badly with class/dataclass-style module initialization.

## Repair strategy

The replacement module uses plain dictionaries and simple functions only. It keeps the required readiness and customer-protection constants while avoiding import-time structures that can fail under dynamic checkpoint loading.

## Files replaced

```text
app\paid_simulator\phase3f_customer_preview_route.py
```

## Files added

```text
docs\phase3f_3_customer_preview_route_repair.md
```

## Dashboard status

This repair does not modify:

```text
app\paid_simulator\config_form_app.py
```

The Phase 3F-3 installer already added the guarded dashboard helper and created a timestamped backup. Re-run the same Phase 3F-3 checkpoint after installing this repair.
