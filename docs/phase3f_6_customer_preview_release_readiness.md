# Phase 3F-6 — Customer-Preview Release-Readiness Gate

This checkpoint validates whether the protected customer-preview workflow is structurally ready for a later controlled enablement step.

It does not expose the Phase 3E/3F workflow to the ordinary Customer view.

## Added files

- `app/paid_simulator/phase3f_customer_preview_release_readiness.py`
- `app/run_paid_simulator_phase3f_6_release_readiness_check.py`
- `docs/phase3f_6_customer_preview_release_readiness.md`

## Guardrail rule

The ordinary Customer view remains disabled. Protected preview mode may exist, but public customer release requires a separate explicit checkpoint.

## Run

```text
app\run_paid_simulator_phase3f_6_release_readiness_check.py
```

Expected final line:

```text
Overall Phase 3F-6 checkpoint status: PASS
```
