# Phase 3F-3 — Guarded Customer Preview Dashboard Route

This checkpoint adds a guarded Customer Preview route helper for the paid simulator dashboard.

## Purpose

Phase 3F-3 prepares a protected customer-preview route without exposing the ordinary Customer view to Phase 3F functionality.

The route is intended for controlled testing before a future release-gate step promotes the workflow into a customer-facing dashboard section.

## Added files

```text
app\paid_simulator\phase3f_customer_preview_route.py
app\install_phase3f_3_customer_preview_route.py
app\run_paid_simulator_phase3f_3_customer_preview_route_check.py
docs\phase3f_3_customer_preview_route.md
```

## Dashboard modification

The installer appends a small protected helper block to:

```text
app\paid_simulator\config_form_app.py
```

The installer creates a timestamped backup before writing:

```text
outputs\backups\paid_simulator
```

## Guardrail

The route sets:

```text
PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = False
```

This means the ordinary Customer view remains protected.

## Required run order

Run the installer first:

```text
app\install_phase3f_3_customer_preview_route.py
```

Then run the checkpoint:

```text
app\run_paid_simulator_phase3f_3_customer_preview_route_check.py
```

Expected final line:

```text
Overall Phase 3F-3 checkpoint status: PASS
```
