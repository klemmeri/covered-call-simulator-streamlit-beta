# Phase 3I-1 — Post-Activation Browser/Customer Workflow Verification

This checkpoint verifies the controlled public Customer-view activation after Phase 3H without changing dashboard code.

It checks:

- dashboard syntax
- Phase 3H activation evidence
- Phase 3D/3E/3F/3G marker continuity
- customer-facing payoff labels
- guardrails and warning language
- browser checklist generation

The package is read-only with respect to `app\paid_simulator\config_form_app.py`.

Run:

```text
app\run_paid_simulator_phase3i_1_post_activation_browser_check.py
```

Expected result:

```text
Overall Phase 3I-1 checkpoint status: PASS
```
