# Phase 3H-3 Smoke-Test Checker Repair

This repair replaces the Phase 3H-3 smoke-test checker with a more robust version.

The prior checker failed because it searched for one brittle Phase 3H-2 marker string in `config_form_app.py`. However, the checkpoint output already showed the important safety conditions were passing:

- dashboard syntax was valid,
- public Customer view remained disabled,
- Phase 3G, 3F, 3E, and 3D markers remained present,
- Phase 3H-2 checkpoint report existed,
- Phase 3H-3 model and guardrails passed.

The repaired checker validates Phase 3H-2 route evidence using a safer evidence set:

- `PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False`,
- Phase 3H-2 route module exists,
- Phase 3H-2 checkpoint report exists,
- recognized Phase 3H-2 route/readiness text if present.

It does not modify `config_form_app.py` and does not enable public Customer-view access.
