# Phase 3F-8 — Customer-Preview Completion Gate

This checkpoint validates that Phase 3F is complete as a protected customer-preview layer.

It does not enable the ordinary Customer view. It does not modify `config_form_app.py`.

## Added files

- `app/paid_simulator/phase3f_customer_preview_completion_gate.py`
- `app/run_paid_simulator_phase3f_8_completion_gate_check.py`
- `docs/phase3f_8_customer_preview_completion_gate.md`

## Purpose

Phase 3F created a controlled customer-preview path for the Phase 3E customer payoff workbench. This completion gate confirms that the preview structure, guardrails, and public-release constraints are still in place.

## Expected state

- Protected customer preview: available.
- Ordinary Customer view: disabled.
- Public customer release: disabled.
- Dashboard syntax: valid.
- Phase 3D, Phase 3E, and Phase 3F markers: preserved.

## Run

```text
app\run_paid_simulator_phase3f_8_completion_gate_check.py
```

Expected final line:

```text
Overall Phase 3F-8 checkpoint status: PASS
```

## Next step after pass

After this checkpoint passes, Phase 3F can be treated as complete at the protected-preview level. The next phase should be a deliberate public-release preparation phase, not an automatic Customer-view enablement.
