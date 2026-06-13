# Phase 3H-2 — Guarded Public Customer-view Activation Route

This checkpoint stages a guarded public Customer-view activation route while keeping the ordinary public Customer view disabled.

## Files added

- `app/paid_simulator/phase3h_public_customer_activation_route.py`
- `app/install_phase3h_2_public_activation_route.py`
- `app/run_paid_simulator_phase3h_2_activation_route_check.py`
- `docs/phase3h_2_public_customer_activation_route.md`

## Safety position

The route is staged, but the public activation flag remains false:

```python
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False
```

This means the code path can be tested without exposing the payoff workbench to the ordinary Customer view.

## Required run order

1. `app/install_phase3h_2_public_activation_route.py`
2. `app/run_paid_simulator_phase3h_2_activation_route_check.py`

## Expected result

```text
Overall Phase 3H-2 checkpoint status: PASS
```
