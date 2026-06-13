# Phase 3G-4 — Public Customer-view Route Readiness

This checkpoint prepares a public Customer-view route structure for the customer payoff workbench while keeping the ordinary Customer view disabled.

## Added files

```text
app\paid_simulator\phase3g_public_customer_route_readiness.py
app\install_phase3g_4_public_route_readiness.py
app\run_paid_simulator_phase3g_4_route_readiness_check.py
docs\phase3g_4_public_customer_route_readiness.md
```

## What this checkpoint does

1. Adds a public-candidate route-readiness model.
2. Adds a guarded installer that appends a protected helper block to `config_form_app.py`.
3. Creates a timestamped dashboard backup before any dashboard write.
4. Keeps public Customer-view access disabled.
5. Keeps protected preview required.
6. Verifies that Phase 3D, Phase 3E, and Phase 3F markers remain present.

## Installation reminder

Extract the zip directly into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Do not extract into the `app` folder.

## Run order

First run:

```text
app\install_phase3g_4_public_route_readiness.py
```

Then run:

```text
app\run_paid_simulator_phase3g_4_route_readiness_check.py
```

Expected final line:

```text
Overall Phase 3G-4 checkpoint status: PASS
```

## Important guardrail

This checkpoint does **not** enable public Customer view. It only prepares the route-readiness helper and validates that the ordinary Customer view remains protected.
